from django.contrib.auth.hashers import make_password  # Ensure this import is present
from rest_framework import serializers
from .models import User, Company

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'phone', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True},  # Ensure password is write-only
        }

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
