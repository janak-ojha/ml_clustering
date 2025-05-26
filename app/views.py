import pandas as pd
import numpy as np
from rest_framework.decorators import api_view
from rest_framework.response import Response
from app.utils import extract_psd_featuresv, split_and_add_timestamps,parse_raw_queryset_to_df,perform_gmm_clustering,predict_gmm_clusters,assign_cluster_labels,save_operating_mode_data
from .models import TestRawDataMaster,RawDataMaster
import logging
from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)



# api for training and saving model
@api_view(['GET'])
def train_model_with_data(request):
    mount_id = request.GET.get('mount_id')
    if not mount_id:
        logger.error("mount_id parameter is required")
        return Response({"error": "mount_id parameter is required"}, status=400)

    raw_queryset = RawDataMaster.objects.filter(
        mount_id=mount_id,
        axis='Vertical'
    ).values('timestamp', 'fs', 'no_of_samples', 'raw_data', 'axis', 'mount_id','composite','asset_id' ).order_by('timestamp')

    print("length of raw query", len(raw_queryset))

    if not raw_queryset:
        logger.warning(f"No data found for mount_id: {mount_id}")
        return Response({"message": "No data found for the given mount_id"}, status=404)

    # Step: Parse raw_queryset to DataFrame
    try:
        df = parse_raw_queryset_to_df(raw_queryset)
        logger.info(f"DataFrame created with {df.head()} records")
        print(df.head(20))
    except ValueError as e:
        logger.error(f"Data parsing error: {e}")
        return Response({"error": str(e)}, status=500)

    # Step: Split into windows
    try:
        split_df = split_and_add_timestamps(df)
        logger.info(f"Split data into time windows, resulting shape: {split_df.shape}")
        print(split_df.head(20))
    except Exception as e:
        logger.error(f"Windowing error: {e}")
        return Response({"error": f"Windowing error: {e}"}, status=500)

    # Step: Extract PSD features
    try:
        psd_df = extract_psd_featuresv(split_df)
        logger.info(f"Extracted PSD features, resulting shape: {psd_df.shape}")
        print(psd_df.head(20))
    except Exception as e:
        logger.error(f"PSD extraction error: {e}")
        return Response({"error": f"PSD extraction error: {e}"}, status=500)

    # Step: Apply GMM clustering
    try:
        best_n_clusters, model_filename = perform_gmm_clustering(psd_df, mount_id, logger)
    except Exception as e:
       logger.error(f"GMM/BIC error: {e}")
       return Response({"error": f"GMM/BIC error: {e}"}, status=500)


    return Response({
        "message": "Training and Clustering completed successfully",
        "clusters_found": best_n_clusters,
        "model_file": model_filename
    })





#api for prediction and saving data with label
@api_view(['GET'])
def test_model_with_data(request):
    mount_id = request.GET.get('mount_id')
    if not mount_id:
        logger.error("mount_id parameter is required")
        return Response({"error": "mount_id parameter is required"}, status=400)

    logger.info(f"Testing model with data for mount_id: {mount_id}")

    raw_queryset = TestRawDataMaster.objects.filter(
        mount_id=mount_id, axis='Vertical', flag=False,
    ).values('timestamp', 'fs', 'no_of_samples', 'raw_data', 'axis', 'mount_id','composite','asset_id')

    if not raw_queryset:
        logger.warning(f"No data found with flag=True for mount_id: {mount_id}")
        return Response({"message": "No data found for the given mount_id"}, status=404)
    
    # Step: Parse raw_queryset to DataFrame
    try:
        df = parse_raw_queryset_to_df(raw_queryset)
        logger.info(f"DataFrame created with {len(df)} records")
    except ValueError as e:
        logger.error(f"Data parsing error: {e}")
        return Response({"error": str(e)}, status=500)
    
     # Step: Split into windows
    try:
        window_duration = 0.079  # seconds
        split_df = split_and_add_timestamps(df, window_duration)
        logger.info(f"Split data into windows, shape: {split_df.shape}")
    except Exception as e:
        logger.error(f"Windowing error: {e}")
        return Response({"error": f"Windowing error: {e}"}, status=500)
    
    # Step: Extract PSD features
    try:
        psd_df = extract_psd_featuresv(split_df)
        df_time_stamp_mid = split_df.drop(['axis', 'no_of_samples', 'fs', 'raw_data'], axis=1)
        psd_df_clean = pd.concat([df_time_stamp_mid, psd_df], axis=1)
        logger.info(f"Extracted PSD features and combined data, shape: {psd_df_clean.shape}")
    except Exception as e:
        logger.error(f"PSD extraction error: {e}")
        return Response({"error": f"PSD extraction error: {e}"}, status=500)
    
    # Step: Apply GMM prediction
    try:
       new_df = predict_gmm_clusters(psd_df_clean, mount_id)
    except Exception as e:
       return Response({"error": f"Prediction error: {e}"}, status=500)
    
    # Assign  labels based on test_score and cluster
    try:
        
        result = assign_cluster_labels(new_df, score_col='v_coeff_mean', cluster_col='cluster_id')
        logger.info(f"sassshape, shape: {result.shape}")
        logger.info("Status labels assigned based on test_score")
    except Exception as e:
        logger.warning(f"Could not assign status labels: {e}")

    #saving to db   
    try:
        saved_count = save_operating_mode_data(result, mount_id)
    except ValidationError as ve:
        return Response({"error": "Validation failed", "details": ve.detail}, status=400)


    return Response({
        "message": "Prediction and save successful",
        "saved_records": saved_count,
        
    })
    



