from drf_yasg import openapi
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token  # Only if using token authentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from .models import User, Company, CustomToken
from .serializers import UserSerializer, CompanySerializer, UserProfileSerializer
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.exceptions import ValidationError

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()   
    serializer_class = UserSerializer

    @swagger_auto_schema(
        operation_description="Custom action: User registration",
        request_body=UserSerializer,
        responses={
            201: "User registered successfully!",
            400: "Validation error",
        },
    )
    @action(detail=False, methods=["post"], url_path="register")
    def register(self, request):
        print(f"Request Data: {request.data}")  # Log the incoming request data
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            phone = serializer.validated_data.get("phone")
            print(f"Validated Email: {email}, Validated Phone: {phone}")  # Log validated email and phone

            # Check for duplicates
            email_exists = User.objects.filter(email=email).exists()
            phone_exists = User.objects.filter(phone=phone).exists()
            print(f"Email Exists: {email_exists}, Phone Exists: {phone_exists}")  # Log the existence checks

            if email_exists and phone_exists:
                print("Error: Both email and phone already exist.")  # Log the error
                return Response(
                    {"error": "Комбинация такого email и телефона уже есть.", "code": "EMAIL_AND_PHONE_ALREADY_EXISTS"},
                    status=status.HTTP_409_CONFLICT,
                )
            elif email_exists:
                print("Error: Email already exists.")  # Log the error
                return Response(
                    {"error": "Пользователь с таким email уже существует.", "code": "EMAIL_ALREADY_EXISTS"},
                    status=status.HTTP_409_CONFLICT,
                )
            elif phone_exists:
                print("Error: Phone number already exists.")  # Log the error
                return Response(
                    {"error": "Пользователь с таким телефоном уже существует.", "code": "PHONE_NUMBER_ALREADY_EXISTS"},
                    status=status.HTTP_409_CONFLICT,
                )

            # Save the user (no password hashing)
            user = serializer.save()
            print(f"User Created: {user}")  # Log the created user
            return Response(
                {"message": "Регистрация прошла успешно!", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )

        print(f"Validation Errors: {serializer.errors}")  # Log validation errors
        return Response(
            {"error": "Ошибка валидации данных.", "details": serializer.errors},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY
        )



    @swagger_auto_schema(
        operation_description="Custom action: User login",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, description="User's email"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, description="User's password"),
            },
            required=["email", "password"],
        ),
        responses={
            200: "Login successful!",
            401: "Invalid credentials",
            403: "Account is inactive",
        },
    )
    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request):
        email = request.data.get("email", "").strip().lower()
        password = request.data.get("password")
        print(f"Login attempt with email: {email}")

        user = User.objects.filter(email=email).first()
        print(f"User found: {user}")

        # Check if user exists and password matches (no hashing)
        if user and user.password == password:
            print(f"Password matches: {user.password == password}")
            if user.is_active:
                print("User is active. Creating token...")
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
                        },
                        "token": token.key,
                    },
                    status=status.HTTP_200_OK,
                )
            print("User is inactive.")
            return Response(
                {"error": "Аккаунт не активен. Свяжитесь с поддержкой."},
                status=status.HTTP_403_FORBIDDEN,
            )
        print("Invalid credentials.")
        return Response({"error": "Неверные учетные данные."}, status=status.HTTP_401_UNAUTHORIZED)





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
