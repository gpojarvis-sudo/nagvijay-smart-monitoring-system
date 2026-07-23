import { Routes, Route, Navigate } from 'react-router-dom'
import { useEffect } from 'react'
import MainLayout from './layouts/MainLayout'
import AuthLayout from './layouts/AuthLayout'
import ProtectedRoute from './components/ProtectedRoute'

import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import OfficeMasterPage from './pages/OfficeMasterPage'
import EmployeeMasterPage from './pages/EmployeeMasterPage'
import TargetsPage from './pages/TargetsPage'
import AnalyticsPage from './pages/AnalyticsPage'
import ReportsPage from './pages/ReportsPage'
import AIChatPage from './pages/AIChatPage'
import SettingsPage from './pages/SettingsPage'
import NotificationsPage from './pages/NotificationsPage'
import NotFoundPage from './pages/NotFoundPage'

import { useAuthStore } from './services/authStore'

function App() {
  const { checkAuth } = useAuthStore()

  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  return (
    <Routes>
      {/* Public - Auth */}
      <Route element={<AuthLayout />}>
        <Route path="/login" element={<LoginPage />} />
      </Route>

      {/* Protected */}
      <Route element={
        <ProtectedRoute>
          <MainLayout />
        </ProtectedRoute>
      }>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/offices" element={<OfficeMasterPage />} />
        <Route path="/offices/:id" element={<OfficeMasterPage />} />
        <Route path="/employees" element={<EmployeeMasterPage />} />
        <Route path="/targets" element={<TargetsPage />} />
        <Route path="/targets/:tab" element={<TargetsPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/ai-chat" element={<AIChatPage />} />
        <Route path="/notifications" element={<NotificationsPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>

      {/* 404 */}
      <Route path="/404" element={<NotFoundPage />} />
      <Route path="*" element={<Navigate to="/404" replace />} />
    </Routes>
  )
}

export default App
