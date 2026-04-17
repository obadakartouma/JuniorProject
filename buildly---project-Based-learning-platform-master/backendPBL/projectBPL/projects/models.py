# projects/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from courses.models import Course
from account.models import CustomUser

class Project(models.Model):
    """نموذج مشروع تعليمي"""
    
    # مستويات المشروع
    LEVEL_CHOICES = (
        ('beginner', 'مبتدئ'),
        ('intermediate', 'متوسط'),
        ('advanced', 'متقدم'),
        ('expert', 'خبير'),
    )
    
    # لغات البرمجة
    PROGRAMMING_LANGUAGE_CHOICES = (
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('java', 'Java'),
        ('csharp', 'C#'),
        ('cpp', 'C++'),
        ('php', 'PHP'),
        ('ruby', 'Ruby'),
        ('go', 'Go'),
        ('swift', 'Swift'),
        ('kotlin', 'Kotlin'),
        ('typescript', 'TypeScript'),
        ('dart', 'Dart'),
        ('rust', 'Rust'),
        ('other', 'أخرى'),
    )
    
    id = models.AutoField(primary_key=True, verbose_name='معرف المشروع')
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='projects',
        verbose_name='المسار التعليمي',
        help_text='المسار التعليمي الذي ينتمي إليه هذا المشروع'
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name='عنوان المشروع',
        help_text='أدخل عنواناً واضحاً ومعبراً للمشروع'
    )
    
    description = models.TextField(
        verbose_name='وصف المشروع',
        help_text='أدخل وصفاً مفصلاً للمشروع وأهدافه'
    )
    
    requirements = models.TextField(
        verbose_name='المتطلبات',
        help_text='متطلبات إنجاز المشروع (المهارات المطلوبة، المعرفة السابقة)',
        blank=True
    )
    
    objectives = models.TextField(
        verbose_name='الأهداف التعليمية',
        help_text='الأهداف التي سيحققها الطالب بعد إكمال المشروع',
        blank=True
    )
    
    resources = models.TextField(
        verbose_name='الموارد',
        help_text='الموارد والمراجع المطلوبة لإنجاز المشروع',
        blank=True
    )
    
    estimated_time = models.IntegerField(
        verbose_name='الوقت المقدر (بالساعات)',
        help_text='الوقت المقدر لإنجاز المشروع بالساعات'
    )
    
    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        verbose_name='المستوى',
        help_text='مستوى صعوبة المشروع'
    )
    
    language = models.CharField(
        max_length=20,
        choices=PROGRAMMING_LANGUAGE_CHOICES,
        verbose_name='لغة البرمجة',
        help_text='لغة البرمجة الرئيسية للمشروع'
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
        verbose_name='نشط'
    )
    
    order = models.IntegerField(
        default=0,
        verbose_name='الترتيب',
        help_text='ترتيب المشروع ضمن المسار'
    )
    
    class Meta:
        verbose_name = _('مشروع')
        verbose_name_plural = _('المشاريع')
        ordering = ['course', 'order', 'created_at']
        indexes = [
            models.Index(fields=['course', 'is_active']),
            models.Index(fields=['level']),
            models.Index(fields=['language']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['course', 'title'],
                name='unique_project_title_per_course',
                violation_error_message='يوجد بالفعل مشروع بهذا العنوان في هذا المسار'
            )
        ]
    
    def __str__(self):
        return f"{self.title} - {self.course.title}"
    
    def save(self, *args, **kwargs):
        # إذا لم يتم تحديد ترتيب، اجعله الأخير في المسار
        if not self.order:
            last_project = Project.objects.filter(course=self.course).order_by('-order').first()
            self.order = (last_project.order + 1) if last_project else 1
        
        # حفظ المشروع
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # ⭐⭐ تحديث عدد المشاريع في المسار بعد الحفظ (للجديد فقط)
        if is_new:
            self.course.update_projects_count()
    
    def delete(self, *args, **kwargs):
        """
        الحذف الفعلي للمشروع مع تحديث عدد المشاريع في المسار
        """
        course = self.course
        result = super().delete(*args, **kwargs)
        
        # تحديث عدد المشاريع في المسار بعد الحذف
        course.update_projects_count()
        
        return result
    
    def get_absolute_url(self):
        """الحصول على رابط المشروع"""
        from django.urls import reverse
        return reverse('projects:project-detail', kwargs={'pk': self.id})