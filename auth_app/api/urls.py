from django.urls import path
from .views import (
    RegistrationView,
    LoginView,
    EmailCheckView
)

urlpatterns = [
    path("registration/", RegistrationView.as_view()),
    path("login/", LoginView.as_view()),
    path("email-check/",EmailCheckView.as_view(),name="email-check"),
]
