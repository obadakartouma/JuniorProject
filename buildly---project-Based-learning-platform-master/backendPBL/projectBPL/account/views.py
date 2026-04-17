from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from django.contrib.auth import logout
from django.utils.translation import gettext_lazy as _
from .serializers import (
    RegisterLearnerSerializer, 
    RegisterAdminSerializer, 
    LoginSerializer, 
    ProfileSerializer
)
from .models import CustomUser

class RegisterLearnerView(generics.CreateAPIView):
    """إنشاء حساب متعلم"""
    queryset = CustomUser.objects.all()
    serializer_class = RegisterLearnerSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # إنشاء توكنات JWT
        refresh = RefreshToken.for_user(user)
        
        # تحضير بيانات المستخدم حسب النوع
        user_data = {
            'id': user.id,
            'email': user.email,
            'user_type': user.get_user_type_display(),
        }
        
        # إضافة بيانات المسارات فقط للمتعلمين
        if user.is_learner:
            user_data['enrolled_courses_count'] = user.get_enrolled_courses_count()
            user_data['enrolled_courses_titles'] = user.get_enrolled_courses_list()
        
        return Response({
            'message': _('تم إنشاء حساب المتعلم بنجاح'),
            'user': user_data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)

class RegisterAdminView(generics.CreateAPIView):
    """إنشاء حساب مشرف"""
    queryset = CustomUser.objects.all()
    serializer_class = RegisterAdminSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # إنشاء توكنات JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': _('تم إنشاء حساب المشرف بنجاح'),
            'user': {
                'id': user.id,
                'email': user.email,
                'user_type': user.get_user_type_display()
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    """تسجيل الدخول"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # إنشاء توكنات JWT
        refresh = RefreshToken.for_user(user)
        
        # تحضير بيانات المستخدم حسب النوع
        user_data = {
            'id': user.id,
            'email': user.email,
            'user_type': user.get_user_type_display(),
        }
        
        # إضافة بيانات المسارات فقط للمتعلمين
        if user.is_learner:
            user_data['enrolled_courses_count'] = user.get_enrolled_courses_count()
            user_data['enrolled_courses_titles'] = user.get_enrolled_courses_list()
        
        return Response({
            'message': _('تم تسجيل الدخول بنجاح'),
            'user': user_data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })

class LogoutView(APIView):
    """تسجيل الخروج"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            
            if not refresh_token:
                return Response({
                    'error': _('refresh_token مطلوب')
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # إضافة التوكن للقائمة السوداء
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            # تسجيل خروج Django
            logout(request)
            
            return Response({
                'message': _('تم تسجيل الخروج بنجاح')
            }, status=status.HTTP_205_RESET_CONTENT)
            
        except Exception as e:
            return Response({
                'error': _('حدث خطأ أثناء تسجيل الخروج'),
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(generics.RetrieveUpdateAPIView):
    """عرض وتعديل الملف الشخصي"""
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        response_data = {
            'message': _('تم جلب بيانات الملف الشخصي'),
            'user': serializer.data
        }
        
        # **إضافة بيانات إضافية للمتعلمين فقط**
        if instance.is_learner:
            response_data['enrollment_info'] = {
                'enrolled_courses_count': instance.get_enrolled_courses_count(),
                'enrolled_courses_titles': instance.get_enrolled_courses_list(),
                'note': _('المسارات التعليمية المنضم لها')
            }
        
        
        return Response(response_data)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'message': _('تم تحديث الملف الشخصي بنجاح'),
            'user': serializer.data
        })