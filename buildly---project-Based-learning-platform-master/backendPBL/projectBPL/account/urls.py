# accounts/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterLearnerView,
    RegisterAdminView,
    LoginView,
    LogoutView,
    ProfileView,

)
from .views_dashboard import (
    LearnerDashboardView,
    LearnerProgressAPIView,
)

urlpatterns = [
    path('register/learner/', RegisterLearnerView.as_view(), name='register-learner'),
    path('register/admin/', RegisterAdminView.as_view(), name='register-admin'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),  




     # مسارات لوحة تحكم المتعلم
    path('learner/dashboard/', LearnerDashboardView.as_view(), name='learner-dashboard'),
    path('learner/progress/', LearnerProgressAPIView.as_view(), name='learner-progress'),
    ]