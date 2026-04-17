import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { coursesAPI } from '../services/api'
import './Form.css'

const CourseEdit = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    level: 'beginner',
    category: 'other',
    estimated_duration: '',
    is_public: false,
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [fetching, setFetching] = useState(true)

  useEffect(() => {
    fetchCourse()
  }, [id])

  const fetchCourse = async () => {
    try {
      setFetching(true)
      const response = await coursesAPI.get(id)
      const course = response.data.course
      setFormData({
        title: course.title,
        description: course.description,
        level: course.level,
        category: course.category,
        estimated_duration: course.estimated_duration,
        is_public: course.is_public,
      })
    } catch (err) {
      setError('فشل تحميل بيانات المسار')
    } finally {
      setFetching(false)
    }
  }

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value,
    })
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await coursesAPI.update(id, formData)
      navigate(`/courses/${id}`)
    } catch (err) {
      const errorData = err.response?.data
      if (errorData?.errors) {
        setError(Array.isArray(errorData.errors) ? errorData.errors.join(', ') : errorData.errors)
      } else if (errorData?.message) {
        setError(errorData.message)
      } else {
        setError('حدث خطأ أثناء تحديث المسار')
      }
    } finally {
      setLoading(false)
    }
  }

  if (fetching) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    )
  }

  return (
    <div className="container">
      <div className="page-header">
        <h1>تعديل المسار</h1>
      </div>

      <div className="form-container">
        {error && <div className="alert alert-error">{error}</div>}

        <form onSubmit={handleSubmit} className="form">
          <div className="input-group">
            <label htmlFor="title">عنوان المسار *</label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              required
              minLength={3}
              placeholder="أدخل عنوان المسار"
            />
          </div>

          <div className="input-group">
            <label htmlFor="description">وصف المسار *</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              required
              minLength={20}
              placeholder="أدخل وصفاً مفصلاً للمسار"
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
              <label htmlFor="category">الفئة *</label>
              <select
                id="category"
                name="category"
                value={formData.category}
                onChange={handleChange}
                required
              >
                <option value="web">تطوير الويب</option>
                <option value="mobile">تطوير الموبايل</option>
                <option value="data">علوم البيانات</option>
                <option value="ai">الذكاء الاصطناعي</option>
                <option value="design">التصميم</option>
                <option value="business">أعمال</option>
                <option value="language">لغات</option>
                <option value="other">أخرى</option>
              </select>
            </div>
          </div>

          <div className="input-group">
            <label htmlFor="estimated_duration">المدة المقدرة (بالساعات) *</label>
            <input
              type="number"
              id="estimated_duration"
              name="estimated_duration"
              value={formData.estimated_duration}
              onChange={handleChange}
              required
              min="1"
              max="1000"
              placeholder="أدخل المدة بالساعات"
            />
          </div>

          <div className="input-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                name="is_public"
                checked={formData.is_public}
                onChange={handleChange}
              />
              <span>مسار عام (متاح للجميع)</span>
            </label>
          </div>

          <div className="form-actions">
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'جاري التحديث...' : 'حفظ التغييرات'}
            </button>
            <button
              type="button"
              onClick={() => navigate(`/courses/${id}`)}
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

export default CourseEdit

