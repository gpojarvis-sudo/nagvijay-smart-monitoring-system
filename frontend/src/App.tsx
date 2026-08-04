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
import DailyMonitoringPage from "./pages/DailyMonitoringPage"

import { useAuthStore } from './services/authStore'

function App() {
  const { checkAuth, user } = useAuthStore()

  useEffect(() => {
    checkAuth()
  }, [checkAuth])


  // AUTO_IDLE_TIMEOUT_NSMS
  useEffect(() => {
    if (!user) return;

    const timeout =
      user.role === "SUPER_ADMIN"
        ? 5 * 60 * 1000
        : 10 * 60 * 1000;

    let timer:any;

    const resetTimer = () => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        useAuthStore.getState().logout();
      }, timeout);
    };

    [
      "mousemove",
      "mousedown",
      "keydown",
      "scroll",
      "touchstart",
      "click"
    ].forEach(e=>window.addEventListener(e,resetTimer));

    resetTimer();

    return ()=>{
      clearTimeout(timer);
      [
        "mousemove",
        "mousedown",
        "keydown",
        "scroll",
        "touchstart",
        "click"
      ].forEach(e=>window.removeEventListener(e,resetTimer));
    };

  },[user])


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
        <Route path="/daily-monitoring" element={<DailyMonitoringPage />} />
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
