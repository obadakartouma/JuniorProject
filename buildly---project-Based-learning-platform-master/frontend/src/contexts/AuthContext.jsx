import React, { createContext, useState, useEffect, useContext } from 'react'
import { accountAPI } from '../services/api'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    // تحميل بيانات المستخدم من localStorage
    const storedUser = localStorage.getItem('user')
    const accessToken = localStorage.getItem('access_token')

    if (storedUser && accessToken) {
      try {
        const userData = JSON.parse(storedUser)
        setUser(userData)
        setIsAuthenticated(true)
      } catch (error) {
        console.error('Error parsing user data:', error)
        localStorage.removeItem('user')
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
      }
    }

    setLoading(false)
  }, [])

  const login = async (email, password) => {
    try {
      const response = await accountAPI.login(email, password)
      const { user: userData, tokens } = response.data

      localStorage.setItem('access_token', tokens.access)
      localStorage.setItem('refresh_token', tokens.refresh)
      localStorage.setItem('user', JSON.stringify(userData))

      setUser(userData)
      setIsAuthenticated(true)

      return { success: true, data: response.data }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data || { message: 'حدث خطأ أثناء تسجيل الدخول' },
      }
    }
  }

  const register = async (email, password, password2, userType = 'learner') => {
    try {
      const apiCall =
        userType === 'admin'
          ? accountAPI.registerAdmin(email, password, password2)
          : accountAPI.registerLearner(email, password, password2)

      const response = await apiCall
      const { user: userData, tokens } = response.data

      localStorage.setItem('access_token', tokens.access)
      localStorage.setItem('refresh_token', tokens.refresh)
      localStorage.setItem('user', JSON.stringify(userData))

      setUser(userData)
      setIsAuthenticated(true)

      return { success: true, data: response.data }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data || { message: 'حدث خطأ أثناء التسجيل' },
      }
    }
  }

  const logout = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        await accountAPI.logout(refreshToken)
      }
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      setUser(null)
      setIsAuthenticated(false)
    }
  }

  const updateUser = (userData) => {
    setUser(userData)
    localStorage.setItem('user', JSON.stringify(userData))
  }

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    register,
    logout,
    updateUser,
    isAdmin: user?.user_type === 'مشرف' || user?.user_type === 'admin',
    isLearner: user?.user_type === 'متعلم' || user?.user_type === 'learner',
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

