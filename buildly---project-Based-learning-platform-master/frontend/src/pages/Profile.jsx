import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { accountAPI } from '../services/api'
import './Profile.css'

const Profile = () => {
  const { user, updateUser } = useAuth()
  const [formData, setFormData] = useState({
    email: '',
  })
  const [profileData, setProfileData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    fetchProfile()
  }, [])

  const fetchProfile = async () => {
    try {
      setLoading(true)
      const response = await accountAPI.getProfile()
      const userData = response.data.user
      setProfileData(userData)
      setFormData({
        email: userData.email || '',
      })
    } catch (err) {
      setError('فشل تحميل بيانات الملف الشخصي')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData({
      ...formData,
      [name]: value,
    })
    setError('')
    setSuccess('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setSaving(true)

    try {
      const response = await accountAPI.updateProfile(formData)
      const updatedUser = response.data.user
      updateUser(updatedUser)
      setProfileData(updatedUser)
      setSuccess('تم تحديث الملف الشخصي بنجاح')
    } catch (err) {
      const errorData = err.response?.data
      if (errorData?.email) {
        setError(Array.isArray(errorData.email) ? errorData.email[0] : errorData.email)
      } else if (errorData?.message) {
        setError(errorData.message)
      } else {
        setError('حدث خطأ أثناء تحديث الملف الشخصي')
      }
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    )
  }

  return (
    <div className="container">
      <div className="page-header">
        <h1>الملف الشخصي</h1>
      </div>

      <div className="profile-container">
        <div className="profile-sidebar">
          <div className="card">
            <div className="profile-avatar">
              <div className="avatar-circle">
                {user?.email?.charAt(0).toUpperCase()}
              </div>
            </div>
            <h2>{user?.email}</h2>
            <p className="user-type">{user?.user_type}</p>
          </div>

          {profileData?.enrollment_info && (
            <div className="card">
              <h3>معلومات الانضمام</h3>
              <div className="info-list">
                <div className="info-item">
                  <span className="info-label">عدد المسارات:</span>
                  <span className="info-value">
                    {profileData.enrollment_info.enrolled_courses_count || 0}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="profile-main">
          <div className="card">
            <h2>تعديل الملف الشخصي</h2>

            {error && <div className="alert alert-error">{error}</div>}
            {success && <div className="alert alert-success">{success}</div>}

            <form onSubmit={handleSubmit} className="profile-form">
              <div className="input-group">
                <label htmlFor="email">البريد الإلكتروني *</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  placeholder="أدخل بريدك الإلكتروني"
                />
              </div>

              <div className="form-actions">
                <button type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? 'جاري الحفظ...' : 'حفظ التغييرات'}
                </button>
              </div>
            </form>
          </div>

          <div className="card">
            <h2>معلومات الحساب</h2>
            <div className="info-list">
              <div className="info-item">
                <span className="info-label">نوع المستخدم:</span>
                <span className="info-value">{profileData?.user_type}</span>
              </div>
              <div className="info-item">
                <span className="info-label">تاريخ الانضمام:</span>
                <span className="info-value">
                  {profileData?.date_joined
                    ? new Date(profileData.date_joined).toLocaleDateString('ar-SA')
                    : '-'}
                </span>
              </div>
              <div className="info-item">
                <span className="info-label">آخر تسجيل دخول:</span>
                <span className="info-value">
                  {profileData?.last_login
                    ? new Date(profileData.last_login).toLocaleDateString('ar-SA')
                    : '-'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Profile

