# projects/serializers.py
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import Project
from courses.models import Course




class ProjectCreateSerializer(serializers.ModelSerializer):
    """Serializer لإنشاء مشروع جديد"""
    
    # ⭐ تغيير: استخدام course_id (رقم عادي) بدلاً من path_id (UUID)
    course_id = serializers.IntegerField(
        write_only=True,
        required=True,
        help_text='معرف المسار التعليمي (course_id)'
    )
    
    class Meta:
        model = Project
        fields = [
            'course_id', 'title', 'description', 'requirements',
            'objectives', 'resources', 'estimated_time',
            'level', 'language', 'order'
        ]
        extra_kwargs = {
            'title': {
                'required': True,
                'allow_blank': False,
                'error_messages': {
                    'required': _('عنوان المشروع مطلوب'),
                    'blank': _('عنوان المشروع لا يمكن أن يكون فارغاً')
                }
            },
            'description': {
                'required': True,
                'allow_blank': False,
                'error_messages': {
                    'required': _('وصف المشروع مطلوب'),
                    'blank': _('وصف المشروع لا يمكن أن يكون فارغاً')
                }
            },
            'estimated_time': {
                'required': True,
                'error_messages': {
                    'required': _('الوقت المقدر مطلوب'),
                    'invalid': _('الوقت يجب أن يكون رقم صحيح')
                }
            },
            'level': {
                'required': True,
                'error_messages': {
                    'required': _('مستوى المشروع مطلوب'),
                    'invalid_choice': _('المستوى المحدد غير صالح')
                }
            },
            'language': {
                'required': True,
                'error_messages': {
                    'required': _('لغة البرمجة مطلوبة'),
                    'invalid_choice': _('لغة البرمجة المحددة غير صالحة')
                }
            },
        }
    
    def validate_course_id(self, value):
        """التحقق من وجود المسار فقط"""
        request = self.context.get('request')
        
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError(_('يجب تسجيل الدخول أولاً'))
        
        # التحقق من أن المستخدم مشرف
        if not request.user.is_admin:
            raise serializers.ValidationError(
                _('يجب أن تكون مشرفاً لإنشاء مشروع')
            )
        
        try:
            # ⭐ تغيير: البحث عن المسار باستخدام course_id (رقم عادي)
            course = Course.objects.get(id=value)
            
            # إضافة المسار للبيانات المحققة
            self.context['course'] = course
            return value
            
        except Course.DoesNotExist:
            raise serializers.ValidationError(_('المسار التعليمي غير موجود'))
    
    def validate_title(self, value):
        """التحقق من صحة العنوان والتحقق من عدم تكراره في نفس المسار"""
        value = value.strip()
        
        # التحقق من صحة البيانات الأساسية
        if len(value) < 3:
            raise serializers.ValidationError(
                _('العنوان يجب أن يكون على الأقل 3 أحرف')
            )
        
        # التحقق من عدم تكرار العنوان في نفس المسار
        course = self.context.get('course')
        if course:
            # تحقق مما إذا كان هناك مشروع بنفس العنوان في نفس المسار
            if Project.objects.filter(
                course=course,
                title=value,
                is_active=True
            ).exists():
                raise serializers.ValidationError(
                    _('يوجد بالفعل مشروع بهذا العنوان في هذا المسار. الرجاء اختيار عنوان مختلف.')
                )
        
        return value
    
    def validate_description(self, value):
        """التحقق من صحة الوصف"""
        if len(value.strip()) < 20:
            raise serializers.ValidationError(
                _('الوصف يجب أن يكون على الأقل 20 حرفاً')
            )
        return value.strip()
    
    def validate_estimated_time(self, value):
        """التحقق من صحة الوقت المقدر"""
        if value <= 0:
            raise serializers.ValidationError(
                _('الوقت المقدر يجب أن يكون أكبر من صفر')
            )
        if value > 500:  # حد أقصى 500 ساعة
            raise serializers.ValidationError(
                _('الوقت المقدر لا يمكن أن يتجاوز 500 ساعة')
            )
        return value
    
    def create(self, validated_data):
        """إنشاء المشروع"""
        # إزالة course_id من البيانات لأننا نستخدم course
        validated_data.pop('course_id')
        
        # استخدام المسار الذي تم التحقق منه
        course = self.context.get('course')
        
        try:
            # إنشاء المشروع
            project = Project.objects.create(
                course=course,
                **validated_data
            )
            return project
            
        except Exception as e:
            # التقاط أي استثناءات أخرى (مثل انتهاك القيود في قاعدة البيانات)
            if 'unique_project_title_per_course' in str(e):
                raise serializers.ValidationError({
                    'title': [_('يوجد بالفعل مشروع بهذا العنوان في هذا المسار. الرجاء اختيار عنوان مختلف.')]
                })
            raise e



class ProjectListSerializer(serializers.ModelSerializer):
    """Serializer لعرض قائمة المشاريع"""
    
    # ⭐ تغيير: استخدام id بدلاً من project_id
    project_id = serializers.IntegerField(source='id')
    course_id = serializers.IntegerField(source='course.id')
    course_title = serializers.CharField(source='course.title')
    instructor_name = serializers.SerializerMethodField()
    level_display = serializers.CharField(source='get_level_display')
    language_display = serializers.CharField(source='get_language_display')
    total_course_projects = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'project_id', 'course_id', 'course_title',
            'title', 'description', 'requirements',
            'objectives', 'resources', 'estimated_time',
            'level', 'level_display', 'language', 'language_display',
            'order', 'is_active', 'created_at', 'updated_at',
            'instructor_name', 'total_course_projects'
        ]
    
    def get_instructor_name(self, obj):
        """الحصول على اسم مشرف المسار"""
        return f"{obj.course.instructor.first_name} {obj.course.instructor.last_name}"
    
    def get_total_course_projects(self, obj):
        """الحصول على عدد المشاريع الكلي في هذا المسار"""
        # ⭐ استخدام حقل projects_count من المسار
        return obj.course.projects_count if hasattr(obj.course, 'projects_count') else 0


class ProjectDetailSerializer(ProjectListSerializer):
    """Serializer لعرض تفاصيل مشروع معين"""
    
    class Meta(ProjectListSerializer.Meta):
        fields = ProjectListSerializer.Meta.fields + [
            # يمكن إضافة حقول إضافية للتفاصيل
        ]


class ProjectUpdateSerializer(serializers.ModelSerializer):
    """Serializer لتحديث مشروع موجود (UC-05)"""
    
    class Meta:
        model = Project
        fields = [
            'title', 'description', 'requirements', 'objectives',
            'resources', 'estimated_time', 'level', 'language', 'order'
        ]
        extra_kwargs = {
            'title': {
                'required': True,
                'allow_blank': False,
                'error_messages': {
                    'required': _('عنوان المشروع مطلوب'),
                    'blank': _('عنوان المشروع لا يمكن أن يكون فارغاً')
                }
            },
            'description': {
                'required': True,
                'allow_blank': False,
                'error_messages': {
                    'required': _('وصف المشروع مطلوب'),
                    'blank': _('وصف المشروع لا يمكن أن يكون فارغاً')
                }
            },
            'estimated_time': {
                'required': True,
                'error_messages': {
                    'required': _('الوقت المقدر مطلوب'),
                    'invalid': _('الوقت يجب أن يكون رقم صحيح')
                }
            },
            'level': {
                'required': True,
                'error_messages': {
                    'required': _('مستوى المشروع مطلوب'),
                    'invalid_choice': _('المستوى المحدد غير صالح')
                }
            },
            'language': {
                'required': True,
                'error_messages': {
                    'required': _('لغة البرمجة مطلوبة'),
                    'invalid_choice': _('لغة البرمجة المحددة غير صالحة')
                }
            },
        }
    
    def validate_title(self, value):
        """التحقق من أن العنوان الجديد لا يتعارض مع عناوين أخرى في نفس المسار"""
        value = value.strip()
        
        # التحقق من صحة البيانات
        if len(value) < 3:
            raise serializers.ValidationError(
                _('العنوان يجب أن يكون على الأقل 3 أحرف')
            )
        
        # الحصول على المشروع الحالي من context
        instance = self.context.get('instance')
        if not instance:
            # إذا لم يكن هناك instance، نعيد القيمة كما هي
            return value
        
        # إذا كان العنوان نفس العنوان الحالي، نسمح به
        if instance.title == value:
            return value
        
        # التحقق من عدم وجود مشروع آخر بنفس العنوان في نفس المسار
        if Project.objects.filter(
            course=instance.course,
            title=value,
            is_active=True
        ).exclude(id=instance.id).exists():  # ⭐ تغيير: استخدم id بدلاً من project_id
            raise serializers.ValidationError(
                _('يوجد بالفعل مشروع بهذا العنوان في هذا المسار')
            )
        
        return value
    
    def validate_description(self, value):
        """التحقق من صحة الوصف"""
        if len(value.strip()) < 20:
            raise serializers.ValidationError(
                _('الوصف يجب أن يكون على الأقل 20 حرفاً')
            )
        return value.strip()
    
    def validate_estimated_time(self, value):
        """التحقق من صحة الوقت المقدر"""
        if value <= 0:
            raise serializers.ValidationError(
                _('الوقت المقدر يجب أن يكون أكبر من صفر')
            )
        if value > 500:
            raise serializers.ValidationError(
                _('الوقت المقدر لا يمكن أن يتجاوز 500 ساعة')
            )
        return value
    
    def update(self, instance, validated_data):
        """
        تحديث بيانات المشروع
        أي مشرف يستطيع التعديل
        """
        # تحديث الحقول
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance
    





# projects/serializers.py - إضافة في نهاية الملف

class ProjectDeleteConfirmationSerializer(serializers.ModelSerializer):
    """Serializer لعرض معلومات المشروع قبل الحذف"""
    
    course_info = serializers.SerializerMethodField()
    deletion_impact = serializers.SerializerMethodField()
    current_user = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'requirements', 
            'objectives', 'estimated_time', 'level', 'language',
            'created_at', 'updated_at', 'course_info', 
            'deletion_impact', 'current_user'
        ]
        read_only_fields = fields
    
    def get_course_info(self, obj):
        return {
            'course_id': obj.course.id,
            'course_title': obj.course.title,
            'instructor': f"{obj.course.instructor.first_name} {obj.course.instructor.last_name}",
            'total_projects': obj.course.projects_count
        }
    
    def get_deletion_impact(self, obj):
        return {
            'remaining_projects': obj.course.projects_count - 1,
            'message': _('سيبقى {} مشروع في المسار بعد الحذف').format(obj.course.projects_count - 1)
        }
    
    def get_current_user(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return {
                'name': f"{request.user.first_name} {request.user.last_name}",
                'email': request.user.email,
                'role': 'مشرف' if request.user.is_admin else 'مستخدم'
            }
        return None