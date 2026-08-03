import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/services/authStore'

export default function LoginPage() {
  const navigate = useNavigate()
  const { loginWithPassword } = useAuthStore()

  const [username, setEmployeeId] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    setLoading(true)
    setError('')

    try {
      const user = await loginWithPassword(username.trim().toUpperCase(), password)

      if (user.role === 'OFFICE_ADMIN') {
        navigate('/daily-monitoring', { replace: true })
      } else {
        navigate('/dashboard', { replace: true })
      }
    } catch (err: any) {
      setError(
        err?.response?.data?.error?.message ||
        err?.message ||
        'Invalid Username or Password'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">

      <div className="w-full max-w-md bg-white rounded-xl shadow-xl p-8">

        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-red-700">
            NagVijay NSMS
          </h1>

          <p className="text-gray-500 mt-2">
            India Post • Nagpur City Division
          </p>
        </div>

        {error && (
          <div className="mb-4 rounded-lg bg-red-100 border border-red-300 p-3 text-red-700 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">

          <div>
            <label className="block mb-2 font-medium">
              Username
            </label>

            <input
              className="w-full border rounded-lg p-3"
              type="text"
              value={username}
              onChange={(e)=>setEmployeeId(e.target.value.toUpperCase())}
              required
            />
          </div>

          <div>
            <label className="block mb-2 font-medium">
              Password
            </label>

            <input
              className="w-full border rounded-lg p-3"
              type="password"
              value={password}
              onChange={(e)=>setPassword(e.target.value)}
              required
            />
          </div>

          <button
            disabled={loading}
            className="w-full bg-red-600 hover:bg-red-700 text-white rounded-lg py-3 font-semibold"
          >
            {loading ? 'Signing In...' : 'Login'}
          </button>

        </form>

        <div className="mt-8 text-center text-xs text-gray-500">
          Smart Monitoring System<br />
          Nagpur City Division
        </div>

      </div>

    </div>
  )
}

