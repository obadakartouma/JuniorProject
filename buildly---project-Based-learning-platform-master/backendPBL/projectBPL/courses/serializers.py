# courses/serializers.py
from datetime import datetime
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import Course

class CourseCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Course
        fields = [
            'title', 'description', 'level', 'category',
            'estimated_duration', 'is_public'
        ]
        extra_kwargs = {
            'title': {
                'required': True,
                'allow_blank': False,
                'error_messages': {
                    'required': _('عنوان المسار مطلوب'),
                    'blank': _('عنوان المسار لا يمكن أن يكون فارغاً')
                }
            },
            'description': {
                'required': True,
                'allow_blank': False,
                'error_messages': {
                    'required': _('وصف المسار مطلوب'),
                    'blank': _('وصف المسار لا يمكن أن يكون فارغاً')
                }
            },
            'estimated_duration': {
                'required': True,
                'error_messages': {
                    'required': _('المدة المقدرة مطلوبة'),
                    'invalid': _('المدة يجب أن تكون رقم صحيح')
                }
            },
            'is_public': {
                'required': False,
                'default': False
            }
        }
    
    def validate_title(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(_('عنوان المسار مطلوب'))

        if len(value) < 3:
            raise serializers.ValidationError(_('العنوان يجب أن يكون 3 أحرف على الأقل'))

        # التحقق من التكرار للمسارات النشطة فقط
        exists = Course.objects.filter(
            title__iexact=value,
            is_active=True
        ).exists()

        if exists:
            raise serializers.ValidationError(
                _('يوجد بالفعل مسار نشط بنفس العنوان في النظام. الرجاء اختيار عنوان مختلف.')
            )

        return value

    def validate_description(self, value):
        if len(value.strip()) < 20:
            raise serializers.ValidationError(
                _('الوصف يجب أن يكون على الأقل 20 حرفاً')
            )
        return value.strip()
    
    def validate_estimated_duration(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                _('المدة يجب أن تكون أكبر من صفر')
            )
        if value > 1000:
            raise serializers.ValidationError(
                _('المدة لا يمكن أن تتجاوز 1000 ساعة')
            )
        return value
    
    def create(self, validated_data):
        request = self.context.get('request')
        
        if not request.user.is_admin:
            raise serializers.ValidationError(
                _('يجب أن تكون مشرفاً لإنشاء مسار')
            )
        
        title = validated_data.get('title')
        
        # التحقق النهائي قبل الإنشاء
        if Course.objects.filter(title__iexact=title, is_active=True).exists():
            raise serializers.ValidationError({
                'message': _('تعذر إنشاء المسار بسبب تعارض في العنوان.'),
                'details': _('تم اكتشاف مسار آخر بنفس العنوان أثناء عملية الإنشاء.'),
                'action': _('الرجاء تحديث الصفحة والمحاولة مرة أخرى.'),
            })
        
        # تعيين projects_count = 0 تلقائياً
        validated_data['projects_count'] = 0
        
        course = Course.objects.create(
            instructor=request.user,
            **validated_data
        )
        
        course.enrolled_learners.clear()
        
        print(f"✅ تم إنشاء المسار '{course.title}' - المتعلمين المنضمين: 0")
        
        return course

class CourseListSerializer(serializers.ModelSerializer):
    
    # ⭐⭐ تحسين instructor_name
    instructor_name = serializers.SerializerMethodField()
    level_display = serializers.CharField(source='get_level_display')
    category_display = serializers.CharField(source='get_category_display')
    enrolled_students_count = serializers.SerializerMethodField()
    
    # ⭐⭐ إضافة حقل للمشاريع المحسوبة فعلياً
    actual_projects_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'level', 'level_display',
            'category', 'category_display', 'estimated_duration',
            'projects_count', 'actual_projects_count', 'is_public', 'is_active', 'created_at',  
            'updated_at', 'instructor_name', 'enrolled_students_count'
        ]
        read_only_fields = ['projects_count']
    
    def get_instructor_name(self, obj):
        """⭐ تحسين لمعالجة الأسماء الفارغة"""
        first_name = obj.instructor.first_name or ""
        last_name = obj.instructor.last_name or ""
        
        if first_name or last_name:
            return f"{first_name} {last_name}".strip()
        else:
            # عرض البريد الإلكتروني إذا لم يكن هناك اسم
            return obj.instructor.email or "مشرف النظام"
    
    def get_enrolled_students_count(self, obj):
        return obj.get_enrolled_students_count()
    
    def get_actual_projects_count(self, obj):
        """⭐ الحصول على العدد الفعلي للمشاريع (محتسب)"""
        return obj.get_actual_projects_count()

class CourseDetailSerializer(serializers.ModelSerializer):
    course_projects = serializers.SerializerMethodField()

    # ⭐⭐ تحسين instructor_name
    instructor_name = serializers.SerializerMethodField()
    level_display = serializers.CharField(source='get_level_display')
    category_display = serializers.CharField(source='get_category_display')
    
    enrolled_students_count = serializers.SerializerMethodField()
    enrolled_students_emails = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()
    can_join = serializers.SerializerMethodField()
    
    # ⭐⭐ إضافة حقل للمشاريع المحسوبة فعلياً
    actual_projects_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'level', 'level_display',
            'category', 'category_display', 'estimated_duration',
            'projects_count', 'actual_projects_count', 'is_public', 'created_at', 'instructor_name',
            'enrolled_students_count', 'enrolled_students_emails', 'is_enrolled', 'can_join', 'course_projects'
        ]
        read_only_fields = ['projects_count']
    
    def get_instructor_name(self, obj):
        """⭐ تحسين لمعالجة الأسماء الفارغة"""
        first_name = obj.instructor.first_name or ""
        last_name = obj.instructor.last_name or ""
        
        if first_name or last_name:
            return f"{first_name} {last_name}".strip()
        else:
            # عرض البريد الإلكتروني إذا لم يكن هناك اسم
            return obj.instructor.email or "مشرف النظام"
    
    def get_enrolled_students_count(self, obj):
        return obj.get_enrolled_students_count()
    
    def get_enrolled_students_emails(self, obj):
        return obj.get_enrolled_emails()
    
    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user.is_learner:
            return obj.is_student_enrolled(request.user)
        return False
    
    def get_can_join(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user.is_learner:
            return obj.is_active and not obj.is_student_enrolled(request.user)
        return False
    
    def get_actual_projects_count(self, obj):
        """⭐ الحصول على العدد الفعلي للمشاريع (محتسب)"""
        return obj.get_actual_projects_count()
    
    def get_course_projects(self, obj):
        """
        إرجاع قائمة المشاريع في هذا المسار
        """
        request = self.context.get('request')
        from projects.serializers import ProjectListSerializer
        
        # جلب المشاريع النشطة في المسار
        projects = obj.projects.filter(is_active=True).order_by('order')
        
        # استخدام ProjectListSerializer لتحويل المشاريع
        serializer = ProjectListSerializer(
            projects, 
            many=True,
            context={'request': request}
        )
        
        return serializer.data

# باقي الـ serializers كما هي...






class CourseUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Course
        fields = [
            'title', 'description', 'level',
            'category', 'estimated_duration', 'is_public'
        ]
        extra_kwargs = {
            'title': {
                'required': True,
                'allow_blank': False,
                'error_messages': {
                    'required': _('عنوان المسار مطلوب ولا يمكن أن يكون فارغاً'),
                    'blank': _('عنوان المسار لا يمكن أن يكون فارغاً')
                }
            },
            'description': {
                'required': True,
                'allow_blank': False,
                'error_messages': {
                    'required': _('وصف المسار مطلوب ولا يمكن أن يكون فارغاً'),
                    'blank': _('وصف المسار لا يمكن أن يكون فارغاً')
                }
            },
            'estimated_duration': {
                'required': True,
                'error_messages': {
                    'required': _('المدة المقدرة مطلوبة'),
                    'invalid': _('المدة يجب أن تكون رقم صحيح')
                }
            }
        }
    
    def validate_title(self, value):
        request = self.context.get('request')
        value = value.strip()
        
        # التحقق من عدم الفراغ
        if not value:
            raise serializers.ValidationError({
                'message': _('حقل العنوان مطلوب'),
                'details': _('يرجى إدخال عنوان للمسار التعليمي'),
                'field': 'title'
            })
        
        # التحقق من الطول الأدنى
        if len(value) < 3:
            raise serializers.ValidationError({
                'message': _('العنوان قصير جداً'),
                'details': _('عنوان المسار يجب أن يكون 3 أحرف على الأقل'),
                'field': 'title',
                'min_length': 3,
                'current_length': len(value)
            })
        
        # التحقق من عدم التكرار (للمسارات النشطة فقط)
        instance = self.instance
        if instance:
            # التحقق من وجود مسار نشط آخر بنفس العنوان
            exists = Course.objects.filter(
                title__iexact=value,
                is_active=True
            ).exclude(id=instance.id).exists()
            
            if exists:
                raise serializers.ValidationError({
                    'message': _('تعذر تحديث المسار'),
                    'details': _('يوجد بالفعل مسار نشط بنفس العنوان في النظام'),
                    'field': 'title',
                    'action': _('الرجاء اختيار عنوان مختلف')
                })
        
        return value
    
    def validate_description(self, value):
        value = value.strip()
        
        # التحقق من عدم الفراغ
        if not value:
            raise serializers.ValidationError({
                'message': _('حقل الوصف مطلوب'),
                'details': _('يرجى إدخال وصف للمسار التعليمي'),
                'field': 'description'
            })
        
        # التحقق من الطول الأدنى
        if len(value) < 20:
            raise serializers.ValidationError({
                'message': _('الوصف قصير جداً'),
                'details': _('وصف المسار يجب أن يكون 20 حرفاً على الأقل'),
                'field': 'description',
                'min_length': 20,
                'current_length': len(value)
            })
        
        return value
    
    def validate_estimated_duration(self, value):
        # التحقق من أن القيمة رقم موجب
        if value <= 0:
            raise serializers.ValidationError({
                'message': _('المدة غير صالحة'),
                'details': _('المدة المقدرة يجب أن تكون أكبر من صفر'),
                'field': 'estimated_duration',
                'min_value': 1
            })
        
        # التحقق من الحد الأعلى
        if value > 1000:
            raise serializers.ValidationError({
                'message': _('المدة طويلة جداً'),
                'details': _('المدة لا يمكن أن تتجاوز 1000 ساعة'),
                'field': 'estimated_duration',
                'max_value': 1000,
                'current_value': value
            })
        
        return value
    
    def update(self, instance, validated_data):
        # التحقق من أن المستخدم المشرف فقط يمكنه التعديل
        request = self.context.get('request')
        if request and not request.user.is_admin:
            raise serializers.ValidationError({
                'message': _('صلاحية غير كافية'),
                'details': _('يجب أن تكون مشرفاً لتعديل المسار'),
                'code': 'permission_denied'
            })
        
        # التحقق النهائي من عنوان المسار قبل التحديث
        new_title = validated_data.get('title', instance.title).strip()
        
        if new_title.lower() != instance.title.lower():
            # التحقق من التكرار مرة أخرى (حالة السباق)
            exists = Course.objects.filter(
                title__iexact=new_title,
                is_active=True
            ).exclude(id=instance.id).exists()
            
            if exists:
                raise serializers.ValidationError({
                    'message': _('تعذر تحديث المسار'),
                    'details': _('تم اكتشاف تعارض في العنوان أثناء عملية التحديث'),
                    'field': 'title',
                    'action': _('الرجاء تحديث الصفحة والمحاولة مرة أخرى')
                })
        
        # تحديث البيانات
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        
        # إرجاع رسالة نجاح
        self.success_message = {
            'message': _('تم تحديث المسار بنجاح'),
            'details': _('تم حفظ التغييرات على المسار التعليمي'),
            'course_id': instance.id,
            'course_title': instance.title
        }
        
        return instance

class CourseEnrollmentSerializer(serializers.Serializer):
    
    def validate(self, data):
        request = self.context.get('request')
        course = self.context.get('course')
        
        if not request.user.is_learner:
            raise serializers.ValidationError(
                _('يجب أن تكون متعلم للانضمام للمسار')
            )
        
        if not course.is_active:
            raise serializers.ValidationError(
                _('هذا المسار غير متاح حالياً')
            )
        
        if course.is_student_enrolled(request.user):
            raise serializers.ValidationError(
                _('أنت منضم بالفعل لهذا المسار')
            )
        
        return data