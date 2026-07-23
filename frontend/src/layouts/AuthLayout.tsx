import { Outlet, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/services/authStore'

export default function AuthLayout() {
  const { isAuthenticated } = useAuthStore()

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 via-white to-orange-50 flex">
      {/* Left - Branding */}
      <div className="hidden lg:flex lg:w-[55%] bg-gradient-to-br from-red-600 via-red-700 to-orange-600 p-12 text-white flex-col justify-between relative overflow-hidden">
        <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10"></div>
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-12">
            <div className="w-12 h-12 bg-white rounded-xl flex items-center justify-center text-red-600 font-bold text-xl">N</div>
            <div>
              <h1 className="font-bold text-xl">NagVijay NSMS</h1>
              <p className="text-red-100 text-sm">India Post • Enterprise Platform</p>
            </div>
          </div>
          
          <div className="max-w-md">
            <h2 className="text-4xl font-bold leading-tight mb-6">Smart Monitoring for India Post</h2>
            <p className="text-red-100 text-lg leading-relaxed">Unified platform for Nagpur City Division. Track offices, employees, targets, and performance in real-time. Scalable to Region, Circle, and National.</p>
            
            <div className="mt-10 grid grid-cols-2 gap-4">
              <div className="bg-white/10 backdrop-blur rounded-xl p-4 border border-white/20">
                <p className="text-2xl font-bold">150+</p>
                <p className="text-sm text-red-100">Post Offices</p>
              </div>
              <div className="bg-white/10 backdrop-blur rounded-xl p-4 border border-white/20">
                <p className="text-2xl font-bold">AI</p>
                <p className="text-sm text-red-100">Powered Insights</p>
              </div>
            </div>
          </div>
        </div>
        
        <div className="relative z-10">
          <p className="text-sm text-red-200">© 2026 India Post • Nagpur City Division • MVP Phase</p>
          <p className="text-xs text-red-300 mt-1">Built for scale: Region → Maharashtra Circle → National</p>
        </div>
      </div>

      {/* Right - Auth */}
      <div className="flex-1 flex items-center justify-center p-6 lg:p-12 bg-white">
        <div className="w-full max-w-md">
          <div className="lg:hidden flex items-center gap-3 mb-8">
            <div className="w-10 h-10 bg-red-600 rounded-xl flex items-center justify-center text-white font-bold">N</div>
            <div>
              <h1 className="font-bold">NagVijay NSMS</h1>
              <p className="text-xs text-gray-500">India Post</p>
            </div>
          </div>
          
          <Outlet />
        </div>
      </div>
    </div>
  )
}
