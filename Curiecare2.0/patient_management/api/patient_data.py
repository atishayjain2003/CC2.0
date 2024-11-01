import datetime
from typing import Dict, Any, List, Optional

# Configurable Parameters
CONFIG = {
    "Y": 5,        # Days since last contact to trigger certain actions
    "Z": 2,        # Days until admission approaches
    "Final": 3     # Number of follow-up attempts considered final
}

# Define the cohort configuration as a nested dictionary
COHORTS = {
    "A": {
        "name": "Pre-Admission",
        "actionable_buckets": {
            "A1": {
                "name": "New Recommendations",
                "criteria": {"status": "IP Recommended"},
                "actions": ["inform_recommendation", "assess_additional_requirements"],
                "disposition_rules": {
                    "if_clinical_intervention_needed": {
                        "condition": {"clinical_intervention_required": True},
                        "action": "move_to_actionable_bucket",
                        "target_cohort": "A",
                        "target_actionable_bucket": "A2"
                    },
                    "if_quotation_phase_needed": {
                        "condition": {
                            "quotation_phase_required": True,
                            "clinical_intervention_required": False
                        },
                        "action": "move_to_actionable_bucket",
                        "target_cohort": "A",
                        "target_actionable_bucket": "A3"
                    },
                    "if_both_needed": {
                        "condition": {
                            "clinical_intervention_required": True,
                            "quotation_phase_required": True
                        },
                        "action": "move_to_actionable_bucket",
                        "target_cohort": "A",
                        "target_actionable_bucket": "A2"
                    },
                    "if_ready_to_schedule": {
                        "condition": {
                            "clinical_intervention_required": False,
                            "quotation_phase_required": False,
                            "patient_ready": True
                        },
                        "action": "move_to_actionable_bucket",
                        "target_cohort": "A",
                        "target_actionable_bucket": "A4"
                    }
                }
            },
            "A2": {
                "name": "Clinical Intervention",
                "criteria": {"status": "Clinical Intervention Required"},
                "actions": ["schedule_clinical_intervention", "notify_patient_clinical_steps"],
                "disposition_rules": {
                    "on_clinical_intervention_completed_quotation_needed": {
                        "condition": {
                            "clinical_intervention_completed": True,
                            "quotation_phase_required": True
                        },
                        "action": "move_to_actionable_bucket",
                        "target_cohort": "A",
                        "target_actionable_bucket": "A3"
                    },
                    "on_clinical_intervention_completed_no_quotation_needed": {
                        "condition": {
                            "clinical_intervention_completed": True,
                            "quotation_phase_required": False
                        },
                        "action": "move_to_actionable_bucket",
                        "target_cohort": "A",
                        "target_actionable_bucket": "A4"
                    },
                    "on_no_response": {
                        "condition": {
                            "days_since_last_contact": f">= {CONFIG['Y']}",
                            "clinical_intervention_completed": False
                        },
                        "action": "move_to_actionable_bucket",
                        "target_cohort": "C",
                        "target_actionable_bucket": "C2"
                    }
                }
            },
            "A3": {
                "name": "Quotation Phase",
                "criteria": {"status": "Quotation Phase Required"},
                "actions": ["provide_quotation", "discuss_financial_options"],
                "disposition_rules": {
                    "on_quotation_accepted": {
                        "condition": {"quotation_accepted": True},
                        "action": "move_to_actionable_bucket",
                        "target_cohort": "A",
                        "target_actionable_bucket": "A4"
                    },
                    "on_no_response": {
                        "condition": {
                            "days_since_last_contact": f">= {CONFIG['Y']}",
                            "quotation_accepted": False
                        },
                        "action": "move_to_actionable_bucket",
                        "target_cohort": "C",
                        "target_actionable_bucket": "C3"
                    }
                }
            },
            "A4": {
                "name": "Ready to Schedule",
                "criteria": {"status": "Ready to Schedule Admission"},
                "actions": ["follow_up_to_schedule_admission"],
                "disposition_rules": {
                    "on_admission_scheduled": {
                        "condition": {"scheduled_admission": True},
                        "action": "move_to_actionable_bucket",
                        "target_cohort": "B",
                        "target_actionable_bucket": "B1"
                    },
                    "on_no_response": {
                        "condition": {
                            "days_since_last_contact": f">= {CONFIG['Y']}",
                            "scheduled_admission": False
                        },
                        "action": "move_to_actionable_bucket",
                        "target_cohort": "C",
                        "target_actionable_bucket": "C1"
                    }
                }
            }
        }
    },
    "B": {
        "name": "Scheduled Admissions",
        "actionable_buckets": {
            "B1": {
                "name": "Pre-Admission Prep",
                "criteria": {
                    "status": "Admission Scheduled",
                    "scheduled_date_exists": True,
                    "scheduled_date_in_future": True
                },
                "actions": ["provide_pre_admission_instructions", "confirm_admission_details"],
                "disposition_rules": {
                    "when_admission_date_approaches": {
                        "condition": {"days_until_admission": f"<= {CONFIG['Z']}"},
                        "action": "move_to_actionable_bucket",
                        "target_cohort": "B",
                        "target_actionable_bucket": "B2"
                    },
                    "on_admission_postponed": {
                        "condition": {"admission_status": "Postponed"},
                        "action": "move_to_actionable_bucket",
                        "target_cohort": "C",
                        "target_actionable_bucket": "C1"
                    },
                    "on_due_date_passed_without_admission": {
                        "condition": {
                            "scheduled_date_in_past": True,
                            "admission_completed": False
                        },
                        "action": "move_to_actionable_bucket",
                        "target_cohort": "C",
                        "target_actionable_bucket": "C1"
                    }
                }
            },
            "B2": {
                "name": "Admission Soon",
                "criteria": {
                    "status": "Admission Scheduled",
                    "days_until_admission_between": [0, CONFIG['Z']]
                },
                "actions": ["confirm_patient_readiness", "send_admission_reminders"],
                "disposition_rules": {
                    "on_admission_completed": {
                        "condition": {"admission_completed": True},
                        "action": "move_to_actionable_bucket",
                        "target_cohort": "D",
                        "target_actionable_bucket": "D1"
                    },
                    "on_admission_cancelled": {
                        "condition": {"admission_status": "Cancelled"},
                        "action": "move_to_actionable_bucket",
                        "target_cohort": "C",
                        "target_actionable_bucket": "C1"
                    },
                    "on_due_date_passed_without_admission": {
                        "condition": {
                            "scheduled_date_in_past": True,
                            "admission_completed": False
                        },
                        "action": "move_to_actionable_bucket",
                        "target_cohort": "C",
                        "target_actionable_bucket": "C1"
                    }
                }
            }
        }
    },
    "C": {
        "name": "Not Admitted",
        "actionable_buckets": {
            "C1": {
                "name": "Postponed Admissions",
                "criteria": {"status": "Admission Postponed"},
                "actions": ["reschedule_admission_date", "update_patient_instructions"],
                "disposition_rules": {
                    "on_rescheduled": {
                        "condition": {"new_scheduled_date_exists": True},
                        "action": "move_to_actionable_bucket",
                        "target_cohort": "B",
                        "target_actionable_bucket": "B1"
                    },
                    "on_no_response": {
                        "condition": {
                            "days_since_last_contact": f">= {CONFIG['Y']}",
                            "new_scheduled_date_exists": False
                        },
                        "action": "move_to_actionable_bucket",
                        "target_cohort": "E",
                        "target_actionable_bucket": "E1"
                    }
                }
            },
            "C2": {
                "name": "Clinical Stage",
                "criteria": {"status": "Clinical Intervention Required", "admission_completed": False},
                "actions": ["reassess_clinical_requirements", "follow_up_for_intervention"],
                "disposition_rules": {
                    "on_clinical_intervention_completed": {
                        "condition": {"clinical_intervention_completed": True},
                        "action": "move_to_actionable_bucket",
                        "target_cohort": "A",
                        "target_actionable_bucket": "A3"
                    },
                    "on_no_response": {
                        "condition": {
                            "days_since_last_contact": f">= {CONFIG['Y']}"
                        },
                        "action": "move_to_actionable_bucket",
                        "target_cohort": "E",
                        "target_actionable_bucket": "E1"
                    }
                }
            },
            "C3": {
                "name": "Quotation Stage",
                "criteria": {"status": "Quotation Phase Required", "admission_completed": False},
                "actions": ["revisit_quotation", "offer_alternate_financial_options"],
                "disposition_rules": {
                    "on_quotation_accepted": {
                        "condition": {"quotation_accepted": True},
                        "action": "move_to_actionable_bucket",
                        "target_cohort": "A",
                        "target_actionable_bucket": "A4"
                    },
                    "on_no_response": {
                        "condition": {
                            "days_since_last_contact": f">= {CONFIG['Y']}"
                        },
                        "action": "move_to_actionable_bucket",
                        "target_cohort": "E",
                        "target_actionable_bucket": "E1"
                    }
                }
            }
        }
    },
    "D": {
        "name": "Admitted Patients",
        "actionable_buckets": {
            "D1": {
                "name": "Inpatient Transition",
                "criteria": {"status": "Admitted"},
                "actions": ["transition_to_inpatient_care", "update_patient_records"],
                "disposition_rules": {
                    "lead_management_ends": {
                        "condition": {},  # No conditions, end lead management
                        "action": "end_lead_management"
                    }
                }
            }
        }
    },
    "E": {
        "name": "At Risk",
        "actionable_buckets": {
            "E1": {
                "name": "Final Outreach",
                "criteria": {"status": "Unresponsive"},
                "actions": ["make_final_contact_attempts", "assess_non_response_reasons"],
                "disposition_rules": {
                    "on_patient_reengaged": {
                        "condition": {"response_received": True},
                        "action": "move_to_previous_actionable_bucket"
                    },
                    "on_no_response_after_final_attempts": {
                        "condition": {
                            "follow_up_attempts": f">= {CONFIG['Final']}",
                            "response_received": False
                        },
                        "action": "move_to_actionable_bucket",
                        "target_cohort": "E",
                        "target_actionable_bucket": "E2"
                    }
                }
            },
            "E2": {
                "name": "Closure Analysis",
                "criteria": {
                    "status": "Lost",
                    "reason": "Declined or Unresponsive"
                },
                "actions": ["record_loss_reason", "analyze_for_improvement"],
                "disposition_rules": {
                    "lead_management_ends": {
                        "condition": {},  # No conditions, end lead management
                        "action": "end_lead_management"
                    }
                }
            }
        }
    }
}

# Placeholder action functions
def inform_recommendation(patient: Dict[str, Any]):
    print(f"Action: Informing recommendation for patient {patient['id']}.")

def assess_additional_requirements(patient: Dict[str, Any]):
    print(f"Action: Assessing additional requirements for patient {patient['id']}.")

def schedule_clinical_intervention(patient: Dict[str, Any]):
    print(f"Action: Scheduling clinical intervention for patient {patient['id']}.")

def notify_patient_clinical_steps(patient: Dict[str, Any]):
    print(f"Action: Notifying patient {patient['id']} of clinical steps.")

def provide_quotation(patient: Dict[str, Any]):
    print(f"Action: Providing quotation to patient {patient['id']}.")

def discuss_financial_options(patient: Dict[str, Any]):
    print(f"Action: Discussing financial options with patient {patient['id']}.")

def follow_up_to_schedule_admission(patient: Dict[str, Any]):
    print(f"Action: Following up to schedule admission for patient {patient['id']}.")

def provide_pre_admission_instructions(patient: Dict[str, Any]):
    print(f"Action: Providing pre-admission instructions to patient {patient['id']}.")

def confirm_admission_details(patient: Dict[str, Any]):
    print(f"Action: Confirming admission details for patient {patient['id']}.")

def confirm_patient_readiness(patient: Dict[str, Any]):
    print(f"Action: Confirming patient readiness for admission {patient['id']}.")

def send_admission_reminders(patient: Dict[str, Any]):
    print(f"Action: Sending admission reminders to patient {patient['id']}.")

def transition_to_inpatient_care(patient: Dict[str, Any]):
    print(f"Action: Transitioning patient {patient['id']} to inpatient care.")

def update_patient_records(patient: Dict[str, Any]):
    print(f"Action: Updating patient records for patient {patient['id']}.")

def reschedule_admission_date(patient: Dict[str, Any]):
    print(f"Action: Rescheduling admission date for patient {patient['id']}.")

def update_patient_instructions(patient: Dict[str, Any]):
    print(f"Action: Updating patient instructions for patient {patient['id']}.")

def reassess_clinical_requirements(patient: Dict[str, Any]):
    print(f"Action: Reassessing clinical requirements for patient {patient['id']}.")

def follow_up_for_intervention(patient: Dict[str, Any]):
    print(f"Action: Following up for intervention with patient {patient['id']}.")

def revisit_quotation(patient: Dict[str, Any]):
    print(f"Action: Revisiting quotation for patient {patient['id']}.")

def offer_alternate_financial_options(patient: Dict[str, Any]):
    print(f"Action: Offering alternate financial options to patient {patient['id']}.")

def make_final_contact_attempts(patient: Dict[str, Any]):
    print(f"Action: Making final contact attempts to patient {patient['id']}.")

def assess_non_response_reasons(patient: Dict[str, Any]):
    print(f"Action: Assessing non-response reasons for patient {patient['id']}.")

def record_loss_reason(patient: Dict[str, Any]):
    print(f"Action: Recording loss reason for patient {patient['id']}.")

def analyze_for_improvement(patient: Dict[str, Any]):
    print(f"Action: Analyzing for improvement based on patient {patient['id']} data.")

# Mapping of action names to functions
ACTION_MAPPING = {
    "inform_recommendation": inform_recommendation,
    "assess_additional_requirements": assess_additional_requirements,
    "schedule_clinical_intervention": schedule_clinical_intervention,
    "notify_patient_clinical_steps": notify_patient_clinical_steps,
    "provide_quotation": provide_quotation,
    "discuss_financial_options": discuss_financial_options,
    "follow_up_to_schedule_admission": follow_up_to_schedule_admission,
    "provide_pre_admission_instructions": provide_pre_admission_instructions,
    "confirm_admission_details": confirm_admission_details,
    "confirm_patient_readiness": confirm_patient_readiness,
    "send_admission_reminders": send_admission_reminders,
    "transition_to_inpatient_care": transition_to_inpatient_care,
    "update_patient_records": update_patient_records,
    "reschedule_admission_date": reschedule_admission_date,
    "update_patient_instructions": update_patient_instructions,
    "reassess_clinical_requirements": reassess_clinical_requirements,
    "follow_up_for_intervention": follow_up_for_intervention,
    "revisit_quotation": revisit_quotation,
    "offer_alternate_financial_options": offer_alternate_financial_options,
    "make_final_contact_attempts": make_final_contact_attempts,
    "assess_non_response_reasons": assess_non_response_reasons,
    "record_loss_reason": record_loss_reason,
    "analyze_for_improvement": analyze_for_improvement
}

# Function to execute actions
def execute_actions(actions: List[str], patient: Dict[str, Any]):
    for action in actions:
        func = ACTION_MAPPING.get(action)
        if func:
            func(patient)
        else:
            print(f"Action '{action}' not recognized for patient {patient['id']}.")

# Function to evaluate conditions
def evaluate_condition(condition: Dict[str, Any], patient: Dict[str, Any]) -> bool:
    for key, value in condition.items():
        if isinstance(value, str) and value.startswith(">="):
            operator, threshold = value.split()
            try:
                patient_value = int(patient.get(key, 0))
                threshold = int(threshold)
                if operator == ">=" and not (patient_value >= threshold):
                    return False
                elif operator == "<=" and not (patient_value <= threshold):
                    return False
                else:
                    return False  # Unsupported operator
            except ValueError:
                return False
        elif isinstance(value, str) and value.startswith("<="):
            operator, threshold = value.split()
            try:
                patient_value = int(patient.get(key, 0))
                threshold = int(threshold)
                if operator == "<=" and not (patient_value <= threshold):
                    return False
                elif operator == ">=" and not (patient_value >= threshold):
                    return False
                else:
                    return False  # Unsupported operator
            except ValueError:
                return False
        elif key == "follow_up_attempts":
            if isinstance(value, str) and value.startswith(">="):
                operator, threshold = value.split()
                try:
                    patient_value = int(patient.get(key, 0))
                    threshold = int(threshold)
                    if operator == ">=" and not (patient_value >= threshold):
                        return False
                except ValueError:
                    return False
        elif key == "days_until_admission_between":
            if isinstance(value, list) and len(value) == 2:
                lower, upper = value
                patient_value = patient.get("days_until_admission")
                if patient_value is None:
                    return False
                try:
                    patient_value = int(patient_value)
                    lower = int(lower)
                    upper = int(upper)
                    if not (lower <= patient_value <= upper):
                        return False
                except ValueError:
                    return False
        elif key == "scheduled_date_in_past":
            if value:
                scheduled_date = patient.get("scheduled_date")
                if not scheduled_date:
                    return False
                try:
                    scheduled_date_obj = datetime.datetime.strptime(scheduled_date, "%Y-%m-%d").date()
                    today = datetime.date.today()
                    if not (scheduled_date_obj < today):
                        return False
                except ValueError:
                    return False
        elif key == "scheduled_date_in_future":
            if value:
                scheduled_date = patient.get("scheduled_date")
                if not scheduled_date:
                    return False
                try:
                    scheduled_date_obj = datetime.datetime.strptime(scheduled_date, "%Y-%m-%d").date()
                    today = datetime.date.today()
                    if not (scheduled_date_obj > today):
                        return False
                except ValueError:
                    return False
        elif key == "follow_up_date":
            if value == "today":
                today = datetime.date.today().strftime('%Y-%m-%d')
                if patient.get("follow_up_date") != today:
                    return False
        elif key == "reason":
            if patient.get("reason") != value:
                return False
        elif key == "status":
            if patient.get("status") != value:
                return False
        elif key == "admission_status":
            if patient.get("admission_status") != value:
                return False
        elif key == "new_scheduled_date_exists":
            if value and not patient.get("new_scheduled_date"):
                return False
            elif not value and patient.get("new_scheduled_date"):
                return False
        elif key == "response_received":
            if patient.get("response_received") != value:
                return False
        else:
            # Generic equality check
            if patient.get(key) != value:
                return False
    return True

# Function to move patient to a different actionable bucket
def move_to_actionable_bucket(patient: Dict[str, Any], target_cohort: str, target_bucket: str):
    print(f"Moving patient {patient['id']} to cohort {target_cohort} bucket {target_bucket}.")
    patient['current_cohort'] = target_cohort
    patient['current_actionable_bucket'] = target_bucket

# Function to move patient to the previous actionable bucket (used in cohort E1)
def move_to_previous_actionable_bucket(patient: Dict[str, Any]):
    # This function would need logic to determine the previous bucket.
    # For simplicity, let's assume it moves back to a specific cohort and bucket.
    print(f"Re-engaging patient {patient['id']} and moving back to previous actionable bucket.")
    # Example: moving back to Pre-Admission A1
    patient['current_cohort'] = "A"
    patient['current_actionable_bucket'] = "A1"

# Function to end lead management
def end_lead_management(patient: Dict[str, Any]):
    print(f"Ending lead management for patient {patient['id']}.")
    patient['lead_management_active'] = False

# Function to handle disposition actions
def handle_disposition_action(action: str, patient: Dict[str, Any], rule: Dict[str, Any]):
    if action == "move_to_actionable_bucket":
        target_cohort = rule.get("target_cohort")
        target_bucket = rule.get("target_actionable_bucket")
        move_to_actionable_bucket(patient, target_cohort, target_bucket)
    elif action == "move_to_previous_actionable_bucket":
        move_to_previous_actionable_bucket(patient)
    elif action == "end_lead_management":
        end_lead_management(patient)
    else:
        print(f"Disposition action '{action}' not recognized for patient {patient['id']}.")

# Main processing function
def process_patient(patient: Dict[str, Any], cohorts: Dict[str, Any]):
    messages = []
    current_cohort_key = patient.get("current_cohort")
    current_bucket_key = patient.get("current_actionable_bucket")

    if not current_cohort_key or not current_bucket_key:
        messages.append(f"Patient {patient.get('id')} does not have a valid cohort or actionable bucket.")
        return {"messages": messages, "patient_id": patient.get('id')}

    cohort = cohorts.get(current_cohort_key)
    if not cohort:
        messages.append(f"Cohort {current_cohort_key} not found for patient {patient.get('id')}.")
        return {"messages": messages, "patient_id": patient.get('id')}

    bucket = cohort["actionable_buckets"].get(current_bucket_key)
    if not bucket:
        messages.append(f"Actionable bucket {current_bucket_key} not found in cohort {current_cohort_key} for patient {patient.get('id')}.")
        return {"messages": messages, "patient_id": patient.get('id')}

    # Check if patient meets the bucket's criteria
    if not evaluate_condition(bucket.get("criteria", {}), patient):
        messages.append(f"Patient {patient['id']} does not meet the criteria for cohort {current_cohort_key} bucket {current_bucket_key}.")
        return {"messages": messages, "patient_id": patient.get('id')}

    # Execute actions
    execute_actions(bucket.get("actions", []), patient)

    # Evaluate disposition rules
    disposition_rules = bucket.get("disposition_rules", {})
    for rule_name, rule in disposition_rules.items():
        condition = rule.get("condition", {})
        if evaluate_condition(condition, patient):
            action = rule.get("action")
            if action:
                handle_disposition_action(action, patient, rule)
            return {"messages": messages, "patient_id": patient.get('id')}  # Exit after handling one rule

    # If no disposition rules matched, check for actions to end lead management
    if disposition_rules.get("lead_management_ends"):
        handle_disposition_action("end_lead_management", patient, {})

    # Final messages to include in the response
    messages.append("Lead Management Active: True")

    return {
        "messages": messages,
        "patient_id": patient.get('id'),
        "current_cohort": current_cohort_key,  # Reflect the current cohort
        "current_actionable_bucket": current_bucket_key,  # Reflect the current bucket
        "lead_management_active": True
    }


    


    
    

# # # Example patient data
# patients = [
# #     # Scenario 1: New Recommendation Requiring Clinical Intervention
#     {
#         "id": "P001",
#         "current_cohort": "A",
#         "current_actionable_bucket": "A1",
#         "status": "IP Recommended",
#         "clinical_intervention_required": True,
#         "quotation_phase_required": False,
#         "patient_ready": False,
#         "days_since_last_contact": 3
#     },
# #     # Scenario 2: Clinical Intervention Completed with Quotation Needed
# #     {
# #         "id": "P002",
# #         "current_cohort": "A",
# #         "current_actionable_bucket": "A2",
# #         "status": "Clinical Intervention Required",
# #         "clinical_intervention_completed": True,
# #         "quotation_phase_required": True,
# #         "days_since_last_contact": 2
# #     },
# #     # Scenario 3: Quotation Accepted
#     {
#         "id": "P003",
#         "current_cohort": "A",
#         "current_actionable_bucket": "A3",
#         "status": "Quotation Phase Required",
#         "quotation_accepted": True,
#         "days_since_last_contact": 1
#     },
# #     # Scenario 4: Ready to Schedule Admission and Admission Scheduled
#     {
#         "id": "P004",
#         "current_cohort": "A",
#         "current_actionable_bucket": "A4",
#         "status": "Ready to Schedule Admission",
#         "scheduled_admission": True,
#         "days_since_last_contact": 2
#  },
# # #     # Scenario 5: Admission Date Approaching
# #     {
# #         "id": "P005",
# #         "current_cohort": "B",
# #         "current_actionable_bucket": "B1",
# #         "status": "Admission Scheduled",
# #         "scheduled_date_exists": True,
# #         "scheduled_date_in_future": True,
# #         "days_until_admission": 1,
# #         "admission_status": "Scheduled",
# #         "admission_completed": False,
# #         "scheduled_date": (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
# #     },
# #     # Scenario 6: Admission Completed
# #     {
# #         "id": "P006",
# #         "current_cohort": "B",
# #         "current_actionable_bucket": "B2",
# #         "status": "Admission Scheduled",
# #         "days_until_admission_between": [0, CONFIG['Z']],
# #         "admission_completed": True,
# #         "admission_status": "Scheduled",
# #         "scheduled_date": (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
# #     },
# #     # Scenario 7: Admission Postponed
# #     {
# #         "id": "P007",
# #         "current_cohort": "B",
# #         "current_actionable_bucket": "B1",
# #         "status": "Admission Scheduled",
# #         "admission_status": "Postponed",
# #         "days_since_last_contact": 6,
# #         "scheduled_date_in_past": False
# #     },
# #     # Scenario 8: Postponed Admission Rescheduled
# #     {
# #         "id": "P008",
# #         "current_cohort": "C",
# #         "current_actionable_bucket": "C1",
# #         "status": "Admission Postponed",
# #         "new_scheduled_date_exists": True,
# #         "days_since_last_contact": 2,
# #         "new_scheduled_date": (datetime.date.today() + datetime.timedelta(days=3)).strftime('%Y-%m-%d')
# #     },
# #     # Scenario 9: Postponed Admission No Response
# #     {
# #         "id": "P009",
# #         "current_cohort": "C",
# #         "current_actionable_bucket": "C1",
# #         "status": "Admission Postponed",
# #         "new_scheduled_date_exists": False,
# #         "days_since_last_contact": 6
# #     },
# #     # Scenario 10: Final Outreach Patient Reengaged
# #     {
# #         "id": "P010",
# #         "current_cohort": "E",
# #         "current_actionable_bucket": "E1",
# #         "status": "Unresponsive",
# #         "follow_up_attempts": 3,
# #         "response_received": True
# #     },
# #     # Scenario 11: Final Outreach No Response After Final Attempts
# #     {
# #         "id": "P011",
# #         "current_cohort": "E",
# #         "current_actionable_bucket": "E1",
# #         "status": "Unresponsive",
# #         "follow_up_attempts": 3,
# #         "response_received": False
# #     },
# #     # Scenario 12: Admitted Patient Lead Management Ends
# #     {
# #         "id": "P012",
# #         "current_cohort": "D",
# #         "current_actionable_bucket": "D1",
# #         "status": "Admitted"
# #     },
# #     # Additional Scenarios
# #     # Scenario 13: Clinical Intervention Not Completed and No Response
# #     {
# #         "id": "P013",
# #         "current_cohort": "A",
# #         "current_actionable_bucket": "A2",
# #         "status": "Clinical Intervention Required",
# #         "clinical_intervention_completed": False,
# #         "quotation_phase_required": False,
# #         "days_since_last_contact": 7
# #     },
# #     # Scenario 14: Quotation Not Accepted and No Response
# #     {
# #         "id": "P014",
# #         "current_cohort": "A",
# #         "current_actionable_bucket": "A3",
# #         "status": "Quotation Phase Required",
# #         "quotation_accepted": False,
# #         "days_since_last_contact": 6
# #     },
# #     # Scenario 15: Closure Analysis Completed
# #     {
# #         "id": "P015",
# #         "current_cohort": "E",
# #         "current_actionable_bucket": "E2",
# #         "status": "Lost",
# #         "reason": "Declined or Unresponsive"
# #     }
# ]

# # Process each patient
# for patient in patients:
    # print(f"\nProcessing patient {patient['id']}...")
    # process_patient(patient, COHORTS)
    # print(f"Patient {patient['id']} is now in cohort {patient.get('current_cohort')} bucket {patient.get('current_actionable_bucket')}.")
    # print(f"Lead Management Active: {patient.get('lead_management_active', True)}")