from django.urls import path
from .views import process_patient_view  # Ensure you import your view

urlpatterns = [
    path('process-patient/', process_patient_view, name='process_patient'),
]
