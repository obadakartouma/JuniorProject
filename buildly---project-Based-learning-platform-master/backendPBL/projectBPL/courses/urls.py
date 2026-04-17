# courses/urls.py
from django.urls import path
from .views import (
    CreateCourseView, 
    ListCoursesView,
    UpdateCourseView,
    RetrieveCourseView,
    DeleteCourseView,      
    ConfirmDeleteCourseView,
    CourseDetailView,
    JoinCourseView,
    UserEnrolledCoursesView,
    CheckEnrollmentView
)

app_name = 'courses'

urlpatterns = [
    path('', ListCoursesView.as_view(), name='list-courses'),
    path('create/', CreateCourseView.as_view(), name='create-course'),
    path('<int:id>/', RetrieveCourseView.as_view(), name='retrieve-course'),
    path('<int:id>/update/', UpdateCourseView.as_view(), name='update-course'),
    path('<int:id>/confirm-delete/', ConfirmDeleteCourseView.as_view(), name='confirm-delete'),
    path('<int:id>/delete/', DeleteCourseView.as_view(), name='delete-course'),
    path('<int:id>/details/', CourseDetailView.as_view(), name='course-detail'),
    path('<int:id>/join/', JoinCourseView.as_view(), name='join-course'),
    path('my-courses/', UserEnrolledCoursesView.as_view(), name='my-courses'),
    path('<int:id>/check-enrollment/', CheckEnrollmentView.as_view(), name='check-enrollment'),
]