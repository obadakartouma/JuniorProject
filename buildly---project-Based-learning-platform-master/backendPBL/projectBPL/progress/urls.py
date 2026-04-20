from django.urls import path
from .views import CompleteProjectView, UserProjectProgressView

urlpatterns = [
    path('projects/', UserProjectProgressView.as_view(), name='project-progress'),
    path('projects/<int:project_id>/complete/', CompleteProjectView.as_view(), name='complete-project'),
]