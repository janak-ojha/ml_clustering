# cron.py
from datetime import timezone
import logging
import requests
from django.conf import settings
from django.db import transaction
from app.models import TestRawDataMaster

# Configure logger for cron jobs
logger = logging.getLogger('cron')

def run_model_prediction_cron():
    logger.info("Starting model prediction cron job")
    
    try:
        # Get all unique mount_ids that have data with flag=True
        mount_ids = TestRawDataMaster.objects.filter(
            axis='Vertical', 
            flag=False
        ).values_list('mount_id', flat=True).distinct()
        
        if not mount_ids:
            logger.info("No mount_ids found with flag=True. Skipping cron job.")
            return
        
        logger.info(f"Found {len(mount_ids)} mount_ids to process: {list(mount_ids)}")
        
        # Process each mount_id
        for mount_id in mount_ids:
            if mount_id:  # Skip None values
                process_mount_id(mount_id)
        
        logger.info("Model prediction cron job completed successfully")
        logger.info("Data saved in db succesfully")
        
    except Exception as e:
        logger.error(f"Error in model prediction cron job: {str(e)}")
        # You might want to send an alert/notification here



def process_mount_id(mount_id):
    """
    Process a specific mount_id by calling the test_model_with_data API
    """
    try:
        logger.info(f"Processing mount_id: {mount_id}")
        
        # Make internal API call
        # Option 1: Direct function call (recommended for better performance)
        from app.views import test_model_with_data  # Replace with actual import
        from django.http import HttpRequest
        
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

