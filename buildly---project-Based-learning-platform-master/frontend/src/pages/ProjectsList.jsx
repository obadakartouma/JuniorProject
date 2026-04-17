import React, { useState, useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { projectsAPI } from '../services/api'
import './Projects.css'

const ProjectsList = () => {
  const { isAdmin } = useAuth()
  const [searchParams] = useSearchParams()
  const courseId = searchParams.get('course_id')
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchProjects()
  }, [courseId])

  const fetchProjects = async () => {
    try {
      setLoading(true)
      const response = await projectsAPI.list(courseId)
      setProjects(response.data.projects || [])
    } catch (err) {
      setError('فشل تحميل المشاريع')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('هل أنت متأكد من حذف هذا المشروع؟')) {
      return
    }

    try {
      await projectsAPI.delete(id)
      setProjects(projects.filter((project) => project.project_id !== id))
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

  if (error) {
    return <div className="alert alert-error">{error}</div>
  }

  return (
    <div className="container">
      <div className="page-header">
        <h1>المشاريع التعليمية</h1>
        {isAdmin && (
          <Link to="/projects/create" className="btn btn-primary">
            إضافة مشروع جديد
          </Link>
        )}
      </div>

      {projects.length === 0 ? (
        <div className="empty-state">
          <p>لا توجد مشاريع متاحة</p>
          {isAdmin && (
            <Link to="/projects/create" className="btn btn-primary">
              إنشاء أول مشروع
            </Link>
          )}
        </div>
      ) : (
        <div className="projects-grid">
          {projects.map((project) => (
            <div key={project.project_id} className="project-card">
              <div className="project-header">
                <h3>{project.title}</h3>
                <div className="project-badges">
                  <span className="badge badge-info">{project.level_display}</span>
                  <span className="badge badge-warning">{project.language_display}</span>
                </div>
              </div>
              <p className="project-description">
                {project.description?.substring(0, 150)}...
              </p>
              <div className="project-meta">
                <div className="meta-item">
                  <span className="meta-label">المسار:</span>
                  <span className="meta-value">{project.course_title}</span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">الوقت المقدر:</span>
                  <span className="meta-value">{project.estimated_time} ساعة</span>
                </div>
              </div>
              <div className="project-actions">
                <Link to={`/projects/${project.project_id}`} className="btn btn-primary">
                  عرض التفاصيل
                </Link>
                {isAdmin && (
                  <>
                    <Link
                      to={`/projects/${project.project_id}/edit`}
                      className="btn btn-secondary"
                    >
                      تعديل
                    </Link>
                    <button
                      onClick={() => handleDelete(project.project_id)}
                      className="btn btn-danger"
                    >
                      حذف
                    </button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default ProjectsList

