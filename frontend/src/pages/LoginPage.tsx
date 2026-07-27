import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/services/authStore'
import api from '@/services/api'

declare global {
  interface Window {
    google?: any
  }
}

export default function LoginPage() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [employeeId, setEmployeeId] = useState('')
  const [password, setPassword] = useState('')
  const { loginWithPassword } = useAuthStore()
  const navigate = useNavigate()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      await loginWithPassword(employeeId, password)
      navigate('/')
    } catch (err: any) {
      setError(err?.response?.data?.message || err?.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleLogin = async () => {
    setError(null)
    setLoading(true)
    try {
      const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID
      if (!clientId) {
        setError('Google OAuth not configured. Please use Employee ID login.')
        setLoading(false)
        return
      }
      const res = await api.get('/auth/google/url')
      window.location.href = res.data.data.auth_url
    } catch (err: any) {
      setError(err.message || 'Google login failed')
      setLoading(false)
    }
  }

  const handleDemoLogin = async () => {
    setEmployeeId('12345678')
    setPassword('Admin@123')
    // Auto-submit the form after setting fields
    setTimeout(() => {
      document.getElementById('login-form')?.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }))
    }, 100)
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Welcome back</h1>
        <p className="mt-2 text-gray-600">Sign in to NagVijay Smart Monitoring System</p>
        <p className="text-sm text-gray-500 mt-1">Nagpur City Division • India Post</p>
      </div>

      {error && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
          <p className="text-sm text-amber-800">{error}</p>
        </div>
      )}

      <div className="space-y-4">
        <form id="login-form" onSubmit={handleLogin} className="space-y-3">
          <input
            type="text"
            placeholder="Employee ID"
            value={employeeId}
            onChange={(e) => setEmployeeId(e.target.value)}
            className="w-full rounded-xl border border-gray-300 px-4 py-3"
            required
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-xl border border-gray-300 px-4 py-3"
            required
          />

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-xl bg-red-600 px-4 py-3 text-white font-medium"
          >
            {loading ? 'Signing in...' : 'Sign in'}
          </button>
        </form>

        <button
          onClick={handleGoogleLogin}
          disabled={loading}
          className="w-full flex items-center justify-center gap-3 px-4 py-3.5 bg-white border border-gray-300 rounded-xl shadow-sm hover:bg-gray-50 hover:border-gray-400 transition-all disabled:opacity-50 font-medium text-gray-700"
        >
          <img src="https://www.svgrepo.com/show/475656/google-color.svg" alt="Google" className="w-5 h-5" />
          {loading ? 'Signing in...' : 'Continue with Google'}
        </button>

        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-200"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-3 bg-white text-gray-500">Or</span>
          </div>
        </div>

        <button
          onClick={handleDemoLogin}
          disabled={loading}
          className="w-full px-4 py-3.5 bg-gradient-to-r from-red-600 to-red-700 text-white rounded-xl shadow-sm hover:from-red-700 hover:to-red-800 transition-all disabled:opacity-50 font-medium"
        >
          Demo Login (Employee ID: 12345678 / Password: Admin@123)
        </button>

        <div className="bg-gray-50 rounded-xl p-4 border">
          <h3 className="font-semibold text-sm text-gray-900 mb-2">Login Instructions</h3>
          <ul className="text-xs text-gray-600 space-y-1 list-disc list-inside">
            <li>Use Employee ID: <strong>12345678</strong> and Password: <strong>Admin@123</strong></li>
            <li>Or click "Demo Login" to auto-fill</li>
            <li>If you see "Request failed with status code 404", ensure backend is running on port 8000</li>
          </ul>
        </div>

        <div className="text-center">
          <p className="text-xs text-gray-500">
            By signing in, you agree to India Post IT policies.<br />
            Role-based access: Super Admin • Division Admin • Office Admin • Employee • Auditor
          </p>
        </div>
      </div>

      <div className="border-t pt-6">
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>MVP Phase 1</span>
          <span>Future: Region → Circle → National</span>
        </div>
      </div>
    </div>
  )
}
