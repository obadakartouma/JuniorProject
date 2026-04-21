from django.db import models
from account.models import CustomUser
from projects.models import Project

class ProjectProgress(models.Model):
    STATUS_CHOICES = (
        ('not_started', 'لم يبدأ'),
        ('in_progress', 'قيد التنفيذ'),
        ('completed', 'مكتمل'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    progress_percentage = models.IntegerField(default=0)

    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    is_graded = models.BooleanField(default=False, verbose_name='تم التقييم')
    feedback = models.TextField(null=True, blank=True, verbose_name='ملاحظات التقييم')
    grade_stars = models.IntegerField(null=True, blank=True, verbose_name='نسبة الدرجة')


    class Meta:
        unique_together = ('user', 'project')