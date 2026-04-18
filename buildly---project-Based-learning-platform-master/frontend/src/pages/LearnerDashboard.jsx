import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { accountAPI } from '../services/api'
import './Dashboard.css'

const LearnerDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      const response = await accountAPI.getLearnerDashboard()
      setDashboardData(response.data)
    } catch (err) {
      setError('فشل تحميل بيانات لوحة التحكم')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    )
  }

  if (error) {
    return <div className="alert alert-error">{error}</div>
  }

  if (!dashboardData) {
    return null
  }

  const {
    dashboard_stats,
    enrolled_projects,
    learning_progress,
    notifications,
    recent_activity,
    suggested_projects
  } = dashboardData

  return (
    <div className="container">
      <div className="dashboard-header">
        <h1>لوحة تحكم المتعلم</h1>
        <p>مرحباً بك في لوحة التحكم الخاصة بك</p>
      </div>

      {/* الإحصائيات */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#dbeafe' }}>
            <span style={{ color: '#3b82f6' }}>📚</span>
          </div>
          <div className="stat-content">
            <h3>{dashboard_stats?.total_enrolled_projects || 0}</h3>
            <p>المسارات المنضم إليها</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#d1fae5' }}>
            <span style={{ color: '#10b981' }}>✅</span>
          </div>
          <div className="stat-content">
            <h3>{dashboard_stats?.completed_projects || 0}</h3>
            <p>المشاريع المكتملة</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#fef3c7' }}>
            <span style={{ color: '#f59e0b' }}>⏳</span>
          </div>
          <div className="stat-content">
            <h3>{dashboard_stats?.in_progress_projects || 0}</h3>
            <p>المشاريع قيد التنفيذ</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#e9d5ff' }}>
            <span style={{ color: '#8b5cf6' }}>⏰</span>
          </div>
          <div className="stat-content">
            <h3>{dashboard_stats?.total_hours_spent || 0}</h3>
            <p>ساعات التعلم</p>
          </div>
        </div>
      </div>

      <div className="dashboard-grid">
        {/* المسارات المنضم إليها */}
        <div className="dashboard-card">
          <div className="card-header">
            <h2>مساراتي</h2>
            <Link to="/my-courses" className="btn btn-secondary">
              عرض الكل
            </Link>
          </div>
          <div className="projects-list">
            {enrolled_projects?.projects?.length > 0 ? (
              enrolled_projects.projects.map((project) => (
                <div key={project.id} className="project-item">
                  <div className="project-info">
                    <h4>{project.title}</h4>
                    <p>{project.description}</p>
                    <div className="project-meta">
                      <span className="badge badge-info">{project.category}</span>
                      <span className="badge badge-warning">{project.difficulty}</span>
                    </div>
                  </div>
                  <div className="project-progress">
                    <div className="progress-bar">
                      <div
                        className="progress-fill"
                        style={{ width: `${project.progress_percentage}%` }}
                      ></div>
                    </div>
                    <span>{project.progress_percentage}%</span>
                  </div>
                </div>
              ))
            ) : (
              <p className="empty-state">لم تنضم لأي مسار بعد</p>
            )}
          </div>
        </div>

        {/* التقدم التعليمي */}
        <div className="dashboard-card">
          <div className="card-header">
            <h2>التقدم التعليمي</h2>
          </div>
          <div className="progress-overview">
            <div className="progress-circle">
              <div className="progress-value">
                {learning_progress?.overall_progress_percentage || 0}%
              </div>
            </div>
            <p>معدل الإتمام الإجمالي</p>
          </div>
        </div>

        {/* الإشعارات */}
        <div className="dashboard-card">
          <div className="card-header">
            <h2>الإشعارات</h2>
          </div>
          <div className="notifications-list">
            {notifications?.length > 0 ? (
              notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`notification-item ${!notification.read ? 'unread' : ''}`}
                >
                  <h4>{notification.title}</h4>
                  <p>{notification.message}</p>
                  <span className="notification-time">
                    {new Date(notification.timestamp).toLocaleDateString('ar-SA')}
                  </span>
                </div>
              ))
            ) : (
              <p className="empty-state">لا توجد إشعارات</p>
            )}
          </div>
        </div>

        {/* النشاطات الحديثة */}
        <div className="dashboard-card">
          <div className="card-header">
            <h2>النشاطات الحديثة</h2>
          </div>
          <div className="activity-list">
            {recent_activity?.length > 0 ? (
              recent_activity.map((activity) => (
                <div key={activity.id} className="activity-item">
                  <div className="activity-icon">{activity.icon}</div>
                  <div className="activity-content">
                    <p>{activity.action}</p>
                    <span>{activity.project}</span>
                  </div>
                  <span className="activity-time">
                    {new Date(activity.timestamp).toLocaleDateString('ar-SA')}
                  </span>
                </div>
              ))
            ) : (
              <p className="empty-state">لا توجد نشاطات</p>
            )}
          </div>
        </div>
      </div>

      {/* المشاريع المقترحة */}
      {suggested_projects?.length > 0 && (
        <div className="dashboard-card">
          <div className="card-header">
            <h2>مشاريع مقترحة</h2>
          </div>

          
          {!dashboardData?.user_profile?.is_rated ? (
            <div className="empty-state">
              <p>قم بإجراء الاختبار للحصول على مشاريع مناسبة لك</p>
              <Link to="/courses" className="btn btn-primary">
                ابدأ الاختبار
              </Link>
            </div>
          ) : suggested_projects?.length > 0 ? (

            <div className="suggested-projects">
              {suggested_projects.map((project) => (
                <div key={project.id} className="suggested-project-card">
                  <h4>{project.title}</h4>
                  <p>{project.description}</p>

                  <div className="project-tags">
                    <span className="badge">{project.category}</span>
                    <span className="badge">{project.difficulty}</span>
                  </div>

                  <div className="match-percentage">
                    <span>يتناسب معك: {project.match_percentage}%</span>
                  </div>
                </div>
              ))}
            </div>

          ) : (
            <p className="empty-state">لا توجد مشاريع مناسبة حالياً</p>
          )}
        </div>
      )}
    </div>
  )
}

export default LearnerDashboard

