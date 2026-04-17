# projects/urls.py
from django.urls import path
from .views import (
    CreateProjectView,
    ListProjectsView,
    ProjectDetailView,
    CourseProjectsView,
    UpdateProjectView,
    DeleteProjectView,
    ConfirmDeleteProjectView,  # ⭐ إضافة الاستيراد
    StartProjectView,
    
)

app_name = 'projects'

urlpatterns = [
    path('create/', CreateProjectView.as_view(), name='create-project'),
    path('<int:pk>/update/', UpdateProjectView.as_view(), name='update-project'),
    path('<int:pk>/confirm-delete/', ConfirmDeleteProjectView.as_view(), name='confirm-delete'),  # ⭐ إضافة مسار التأكيد
    path('<int:pk>/delete/', DeleteProjectView.as_view(), name='delete-project'),
    path('', ListProjectsView.as_view(), name='list-projects'),
    path('<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    path('course/<int:course_id>/', CourseProjectsView.as_view(), name='course-projects'),
    path('<int:pk>/start/', StartProjectView.as_view(), name='start-project'),


]