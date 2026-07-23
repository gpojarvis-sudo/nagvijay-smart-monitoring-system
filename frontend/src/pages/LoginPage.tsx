import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/services/authStore'

declare global {
  interface Window {
    google?: any
  }
}

export default function LoginPage() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { login } = useAuthStore()
  const navigate = useNavigate()

  const handleGoogleLogin = async () => {
    setError(null)
    setLoading(true)
    
    try {
      // Check if Google OAuth is configured
      const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID
      
      if (!clientId) {
        // Demo login for MVP without Google configured
        // Simulate token for demo
        const demoToken = 'demo-token-' + Date.now()
        // Try real login anyway - backend will handle demo if needed
        // For demo, we create mock user via backend if Google not configured
        setError('Google OAuth not configured. Using demo login - contact admin to configure GOOGLE_CLIENT_ID')
        
        // For MVP, allow demo credentials
        // In production, this would be removed
        const demoIdToken = prompt('Enter demo ID token or use Google OAuth. For demo, type any email:')
        if (!demoIdToken) {
          setLoading(false)
          return
        }
        
        // Attempt login with whatever token - backend will try to verify, but for demo we show message
        throw new Error('Google OAuth not configured. Please set VITE_GOOGLE_CLIENT_ID and configure backend GOOGLE_CLIENT_ID')
      }

      // Production Google OAuth flow
      // This is simplified - in real app, use @react-oauth/google or GIS
      window.location.href = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/auth/google/url`
      
    } catch (err: any) {
      setError(err.message || 'Login failed')
      setLoading(false)
    }
  }

  const handleDemoLogin = async () => {
    setLoading(true)
    setError(null)
    try {
      // Demo: direct API call with mock google token - backend should handle demo mode
      // For this MVP frontend, we simulate successful login structure
      // Real implementation would have proper Google GIS integration
      
      // Simulate API delay
      await new Promise(r => setTimeout(r, 1000))
      
      // For demo purposes, if backend is not configured, show instructions
      setError('Demo Mode: To enable full login, configure Google OAuth in .env. Meanwhile, you can explore UI in demo mode.')
      
      // Mock login for UI demonstration - in real deployment, remove this
      // We'll attempt actual backend login with a test endpoint
      try {
        const api = (await import('@/services/api')).default
        // Try to get frontend config to see if backend is reachable
        const cfg = await api.get('/settings/frontend-config')
        console.log('Frontend config:', cfg.data)
        setError(`Backend reachable at ${import.meta.env.VITE_API_URL || 'http://localhost:8000'}. Configure Google OAuth for full login. Config: ${JSON.stringify(cfg.data.data).slice(0,200)}`)
      } catch (e: any) {
        setError(`Backend not reachable at ${import.meta.env.VITE_API_URL || 'http://localhost:8000'}. Ensure backend is running. Error: ${e.message}`)
      }
      
    } finally {
      setLoading(false)
    }
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
          <p className="text-xs text-amber-600 mt-2">For production: Set GOOGLE_CLIENT_ID in frontend .env and backend .env, enable Google OAuth in Google Cloud Console.</p>
        </div>
      )}

      <div className="space-y-4">
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
          Demo Login (Check Configuration)
        </button>

        <div className="bg-gray-50 rounded-xl p-4 border">
          <h3 className="font-semibold text-sm text-gray-900 mb-2">Setup Instructions</h3>
          <ol className="text-xs text-gray-600 space-y-1 list-decimal list-inside">
            <li>Set VITE_API_URL in frontend/.env</li>
            <li>Set GOOGLE_CLIENT_ID in both frontend and backend</li>
            <li>Configure Supabase URL and keys</li>
            <li>Enable Google OAuth in Google Cloud Console</li>
            <li>Backend: /api/v1/auth/google expects ID token from GIS</li>
          </ol>
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
