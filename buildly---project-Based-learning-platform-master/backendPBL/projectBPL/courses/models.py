# courses/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from account.models import CustomUser

class Course(models.Model):
    """نموذج المسار التعليمي"""
    LEVEL_CHOICES = (
        ('beginner', 'مبتدئ'),
        ('intermediate', 'متوسط'),
        ('advanced', 'متقدم'),
        ('expert', 'خبير'),
    )
    CATEGORY_CHOICES = (
        ('web', 'تطوير الويب'),
        ('mobile', 'تطوير الموبايل'),
        ('data', 'علوم البيانات'),
        ('ai', 'الذكاء الاصطناعي'),
        ('design', 'التصميم'),
        ('business', 'أعمال'),
        ('language', 'لغات'),
        ('other', 'أخرى'),
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name='عنوان المسار',
        help_text='أدخل عنواناً واضحاً ومعبراً للمسار'
    )
    description = models.TextField(
        verbose_name='وصف المسار',
        help_text='أدخل وصفاً مفصلاً للمسار التعليمي'
    )
    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default='beginner',
        verbose_name='المستوى'
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other',
        verbose_name='الفئة'
    )
    estimated_duration = models.IntegerField(
        verbose_name='المدة المقدرة (بالساعات)',
        help_text='أدخل المدة المقدرة لإتمام المسار بالساعات'
    )
    projects_count = models.IntegerField(
        default=0,
        verbose_name='عدد المشاريع',
        help_text='عدد المشاريع العملية في هذا المسار',
        editable=False
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name='عام للجميع',
        help_text='هل هذا المسار متاح للجميع؟'
    )
    instructor = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='courses_created',
        verbose_name='المشرف'
    )
    enrolled_learners = models.ManyToManyField(
        CustomUser,
        related_name='enrolled_courses_as_learner',
        verbose_name='المتعلمين المنضمين',
        blank=True,
        help_text='المتعلمين المنضمين فقط - لا يتم إضافة مشرفين',
        limit_choices_to={'user_type': 'learner'} 
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإنشاء'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاريخ التحديث'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='نشط',
        help_text='هل هذا المسار نشط أم معطل؟'
    )
    
    class Meta:
        verbose_name = _('مسار تعليمي')
        verbose_name_plural = _('المسارات التعليمية')
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['title'],
                name='unique_course_title',
                condition=models.Q(is_active=True),
                violation_error_message='يوجد بالفعل مسار نشط بهذا العنوان في النظام'
            )
        ]
    
    def __str__(self):
        return f"{self.title} - {self.get_level_display()}"
    
    def save(self, *args, **kwargs):
        # منع التعديل اليدوي لـ projects_count في save
        if self.pk:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT projects_count FROM courses_course WHERE id = %s",
                    [self.pk]
                )
                old_count = cursor.fetchone()[0]
                if self.projects_count != old_count:
                    # استعادة القيمة القديمة
                    self.projects_count = old_count
        
        if not self.instructor.is_admin:
            raise ValueError('يجب أن يكون منشئ المسار مشرفاً')
        
        super().save(*args, **kwargs)
    
    # ⭐⭐ دالة محسنة لتحديث عدد المشاريع
    def update_projects_count(self):
        """تحديث عدد المشاريع النشطة في المسار - تلقائي"""
        try:
            from projects.models import Project
            
            # حساب المشاريع النشطة فعليًا
            actual_count = Project.objects.filter(
                course=self,
                is_active=True
            ).count()
            
            # تحديث مباشر في قاعدة البيانات لتجنب recursion
            if self.projects_count != actual_count:
                Course.objects.filter(pk=self.pk).update(
                    projects_count=actual_count,
                    updated_at=timezone.now()
                )
                # تحديث نسخة الـ instance أيضًا
                self.projects_count = actual_count
                
                print(f"✅ تم تحديث عدد المشاريع للمسار '{self.title}' إلى: {actual_count}")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ خطأ في تحديث عدد المشاريع: {e}")
            return False
    
    # ⭐⭐ دالة مساعدة للحصول على العدد الحقيقي (للاستخدام في الاستعلامات)
    def get_actual_projects_count(self):
        """الحصول على العدد الحقيقي للمشاريع (دون الاعتماد على الحقل المخزن)"""
        try:
            from projects.models import Project
            return Project.objects.filter(
                course=self,
                is_active=True
            ).count()
        except:
            return 0
    
    # باقي الدوال كما هي...
    def is_student_enrolled(self, student):
        if not student.is_learner:
            return False
        return self.enrolled_learners.filter(id=student.id).exists()

    def get_enrolled_students_count(self):
        return self.enrolled_learners.count()
    
    def get_enrolled_learners_count(self):
        return self.enrolled_learners.count()
    
    def add_learner(self, user):
        if user.is_learner:
            if not self.enrolled_learners.filter(id=user.id).exists():
                self.enrolled_learners.add(user)
                user.add_enrolled_course(self.title)
                
                print(f"✅ تم إضافة المتعلم '{user.email}' للمسار '{self.title}'")
                return True
            else:
                print(f"⚠️  المتعلم '{user.email}' موجود بالفعل في المسار '{self.title}'")
                return False
        else:
            print(f"❌ المستخدم '{user.email}' ليس متعلمًا، لا يمكن إضافته للمسار")
            return False
    
    def remove_learner(self, user):
        if user.is_learner and self.enrolled_learners.filter(id=user.id).exists():
            self.enrolled_learners.remove(user)
            user.remove_enrolled_course(self.title)
            
            print(f"✅ تم إزالة المتعلم '{user.email}' من المسار '{self.title}'")
            return True
        return False
    
    def get_enrolled_learners_list(self):
        return self.enrolled_learners.all()
    
    def get_enrolled_emails(self):
        return list(self.enrolled_learners.values_list('email', flat=True))
    
    def can_update_title(self, new_title):
        """
        التحقق من إمكانية تحديث العنوان
        السماح بالتحديث إذا كان العنوان نفسه أو مختلف وغير مستخدم
        """
        new_title = new_title.strip()
        current_title = self.title.strip()
        
        # إذا كان نفس العنوان، السماح بالتحديث
        if current_title.lower() == new_title.lower():
            return True, "نفس العنوان - مسموح"
        
        # إذا كان مختلف، التحقق من التكرار
        existing_courses = Course.objects.filter(
            title__iexact=new_title,
            is_active=True
        ).exclude(pk=self.pk)
        
        if existing_courses.exists():
            return False, "العنوان مستخدم مسبقاً"
        
        return True, "عنوان جديد - مسموح"