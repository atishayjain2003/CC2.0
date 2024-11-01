import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .patient_data import COHORTS, process_patient
from .models import Patient
from .serializers import PatientSerializer

@csrf_exempt
def process_patient_view(request):
    if request.method == 'POST':
        try:
            # Load the patient data from the request body
            patient_data = json.loads(request.body)
            if not patient_data:
                return JsonResponse({"error": "Received empty data"}, status=400)

            # Validate and save the patient data
            serializer = PatientSerializer(data=patient_data)
            if serializer.is_valid():
                patient = serializer.save()

                # Call process_patient and get the response
                response_data = process_patient(patient_data, COHORTS)

                # Check if response_data contains messages
                if 'messages' in response_data:
                    return JsonResponse({
                        "messages": response_data["messages"],
                        "patient_id": patient.id,
                        "current_cohort": response_data.get("current_cohort", patient_data["current_cohort"]),
                        "current_actionable_bucket": response_data.get("current_actionable_bucket", patient_data["current_actionable_bucket"]),
                        "lead_management_active": response_data.get("lead_management_active", True)
                    }, status=200)
                else:
                    return JsonResponse({"error": "No messages returned from processing."}, status=400)

            # If the serializer is invalid, return the errors
            return JsonResponse(serializer.errors, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    # Handle non-POST requests
    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)
