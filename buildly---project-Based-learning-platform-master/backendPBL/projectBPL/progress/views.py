from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from projects.models import Project
from progress.models import ProjectProgress

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
