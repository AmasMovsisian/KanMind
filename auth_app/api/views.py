from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from django.core.validators import validate_email
from .serializers import (
    RegistrationSerializer,
    LoginSerializer
)
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated

User = get_user_model()



class RegistrationView(APIView):
    """
    API endpoint for user registration.

    Creates a new user account and returns an authentication token along with user details.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Registers a new user and returns authentication data.
        """
        serializer = RegistrationSerializer(
            data=request.data
        )
        if serializer.is_valid():
            user = serializer.save()

            token, _ = Token.objects.get_or_create(
                user=user
            )
            return Response(
                {
                    "token": token.key,
                    "fullname": user.fullname,
                    "email": user.email,
                    "user_id": user.id,
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )



class LoginView(APIView):
    """
    API endpoint for user authentication (login).

    Validates credentials and returns an authentication token if successful.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Authenticates a user and returns an access token.
        """
        serializer = LoginSerializer(
            data=request.data
        )
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]
            user = authenticate(
                request,
                username=email,
                password=password
            )
            if not user:
                return Response(
                    {"error": "Invalid credentials"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            token, _ = Token.objects.get_or_create(
                user=user
            )
            return Response(
                {
                    "token": token.key,
                    "fullname": user.fullname,
                    "email": user.email,
                    "user_id": user.id,
                },
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )



class EmailCheckView(APIView):
    """
    API endpoint for validating and retrieving a user by email address.

    Ensures the email format is valid and returns user data if the user exists.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Validates an email address and returns matching user information.
        """
        email = request.query_params.get("email")
        if not email:
            return Response(
                {"detail": "Email query parameter is required"},
                status=400
            )
        try:
            validate_email(email)
        except Exception:
            return Response(
                {"detail": "Invalid email format"},
                status=400
            )
        user = User.objects.filter(email=email).first()
        if not user:
            return Response(
                {"detail": "Email not found"},
                status=404
            )
        return Response({
            "id": user.id,
            "email": user.email,
            "fullname": user.fullname
        }, status=200)