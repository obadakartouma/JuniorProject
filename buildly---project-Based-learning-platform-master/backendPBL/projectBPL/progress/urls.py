from django.urls import path
from .views import AdminProjectReviewView, AdminProjectSubmissionsView, AdminSingleSubmissionView, CompleteProjectView, ProjectProgressDetailView, UserProjectProgressView

urlpatterns = [
    path('projects/', UserProjectProgressView.as_view(), name='projects-progress'),
    path('projects/<int:project_id>/complete/', CompleteProjectView.as_view(), name='complete-project'),
    path('projects/<int:project_id>/progress/', ProjectProgressDetailView.as_view(), name='project-progress'),
    path('projects/<int:project_id>/submissions/', AdminProjectSubmissionsView.as_view(), name='completed-progress'),
    path('projects/<int:project_id>/review/', AdminProjectReviewView.as_view(), name='admin-project-review'),
    path('projects/<int:project_id>/review/<user_id>/', AdminSingleSubmissionView.as_view(), name='get-project-review'),
]