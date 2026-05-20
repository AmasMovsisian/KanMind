from django.urls import path
from .views import startKanmind

urlpatterns = [
    path('kanmind/', startKanmind)
]
