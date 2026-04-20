from django.urls import path
from .views import CompleteProjectView, ProjectProgressDetailView, UserProjectProgressView

urlpatterns = [
    path('projects/', UserProjectProgressView.as_view(), name='projects-progress'),
    path('projects/<int:project_id>/complete/', CompleteProjectView.as_view(), name='complete-project'),
    path('projects/<int:project_id>/progress/', ProjectProgressDetailView.as_view(), name='project-progress'),
]