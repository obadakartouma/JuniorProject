from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from projects.models import Project
from progress.models import ProjectProgress
from django.utils import timezone
from rest_framework.generics import get_object_or_404

class UserProjectProgressView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        progresses = ProjectProgress.objects.filter(user=request.user)

        data = {
            p.project.id: {
                'status': p.status,
                'started_at': p.started_at,
                'completed_at': p.completed_at,
            }
            for p in progresses
        }

        return Response(data)

class CompleteProjectView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, project_id):
        progress, created = ProjectProgress.objects.get_or_create(
            user=request.user, 
            project_id=project_id
        )
        
        progress.status = 'completed'
        progress.progress_percentage = 100
        progress.completed_at = timezone.now()
        progress.save()
        
        return Response({'status': 'project completed successfully'})
    
class ProjectProgressDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, project_id):
        progress = get_object_or_404(ProjectProgress, user=request.user, project_id=project_id)
        
        # Berechnung der Dauer, falls abgeschlossen
        duration = None
        if progress.started_at and progress.completed_at:
            diff = progress.completed_at - progress.started_at
            # Dauer in Minuten umrechnen
            duration = round(diff.total_seconds() / 60) 

        return Response({
            'status': progress.status,
            'started_at': progress.started_at,
            'completed_at': progress.completed_at,
            'duration_minutes': duration,
            'progress_percentage': progress.progress_percentage
        })
