import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { coursesAPI } from '../services/api'
import './Courses.css'

const MyCourses = () => {
  const [courses, setCourses] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchMyCourses()
  }, [])

  const fetchMyCourses = async () => {
    try {
      setLoading(true)
      const response = await coursesAPI.myCourses()
      setCourses(response.data.courses || [])
    } catch (err) {
      setError('فشل تحميل مساراتك')
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

  return (
    <div className="container">
      <div className="page-header">
        <h1>مساراتي</h1>
        <Link to="/courses" className="btn btn-secondary">
          استكشف المزيد
        </Link>
      </div>

      {courses.length === 0 ? (
        <div className="empty-state">
          <p>لم تنضم لأي مسار بعد</p>
          <Link to="/courses" className="btn btn-primary">
            تصفح المسارات المتاحة
          </Link>
        </div>
      ) : (
        <div className="courses-grid">
          {courses.map((course) => (
            <div key={course.id} className="course-card">
              <div className="course-header">
                <h3>{course.title}</h3>
                <div className="course-badges">
                  <span className="badge badge-info">{course.level_display}</span>
                  <span className="badge badge-warning">{course.category_display}</span>
                </div>
              </div>
              <p className="course-description">
                {course.description?.substring(0, 150)}...
              </p>
              <div className="course-meta">
                <div className="meta-item">
                  <span className="meta-label">المدة:</span>
                  <span className="meta-value">{course.estimated_duration} ساعة</span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">المشاريع:</span>
                  <span className="meta-value">{course.projects_count || 0}</span>
                </div>
              </div>
              <div className="course-actions">
                <Link to={`/courses/${course.id}`} className="btn btn-primary">
                  عرض التفاصيل
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default MyCourses

