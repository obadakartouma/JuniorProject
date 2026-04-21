# projects/urls.py
from django.urls import path
from .views import (
    AdminGetStudentSubmissionView,
    AdminTaskFeedbackView,
    CreateProjectTaskView,
    CreateProjectView,
    ExecuteCodeView,
    GetTaskSubmissionView,
    ListProjectsView,
    ProjectDetailView,
    CourseProjectsView,
    ProjectTaskDeleteView,
    ProjectTasksListView,
    SaveTaskSubmissionView,
    UpdateProjectView,
    DeleteProjectView,
    ConfirmDeleteProjectView,  # ⭐ إضافة الاستيراد
    StartProjectView,
    UploadStarterFileView,
    
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
    path('<int:pk>/starter-file/', UploadStarterFileView.as_view(), name='upload-starter-file'),
    path('tasks/create/', CreateProjectTaskView.as_view(), name='create-task'),
    path('<int:project_id>/tasks/', ProjectTasksListView.as_view(), name='project-tasks'),
    path('code/execute/', ExecuteCodeView.as_view(), name='execute-code'),
    path('tasks/<int:task_id>/save/', SaveTaskSubmissionView.as_view(), name='save-task-progress'),
    path('tasks/<int:task_id>/get/', GetTaskSubmissionView.as_view(), name='get-task'),
    path('tasks/<int:id>/delete/', ProjectTaskDeleteView.as_view(), name='delete-task'),
    path('tasks/<int:task_id>/feedback/', AdminTaskFeedbackView.as_view(), name='admin-task-feedback'),
    path('tasks/<int:task_id>/submission/<int:user_id>/', AdminGetStudentSubmissionView.as_view(), name='admin-get-student-submission'),
]