# cron.py
from datetime import timezone
import logging
import requests
from django.conf import settings
from django.db import transaction
from app.models import RawDataMaster,AccelerationStatTimeOptimized
from django.db.models import Count
from app.views import test_model_with_data ,train_model_with_data ,predict_rms # Replace with actual import
from django.http import HttpRequest


# Configure logger for cron jobs
logger = logging.getLogger('cron')



# prediction cron job

def run_model_prediction_cron_prediction():
    logger.info("Starting model prediction cron job")
    
    try:
        # Get all unique mount_ids that have data with flag=True
        mount_ids = RawDataMaster.objects.filter(
            axis='Vertical', 
            predict_flag=False
        ).values_list('mount_id', flat=True).distinct()
        
        if not mount_ids:
            logger.info("No mount_ids found with flag=True. Skipping cron job.")
            return
        
        logger.info(f"Found {len(mount_ids)} mount_ids to process: {list(mount_ids)}")
        
        # Process each mount_id
        for mount_id in mount_ids:
            if mount_id:  # Skip None values
                process_mount_id_prediction(mount_id)
        
        logger.info("Model prediction cron job completed successfully")
        logger.info("Data saved in db succesfully")
        
    except Exception as e:
        logger.error(f"Error in model prediction cron job: {str(e)}")
        # You might want to send an alert/notification here



def process_mount_id_prediction(mount_id):
    """
    Process a specific mount_id by calling the test_model_with_data API
    """
    try:
        logger.info(f"Processing mount_id: {mount_id}")
        # Create a mock request object
        request = HttpRequest()
        request.method = 'GET'
        request.GET = {'mount_id': mount_id}
        
        # Call the function directly
        response = test_model_with_data(request)
        
        if response.status_code == 200:
            logger.info(f"Successfully processed mount_id: {mount_id}")
        else:
            logger.error(f"Failed to process mount_id: {mount_id}, Status: {response.status_code}, Data: {response.data}")
            
    except Exception as e:
        logger.error(f"Error processing mount_id {mount_id}: {str(e)}")




# training cron job
def run_model_prediction_cron_training():
    logger.info("Starting model prediction cron job")
    
    try:
        # Get all unique mount_ids that have data with flag=True
        mount_ids = (
            RawDataMaster.objects
            .filter(axis='Vertical', train_flag=False)
            .values_list('mount_id', flat=True)
            .distinct()
        )
        
        if not mount_ids:
            logger.info("No mount_ids found with flag=True. Skipping cron job.")
            return
        
        logger.info(f"Found {len(mount_ids)} mount_ids to process: {list(mount_ids)}")
        
        # Process each mount_id
        for mount_id in mount_ids:
            if mount_id:  # Skip None values
                process_mount_id_training(mount_id)
        
        logger.info("Model prediction cron job completed successfully")
        logger.info("Data saved in db succesfully")
        
    except Exception as e:
        logger.error(f"Error in model prediction cron job: {str(e)}")
        # You might want to send an alert/notification here




def process_mount_id_training(mount_id):
    """
    Process a specific mount_id by calling the test_model_with_data API
    """
    try:
        logger.info(f"Processing mount_id: {mount_id}")
        
        # Create a mock request object
        request = HttpRequest()
        request.method = 'GET'
        request.GET = {'mount_id': mount_id}
        
        # Call the function directly
        response = train_model_with_data(request)
        
        if response.status_code == 200:
            logger.info(f"Successfully processed mount_id: {mount_id}")
        else:
            logger.error(f"Failed to process mount_id: {mount_id}, Status: {response.status_code}, Data: {response.data}")
            
    except Exception as e:
        logger.error(f"Error processing mount_id {mount_id}: {str(e)}")




def run_model_prediction_cron_prediction_rms():
    logger.info("Starting model prediction cron job")
    
    try:
        # Get all unique mount_ids that have data with flag=True
        mount_ids = AccelerationStatTimeOptimized.objects.filter(
            cluster_flag=False
        ).values_list('mount_id', flat=True).distinct()
        
        if not mount_ids:
            logger.info("No mount_ids found with flag=True. Skipping cron job.")
            return
        
        logger.info(f"Found {len(mount_ids)} mount_ids to process: {list(mount_ids)}")
        
        # Process each mount_id
        for mount_id in mount_ids:
            if mount_id:  # Skip None values
                process_mount_id_prediction_rms(mount_id)
        
        logger.info("Model prediction cron job completed successfully")
        logger.info("Data saved in db succesfully")
        
    except Exception as e:
        logger.error(f"Error in model prediction cron job: {str(e)}")
        # You might want to send an alert/notification here




def process_mount_id_prediction_rms(mount_id):
    """
    Process a specific mount_id by calling the test_model_with_data API
    """
    try:
        logger.info(f"Processing mount_id: {mount_id}")
        
        # Create a mock request object
        request = HttpRequest()
        request.method = 'GET'
        request.GET = {'mount_id': mount_id}
        
        # Call the function directly
        response = predict_rms(request)
        
        if response.status_code == 200:
            logger.info(f"Successfully processed mount_id: {mount_id}")
        else:
            logger.error(f"Failed to process mount_id: {mount_id}, Status: {response.status_code}, Data: {response.data}")
            
    except Exception as e:
        logger.error(f"Error processing mount_id {mount_id}: {str(e)}")

