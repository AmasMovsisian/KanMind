from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()



class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Handles creation of a new user account with password confirmation
    and ensures both password fields match before user creation.
    """

    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "fullname",
            "email",
            "password",
            "repeated_password",
        ]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def validate(self, attrs):
        """
        Validates that password and repeated_password fields match.
        """
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError(
                {"password": "Passwords do not match"}
            )
        return attrs

    def create(self, validated_data):
        """
        Creates and returns a new user instance using Django's custom user manager.
        """
        validated_data.pop("repeated_password")
        user = User.objects.create_user(
            email=validated_data["email"],
            fullname=validated_data["fullname"],
            password=validated_data["password"],
        )
        return user



class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.

    Validates email and password credentials.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)