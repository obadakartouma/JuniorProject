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
  const [progress, setProgress] = useState(null)
  const [submissions, setSubmissions] = useState([])
  const [filterGraded, setFilterGraded] = useState('all')

  useEffect(() => {
    fetchProjectDetails()
    if (isAdmin) {
      fetchSubmissions();
    }
  }, [id, isAdmin])

  const fetchProjectDetails = async () => {
    try {
      setLoading(true)
      const response = await projectsAPI.get(id)
      setProject(response.data.project)
      if (isLearner) {
        try {
          const progRes = await projectsAPI.getProjectProgress(id)
          setProgress(progRes.data)
        } catch (e) {
          setProgress(null)
        }
      }
    } catch (err) {
      setError('فشل تحميل تفاصيل المشروع')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const fetchSubmissions = async () => {
    try {
      const response = await projectsAPI.getSubmissions(id);
      setSubmissions(response.data);
    } catch (err) {
      console.error("Failed to fetch submissions", err);
    }
  };

  const filteredSubmissions = submissions.filter(s => {
    if (filterGraded === 'graded') return s.is_graded;
    if (filterGraded === 'ungraded') return !s.is_graded;
    return true;
  });

  const handleStart = async () => {
    try {
      setStarting(true)

      const response = await projectsAPI.start(id)

      navigate(`/projects/${id}/work`)
    } catch (err) {
      const errorMsg =
        err.response?.data?.message ||
        err.response?.data?.error ||
        'فشل بدء المشروع'

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

  const formatDate = (dateString) => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleString('ar-EG', {
      year: 'numeric', month: 'long', day: 'numeric',
      hour: '2-digit', minute: '2-digit'
    })
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

          {project.starter_file && (
            <div className="card">
              <h2>ملف البداية</h2>

              <div className="starter-file-single">

                <div className="file-info">
                  <span className="file-icon">📄</span>
                  <span className="file-name">
                    {project.starter_file.file_name}
                  </span>
                </div>

                <a
                  href={project.starter_file.file_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-secondary"
                >
                  تحميل الملف
                </a>

              </div>
            </div>
          )}

          {isAdmin && (
            <div className="card submissions-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                <h2>قائمة التسليمات ({submissions.length})</h2>

                {/* Filter-Dropdown */}
                <select
                  value={filterGraded}
                  onChange={(e) => setFilterGraded(e.target.value)}
                  className="filter-select"
                >
                  <option value="all">الكل</option>
                  <option value="ungraded">لم يتم تقييمها</option>
                  <option value="graded">تم تقييمها</option>
                </select>
              </div>

              {filteredSubmissions.length === 0 ? (
                <p>لا يوجد تسليمات تطابق الفلتر حالياً.</p>
              ) : (
                <div className="table-responsive">
                  <table className="submissions-table">
                    <thead>
                      <tr>
                        <th>الطالب</th>
                        <th>تاريخ التسليم</th>
                        <th>الحالة</th>
                        <th>الدرجة</th>
                        <th>إجراءات</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredSubmissions.map(sub => (
                        <tr key={sub.id}>
                          <td>
                            <div>{sub.user_name}</div>
                            <small style={{ color: '#666' }}>{sub.user_email}</small>
                          </td>
                          <td>{formatDate(sub.completed_at)}</td>
                          <td>
                            <span className={`status-badge ${sub.is_graded ? 'completed' : 'in_progress'}`}>
                              {sub.is_graded ? 'مقيم' : 'بانتظار التقييم'}
                            </span>
                          </td>
                          <td>{sub.grade_stars !== null ? `${sub.grade_stars}★` : '-'}</td>
                          <td>
                            <button
                              className="btn btn-secondary btn-sm"
                              onClick={() => navigate(`/projects/${id}/review/${sub.user_id}`)}
                            >
                              تقييم
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
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
            <>
              {/* Statistiken Card */}
              {progress && (
                <div className="card stats-card">
                  <h3>إحصائيات الإنجاز</h3>
                  <div className="info-list">
                    <div className="info-item">
                      <span className="info-label">حالة المشروع:</span>
                      <span className={`status-badge ${progress.status}`}>
                        {progress.status === 'completed' ? 'مكتمل' : 'قيد التنفيذ'}
                      </span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">وقت البدء:</span>
                      <span className="info-value">{formatDate(progress.started_at)}</span>
                    </div>
                    {progress.completed_at && (
                      <>
                        <div className="info-item">
                          <span className="info-label">وقت الإنجاز:</span>
                          <span className="info-value">{formatDate(progress.completed_at)}</span>
                        </div>
                        <div className="info-item">
                          <span className="info-label">المستغرق:</span>
                          <span className="info-value">{progress.duration_minutes} دقيقة</span>
                        </div>
                      </>
                    )}
                  </div>
                </div>
              )}

              <div className="card">
                <button
                  onClick={handleStart}
                  className="btn btn-primary"
                  disabled={starting || progress?.status === 'completed'}
                  style={{ width: '100%' }}
                >
                  {starting ? 'جاري البدء...' :
                    progress?.status === 'completed' ? 'مراجعة المشروع' :
                      progress ? 'مواصلة العمل' : 'بدء المشروع'}
                </button>
              </div>
            </>
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

