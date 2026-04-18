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

    class Meta:
        unique_together = ('user', 'project')