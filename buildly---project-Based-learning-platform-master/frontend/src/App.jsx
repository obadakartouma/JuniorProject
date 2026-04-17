import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import PrivateRoute from './components/PrivateRoute'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import LearnerDashboard from './pages/LearnerDashboard'
import AdminDashboard from './pages/AdminDashboard'
import CoursesList from './pages/CoursesList'
import CourseDetail from './pages/CourseDetail'
import CourseCreate from './pages/CourseCreate'
import CourseEdit from './pages/CourseEdit'
import ProjectsList from './pages/ProjectsList'
import ProjectDetail from './pages/ProjectDetail'
import ProjectCreate from './pages/ProjectCreate'
import ProjectEdit from './pages/ProjectEdit'
import Profile from './pages/Profile'
import MyCourses from './pages/MyCourses'
import './App.css'

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="app">
          <Navbar />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              
              <Route
                path="/dashboard"
                element={
                  <PrivateRoute>
                    <LearnerDashboard />
                  </PrivateRoute>
                }
              />
              
              <Route
                path="/admin/dashboard"
                element={
                  <PrivateRoute requireAdmin>
                    <AdminDashboard />
                  </PrivateRoute>
                }
              />
              
              <Route
                path="/courses"
                element={
                  <PrivateRoute>
                    <CoursesList />
                  </PrivateRoute>
                }
              />
              
              <Route
                path="/courses/create"
                element={
                  <PrivateRoute requireAdmin>
                    <CourseCreate />
                  </PrivateRoute>
                }
              />
              
              <Route
                path="/courses/:id"
                element={
                  <PrivateRoute>
                    <CourseDetail />
                  </PrivateRoute>
                }
              />
              
              <Route
                path="/courses/:id/edit"
                element={
                  <PrivateRoute requireAdmin>
                    <CourseEdit />
                  </PrivateRoute>
                }
              />
              
              <Route
                path="/my-courses"
                element={
                  <PrivateRoute>
                    <MyCourses />
                  </PrivateRoute>
                }
              />
              
              <Route
                path="/projects"
                element={
                  <PrivateRoute>
                    <ProjectsList />
                  </PrivateRoute>
                }
              />
              
              <Route
                path="/projects/create"
                element={
                  <PrivateRoute requireAdmin>
                    <ProjectCreate />
                  </PrivateRoute>
                }
              />
              
              <Route
                path="/projects/:id"
                element={
                  <PrivateRoute>
                    <ProjectDetail />
                  </PrivateRoute>
                }
              />
              
              <Route
                path="/projects/:id/edit"
                element={
                  <PrivateRoute requireAdmin>
                    <ProjectEdit />
                  </PrivateRoute>
                }
              />
              
              <Route
                path="/profile"
                element={
                  <PrivateRoute>
                    <Profile />
                  </PrivateRoute>
                }
              />
            </Routes>
          </main>
        </div>
      </Router>
    </AuthProvider>
  )
}

export default App

