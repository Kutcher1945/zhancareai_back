from django.contrib.auth.hashers import make_password  # Ensure this import is present
from rest_framework import serializers
from .models import User, Company, Consultation

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

class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.SerializerMethodField()  # ✅ Returns role in Russian

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "phone", "email", "password", "role", "role_display"]
        extra_kwargs = {"password": {"write_only": True}}

    def get_role_display(self, obj):
        return dict(User.ROLE_CHOICES).get(obj.role, "Неизвестно")  # ✅ Show role in Russian

    # def create(self, validated_data):
    #     validated_data["password"] = make_password(validated_data["password"])  # ✅ Hash password
    #     return User.objects.create(**validated_data)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value

    def create(self, validated_data):
        # Save the password as is, without hashing
        return User.objects.create(**validated_data)



class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile details."""
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'phone', 'email',]
        read_only_fields = ['email']  # Email should not be editable


class CompanySerializer(serializers.ModelSerializer):
    """Serializer for company details."""
    class Meta:
        model = Company
        fields = '__all__'
