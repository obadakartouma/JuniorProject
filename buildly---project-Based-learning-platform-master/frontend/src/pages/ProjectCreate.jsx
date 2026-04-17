import React, { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { coursesAPI, projectsAPI } from '../services/api'
import './Form.css'

const ProjectCreate = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const courseIdFromState = location.state?.courseId
  const [courses, setCourses] = useState([])
  const [formData, setFormData] = useState({
    course_id: courseIdFromState || '',
    title: '',
    description: '',
    requirements: '',
    objectives: '',
    resources: '',
    estimated_time: '',
    level: 'beginner',
    language: 'python',
    order: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [fetchingCourses, setFetchingCourses] = useState(true)

  useEffect(() => {
    fetchCourses()
  }, [])

  const fetchCourses = async () => {
    try {
      setFetchingCourses(true)
      const response = await coursesAPI.list()
      setCourses(response.data.courses || [])
      if (courseIdFromState) {
        setFormData((prev) => ({ ...prev, course_id: courseIdFromState }))
      }
    } catch (err) {
      console.error('Error fetching courses:', err)
    } finally {
      setFetchingCourses(false)
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData({
      ...formData,
      [name]: value,
    })
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const submitData = {
        ...formData,
        course_id: parseInt(formData.course_id),
        estimated_time: parseInt(formData.estimated_time),
        order: formData.order ? parseInt(formData.order) : undefined,
      }
      const response = await projectsAPI.create(submitData)
      if (response.data.success) {
        navigate(`/projects/${response.data.project.project_id}`)
      }
    } catch (err) {
      const errorData = err.response?.data
      if (errorData?.errors) {
        setError(Array.isArray(errorData.errors) ? errorData.errors.join(', ') : errorData.errors)
      } else if (errorData?.message) {
        setError(errorData.message)
      } else {
        setError('حدث خطأ أثناء إنشاء المشروع')
      }
    } finally {
      setLoading(false)
    }
  }

  if (fetchingCourses) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    )
  }

  return (
    <div className="container">
      <div className="page-header">
        <h1>إنشاء مشروع جديد</h1>
      </div>

      <div className="form-container">
        {error && <div className="alert alert-error">{error}</div>}

        <form onSubmit={handleSubmit} className="form">
          <div className="input-group">
            <label htmlFor="course_id">المسار التعليمي *</label>
            <select
              id="course_id"
              name="course_id"
              value={formData.course_id}
              onChange={handleChange}
              required
            >
              <option value="">اختر المسار</option>
              {courses.map((course) => (
                <option key={course.id} value={course.id}>
                  {course.title}
                </option>
              ))}
            </select>
          </div>

          <div className="input-group">
            <label htmlFor="title">عنوان المشروع *</label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              required
              minLength={3}
              placeholder="أدخل عنوان المشروع"
            />
          </div>

          <div className="input-group">
            <label htmlFor="description">وصف المشروع *</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              required
              minLength={20}
              placeholder="أدخل وصفاً مفصلاً للمشروع"
            />
          </div>

          <div className="input-group">
            <label htmlFor="requirements">المتطلبات</label>
            <textarea
              id="requirements"
              name="requirements"
              value={formData.requirements}
              onChange={handleChange}
              placeholder="متطلبات إنجاز المشروع"
            />
          </div>

          <div className="input-group">
            <label htmlFor="objectives">الأهداف التعليمية</label>
            <textarea
              id="objectives"
              name="objectives"
              value={formData.objectives}
              onChange={handleChange}
              placeholder="الأهداف التي سيحققها الطالب"
            />
          </div>

          <div className="input-group">
            <label htmlFor="resources">الموارد</label>
            <textarea
              id="resources"
              name="resources"
              value={formData.resources}
              onChange={handleChange}
              placeholder="الموارد والمراجع المطلوبة"
            />
          </div>

          <div className="form-row">
            <div className="input-group">
              <label htmlFor="level">المستوى *</label>
              <select
                id="level"
                name="level"
                value={formData.level}
                onChange={handleChange}
                required
              >
                <option value="beginner">مبتدئ</option>
                <option value="intermediate">متوسط</option>
                <option value="advanced">متقدم</option>
                <option value="expert">خبير</option>
              </select>
            </div>

            <div className="input-group">
              <label htmlFor="language">لغة البرمجة *</label>
              <select
                id="language"
                name="language"
                value={formData.language}
                onChange={handleChange}
                required
              >
                <option value="python">Python</option>
                <option value="javascript">JavaScript</option>
                <option value="java">Java</option>
                <option value="csharp">C#</option>
                <option value="cpp">C++</option>
                <option value="php">PHP</option>
                <option value="ruby">Ruby</option>
                <option value="go">Go</option>
                <option value="swift">Swift</option>
                <option value="kotlin">Kotlin</option>
                <option value="typescript">TypeScript</option>
                <option value="dart">Dart</option>
                <option value="rust">Rust</option>
                <option value="other">أخرى</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="input-group">
              <label htmlFor="estimated_time">الوقت المقدر (بالساعات) *</label>
              <input
                type="number"
                id="estimated_time"
                name="estimated_time"
                value={formData.estimated_time}
                onChange={handleChange}
                required
                min="1"
                max="500"
                placeholder="أدخل الوقت المقدر"
              />
            </div>

            <div className="input-group">
              <label htmlFor="order">الترتيب</label>
              <input
                type="number"
                id="order"
                name="order"
                value={formData.order}
                onChange={handleChange}
                min="0"
                placeholder="ترتيب المشروع في المسار"
              />
            </div>
          </div>

          <div className="form-actions">
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'جاري الإنشاء...' : 'إنشاء المشروع'}
            </button>
            <button
              type="button"
              onClick={() => navigate('/projects')}
              className="btn btn-secondary"
            >
              إلغاء
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default ProjectCreate

