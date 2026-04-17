# accounts/views_dashboard.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
from .models import CustomUser
from .serializers import ProfileSerializer
import json

class LearnerDashboardView(APIView):
    """لوحة تحكم المتعلم"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # التحقق من أن المستخدم متعلم
        if not user.is_learner:
            return Response({
                'error': _('هذه اللوحة مخصصة للمتعلمين فقط')
            }, status=status.HTTP_403_FORBIDDEN)
        
        # بيانات الملف الشخصي
        profile_serializer = ProfileSerializer(user)
        
        # الإحصائيات
        stats = self.get_learner_stats(user)
        
        # المسارات التعليمية (المشاريع)
        enrolled_projects = self.get_enrolled_projects(user)
        
        # التقدم التعليمي
        progress = self.get_learning_progress(user)
        
        # الإشعارات والنشاطات
        notifications = self.get_recent_notifications(user)
        recent_activity = self.get_recent_activity(user)
        
        # المشاريع المقترحة
        suggested_projects = self.get_suggested_projects(user)
        
        return Response({
            'message': _('لوحة تحكم المتعلم'),
            'user_profile': profile_serializer.data,
            'dashboard_stats': stats,
            'enrolled_projects': enrolled_projects,
            'learning_progress': progress,
            'notifications': notifications,
            'recent_activity': recent_activity,
            'suggested_projects': suggested_projects,
            'quick_actions': self.get_quick_actions(),
        })
    
    def get_learner_stats(self, user):
        """الحصول على إحصائيات المتعلم"""
        enrolled_courses = user.get_enrolled_courses_list() or []
        
        # محاكاة بيانات المشاريع (في النظام الحقيقي سيتم جلبها من قاعدة البيانات)
        completed_projects = len(enrolled_courses) // 2  # افتراضية
        in_progress_projects = len(enrolled_courses) - completed_projects
        total_hours_spent = len(enrolled_courses) * 10  # افتراضية
        skill_level = self.calculate_skill_level(user)
        
        return {
            'total_enrolled_projects': len(enrolled_courses),
            'completed_projects': completed_projects,
            'in_progress_projects': in_progress_projects,
            'total_hours_spent': total_hours_spent,
            'current_streak_days': self.get_streak_days(user),
            'skill_level': skill_level,
            'completion_rate': self.calculate_completion_rate(user),
            'avg_project_score': self.get_average_score(user),
        }
    
    def get_enrolled_projects(self, user):
        """الحصول على المشاريع المنضم إليها"""
        enrolled_courses = user.get_enrolled_courses_list() or []
        
        projects = []
        for i, course_title in enumerate(enrolled_courses[:5]):  # آخر 5 مشاريع
            # محاكاة حالة المشروع
            status_options = ['قيد التنفيذ', 'تم التقديم', 'قيد المراجعة', 'معتمد']
            status = status_options[i % len(status_options)]
            
            progress = (i + 1) * 20 if status != 'معتمد' else 100
            
            project = {
                'id': i + 1,
                'title': course_title,
                'description': f'مشروع تطبيقي في {course_title}',
                'status': status,
                'progress_percentage': progress,
                'deadline': (timezone.now() + timedelta(days=(30 - i*5))).strftime('%Y-%m-%d'),
                'last_activity': (timezone.now() - timedelta(days=i)).strftime('%Y-%m-%d'),
                'category': self.get_project_category(course_title),
                'difficulty': ['مبتدئ', 'متوسط', 'متقدم'][i % 3],
                'estimated_hours': [10, 15, 20, 25, 30][i % 5],
            }
            projects.append(project)
        
        return {
            'count': len(projects),
            'projects': projects,
            'has_more': len(enrolled_courses) > 5,
            'total_count': len(enrolled_courses)
        }
    
    def get_learning_progress(self, user):
        """تتبع التقدم التعليمي"""
        enrolled_courses = user.get_enrolled_courses_list() or []
        
        # محاكاة بيانات التقدم
        progress_data = []
        for i, course in enumerate(enrolled_courses[:6]):
            progress = {
                'project_name': course,
                'progress': min(100, (i + 1) * 20),
                'skills_gained': self.get_skills_for_project(course),
                'time_spent': (i + 1) * 5,
                'last_update': (timezone.now() - timedelta(days=i)).strftime('%Y-%m-%d'),
            }
            progress_data.append(progress)
        
        # مخطط التقدم الشهري (محاكاة)
        monthly_progress = []
        current_date = timezone.now()
        for i in range(6):
            month_date = current_date - timedelta(days=30*i)
            monthly_progress.append({
                'month': month_date.strftime('%b'),
                'completed_projects': (i + 1) * 2,
                'hours_spent': (i + 1) * 15,
            })
        
        return {
            'overall_progress_percentage': min(100, len(enrolled_courses) * 10),
            'progress_by_project': progress_data,
            'monthly_progress': monthly_progress[::-1],  # عكس الترتيب
            'learning_trend': 'تصاعدي' if len(enrolled_courses) > 0 else 'مستقر',
        }
    
    def get_recent_notifications(self, user):
        """الإشعارات الحديثة"""
        return [
            {
                'id': 1,
                'title': 'تمت مراجعة مشروعك',
                'message': 'تمت مراجعة مشروع تطوير واجهة المستخدم',
                'type': 'review',
                'timestamp': (timezone.now() - timedelta(hours=2)).isoformat(),
                'read': False,
            },
            {
                'id': 2,
                'title': 'مشروع جديد متاح',
                'message': 'تم إضافة مشروع جديد في مجال الذكاء الاصطناعي',
                'type': 'new_project',
                'timestamp': (timezone.now() - timedelta(days=1)).isoformat(),
                'read': True,
            },
            {
                'id': 3,
                'title': 'موعد نهائي قريب',
                'message': 'ينتهي تقديم مشروع تطوير تطبيق الجوال بعد 3 أيام',
                'type': 'deadline',
                'timestamp': (timezone.now() - timedelta(days=2)).isoformat(),
                'read': False,
            }
        ]
    
    def get_recent_activity(self, user):
        """النشاطات الحديثة"""
        return [
            {
                'id': 1,
                'action': 'بدأ مشروع جديد',
                'project': 'تطوير تطبيق ويب متكامل',
                'timestamp': (timezone.now() - timedelta(hours=1)).isoformat(),
                'icon': '🚀',
            },
            {
                'id': 2,
                'action': 'تم تقديم مشروع',
                'project': 'تحليل بيانات باستخدام Python',
                'timestamp': (timezone.now() - timedelta(days=1)).isoformat(),
                'icon': '📤',
            },
            {
                'id': 3,
                'action': 'حصل على درجة ممتازة',
                'project': 'تصميم قاعدة بيانات',
                'timestamp': (timezone.now() - timedelta(days=2)).isoformat(),
                'icon': '🏆',
            },
            {
                'id': 4,
                'action': 'أضاف مشروع للمفضلة',
                'project': 'تطوير الذكاء الاصطناعي',
                'timestamp': (timezone.now() - timedelta(days=3)).isoformat(),
                'icon': '⭐',
            },
        ]
    
    def get_suggested_projects(self, user):
        """المشاريع المقترحة بناءً على التقدم"""
        enrolled_courses = user.get_enrolled_courses_list() or []
        
        suggestions = []
        categories = ['تطوير الويب', 'الذكاء الاصطناعي', 'تحليل البيانات', 'تطوير الجوال', 'الأمن السيبراني']
        
        for i, category in enumerate(categories[:3]):
            suggestion = {
                'id': i + 1,
                'title': f'مشروع {category} متقدم',
                'description': f'مشروع تطبيقي متقدم في مجال {category}',
                'category': category,
                'difficulty': 'متقدم' if i > 1 else 'متوسط',
                'estimated_time': [40, 50, 60][i],
                'prerequisites': ['مستوى متوسط', 'معرفة أساسية بالتخصص'],
                'match_percentage': 80 - (i * 10),
                'reason': 'يتناسب مع مهاراتك السابقة',
            }
            suggestions.append(suggestion)
        
        return suggestions
    
    def get_quick_actions(self):
        """الإجراءات السريعة"""
        return [
            {
                'id': 1,
                'title': 'بدء مشروع جديد',
                'icon': '➕',
                'action': 'start_project',
                'description': 'اختر مشروعًا وابدأ العمل',
            },
            {
                'id': 2,
                'title': 'متابعة المشاريع',
                'icon': '📋',
                'action': 'continue_projects',
                'description': 'استكمل مشاريعك النشطة',
            },
            {
                'id': 3,
                'title': 'مراجعة التقدم',
                'icon': '📊',
                'action': 'review_progress',
                'description': 'راجع إحصائيات تقدمك',
            },
            {
                'id': 4,
                'title': 'طلب مساعدة',
                'icon': '💬',
                'action': 'request_help',
                'description': 'تواصل مع المشرفين',
            },
        ]
    
    # === دوال مساعدة ===
    
    def calculate_skill_level(self, user):
        """حساب مستوى المهارة"""
        enrolled_count = len(user.get_enrolled_courses_list() or [])
        if enrolled_count == 0:
            return 'مبتدئ'
        elif enrolled_count <= 3:
            return 'متوسط'
        elif enrolled_count <= 6:
            return 'متقدم'
        else:
            return 'خبير'
    
    def get_streak_days(self, user):
        """عدد الأيام المتتالية للنشاط"""
        # محاكاة - في النظام الحقيقي سيتم حسابها من سجل النشاط
        return 7  # أسبوع
    
    def calculate_completion_rate(self, user):
        """معدل إتمام المشاريع"""
        enrolled = len(user.get_enrolled_courses_list() or [])
        if enrolled == 0:
            return 0
        completed = enrolled // 2  # افتراضية
        return int((completed / enrolled) * 100)
    
    def get_average_score(self, user):
        """متوسط الدرجات"""
        # محاكاة
        return 85
    
    def get_project_category(self, project_title):
        """تحديد تصنيف المشروع من عنوانه"""
        categories = {
            'ويب': 'تطوير الويب',
            'تطبيق': 'تطوير التطبيقات',
            'بيانات': 'تحليل البيانات',
            'ذكاء': 'الذكاء الاصطناعي',
            'أمن': 'الأمن السيبراني',
            'تصميم': 'تصميم واجهات',
        }
        
        for key, category in categories.items():
            if key in project_title:
                return category
        return 'عام'
    
    def get_skills_for_project(self, project_title):
        """المهارات المكتسبة من المشروع"""
        skills_map = {
            'ويب': ['HTML', 'CSS', 'JavaScript', 'React'],
            'تطبيق': ['Flutter', 'React Native', 'Android', 'iOS'],
            'بيانات': ['Python', 'Pandas', 'SQL', 'Tableau'],
            'ذكاء': ['Python', 'TensorFlow', 'ML', 'Deep Learning'],
        }
        
        for key, skills in skills_map.items():
            if key in project_title:
                return skills
        return ['مهارات تقنية', 'حل المشكلات', 'التفكير النقدي']


class LearnerProgressAPIView(APIView):
    """API لمتابعة تقدم المتعلم"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if not user.is_learner:
            return Response({
                'error': _('غير مصرح')
            }, status=status.HTTP_403_FORBIDDEN)
        
        # بيانات التقدم التفصيلية
        progress_data = {
            'overall': {
                'enrollment_date': user.date_joined.strftime('%Y-%m-%d'),
                'days_active': (timezone.now() - user.date_joined).days,
                'total_projects_enrolled': len(user.get_enrolled_courses_list() or []),
                'total_hours_estimated': len(user.get_enrolled_courses_list() or []) * 20,
            },
            'skill_development': self.get_skill_development(user),
            'timeline': self.get_learning_timeline(user),
            'achievements': self.get_achievements(user),
        }
        
        return Response({
            'message': _('تتبع تقدم المتعلم'),
            'progress_data': progress_data,
        })
    
    def get_skill_development(self, user):
        """تطور المهارات"""
        enrolled_courses = user.get_enrolled_courses_list() or []
        
        skills = {}
        for course in enrolled_courses:
            if 'ويب' in course:
                skills['تطوير الويب'] = skills.get('تطوير الويب', 0) + 20
            if 'بيانات' in course:
                skills['تحليل البيانات'] = skills.get('تحليل البيانات', 0) + 25
            if 'ذكاء' in course:
                skills['الذكاء الاصطناعي'] = skills.get('الذكاء الاصطناعي', 0) + 30
            if 'تطبيق' in course:
                skills['تطوير التطبيقات'] = skills.get('تطوير التطبيقات', 0) + 25
        
        return skills
    
    def get_learning_timeline(self, user):
        """خط زمني للتعلم"""
        timeline = []
        enrolled_courses = user.get_enrolled_courses_list() or []
        
        for i, course in enumerate(enrolled_courses[:10]):
            timeline.append({
                'date': (timezone.now() - timedelta(days=i*30)).strftime('%Y-%m'),
                'event': f'الانضمام إلى مشروع {course}',
                'milestone': 'بداية المشروع' if i == 0 else 'مشروع جديد',
            })
        
        return timeline
    
    def get_achievements(self, user):
        """الإنجازات"""
        enrolled_count = len(user.get_enrolled_courses_list() or [])
        
        achievements = []
        
        if enrolled_count >= 1:
            achievements.append({
                'title': 'المبتدئ المتميز',
                'description': 'إكمال أول مشروع',
                'icon': '🎯',
                'unlocked_at': user.date_joined.strftime('%Y-%m-%d'),
            })
        
        if enrolled_count >= 3:
            achievements.append({
                'title': 'المتعلم النشط',
                'description': 'إكمال 3 مشاريع',
                'icon': '⭐',
                'unlocked_at': (timezone.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            })
        
        if enrolled_count >= 5:
            achievements.append({
                'title': 'الخبير الصاعد',
                'description': 'إكمال 5 مشاريع',
                'icon': '🏆',
                'unlocked_at': (timezone.now() - timedelta(days=15)).strftime('%Y-%m-%d'),
            })
        
        return achievements