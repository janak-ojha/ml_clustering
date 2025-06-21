from django.urls import path
from .views import train_model_with_data,test_model_with_data,predict_rms,operating_mode_count

urlpatterns = [
    path('api/train/', train_model_with_data, name='train_model_all_data'),
    path('api/test/', test_model_with_data, name='predict_on_new_data'),
    path('api/predict_mode_rms/',predict_rms,name='predict mode with rms value'),
    path('api/operating_mode_count/', operating_mode_count, name='operating_mode_count'),
    
    
]
