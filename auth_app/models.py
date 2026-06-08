from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models



class CustomUserManager(BaseUserManager):
    """
    Custom user manager that handles user creation using email as the unique identifier.
    """

    def create_user(
        self,
        email,
        password=None,
        **extra_fields
    ):
        """
        Creates and returns a regular user with the given email and password.

        Normalizes the email, sets the password securely, and saves the user instance.
        """
        if not email:
            raise ValueError(
                "Email is required"
            )

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(
        self,
        email,
        password=None,
        **extra_fields
    ):
        """
        Creates and returns a superuser with staff and superuser privileges enabled.
        """
        extra_fields.setdefault(
            "is_staff",
            True
        )

        extra_fields.setdefault(
            "is_superuser",
            True
        )

        return self.create_user(
            email,
            password,
            **extra_fields
        )



class User(AbstractUser):
    """
    Custom User model that uses email as the unique identifier instead of username.

    Extends Django's AbstractUser and removes the username field entirely.
    """

    username = None
    fullname = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        """
        Returns the string representation of the user (email address).
        """
        return self.email