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
import ReportsPageV2 from './pages/ReportsPageV2'
import AIChatPage from './pages/AIChatPage'
import SettingsPage from './pages/SettingsPage'
import NotificationsPage from './pages/NotificationsPage'
import NotFoundPage from './pages/NotFoundPage'
import DailyMonitoringPage from './pages/DailyMonitoringPage'
import OfficeDraftPage from './pages/OfficeDraftPage'

import { useAuthStore } from './services/authStore'

function App() {
  const { checkAuth, user } = useAuthStore()

  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  // AUTO_IDLE_TIMEOUT_NSMS
  useEffect(() => {
    if (!user) return

    const timeout =
      user.role === 'SUPER_ADMIN'
        ? 5 * 60 * 1000
        : 10 * 60 * 1000

    let timer: ReturnType<typeof setTimeout>

    const resetTimer = () => {
      clearTimeout(timer)

      timer = setTimeout(() => {
        useAuthStore.getState().logout()
      }, timeout)
    }

    const events = [
      'mousemove',
      'mousedown',
      'keydown',
      'scroll',
      'touchstart',
      'click',
    ]

    events.forEach((event) =>
      window.addEventListener(event, resetTimer)
    )

    resetTimer()

    return () => {
      clearTimeout(timer)

      events.forEach((event) =>
        window.removeEventListener(event, resetTimer)
      )
    }
  }, [user])

  return (
    <Routes>
      {/* Public - Authentication */}
      <Route element={<AuthLayout />}>
        <Route path="/login" element={<LoginPage />} />
      </Route>

      {/* Protected Routes */}
      <Route
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route
          path="/"
          element={<Navigate to="/dashboard" replace />}
        />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute requiredRole="SUPER_ADMIN">
              <DashboardPage />
            </ProtectedRoute>
          }
        />

        <Route path="/offices" element={<OfficeMasterPage />} />
        <Route path="/offices/:id" element={<OfficeMasterPage />} />

        <Route path="/targets" element={<TargetsPage />} />
        <Route path="/targets/:tab" element={<TargetsPage />} />

        <Route path="/analytics" element={<AnalyticsPage />} />

        <Route path="/reports" element={<ReportsPageV2 />} />
        <Route path="/reports-v2" element={<ReportsPageV2 />} />

        <Route
          path="/daily-monitoring"
          element={<DailyMonitoringPage />}
        />

        {/* Office Draft Generator */}
        <Route
          path="/office-drafts"
          element={<OfficeDraftPage />}
        />

        <Route path="/ai-chat" element={<AIChatPage />} />

        <Route
          path="/notifications"
          element={<NotificationsPage />}
        />

        <Route path="/settings" element={<SettingsPage />} />
      </Route>

      {/* 404 */}
      <Route path="/404" element={<NotFoundPage />} />

      <Route
        path="*"
        element={<Navigate to="/404" replace />}
      />
    </Routes>
  )
}

export default App