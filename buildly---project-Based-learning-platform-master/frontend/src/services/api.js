import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// إضافة token تلقائياً للطلبات
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// معالجة الأخطاء تلقائياً
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/account/token/refresh/`, {
            refresh: refreshToken,
          })

          const { access } = response.data
          localStorage.setItem('access_token', access)
          originalRequest.headers.Authorization = `Bearer ${access}`

          return api(originalRequest)
        }
      } catch (refreshError) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

// Account APIs
export const accountAPI = {
  login: (email, password) =>
    api.post('/account/login/', { email, password }),

  registerLearner: (email, password, password2) =>
    api.post('/account/register/learner/', { email, password, password2 }),

  registerAdmin: (email, password, password2) =>
    api.post('/account/register/admin/', { email, password, password2 }),

  logout: (refreshToken) =>
    api.post('/account/logout/', { refresh_token: refreshToken }),

  getProfile: () =>
    api.get('/account/profile/'),

  updateProfile: (data) =>
    api.patch('/account/profile/', data),

  getLearnerDashboard: () =>
    api.get('/account/learner/dashboard/'),

  getLearnerProgress: () =>
    api.get('/account/learner/progress/'),
}

// Courses APIs
export const coursesAPI = {
  list: () =>
    api.get('/courses/'),

  get: (id) =>
    api.get(`/courses/${id}/`),

  getDetails: (id) =>
    api.get(`/courses/${id}/details/`),

  create: (data) =>
    api.post('/courses/create/', data),

  update: (id, data) =>
    api.put(`/courses/${id}/update/`, data),

  delete: (id) =>
    api.delete(`/courses/${id}/delete/`),

  confirmDelete: (id) =>
    api.get(`/courses/${id}/confirm-delete/`),

  join: (id) =>
    api.post(`/courses/${id}/join/`),

  checkEnrollment: (id) =>
    api.get(`/courses/${id}/check-enrollment/`),

  myCourses: () =>
    api.get('/courses/my-courses/'),
}

// Projects APIs
export const projectsAPI = {
  list: (courseId = null) => {
    const params = courseId ? { course_id: courseId } : {}
    return api.get('/projects/', { params })
  },

  get: (id) =>
    api.get(`/projects/${id}/`),

  create: (data) =>
    api.post('/projects/create/', data),

  update: (id, data) =>
    api.put(`/projects/${id}/update/`, data),

  delete: (id) =>
    api.delete(`/projects/${id}/delete/`),

  confirmDelete: (id) =>
    api.get(`/projects/${id}/confirm-delete/`),

  getByCourse: (courseId) =>
    api.get(`/projects/course/${courseId}/`),

  start: (id) =>
    api.post(`/projects/${id}/start/`),
}

export default api

