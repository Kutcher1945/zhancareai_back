from rest_framework import serializers
from .models import Consultation

class ConsultationSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.first_name", read_only=True)
    doctor_name = serializers.CharField(source="doctor.first_name", read_only=True)

    class Meta:
        model = Consultation
        fields = [
            "id", "patient", "doctor", "patient_name", "doctor_name", "meeting_id",
            "status", "started_at", "ended_at", "created_at"
        ]
        read_only_fields = ["started_at", "ended_at", "created_at"]