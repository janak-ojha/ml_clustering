import pandas as pd
import numpy as np
from scipy.signal import welch
from rest_framework.decorators import api_view
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
import pickle
from django.conf import settings
import logging
import os
from .models import TestRawDataMaster
from datetime import datetime
from django.utils import timezone
import logging
from .serializers import AssetOperatingModeMasterSerializer
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime
import logging
logger= logging.getLogger(__name__)



#make raw data into data frame
def parse_raw_queryset_to_df(raw_queryset):
    parsed_data = []
    for record in raw_queryset:
        try:
            parsed_record = {
                'timestamp': record['timestamp'],
                'fs': float(record['fs']),
                'no_of_samples': int(record['no_of_samples']),
                'raw_data': list(map(float, record['raw_data'])),
                'axis': record['axis'],
                'mount_id': record['mount_id'],
                'composite': record['composite'],
                'asset_id': record['asset_id'],
            }
            parsed_data.append(parsed_record)
        except Exception as e:
            logger.error(f"Data parsing error for record {record}: {e}")
            raise ValueError(f"Data parsing error: {e}")

    df = pd.DataFrame(parsed_data)
    logger.info(f"Parsed {len(df)} records into DataFrame")
    return df



def split_and_add_timestamps(df, n_splits=4, min_remain_ratio=0.3):
    """
    Splits raw_data into approximately `n_splits` parts.
    If the last part is smaller than `min_remain_ratio` of window size,
    it is merged with the previous part.

    Args:
        df (pd.DataFrame): Input DataFrame.
        n_splits (int): Desired number of splits per raw_data.
        min_remain_ratio (float): Minimum remainder threshold for splitting.

    Returns:
        pd.DataFrame or dict: Windowed segments DataFrame or error dict.
    """
    all_windows = []

    try:
        # Convert to safe integer
        n_splits = int(float(n_splits)) if n_splits else 0
        if n_splits <= 0:
            logger.warning("Invalid n_splits value received, defaulting to 4.")
            n_splits = 4  # fallback default

        for index, row in df.iterrows():
            try:
                raw_data = np.array(row['raw_data'])
                fs = float(row['fs'])
                total_samples = int(len(raw_data))

                if pd.isnull(fs) or fs <= 0 or total_samples < n_splits:
                    logger.warning(f"Skipping row {index}: Invalid fs or not enough samples.")
                    continue

                base_window_size = total_samples // n_splits
                remaining_samples = total_samples % n_splits

                merge_remainder = (
                    (remaining_samples / base_window_size) < min_remain_ratio
                    if base_window_size > 0 else True
                )

                # Get timestamp
                timestamp_raw = row.get('timestamp')
                if hasattr(timestamp_raw, 'timestamp'):
                    base_timestamp = int(timestamp_raw.timestamp())
                else:
                    base_timestamp = int(float(timestamp_raw))

                split_indices = []

                for i in range(n_splits):
                    start_idx = int(i * base_window_size)
                    end_idx = int(start_idx + base_window_size)

                    if i == n_splits - 1:
                        if merge_remainder and remaining_samples > 0:
                            end_idx = total_samples  # Merge remainder
                        elif not merge_remainder and remaining_samples > 0:
                            split_indices.append((start_idx, end_idx))
                            split_indices.append((end_idx, total_samples))
                            break

                    split_indices.append((start_idx, min(end_idx, total_samples)))

                for start_idx, end_idx in split_indices:
                    window_data = raw_data[int(start_idx):int(end_idx)]
                    all_windows.append({
                        'timestamp': base_timestamp,
                        'mount_id': row.get('mount_id'),
                        'composite': row.get('composite', None),
                        'asset_id': row.get('asset_id', None),
                        'axis': row.get('axis'),
                        'no_of_samples': int(len(window_data)),
                        'fs': fs,
                        'raw_data': window_data.tolist()
                    })

            except Exception as e:
                logger.exception(f"Windowing error on row {index}: {e}")
                continue  # Skip row instead of failing all

        return pd.DataFrame(all_windows)

    except Exception as e:
        logger.exception(f"Critical error in split_and_add_timestamps: {e}")
        return {"error": f"Windowing error: {e}"}



def extract_psd_featuresv(df, series_col='raw_data', fs_col='fs', num_coeffs=65, nperseg=128):
    
    psd_feature_dicts = []

    for i, row in enumerate(df[series_col]):
        try:
            data = np.array(row)
            fs = df[fs_col].iloc[i]

            # Use min between nperseg and data length to avoid warnings
            current_nperseg = min(nperseg, len(data))

            if len(data) < 4:  # very short signal, Welch may fail
                print(f"Skipping row {i}: too short ({len(data)} samples)")
                psd_dict = {f"V_coeff_{j+1}": None for j in range(num_coeffs)}
            else:
                f, psd = welch(data, fs=fs, nperseg=current_nperseg)
                psd *= 1e6  # optional scaling

                # Pad or truncate to get exactly num_coeffs
                psd_padded = np.pad(psd, (0, max(0, num_coeffs - len(psd))), 'constant')[:num_coeffs]

                psd_dict = {f"V_coeff_{j+1}": psd_padded[j] for j in range(num_coeffs)}

        except Exception as e:
            print(f"Error at row {i}: {e}")
            psd_dict = {f"V_coeff_{j+1}": None for j in range(num_coeffs)}

        psd_feature_dicts.append(psd_dict)

    return pd.DataFrame(psd_feature_dicts)




# make gmm clustering model
def perform_gmm_clustering(psd_df, mount_id, logger):
    # Clean NaNs
    psd_df_clean = psd_df.dropna()
    logger.info(f"Dropped NaNs from PSD features, clean shape: {psd_df_clean.shape}")    
    # Scale
    scaler = MinMaxScaler()
    scaled_features = scaler.fit_transform(psd_df_clean)
    logger.info("Scaled features using MinMaxScaler")

    # PCA
    pca_full = PCA().fit(scaled_features)
    cumulative_variance = np.cumsum(pca_full.explained_variance_ratio_)
    target_range = (0.90, 0.99)
    indices_in_range = np.where((cumulative_variance >= target_range[0]) & (cumulative_variance <= target_range[1]))[0]

    if len(indices_in_range) == 0:
        raise ValueError("No PCA components found in the variance range 0.90 to 0.99")

    best_index = indices_in_range[np.argmax(cumulative_variance[indices_in_range])]
    n_components_best = best_index + 1
    logger.info(f"Selected {n_components_best} PCA components with cumulative variance: {cumulative_variance[best_index]:.4f}")

    # Apply PCA
    pca = PCA(n_components=n_components_best)
    X_pca = pca.fit_transform(scaled_features)
    logger.info(f"Applied PCA, reduced shape: {X_pca.shape}")

    # Fit GMM using BIC
    best_gmm = None
    lowest_bic = float('inf')
    gmm_models = []

    for n in range(2, 11):
        for cov_type in ['full']:    
            gmm = GaussianMixture(n_components=n, covariance_type='full', random_state=42)
            gmm.fit(X_pca)
            bic = gmm.bic(X_pca)
            gmm_models.append((bic, gmm))
            if bic < lowest_bic:
                best_gmm = gmm
                lowest_bic = bic

               # Enforce maximum 4 clusters
    if best_gmm.n_components > 4:
       logger.info(f"Best GMM had {best_gmm.n_components} clusters, capping to 4.")
       best_gmm = GaussianMixture(n_components=4, covariance_type='full', random_state=42)
       best_gmm.fit(X_pca)   

    best_n_clusters = best_gmm.n_components
    best_cov_type = best_gmm.covariance_type
    logger.info(f"Final GMM selected with {best_n_clusters} clusters and covariance type '{best_cov_type}'")

    # Save model
    model_dir = os.path.join(settings.BASE_DIR, 'saved_models')
    os.makedirs(model_dir, exist_ok=True)

    model_filename = f'gmm_model_mount_{mount_id}.pickle'
    model_path = os.path.join(model_dir, model_filename)

    with open(model_path, 'wb') as f:
        pickle.dump({
            "gmm_model": best_gmm,
            "scaler": scaler,
            "pca": pca
        }, f)

    logger.info(f"Saved trained model to {model_path}")

    return best_n_clusters, model_filename




#predict the new data
def predict_gmm_clusters(psd_df_clean, mount_id):
    try:
        logger.debug(psd_df_clean.head())

        test_df = psd_df_clean.drop(['timestamp', 'mount_id', 'composite','asset_id'], axis=1)

        model_path = os.path.join(settings.BASE_DIR, 'saved_models', f'gmm_model_mount_{mount_id}.pickle')
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Trained model not found at {model_path}")

        with open(model_path, 'rb') as f:
            model_bundle = pickle.load(f)
            gmm_model = model_bundle["gmm_model"]
            scaler = model_bundle["scaler"]
            pca = model_bundle["pca"]

        scaled_features = scaler.transform(test_df)
        X_pca = pca.transform(scaled_features)

        cluster_labels = gmm_model.predict(X_pca)

        psd_df_clean['cluster_id'] = cluster_labels
       
        psd_df_clean['v_coeff_mean'] = psd_df_clean.loc[:, 'V_coeff_1':'V_coeff_65'].mean(axis=1)

     
        logger.info(f"Predicted clusters for {len(cluster_labels)} samples")

        # Prepare result DataFrame
        result_df = psd_df_clean.copy()

        # Mark raw data flags as False
        used_timestamps = psd_df_clean['timestamp'].apply(
            lambda x: timezone.make_aware(datetime.fromtimestamp(int(x)))
        ).tolist()

       # Adjust import as per your project
        TestRawDataMaster.objects.filter(
            mount_id=mount_id,
            timestamp__in=used_timestamps,
            flag=False
        ).update(flag=True)
        logger.info(f"Updated flag to False for {len(used_timestamps)} timestamps")

        return result_df

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise




#provide label to cluster
def assign_cluster_labels(df, score_col='v_coeff_mean', cluster_col='cluster_id', labels=['off_mode', 'mode_1', 'mode_2', 'mode_3']):
    
    n_clusters = df[cluster_col].nunique()

    if n_clusters > len(labels):
        raise ValueError(f"Found {n_clusters} clusters, but only {len(labels)} labels are provided.")

    # Step 1: Group by cluster and compute mean score
    cluster_avg = df.groupby(cluster_col)[score_col].mean().sort_values()
  
    # Step 2: Create mapping of cluster to label (taking only required number of labels)
    selected_labels = labels[:n_clusters]
    cluster_label_map = {cluster: label for cluster, label in zip(cluster_avg.index, selected_labels)}
    
    # Step 3: Map labels to the original DataFrame
    df['operating_mode'] = df[cluster_col].map(cluster_label_map)
    
    return df



#save data into db
def save_operating_mode_data(result_df, mount_id):
    """
    Converts the result DataFrame into model records and saves using the serializer.
    Keeps only one row per duplicated timestamp.
    """
    # Keep only the required columns
    new_df = result_df[['timestamp', 'mount_id', 'asset_id', 'composite', 'operating_mode', 'cluster_id']].copy()

    # Drop duplicates — keep only the first occurrence of each timestamp
    new_df = new_df.drop_duplicates(subset='timestamp', keep='first')
    logger.info("Dropped duplicate timestamps, keeping only one occurrence of each.")

    # Create records
    records = []
    for _, row in new_df.iterrows():
        try:
            record = {
                'timestamp': timezone.make_aware(datetime.fromtimestamp(int(row['timestamp']))),
                'mount_id': mount_id,
                'asset_id': row.get('asset_id'),
                'composite': row.get('composite'),
                'operating_mode': row.get('operating_mode', None),
                'cluster_id': str(row.get('cluster_id')),
            }
            records.append(record)
        except Exception as e:
            logger.warning(f"Skipping row due to error: {e}")

    # If nothing to save
    if not records:
        logger.warning("No valid records to save.")
        return 0

    # Save via serializer
    serializer = AssetOperatingModeMasterSerializer(data=records, many=True)
    if serializer.is_valid():
        serializer.save()
        logger.info(f"Saved {len(records)} records to AssetOperatingModeMaster")
        return len(records)
    else:
        logger.error(f"Serializer validation failed: {serializer.errors}")
        raise ValidationError(serializer.errors)
