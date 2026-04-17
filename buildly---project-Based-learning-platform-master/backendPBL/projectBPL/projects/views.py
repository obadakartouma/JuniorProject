# projects/views.py
from rest_framework.views import APIView
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import Project
from .serializers import ProjectCreateSerializer, ProjectListSerializer, ProjectDetailSerializer, ProjectUpdateSerializer, ProjectDeleteConfirmationSerializer
from courses.models import Course


class IsCourseInstructor(permissions.BasePermission):
    """التحقق من أن المستخدم هو مشرف (أي مشرف في النظام)"""
    
    def has_permission(self, request, view):
        # السماح للجميع بالوصول للقراءة فقط
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # لإنشاء/تعديل مشروع، يجب أن يكون المستخدم مشرفاً (أي مشرف في النظام)
        if not request.user.is_admin:
            return False
        
        return True
    
    def has_object_permission(self, request, view, obj):
        """أي مشرف يستطيع تعديل أي مشروع"""
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # فقط المشرفين يمكنهم التعديل
        if not request.user.is_admin:
            return False
        
        return True


# projects/views.py
class CreateProjectView(generics.CreateAPIView):
    """واجهة إنشاء مشروع جديد"""
    
    queryset = Project.objects.all()
    serializer_class = ProjectCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsCourseInstructor]
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # حفظ المشروع
            project = serializer.save()
            
            return Response({
                'success': True,
                'message': _('تم إنشاء المشروع بنجاح'),
                'project': {
                    'project_id': project.id,  # ⭐ تغيير: استخدام id
                    'course_id': project.course.id,  # ⭐ تغيير: استخدام course.id بدلاً من path_id
                    'title': project.title,
                    'description': project.description,
                    'estimated_time': project.estimated_time,
                    'level': project.get_level_display(),
                    'language': project.get_language_display(),
                    'created_at': project.created_at,
                }
            }, status=status.HTTP_201_CREATED)
            
        except ValidationError as e:
            error_messages = []
            
            if hasattr(e, 'detail'):
                if isinstance(e.detail, dict):
                    for field, errors in e.detail.items():
                        if isinstance(errors, list):
                            for error in errors:
                                error_messages.append(f"{field}: {error}")
                        else:
                            error_messages.append(f"{field}: {errors}")
                else:
                    error_messages.append(str(e.detail))
            else:
                error_messages.append(str(e))
            
            # رسالة مبسطة للمستخدم
            user_message = _('فشل إنشاء المشروع')
            if any('يوجد بالفعل مشروع بهذا العنوان' in msg for msg in error_messages):
                user_message = _('يوجد مشروع بنفس العنوان في هذا المسار. الرجاء استخدام عنوان مختلف.')
            
            return Response({
                'success': False,
                'message': user_message,
                'errors': error_messages,
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            # التحقق من خطأ القيد الفريد
            error_message = str(e)
            user_message = _('حدث خطأ أثناء إنشاء المشروع')
            
            if 'unique_project_title_per_course' in error_message or 'UNIQUE constraint failed' in error_message:
                user_message = _('يوجد مشروع بنفس العنوان في هذا المسار. الرجاء استخدام عنوان مختلف.')
            
            return Response({
                'success': False,
                'message': user_message,
                'error': error_message
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ListProjectsView(generics.ListAPIView):
    """واجهة عرض قائمة المشاريع"""
    
    serializer_class = ProjectListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # فلترة حسب المسار إذا تم تمرير course_id
        course_id = self.request.query_params.get('course_id', None)
        
        if course_id:
            try:
                # ⭐ تغيير: البحث باستخدام id بدلاً من pathid
                course = Course.objects.get(id=course_id)
                
                if user.is_admin:
                    return Project.objects.filter(course=course, is_active=True)
                else:
                    if course.is_public and course.is_active:
                        return Project.objects.filter(course=course, is_active=True)
                    else:
                        return Project.objects.none()
                        
            except Course.DoesNotExist:
                return Project.objects.none()
        
        # بدون فلترة
        if user.is_admin:
            return Project.objects.filter(is_active=True).order_by('course', 'order')
        else:
            return Project.objects.filter(
                course__is_public=True,
                course__is_active=True,
                is_active=True
            ).order_by('course', 'order')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        if not queryset.exists():
            return Response({
                'message': _('لا توجد مشاريع متاحة'),
                'projects': []
            })
        
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'message': _('تم جلب المشاريع بنجاح'),
            'count': queryset.count(),
            'projects': serializer.data
        })


class ProjectDetailView(generics.RetrieveAPIView):
    """واجهة عرض تفاصيل مشروع معين (UC-05 الخطوة 3)"""
    
    serializer_class = ProjectDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'  # ⭐ تغيير: استخدام pk بدلاً من project_id
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin:
            return Project.objects.filter(is_active=True)
        else:
            return Project.objects.filter(
                course__is_public=True,
                course__is_active=True,
                is_active=True
            )
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return Response({
            'success': True,
            'message': _('تم جلب تفاصيل المشروع بنجاح'),
            'project': serializer.data,
            # 'available_levels': dict(Project.LEVEL_CHOICES),
            # 'available_languages': dict(Project.PROGRAMMING_LANGUAGE_CHOICES),
            # 'can_edit': request.user.is_admin
        })


class CourseProjectsView(generics.ListAPIView):
    """واجهة عرض مشاريع مسار معين"""
    
    serializer_class = ProjectListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        # ⭐ تغيير: استخدام course_id بدلاً من path_id
        course_id = self.kwargs.get('course_id')
        
        try:
            # ⭐ تغيير: البحث باستخدام id بدلاً من pathid
            self.course = Course.objects.get(id=course_id)
            
            if user.is_admin:
                return Project.objects.filter(course=self.course, is_active=True)
            else:
                if self.course.is_public and self.course.is_active:
                    return Project.objects.filter(course=self.course, is_active=True)
            
            return Project.objects.none()
            
        except Course.DoesNotExist:
            raise ValidationError(_('المسار التعليمي غير موجود'))
    
    def list(self, request, *args, **kwargs):
        """تعديل الـ response لإضافة معلومات إضافية"""
        try:
            queryset = self.get_queryset()
            
            if not queryset.exists():
                return Response({
                    'message': _('لا توجد مشاريع في هذا المسار'),
                    'projects': [],
                    'course_info': {
                        'course_id': self.course.id,  # ⭐ تغيير
                        'title': self.course.title,
                        'total_projects_in_course': self.course.projects_count,
                        'has_projects': False
                    }
                })
            
            serializer = self.get_serializer(queryset, many=True)
            
            return Response({
                'message': _('تم جلب مشاريع المسار بنجاح'),
                'count': queryset.count(),
                'course_info': {
                    'course_id': self.course.id,  # ⭐ تغيير
                    'title': self.course.title,
                    'instructor': f"{self.course.instructor.first_name} {self.course.instructor.last_name}",
                    'total_projects_in_course': self.course.projects_count,
                    'is_public': self.course.is_public,
                    'is_active': self.course.is_active
                },
                'projects': serializer.data
            })
            
        except ValidationError as e:
            return Response({
                'success': False,
                'message': _('خطأ في جلب المشاريع'),
                'error': str(e)
            }, status=status.HTTP_404_NOT_FOUND)


class UpdateProjectView(generics.UpdateAPIView):
    """واجهة تعديل مشروع موجود (UC-05)"""
    
    queryset = Project.objects.filter(is_active=True)
    serializer_class = ProjectUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsCourseInstructor]
    lookup_field = 'pk'  # ⭐ تغيير: استخدام pk بدلاً من project_id
    
    def get_object(self):
        """الحصول على المشروع المطلوب"""
        # ⭐ تغيير: استخدام id (رقم) بدلاً من project_id (UUID)
        pk = self.kwargs.get('pk')
        try:
            return Project.objects.get(id=pk, is_active=True)
        except Project.DoesNotExist:
            raise ValidationError(_('المشروع المطلوب غير موجود'))
    
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        """UC-05 الخطوة 4-6: تحديث بيانات المشروع"""
        try:
            # الحصول على المشروع الحالي
            project = self.get_object()
            
            # ⭐ إرسال instance إلى context حتى يصل للـ serializer
            serializer = self.get_serializer(
                project,
                data=request.data,
                partial=False,
                context={'instance': project, 'request': request}
            )
            serializer.is_valid(raise_exception=True)
            
            # حفظ التعديلات
            updated_project = serializer.save()
            
            return Response({
                'success': True,
                'message': _('تم تعديل المشروع بنجاح'),
                'project': {
                    'project_id': updated_project.id,  # ⭐ تغيير
                    'course_id': updated_project.course.id,  # ⭐ تغيير
                    'title': updated_project.title,
                    'description': updated_project.description,
                    'requirements': updated_project.requirements,
                    'objectives': updated_project.objectives,
                    'estimated_time': updated_project.estimated_time,
                    'level': updated_project.get_level_display(),
                    'language': updated_project.get_language_display(),
                    'order': updated_project.order,
                    'updated_by': f"{request.user.first_name} {request.user.last_name}",
                    'updated_at': updated_project.updated_at,
                }
            })
            
        except ValidationError as e:
            error_messages = []
            
            if hasattr(e, 'detail'):
                if isinstance(e.detail, dict):
                    for field, errors in e.detail.items():
                        if isinstance(errors, list):
                            for error in errors:
                                error_messages.append({
                                    'field': field,
                                    'message': str(error)
                                })
                        else:
                            error_messages.append({
                                'field': field,
                                'message': str(errors)
                            })
                else:
                    error_messages.append({'field': 'general', 'message': str(e.detail)})
            else:
                error_messages.append({'field': 'general', 'message': str(e)})
            
            return Response({
                'success': False,
                'message': _('فشل تعديل المشروع'),
                'errors': error_messages,
                'data': request.data
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Project.DoesNotExist:
            return Response({
                'success': False,
                'message': _('المشروع غير موجود'),
                'error': _('المشروع المطلوب غير موجود')
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': _('حدث خطأ أثناء تعديل المشروع'),
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    



# projects/views.py - إضافة View للحذف
# projects/views.py - تحديث DeleteProjectView ليكون حذف فعلي بعد التأكيد

class DeleteProjectView(generics.DestroyAPIView):
    """واجهة حذف مشروع فعلي بعد التأكيد (UC-06 الخطوة 6-7)"""
    
    queryset = Project.objects.filter(is_active=True)
    serializer_class = ProjectDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsCourseInstructor]
    lookup_field = 'pk'
    
    def get_object(self):
        """الحصول على المشروع المطلوب للحذف"""
        pk = self.kwargs.get('pk')
        try:
            return Project.objects.get(id=pk, is_active=True)
        except Project.DoesNotExist:
            raise ValidationError(_('المشروع المطلوب غير موجود'))
    
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        """
        UC-06 الخطوة 6-7: حذف المشروع فعلياً
        """
        try:
            # الحصول على المشروع
            project = self.get_object()
            
            # حفظ معلومات المشروع قبل الحذف
            project_info = {
                'project_id': project.id,
                'title': project.title,
                'course_id': project.course.id,
                'course_title': project.course.title,
                'level': project.get_level_display(),
                'language': project.get_language_display(),
                'estimated_time': project.estimated_time,
                'created_at': project.created_at,
            }
            
            # الحذف الفعلي (استخدام delete() بدلاً من soft_delete())
            project.delete()
            
            # الخطوة 7: عرض رسالة نجاح
            return Response({
                'success': True,
                'message': _('✅ تم حذف المشروع بنجاح'),
                'deleted_project': project_info,
                'deletion_details': {
                    'deleted_by': f"{request.user.first_name} {request.user.last_name}",
                    'deleted_at': timezone.now(),
                    'course_remaining_projects': Project.objects.filter(
                        course_id=project_info['course_id'],
                        is_active=True
                    ).count(),
                    'action': _('المشروع تم حذفه بشكل دائم من النظام')
                },
                'redirect_info': {
                    'redirect_url': f"/courses/{project_info['course_id']}/projects",
                    'message': _('سيتم إعادة توجيهك إلى صفحة مشاريع المسار')
                }
            }, status=status.HTTP_200_OK)
            
        except ValidationError as e:
            return Response({
                'success': False,
                'message': _('❌ فشل حذف المشروع'),
                'error': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': _('❌ حدث خطأ أثناء حذف المشروع'),
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




# projects/views.py - إضافة في نهاية الملف بعد DeleteProjectView



# projects/views.py - تحديث ConfirmDeleteProjectView

class ConfirmDeleteProjectView(generics.RetrieveAPIView):
    """واجهة تأكيد حذف مشروع (UC-06 الخطوة 4)"""
    
    serializer_class = ProjectDeleteConfirmationSerializer
    permission_classes = [permissions.IsAuthenticated, IsCourseInstructor]
    lookup_field = 'pk'
    
    def get_queryset(self):
        return Project.objects.filter(is_active=True)
    
    def get_object(self):
        """الحصول على المشروع المطلوب"""
        pk = self.kwargs.get('pk')
        try:
            return Project.objects.get(id=pk, is_active=True)
        except Project.DoesNotExist:
            raise ValidationError(_('المشروع المطلوب غير موجود'))
    
    def retrieve(self, request, *args, **kwargs):
        """
        UC-06 الخطوة 4: عرض نافذة تأكيد الحذف
        """
        try:
            project = self.get_object()
            serializer = self.get_serializer(project)
            
            response_data = {
                'success': True,
                'message': _('⚠️ تأكيد حذف المشروع'),
                'confirmation_required': True,
                'project': serializer.data,
                'confirmation_details': {
                    'title': _('هل أنت متأكد من حذف هذا المشروع؟'),
                    'warning': _('هذا الإجراء لا يمكن التراجع عنه'),
                    'consequences': [
                        _('المشروع سيحذف من النظام بشكل دائم'),
                        _('جميع البيانات المرتبطة بالمشروع ستُحذف'),
                        _('لا يمكن استعادة المشروع بعد الحذف')
                    ],
                    'action_buttons': [
                        {
                            'label': _('نعم، احذف المشروع'),
                            'action': 'confirm_delete',
                            'url': f'/api/projects/{project.id}/delete/',
                            'method': 'DELETE',
                            'style': 'danger'
                        },
                        {
                            'label': _('إلغاء'),
                            'action': 'cancel',
                            'style': 'secondary'
                        }
                    ]
                }
            }
            
            return Response(response_data)
            
        except ValidationError as e:
            return Response({
                'success': False,
                'message': _('المشروع غير موجود'),
                'error': str(e)
            }, status=status.HTTP_404_NOT_FOUND)





# projects/views.py - أضف هذا في النهاية (بعد ConfirmDeleteProjectView)

class StartProjectView(APIView):
    """واجهة بدء المشروع من قبل المتعلم (بدون نموذج تقدم)"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        """
        بدء مشروع معين من قبل المتعلم
        """
        try:
            # 1. التحقق من وجود المشروع
            try:
                project = Project.objects.get(id=pk, is_active=True)
            except Project.DoesNotExist:
                return Response({
                    'success': False,
                    'message': _('المشروع غير موجود')
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 2. التحقق من أن المستخدم متعلم
            if not request.user.is_learner:
                return Response({
                    'success': False,
                    'message': _('فقط المتعلمين يمكنهم بدء المشاريع')
                }, status=status.HTTP_403_FORBIDDEN)
            
            # 3. التحقق من أن الطالب منضم للمسار
            if not project.course.is_student_enrolled(request.user):
                return Response({
                    'success': False,
                    'message': _('يجب الانضمام للمسار أولاً لبدء المشروع')
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 4. بدء المشروع (بدون حفظ في قاعدة بيانات)
            # هنا يمكنك إضافة منطق بدء المشروع
            
            return Response({
                'success': True,
                'message': _('🎉 تم بدء المشروع بنجاح!'),
                'project': {
                    'id': project.id,
                    'title': project.title,
                    'description': project.description[:100] + '...',
                    'estimated_time': project.estimated_time,
                    'level': project.get_level_display(),
                    'language': project.get_language_display()
                },
                'instructions': _('يمكنك الآن البدء في تنفيذ المشروع'),
                'next_steps': [
                    _('1. اقرأ المتطلبات والأهداف'),
                    _('2. جهز البيئة اللازمة'),
                    _('3. ابدأ بتنفيذ الخطوات'),
                    _('4. اطلب المساعدة إذا احتجت')
                ]
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': _('حدث خطأ أثناء بدء المشروع'),
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        





