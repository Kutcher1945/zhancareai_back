import logging
from drf_yasg import openapi
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Q
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password, check_password
from .models import User, Company, CustomToken, Consultation
from .serializers import UserSerializer, CompanySerializer, UserProfileSerializer, ConsultationSerializer
from .permissions import IsDoctor, IsAdmin
import uuid
from django.utils import timezone

# Set up logging
logger = logging.getLogger(__name__)

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @swagger_auto_schema(
        operation_description="Register a new user",
        request_body=UserSerializer,
        responses={201: "User registered successfully!", 400: "Validation error", 409: "User with the given email or phone already exists."},
    )
    @action(detail=False, methods=["post"], url_path="register")
    def register(self, request):
        """Handles user registration with role support."""
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]
            phone = serializer.validated_data["phone"]
            role = serializer.validated_data.get("role", "patient")  # ✅ Default to "patient"

            if User.objects.filter(Q(email=email) | Q(phone=phone)).exists():
                return Response({"error": "A user with this email or phone already exists."}, status=status.HTTP_409_CONFLICT)

            serializer.validated_data["password"] = make_password(serializer.validated_data["password"])
            user = serializer.save()

            return Response({"message": "Registration successful!", "user": serializer.data}, status=status.HTTP_201_CREATED)

        return Response({"error": "Validation error", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="User login",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, description="User's email"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, description="User's password"),
            },
            required=["email", "password"],
        ),
        responses={200: "Login successful!", 401: "Invalid credentials", 403: "Account is inactive"},
    )
    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request):
        """Handles user login using email and password."""

        email = request.data.get("email", "").strip().lower()
        password = request.data.get("password")

        print("🔹 Login attempt for email:", email)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(password):
            return Response({"error": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({"error": "Account is inactive. Please contact support."}, status=status.HTTP_403_FORBIDDEN)

        # ✅ Remove existing tokens and generate a new one
        CustomToken.objects.filter(user=user).delete()
        token = CustomToken.objects.create(user=user)

        return Response(
            {
                "message": "Login successful!",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role,
                },
                "token": token.key,  # ✅ Return correct token
            },
            status=status.HTTP_200_OK,
        )


    @swagger_auto_schema(operation_description="Doctor Dashboard")
    @action(detail=False, methods=["get"], permission_classes=[IsDoctor])
    def doctor_dashboard(self, request):
        return Response({"message": "Welcome, Doctor!"})

    @swagger_auto_schema(operation_description="Admin Panel")
    @action(detail=False, methods=["get"], permission_classes=[IsAdmin])
    def admin_panel(self, request):
        return Response({"message": "Welcome, Admin!"})

    # ✅ New endpoint to fetch available doctors
    @swagger_auto_schema(
        operation_description="Get available doctors",
        responses={200: "List of available doctors"},
    )
    @action(detail=False, methods=["get"], url_path="doctor/available")
    def get_available_doctors(self, request):
        """Fetch a list of available doctors."""
        doctors = User.objects.filter(role="doctor", is_active=True)
        
        if not doctors.exists():
            return Response({"error": "No available doctors found."}, status=status.HTTP_404_NOT_FOUND)

        doctor_list = [
            {"id": doctor.id, "name": f"{doctor.first_name} {doctor.last_name}", "email": doctor.email}
            for doctor in doctors
        ]
        return Response({"doctors": doctor_list}, status=status.HTTP_200_OK)

class UserProfileViewSet(ViewSet):
    """
    A ViewSet for handling user profile operations.
    """

    @swagger_auto_schema(
        operation_description="Fetch the authenticated user's profile",
        responses={200: UserProfileSerializer},
    )
    @action(detail=False, methods=["get"], url_path="profile")
    def myprofile(self, request):
        """
        Retrieve the authenticated user's profile.
        """
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Fetch a specific user's profile by user_id",
        responses={200: UserProfileSerializer},
        manual_parameters=[
            openapi.Parameter(
                "user_id",
                openapi.IN_PATH,
                description="The ID of the user to fetch the profile for.",
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
    )
    @action(detail=False, methods=["get"], url_path="profile/(?P<user_id>[^/.]+)")
    def profile_by_id(self, request, user_id):
        """
        Retrieve a specific user's profile by user_id.
        """
        try:
            user = User.objects.get(id=user_id)
            serializer = UserProfileSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        operation_description="Update the authenticated user's profile",
        request_body=UserProfileSerializer,
        responses={
            200: "Profile updated successfully!",
            400: "Validation error",
        },
    )
    @action(detail=False, methods=["put"], url_path="profile")
    def update_profile(self, request):
        """
        Update the authenticated user's profile.
        """
        user = request.user
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Update a specific user's profile by user_id",
        request_body=UserProfileSerializer,
        responses={
            200: "Profile updated successfully!",
            400: "Validation error",
        },
        manual_parameters=[
            openapi.Parameter(
                "user_id",
                openapi.IN_PATH,
                description="The ID of the user to update the profile for.",
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
    )
    @action(detail=False, methods=["put"], url_path="profile/(?P<user_id>[^/.]+)")
    def update_profile_by_id(self, request, user_id):
        """
        Update a specific user's profile by user_id.
        """
        try:
            user = User.objects.get(id=user_id)
            serializer = UserProfileSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )
        

class CompanyViewSet(ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer



class ConsultationViewSet(ModelViewSet):
    queryset = Consultation.objects.all()
    serializer_class = ConsultationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        print("🔍 DEBUG: User Object ->", user)  # ✅ Print the user object
        print("🔍 DEBUG: User Authenticated? ->", user.is_authenticated)

        if not user.is_authenticated:
            return Consultation.objects.none()

        print("🔍 DEBUG: User Role ->", getattr(user, "role", "No role found"))

        if hasattr(user, "role") and user.role == "doctor":
            return Consultation.objects.filter(doctor=user)

        return Consultation.objects.filter(patient=user)

    @action(detail=False, methods=["post"], url_path="start")
    def start_consultation(self, request):
        """
        Patients start a video consultation with an available doctor.
        """
        user = request.user

        if not user.is_authenticated or user.role != "patient":
            return Response({"error": "Only patients can start consultations."}, status=status.HTTP_403_FORBIDDEN)

        doctor_id = request.data.get("doctor_id")
        doctor = User.objects.filter(id=doctor_id, role="doctor", is_active=True).first()

        if not doctor:
            return Response({"error": "Selected doctor is not available."}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Generate a unique meeting ID
        meeting_id = str(uuid.uuid4())

        # ✅ Create a new pending consultation
        consultation = Consultation.objects.create(
            patient=user,
            doctor=doctor,
            meeting_id=meeting_id,
            status="pending",
        )

        # ✅ Notify doctor (Simulated: In production, use WebSockets or a messaging queue)
        print(f"🔔 Doctor {doctor.email} received a consultation request from {user.email}")

        return Response(
            {
                "message": "Consultation request sent!",
                "doctor": {"id": doctor.id, "name": f"{doctor.first_name} {doctor.last_name}", "email": doctor.email},
                "meeting_id": meeting_id,
                "consultation_id": consultation.id,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="accept")
    def accept_consultation(self, request, pk=None):
        """
        Doctor accepts the consultation request.
        """
        user = request.user
        consultation = self.get_object()

        if user.role != "doctor" or consultation.doctor != user:
            return Response({"error": "You are not authorized to accept this consultation."}, status=status.HTTP_403_FORBIDDEN)

        consultation.status = "ongoing"
        consultation.started_at = timezone.now()
        consultation.save()

        return Response(
            {"message": "Consultation started!", "meeting_id": consultation.meeting_id, "status": consultation.status},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="reject")
    def reject_consultation(self, request, pk=None):
        """
        Doctor rejects the consultation request.
        """
        user = request.user
        consultation = self.get_object()

        if user.role != "doctor" or consultation.doctor != user:
            return Response({"error": "You are not authorized to reject this consultation."}, status=status.HTTP_403_FORBIDDEN)

        consultation.status = "cancelled"
        consultation.save()

        return Response({"message": "Consultation rejected.", "status": consultation.status}, status=status.HTTP_200_OK)
    
    # ✅ Notify the patient when doctor accepts the call
    @action(detail=True, methods=["post"], url_path="notify-patient")
    def notify_patient(self, request, pk=None):
        """
        Notifies the patient that the doctor has accepted the call.
        """
        consultation = self.get_object()

        # ✅ Ensure only doctors can notify patients
        if request.user.role != "doctor":
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        # ✅ Update consultation status to 'ongoing'
        consultation.status = "ongoing"
        consultation.save()

        # ✅ Notify the patient (Frontend should poll for status changes)
        return Response({"message": "Patient notified", "meeting_id": consultation.meeting_id}, status=status.HTTP_200_OK)

    # ✅ API to check consultation status
    @action(detail=False, methods=["get"], url_path="status")
    def consultation_status(self, request):
        """
        Checks the status of a consultation based on meeting_id.
        Used to notify the patient when the doctor has accepted the call.
        """
        meeting_id = request.query_params.get("meeting_id")
        if not meeting_id:
            return Response({"error": "Missing meeting_id"}, status=status.HTTP_400_BAD_REQUEST)

        consultation = get_object_or_404(Consultation, meeting_id=meeting_id)

        return Response({"status": consultation.status}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="start-call")
    def start_call(self, request, pk=None):
        """
        Doctor starts the call.
        """
        consultation = self.get_object()
        if consultation.status == "pending":
            consultation.start()
            return Response({"message": "Звонок начался!", "status": consultation.status})
        return Response({"error": "Звонок уже начался"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="end-call")
    def end_call(self, request, pk=None):
        """
        Ends a consultation and saves the end timestamp.
        """
        consultation = self.get_object()
        if consultation.status == "ongoing":
            consultation.end()
            return Response({"message": "Звонок завершён!", "status": consultation.status})
        return Response({"error": "Консультация уже завершена"}, status=status.HTTP_400_BAD_REQUEST)