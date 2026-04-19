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
  const [progress, setProgress] = useState({})
  const [levelFilter, setLevelFilter] = useState('all')

  useEffect(() => {
    fetchProjects()
  }, [courseId])

  const fetchProjects = async () => {
    try {
      setLoading(true)

      const [projectsRes, progressRes] = await Promise.all([
        projectsAPI.list(courseId),
        projectsAPI.getProgress()
      ])

      setProjects(projectsRes.data.projects || [])
      setProgress(progressRes.data || {})
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

  const getStatusLabel = (status) => {
    switch (status) {
      case 'completed':
        return 'مكتمل'
      case 'in_progress':
        return 'قيد التنفيذ'
      default:
        return 'لم يبدأ'
    }
  }

  const getStatusClass = (status) => {
    switch (status) {
      case 'completed':
        return 'status-completed'
      case 'in_progress':
        return 'status-progress'
      default:
        return 'status-not-started'
    }
  }

  const getProjectStatus = (projectId) => {
    return progress[projectId]?.status || 'not_started'
  }

  const filteredProjects = projects.filter((project) => {
    if (levelFilter === 'all') return true
    return project.level === levelFilter
  })

  const groupedProjects = {
    not_started: [],
    in_progress: [],
    completed: []
  }

  filteredProjects.forEach((project) => {
    const status = getProjectStatus(project.project_id)
    groupedProjects[status].push(project)
  })

  const ProjectSection = ({ title, projects, isAdmin, handleDelete }) => {
    if (!projects.length) return null

    return (
      <div className="project-section">
        <h2 className="section-title">{title}</h2>

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
                  <span className="meta-label">الوقت:</span>
                  <span className="meta-value">{project.estimated_time} ساعة</span>
                </div>
              </div>

              <div className="project-actions">
                <Link to={`/projects/${project.project_id}`} className="btn btn-primary">
                  عرض التفاصيل
                </Link>

                {isAdmin && (
                  <>
                    <Link to={`/projects/${project.project_id}/edit`} className="btn btn-secondary">
                      تعديل
                    </Link>
                    <button onClick={() => handleDelete(project.project_id)} className="btn btn-danger">
                      حذف
                    </button>
                  </>
                )}
              </div>

            </div>
          ))}
        </div>
      </div>
    )
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

      <div className="container">
        <div className="page-header">
          <h1>المشاريع التعليمية</h1>
          <div className="filters-bar">
            <select
              value={levelFilter}
              onChange={(e) => setLevelFilter(e.target.value)}
              className="filter-select"
            >
              <option value="all">جميع المستويات</option>
              <option value="beginner">مبتدئ</option>
              <option value="intermediate">متوسط</option>
              <option value="advanced">متقدم</option>
              <option value="expert">خبير</option>
            </select>
          </div>
          {isAdmin && (
            <Link to="/projects/create" className="btn btn-primary">
              إضافة مشروع جديد
            </Link>
          )}
        </div>

        {projects.length === 0 ? (
          <div className="empty-state">
            <p>لا توجد مشاريع متاحة</p>
          </div>
        ) : (
          <div className="projects-sections">

            <ProjectSection
              title="🆕 لم يبدأ"
              projects={groupedProjects.not_started}
              isAdmin={isAdmin}
              handleDelete={handleDelete}
            />

            <ProjectSection
              title="🔄 قيد التنفيذ"
              projects={groupedProjects.in_progress}
              isAdmin={isAdmin}
              handleDelete={handleDelete}
            />

            <ProjectSection
              title="✅ مكتمل"
              projects={groupedProjects.completed}
              isAdmin={isAdmin}
              handleDelete={handleDelete}
            />

          </div>
        )}
      </div>

    </div>
  )
}

export default ProjectsList

