from django.urls import path
from .views import train_model_with_data,test_model_with_data

urlpatterns = [
    path('api/train/', train_model_with_data, name='train_model_all_data'),
    path('api/test/', test_model_with_data, name='predict_on_new_data'),
]
