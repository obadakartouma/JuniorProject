from django.urls import path
from .views import UserProjectProgressView

urlpatterns = [
    path('projects/', UserProjectProgressView.as_view(), name='project-progress'),
]