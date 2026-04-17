import React, { useState, useEffect } from 'react'
import { useParams, useNavigate, Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { projectsAPI } from '../services/api'
import './Projects.css'

const ProjectDetail = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const location = useLocation()
  const { isAdmin, isLearner } = useAuth()
  const [project, setProject] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [starting, setStarting] = useState(false)

  useEffect(() => {
    fetchProjectDetails()
  }, [id])

  const fetchProjectDetails = async () => {
    try {
      setLoading(true)
      const response = await projectsAPI.get(id)
      setProject(response.data.project)
    } catch (err) {
      setError('فشل تحميل تفاصيل المشروع')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleStart = async () => {
    try {
      setStarting(true)
      await projectsAPI.start(id)
      alert('تم بدء المشروع بنجاح!')
    } catch (err) {
      const errorMsg =
        err.response?.data?.message || 'فشل بدء المشروع'
      alert(errorMsg)
    } finally {
      setStarting(false)
    }
  }

  const handleDelete = async () => {
    if (!window.confirm('هل أنت متأكد من حذف هذا المشروع؟')) {
      return
    }

    try {
      await projectsAPI.delete(id)
      navigate('/projects')
    } catch (err) {
      alert('فشل حذف المشروع')
    }
  }

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    )
  }

  if (error || !project) {
    return <div className="alert alert-error">{error || 'المشروع غير موجود'}</div>
  }

  return (
    <div className="container">
      <div className="page-header">
        <div>
          <Link to="/projects" className="back-link">
            ← العودة للمشاريع
          </Link>
          <h1>{project.title}</h1>
        </div>
        {isAdmin && (
          <div className="header-actions">
            <Link to={`/projects/${id}/edit`} className="btn btn-secondary">
              تعديل
            </Link>
            <button onClick={handleDelete} className="btn btn-danger">
              حذف
            </button>
          </div>
        )}
      </div>

      <div className="detail-grid">
        <div className="detail-main">
          <div className="card">
            <h2>الوصف</h2>
            <p>{project.description}</p>
          </div>

          {project.requirements && (
            <div className="card">
              <h2>المتطلبات</h2>
              <p>{project.requirements}</p>
            </div>
          )}

          {project.objectives && (
            <div className="card">
              <h2>الأهداف التعليمية</h2>
              <p>{project.objectives}</p>
            </div>
          )}

          {project.resources && (
            <div className="card">
              <h2>الموارد</h2>
              <p>{project.resources}</p>
            </div>
          )}
        </div>

        <div className="detail-sidebar">
          <div className="card">
            <h3>معلومات المشروع</h3>
            <div className="info-list">
              <div className="info-item">
                <span className="info-label">المسار:</span>
                <span className="info-value">{project.course_title}</span>
              </div>
              <div className="info-item">
                <span className="info-label">المستوى:</span>
                <span className="info-value">{project.level_display}</span>
              </div>
              <div className="info-item">
                <span className="info-label">لغة البرمجة:</span>
                <span className="info-value">{project.language_display}</span>
              </div>
              <div className="info-item">
                <span className="info-label">الوقت المقدر:</span>
                <span className="info-value">{project.estimated_time} ساعة</span>
              </div>
              <div className="info-item">
                <span className="info-label">الترتيب:</span>
                <span className="info-value">{project.order || 0}</span>
              </div>
            </div>
          </div>

          {isLearner && (
            <div className="card">
              <button
                onClick={handleStart}
                className="btn btn-primary"
                disabled={starting}
                style={{ width: '100%' }}
              >
                {starting ? 'جاري البدء...' : 'بدء المشروع'}
              </button>
            </div>
          )}

          {isAdmin && (
            <div className="card">
              <Link
                to={`/courses/${project.course_id}`}
                className="btn btn-secondary"
                style={{ width: '100%', marginBottom: '12px' }}
              >
                عرض المسار
              </Link>
              <Link
                to={`/projects/course/${project.course_id}`}
                className="btn btn-secondary"
                style={{ width: '100%' }}
              >
                مشاريع المسار
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ProjectDetail

