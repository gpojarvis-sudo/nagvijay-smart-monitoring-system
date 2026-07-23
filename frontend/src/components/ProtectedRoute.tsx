import { Navigate } from 'react-router-dom'
import { useAuthStore } from '@/services/authStore'
import { ReactNode } from 'react'

interface Props {
  children: ReactNode
  requiredRole?: string | string[]
  requiredPermission?: string
}

export default function ProtectedRoute({ children, requiredRole, requiredPermission }: Props) {
  const { isAuthenticated, hasRole, hasPermission, user } = useAuthStore()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (requiredRole && !hasRole(requiredRole)) {
    return <Navigate to="/dashboard" replace />
  }

  if (requiredPermission && !hasPermission(requiredPermission)) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center p-8 bg-white rounded-xl shadow-sm border">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h2>
          <p className="text-gray-600 mb-4">You don't have permission to access this page.</p>
          <p className="text-sm text-gray-500">Required: {requiredPermission}</p>
          <p className="text-sm text-gray-500">Your role: {user?.role}</p>
        </div>
      </div>
    )
  }

  return <>{children}</>
}
