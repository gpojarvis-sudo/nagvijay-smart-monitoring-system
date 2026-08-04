import { useState } from 'react'
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Building2, 
  Target, 
  BarChart3, 
  FileText, 
  Bot, 
  Settings, 
  Bell,
  LogOut,
  Menu,
  X,
  Mail
} from 'lucide-react'
import { useAuthStore } from '@/services/authStore'

type NavigationItem = {
  name: string
  href: string
  icon: any
  badge?: string
}


const adminNavigation: NavigationItem[] = [
    { name: 'Daily Monitoring', href: '/daily-monitoring', icon: FileText },
  { name: 'Offices', href: '/offices', icon: Building2 },
  { name: 'Targets', href: '/targets', icon: Target },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Reports', href: '/reports', icon: FileText },
  { name: 'AI Assistant', href: '/ai-chat', icon: Bot, badge: 'AI' },
  { name: 'Notifications', href: '/notifications', icon: Bell },
  { name: 'Settings', href: '/settings', icon: Settings },
]

const officeNavigation: NavigationItem[] = [
  { name: 'Daily Monitoring', href: '/daily-monitoring', icon: FileText },
  { name: 'My Reports', href: '/reports', icon: FileText },
  { name: 'Notifications', href: '/notifications', icon: Bell },
]


export default function MainLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { user, logout } = useAuthStore()

  const navigation = user?.role === 'OFFICE_ADMIN' ? officeNavigation : adminNavigation
  const location = useLocation()
  const navigate = useNavigate()

  const isActive = (path: string) => location.pathname.startsWith(path)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 bg-black/30 lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 w-72 bg-white border-r border-gray-200 transform transition-transform duration-200 ease-in-out lg:translate-x-0 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:fixed`}>
        <div className="flex h-full flex-col">
          {/* Logo */}
          <div className="flex h-16 items-center gap-3 px-6 border-b border-gray-200 bg-gradient-to-r from-red-600 to-red-700 text-white">
            <div className="w-9 h-9 bg-white rounded-lg flex items-center justify-center text-red-600 font-bold text-lg">N</div>
            <div>
              <h1 className="font-bold text-[15px] leading-none">NagVijay NSMS</h1>
              <p className="text-[11px] opacity-90 mt-0.5">India Post • Nagpur</p>
            </div>
            <button className="ml-auto lg:hidden p-1" onClick={() => setSidebarOpen(false)}>
              <X size={20} />
            </button>
          </div>

          {/* User */}
          <div className="p-4 border-b border-gray-100">
            <div className="flex items-center gap-3">
              <img src={user?.avatar_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(user?.full_name || 'User')}&background=DC2626&color=fff`} alt="avatar" className="w-10 h-10 rounded-full" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-gray-900 truncate">{user?.full_name}</p>
                <p className="text-xs text-gray-500 truncate flex items-center gap-1">
                  <Mail size={10} /> {user?.email}
                </p>
                <span className="inline-flex mt-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-red-50 text-red-700 border border-red-200">{user?.role}</span>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto p-4 space-y-1">
            {navigation.map((item) => {
              const active = isActive(item.href)
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                    active ? 'bg-red-50 text-red-700 border border-red-200' : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <item.icon size={18} className={active ? 'text-red-600' : 'text-gray-400'} />
                  {item.name}
                  {item.badge && <span className="ml-auto px-2 py-0.5 text-[10px] font-bold bg-gradient-to-r from-violet-600 to-indigo-600 text-white rounded-full">{item.badge}</span>}
                </Link>
              )
            })}
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-gray-200">
            <button
              onClick={logout}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
            >
              <LogOut size={18} className="text-gray-400" />
              Sign Out
            </button>
            <div className="mt-4 px-3">
              <p className="text-[10px] text-gray-400">MVP v1.0.0 • Nagpur City Division</p>
              <p className="text-[10px] text-gray-400">Scalable to National • India Post</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-72">
        {/* Topbar */}
        <div className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b border-gray-200 bg-white/80 backdrop-blur-xl px-4 lg:px-8">
          <button className="lg:hidden p-2 rounded-lg hover:bg-gray-100" onClick={() => setSidebarOpen(true)}>
            <Menu size={20} />
          </button>
          
          <div className="flex-1">
            <h2 className="text-sm font-medium text-gray-500">
              Enterprise Monitoring Platform • <span className="text-red-600 font-semibold">Nagpur City Division</span>
            </h2>
          </div>

          <div className="flex items-center gap-2">
            <button onClick={() => navigate('/notifications')} className="p-2.5 rounded-lg hover:bg-gray-100 relative">
              <Bell size={18} />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-600 rounded-full"></span>
            </button>
            <button onClick={() => navigate('/settings')} className="p-2.5 rounded-lg hover:bg-gray-100">
              <Settings size={18} />
            </button>
          </div>
        </div>

        {/* Page content */}
        <main className="p-4 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
