# courses/views.py
from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from .models import Course
from .serializers import (
    CourseCreateSerializer, CourseListSerializer, 
    CourseUpdateSerializer, CourseDetailSerializer,
    CourseEnrollmentSerializer
)
from django.db import IntegrityError

class IsAdminUser(permissions.BasePermission):
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)

class IsLearnerUser(permissions.BasePermission):
    
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'learner'
        )

# ======= CreateCourseView =============
class CreateCourseView(generics.CreateAPIView):
    
    queryset = Course.objects.all()
    serializer_class = CourseCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            course = serializer.save()
            
            return Response({
                'success': True,
                'message': _('تم إنشاء المسار التعليمي بنجاح'),
                'course': {
                    'id': course.id,
                    'title': course.title,
                    'description': course.description,
                    'level': course.get_level_display(),
                    'category': course.get_category_display(),
                    'estimated_duration': course.estimated_duration,
                    'projects_count': course.projects_count,
                    'is_public': course.is_public,
                    'created_at': course.created_at,
                }
            }, status=status.HTTP_201_CREATED)
            
        except ValidationError as e:
            error_messages = []
            
            if hasattr(e, 'detail'):
                for field, errors in e.detail.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")
            else:
                error_messages.append(str(e))
            
            return Response({
                'success': False,
                'message': _('فشل إنشاء المسار'),
                'errors': error_messages,
                'data': request.data
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': _('حدث خطأ أثناء إنشاء المسار'),
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ======= UpdateCourseView =============
class UpdateCourseView(generics.UpdateAPIView):

    queryset = Course.objects.filter(is_active=True)
    serializer_class = CourseUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    lookup_field = 'id'

    def get_object(self):
        try:
            return Course.objects.get(id=self.kwargs['id'], is_active=True)
        except Course.DoesNotExist:
            raise ValidationError(_('المسار غير موجود'))

    def get(self, request, *args, **kwargs):
        course = self.get_object()

        return Response({
            'success': True,
            'course': {
                'title': course.title,
                'description': course.description,
                'level': course.level,
                'category': course.category,
                'estimated_duration': course.estimated_duration,
                'is_public': course.is_public
            }
        })

    @transaction.atomic
    def put(self, request, *args, **kwargs):
        course = self.get_object()
        serializer = self.get_serializer(course, data=request.data)

        try:
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'message': _('بيانات غير صالحة'),
                    'errors': serializer.errors,
                    'data': request.data
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            
            return Response({
                'success': True,
                'message': _('تم تعديل المسار التعليمي بنجاح'),
                'course_id': course.id
            }, status=status.HTTP_200_OK)
            
        except IntegrityError as e:
            if 'unique_course_title' in str(e):
                return Response({
                    'success': False,
                    'message': _('فشل التحديث'),
                    'error': _('يوجد بالفعل مسار نشط بنفس العنوان. الرجاء اختيار عنوان مختلف.'),
                    'suggestion': _('يمكنك إضافة رقم أو تاريخ للعنوان ليكون فريداً'),
                    'data': request.data
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    'success': False,
                    'message': _('حدث خطأ في قاعدة البيانات'),
                    'error': str(e),
                    'data': request.data
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'success': False,
                'message': _('حدث خطأ غير متوقع'),
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ======= RetrieveCourseView =============
class RetrieveCourseView(generics.RetrieveAPIView):
    
    serializer_class = CourseListSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    lookup_field = 'id'
    
    def get_queryset(self):
        return Course.objects.filter(is_active=True)
    
    def get_object(self):
        id = self.kwargs.get('id')
        try:
            return Course.objects.get(id=id, is_active=True)
        except Course.DoesNotExist:
            raise ValidationError(_('المسار المطلوب غير موجود'))
    
    def retrieve(self, request, *args, **kwargs):
        try:
            course = self.get_object()
            serializer = self.get_serializer(course)
            
            course_data = serializer.data
            
            return Response({
                'success': True,
                'message': _('تم جلب بيانات المسار بنجاح'),
                'course': course_data
            })
            
        except Course.DoesNotExist:
            return Response({
                'success': False,
                'message': _('المسار غير موجود'),
                'error': _('المسار المطلوب غير موجود')
            }, status=status.HTTP_404_NOT_FOUND)

# ======= DeleteCourseView =============
class DeleteCourseView(generics.DestroyAPIView):
    
    queryset = Course.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    lookup_field = 'id'
    
    def get_object(self):
        id = self.kwargs.get('id')
        try:
            return Course.objects.get(id=id, is_active=True)
        except Course.DoesNotExist:
            raise ValidationError(_('المسار المطلوب غير موجود'))
    
    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        try:
            course = self.get_object()
            
            course.is_active = False
            course.save()
            
            return Response({
                'success': True,
                'message': _('تم حذف المسار التعليمي بنجاح'),
                'deleted_course': {
                    'id': course.id,
                    'title': course.title,
                    'instructor': f"{course.instructor.first_name} {course.instructor.last_name}",
                    'deleted_by': f"{request.user.first_name} {request.user.last_name}",
                    'deleted_at': course.updated_at,
                }
            })
            
        except ValidationError as e:
            return Response({
                'success': False,
                'message': _('فشل حذف المسار'),
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Course.DoesNotExist:
            return Response({
                'success': False,
                'message': _('المسار غير موجود'),
                'error': _('المسار المطلوب غير موجود')
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': _('حدث خطأ أثناء حذف المسار'),
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ======= ConfirmDeleteCourseView =============
class ConfirmDeleteCourseView(APIView):
    
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def get(self, request, id):
        try:
            course = Course.objects.get(id=id, is_active=True)
            
            confirmation_data = {
                'id': course.id,
                'title': course.title,
                'description': course.description,
                'level': course.get_level_display(),
                'category': course.get_category_display(),
                'instructor_name': course.instructor.email,  # ⭐ استخدام البريد بدلاً من الاسم
                'instructor_email': course.instructor.email,
                'created_at': course.created_at,
                'projects_count': course.get_actual_projects_count(),  # ⭐ استخدام العدد المحتسب
                'estimated_duration': course.estimated_duration,
                'is_public': course.is_public,
                'current_user': request.user.email,  # ⭐ استخدام البريد
                'confirmation_message': _('هل أنت متأكد من حذف هذا المسار؟'),
                'warning_message': _('تحذير: هذه العملية لا يمكن التراجع عنها'),
                'note': _('أنت على وشك حذف مسار أنشأه: ') + course.instructor.email
            }
            
            return Response({
                'success': True,
                'message': _('بيانات المسار للتأكيد قبل الحذف'),
                'course': confirmation_data,
                'confirmation_required': True
            })
            
        except Course.DoesNotExist:
            return Response({
                'success': False,
                'message': _('المسار غير موجود'),
                'error': _('المسار المطلوب غير موجود')
            }, status=status.HTTP_404_NOT_FOUND)

# ======= ListCoursesView =============
class ListCoursesView(generics.ListAPIView):
    
    serializer_class = CourseListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin:
            return Course.objects.filter(is_active=True).order_by('-created_at')
        else:
            return Course.objects.filter(is_active=True, is_public=True).order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        if not queryset.exists():
            return Response({
                'message': _('لا توجد مسارات متاحة'),
                'courses': []
            })
        
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'message': _('تم جلب المسارات بنجاح'),
            'count': queryset.count(),
            'courses': serializer.data
        })

# ======= CourseDetailView =============
class CourseDetailView(generics.RetrieveAPIView):
    
    serializer_class = CourseDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin:
            return Course.objects.filter(is_active=True)
        else:
            return Course.objects.filter(is_active=True, is_public=True)
    
    def get_object(self):
        id = self.kwargs.get('id')
        try:
            course = Course.objects.get(id=id, is_active=True)
            return course
            
        except Course.DoesNotExist:
            raise ValidationError(_('المسار المطلوب غير موجود'))
    
    def retrieve(self, request, *args, **kwargs):
        try:
            course = self.get_object()
            serializer = self.get_serializer(course)
            
            # ⭐ تحديث عدد المشاريع قبل الإرجاع
            course.update_projects_count()
            
            # ⭐ استخدام العدد المحتسب في additional_info
            actual_projects_count = course.get_actual_projects_count()
            
            # additional_info = {
            #     'available_levels': dict(Course.LEVEL_CHOICES),
            #     'available_categories': dict(Course.CATEGORY_CHOICES),
            #     'total_enrolled': course.get_enrolled_students_count(),
            #     'has_projects': actual_projects_count > 0,
            #     'actual_projects_count': actual_projects_count,  # ⭐ إضافة العدد الحقيقي
            #     'can_manage_projects': request.user.is_admin
            # }
            
            return Response({
                'success': True,
                'message': _('تم جلب بيانات المسار بنجاح'),
                'course': serializer.data,
                # 'additional_info': additional_info
            })
            
        except ValidationError as e:
            return Response({
                'success': False,
                'message': _('خطأ في جلب بيانات المسار'),
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

# باقي الـ Views كما هي...
class JoinCourseView(APIView):
    
    permission_classes = [permissions.IsAuthenticated, IsLearnerUser]
    
    def post(self, request, id):
        try:
            try:
                course = Course.objects.get(id=id, is_active=True)
            except Course.DoesNotExist:
                return Response({
                    'success': False,
                    'message': _('المسار غير موجود'),
                    'error': _('المسار المطلوب غير موجود')
                }, status=status.HTTP_404_NOT_FOUND)
            
            if request.user.user_type != 'learner':
                return Response({
                    'success': False,
                    'message': _('الانضمام غير مسموح'),
                    'error': _('فقط المتعلمين يمكنهم الانضمام للمسار')
                }, status=status.HTTP_403_FORBIDDEN)
            
            current_students_before = course.get_enrolled_emails()
            current_count_before = course.get_enrolled_students_count()
            
            user_courses_before = request.user.get_enrolled_courses_list()
            
            if course.is_student_enrolled(request.user):
                return Response({
                    'success': False,
                    'message': _('انضممت مسبقاً'),
                    'error': _('أنت منضم بالفعل لهذا المسار')
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if course.add_learner(request.user):
                current_students_after = course.get_enrolled_emails()
                current_count_after = course.get_enrolled_students_count()
                
                user_courses_after = request.user.get_enrolled_courses_list()
                
                return Response({
                    'success': True,
                    'message': _('تم الانضمام للمسار بنجاح'),
                    'course': {
                        'id': course.id,
                        'title': course.title,
                        'description': course.description[:100] + '...',
                        'enrolled_students_count': current_count_after,
                        'enrolled_students_emails': current_students_after
                    },
                    'student': {
                        'name': f"{request.user.first_name} {request.user.last_name}",
                        'email': request.user.email,
                        'enrolled_courses_before': user_courses_before,
                        'enrolled_courses_after': user_courses_after,
                        'enrolled_courses_count': request.user.get_enrolled_courses_count()
                    },
                    'enrollment_info': {
                        'joined_at': course.updated_at,
                        'message': _('يمكنك الآن البدء في دراسة المسار'),
                        'note': _('تم إضافتك كمتعلم في المسار وإضافة المسار إلى قائمتك')
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'message': _('فشل الانضمام'),
                    'error': _('لا يمكن إضافة المستخدم كطالب')
                }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': _('حدث خطأ أثناء الانضمام للمسار'),
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserEnrolledCoursesView(generics.ListAPIView):
    
    serializer_class = CourseListSerializer
    permission_classes = [permissions.IsAuthenticated, IsLearnerUser]
    
    def get_queryset(self):
        user = self.request.user
        return Course.objects.filter(
            enrolled_learners=user,
            is_active=True
        ).order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        if not queryset.exists():
            return Response({
                'message': _('لم تنضم لأي مسار بعد'),
                'courses': []
            })
        
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'message': _('تم جلب المسارات الخاصة بك بنجاح'),
            'count': queryset.count(),
            'courses': serializer.data
        })

class CheckEnrollmentView(APIView):
    
    permission_classes = [permissions.IsAuthenticated, IsLearnerUser]
    
    def get(self, request, id):
        try:
            course = Course.objects.get(id=id, is_active=True)
            
            is_enrolled = course.is_student_enrolled(request.user)
            
            return Response({
                'success': True,
                'is_enrolled': is_enrolled,
                'course': {
                    'id': course.id,
                    'title': course.title,
                    'is_public': course.is_public,
                    'enrolled_learners_count': course.get_enrolled_students_count()
                }
            })
            
        except Course.DoesNotExist:
            return Response({
                'success': False,
                'message': _('المسار غير موجود')
            }, status=status.HTTP_404_NOT_FOUND)