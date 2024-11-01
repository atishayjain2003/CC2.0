from django.db import models

class Patient(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    current_cohort = models.CharField(max_length=10)
    current_actionable_bucket = models.CharField(max_length=10)
    status = models.CharField(max_length=50)
    clinical_intervention_required = models.BooleanField(default=False)
    quotation_phase_required = models.BooleanField(default=False)
    patient_ready = models.BooleanField(default=False)
    days_since_last_contact = models.IntegerField(default=0)
    quotation_accepted=models.BooleanField(default=False)
    lead_management_active = models.BooleanField(default=True)
    def __str__(self):
        return self.id
