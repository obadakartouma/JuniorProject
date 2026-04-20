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
    
    
class ProjectStarterFile(models.Model):
    """ملف البداية الخاص بالمشروع (Starter Code)"""

    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='starter_file',
        verbose_name='المشروع'
    )

    file = models.FileField(
        upload_to='project_starters/',
        verbose_name='ملف البداية'
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    uploaded_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Starter File - {self.project.title}"
    
    
class ProjectTask(models.Model):
    """مراحل المشروع (Tasks)"""

    TASK_TYPE_CHOICES = (
        ('text', 'إجابة نصية'),
        ('code', 'كود برمجي'),
        ('file', 'رفع ملف'),
    )

    id = models.AutoField(primary_key=True)

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks'
    )

    title = models.CharField(max_length=200)

    description = models.TextField()

    task_type = models.CharField(
        max_length=20,
        choices=TASK_TYPE_CHOICES,
        default='text'
    )

    expected_answer = models.TextField(blank=True, null=True)

    hint = models.TextField(
        blank=True,
        null=True,
        verbose_name='تلميح'
    )

    teaching = models.TextField(
        blank=True,
        null=True,
        verbose_name='شرح / درس مستفاد'
    )

    order = models.IntegerField(default=1)

    is_required = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'order'],
                name='unique_task_order_per_project'
            )
        ]

    def __str__(self):
        return f"{self.project.title} - Task {self.order}"
    
    
class TaskSubmission(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    task = models.ForeignKey(ProjectTask, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    answer = models.TextField(blank=True)

    STATUS_CHOICES = (
        ('in_progress', 'In Bearbeitung'),
        ('completed', 'Abgeschlossen'),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_progress'
    )

    is_completed = models.BooleanField(default=False)

    admin_feedback = models.TextField(blank=True, null=True)

    reviewed_at = models.DateTimeField(null=True, blank=True)

    is_correct = models.BooleanField(null=True, blank=True)

    last_saved_at = models.DateTimeField(auto_now=True)

    completed_at = models.DateTimeField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'task')