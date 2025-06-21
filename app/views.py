import pandas as pd
import numpy as np
from rest_framework.decorators import api_view
from rest_framework.response import Response
from app.utils import extract_psd_featuresv, split_and_add_timestamps,parse_raw_queryset_to_df,perform_gmm_clustering,predict_gmm_clusters,assign_cluster_labels,save_operating_mode_data,add_rms_column,assign_cluster_labelrms,assign_mode_labels_rms_Vertical
from .models import TestRawDataMaster,RawDataMaster,AssetOperatingModeMaster,AccelerationStatTimeOptimized
import logging
from rest_framework.exceptions import ValidationError
from django.db.models import Count
logger = logging.getLogger(__name__)



# api for training and saving model
@api_view(['GET'])
def train_model_with_data(request):
    mount_id = request.GET.get('mount_id')
    if not mount_id:
        logger.error("mount_id parameter is required")
        return Response({"error": "mount_id parameter is required"}, status=400)

    raw_queryset = TestRawDataMaster.objects.filter(
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
        logger.info(f"DataFrame created with {df.head(50)} records")
    except ValueError as e:
        logger.error(f"Data parsing error: {e}")
        return Response({"error": str(e)}, status=500)

    # Step: Split into windows
    try:
        split_df = split_and_add_timestamps(df)
        logger.info(f"Split data into time windows, resulting shape: {split_df.shape}")
    except Exception as e:
        logger.error(f"Windowing error: {e}")
        return Response({"error": f"Windowing error: {e}"}, status=500)

    # Step: Extract PSD features
    try:
        psd_df = extract_psd_featuresv(split_df)
        logger.info(f"Extracted PSD features, resulting shape: {psd_df.shape}")
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
        split_df = split_and_add_timestamps(df)
        # df_time_stamp_mid = split_df.drop(['axis', 'no_of_samples', 'fs', 'raw_data'], axis=1)
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
    



# def predict_rms(request):
@api_view(['GET'])
def predict_rms(request):
    mount_id = request.GET.get('mount_id')
    if not mount_id:
        logger.error("mount_id parameter is required")
        return Response({"error": "mount_id parameter is required"}, status=400)

    try:
        # Fetch TestRawDataMaster data
        raw_queryset = TestRawDataMaster.objects.filter(
            mount_id=mount_id, axis='Vertical'
        ).values('raw_data', 'timestamp', 'fs').order_by('timestamp')

        if not raw_queryset.exists():
            logger.error(f"No raw data found for mount_id = {mount_id}")
            return Response({"error": "No raw data found"}, status=404)

        df = pd.DataFrame(list(raw_queryset))
        logger.info(f"Raw data shape: {df.shape}")
        logger.debug(df.head().to_string())

        # Add RMS column
        rms_df = add_rms_column(df)
        logger.info(f"RMS computed for raw data, shape: {rms_df.shape}")

        # Fetch AssetOperatingModeMaster data
        asset_queryset = AssetOperatingModeMaster.objects.filter(
            mount_id=mount_id
        ).values('mount_id', 'cluster_id').order_by('timestamp')

        if not asset_queryset.exists():
            logger.error(f"No asset operating mode data found for mount_id = {mount_id}")
            return Response({"error": "No asset operating mode data found"}, status=404)

        df_new = pd.DataFrame(list(asset_queryset))
        logger.info(f"Operating mode data shape: {df_new.shape}")

        # Combine and assign cluster label
        combined_psd_df = pd.concat([rms_df, df_new], axis=1)
        logger.info("Combined data for cluster label assignment")

        dict_rms_avg = assign_cluster_labelrms(combined_psd_df)
        logger.info(f"Cluster RMS averages: {dict_rms_avg}")

        # Fetch AccelerationStatTimeOptimized data
        rms_value_queryset = AccelerationStatTimeOptimized.objects.filter(
            mount_id=mount_id, rms_only=True
        ).values('timestamp', 'mount_id', 'rms_vertical','asset_id','composite').order_by('timestamp')

        if not rms_value_queryset.exists():
            logger.error(f"No RMS vertical values found for mount_id = {mount_id}")
            return Response({"error": "No RMS values found"}, status=404)

        rms_df = pd.DataFrame(list(rms_value_queryset))
        logger.info(f"RMS values shape: {rms_df.shape}")
        logger.debug(rms_df.head().to_string())

        # Assign mode labels
        updated_rms_mode = assign_mode_labels_rms_Vertical(rms_df, dict_rms_avg)
        logger.info("RMS mode assignment completed")
        # print(updated_rms_mode.iloc[200:250,:])
        
        try:
            saved_count = save_operating_mode_data(updated_rms_mode, mount_id)
        except ValidationError as ve:
              return Response({"error": "Validation failed", "details": ve.detail}, status=400)


        return Response({
        "message": "Prediction and save successful",
        "saved_records": saved_count,
         })
     

    except Exception as e:
        logger.exception("Error occurred in predict_rms view")
        return Response({"error": str(e)}, status=500)




@api_view(['GET'])
def operating_mode_count(request):
    logger.info("API request received for operating_mode_count.")

    mount_id = request.GET.get('mount_id')
    logger.debug(f"Received mount_id: {mount_id}")

    if not mount_id:
        logger.warning("No mount_id provided in request.")
        return Response({"error": "mount_id is required"}, status=400)

    try:
        logger.info(f"Fetching operating_mode counts for mount_id={mount_id}")
        counts = (
            AssetOperatingModeMaster.objects
            .filter(mount_id=mount_id)
            .values('operating_mode')
            .annotate(count=Count('operating_mode'))
            .order_by('-count')
        )

        if not counts:
            logger.info(f"No data found for mount_id={mount_id}")
            return Response({"message": f"No data found for mount_id {mount_id}"}, status=404)

        logger.info(f"Query successful. Found {len(counts)} operating_mode groups for mount_id={mount_id}")
        return Response(counts)

    except Exception as e:
        logger.exception("Error occurred while fetching operating mode counts.")
        return Response({"error": "An error occurred while processing your request."}, status=500)
