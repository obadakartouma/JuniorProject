import React, { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { coursesAPI } from '../services/api'
import './Courses.css'

const CourseDetail = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const { isAdmin, isLearner } = useAuth()
  const [course, setCourse] = useState(null)
  const [isEnrolled, setIsEnrolled] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [joining, setJoining] = useState(false)

  useEffect(() => {
    fetchCourseDetails()
    if (isLearner) {
      checkEnrollment()
    }
  }, [id, isLearner])

  const fetchCourseDetails = async () => {
    try {
      setLoading(true)
      const response = await coursesAPI.getDetails(id)
      setCourse(response.data.course)
    } catch (err) {
      setError('فشل تحميل تفاصيل المسار')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const checkEnrollment = async () => {
    try {
      const response = await coursesAPI.checkEnrollment(id)
      setIsEnrolled(response.data.is_enrolled)
    } catch (err) {
      console.error('Error checking enrollment:', err)
    }
  }

  const handleJoin = async () => {
    try {
      setJoining(true)
      await coursesAPI.join(id)
      setIsEnrolled(true)
      alert('تم الانضمام للمسار بنجاح')
    } catch (err) {
      const errorMsg =
        err.response?.data?.error || err.response?.data?.message || 'فشل الانضمام للمسار'
      alert(errorMsg)
    } finally {
      setJoining(false)
    }
  }

  const handleDelete = async () => {
    if (!window.confirm('هل أنت متأكد من حذف هذا المسار؟')) {
      return
    }

    try {
      await coursesAPI.delete(id)
      navigate('/courses')
    } catch (err) {
      alert('فشل حذف المسار')
    }
  }

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    )
  }

  if (error || !course) {
    return <div className="alert alert-error">{error || 'المسار غير موجود'}</div>
  }

  return (
    <div className="container">
      <div className="page-header">
        <div>
          <Link to="/courses" className="back-link">
            ← العودة للمسارات
          </Link>
          <h1>{course.title}</h1>
        </div>
        {isAdmin && (
          <div className="header-actions">
            <Link to={`/courses/${id}/edit`} className="btn btn-secondary">
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
            <p>{course.description}</p>
          </div>

          {course.course_projects && course.course_projects.length > 0 && (
            <div className="card">
              <h2>المشاريع في هذا المسار</h2>
              <div className="projects-list">
                {course.course_projects.map((project) => (
                  <Link
                    key={project.project_id}
                    to={`/projects/${project.project_id}`}
                    className="project-link"
                  >
                    <div className="project-link-content">
                      <h4>{project.title}</h4>
                      <p>{project.description?.substring(0, 100)}...</p>
                      <div className="project-link-meta">
                        <span className="badge">{project.level_display}</span>
                        <span className="badge">{project.language_display}</span>
                        <span>{project.estimated_time} ساعة</span>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="detail-sidebar">
          <div className="card">
            <h3>معلومات المسار</h3>
            <div className="info-list">
              <div className="info-item">
                <span className="info-label">المستوى:</span>
                <span className="info-value">{course.level_display}</span>
              </div>
              <div className="info-item">
                <span className="info-label">الفئة:</span>
                <span className="info-value">{course.category_display}</span>
              </div>
              <div className="info-item">
                <span className="info-label">المدة المقدرة:</span>
                <span className="info-value">{course.estimated_duration} ساعة</span>
              </div>
              <div className="info-item">
                <span className="info-label">عدد المشاريع:</span>
                <span className="info-value">{course.projects_count || 0}</span>
              </div>
              <div className="info-item">
                <span className="info-label">المتعلمين المنضمين:</span>
                <span className="info-value">{course.enrolled_students_count || 0}</span>
              </div>
              <div className="info-item">
                <span className="info-label">المشرف:</span>
                <span className="info-value">{course.instructor_name}</span>
              </div>
            </div>
          </div>

          {isLearner && (
            <div className="card">
              {isEnrolled ? (
                <div className="enrollment-status enrolled">
                  <h4>أنت منضم لهذا المسار</h4>
                  <Link to="/my-courses" className="btn btn-primary">
                    عرض مساراتي
                  </Link>
                </div>
              ) : (
                <div className="enrollment-status">
                  <h4>انضم للمسار</h4>
                  <button
                    onClick={handleJoin}
                    className="btn btn-primary"
                    disabled={joining}
                  >
                    {joining ? 'جاري الانضمام...' : 'انضم الآن'}
                  </button>
                </div>
              )}
            </div>
          )}

          {isAdmin && (
            <div className="card">
              <Link to={`/projects/course/${id}`} className="btn btn-primary">
                عرض مشاريع المسار
              </Link>
              <Link
                to="/projects/create"
                state={{ courseId: id }}
                className="btn btn-secondary"
                style={{ marginTop: '12px' }}
              >
                إضافة مشروع جديد
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default CourseDetail

