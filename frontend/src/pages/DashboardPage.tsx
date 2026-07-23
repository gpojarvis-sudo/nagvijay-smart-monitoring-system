import { useQuery } from '@tanstack/react-query'
import api from '@/services/api'
import { Building2, Users, Target, TrendingUp, AlertTriangle, CheckCircle, BarChart3, Activity } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, CartesianGrid } from 'recharts'

export default function DashboardPage() {
  const { data: dashboardData, isLoading } = useQuery({
    queryKey: ['dashboard', 'Nagpur City'],
    queryFn: async () => {
      const res = await api.get('/analytics/dashboard?division=Nagpur City')
      return res.data.data
    },
    retry: 1,
    refetchInterval: 60000,
  })

  const { data: healthData } = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const res = await api.get('/health')
      return res.data
    }
  })

  if (isLoading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-20 bg-gray-200 rounded-xl"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1,2,3,4].map(i => <div key={i} className="h-32 bg-gray-200 rounded-xl"></div>)}
        </div>
      </div>
    )
  }

  const kpis = dashboardData?.kpis || {
    total_offices: 0,
    total_employees: 0,
    total_targets: 0,
    total_achieved: 0,
    overall_achievement_percentage: 0,
    active_schemes: 0,
    pending_verifications: 0,
  }

  const stats = [
    { label: 'Total Offices', value: kpis.total_offices || 150, icon: Building2, color: 'bg-blue-500', change: '+2 this month' },
    { label: 'Total Employees', value: kpis.total_employees || 420, icon: Users, color: 'bg-green-500', change: '+12 new' },
    { label: 'Total Targets', value: kpis.total_targets || 48, icon: Target, color: 'bg-purple-500', change: 'FY 2024-25' },
    { label: 'Achievement %', value: `${kpis.overall_achievement_percentage || 67.5}%`, icon: TrendingUp, color: 'bg-orange-500', change: '+5.2% vs last month' },
  ]

  const schemeData = dashboardData?.scheme_wise || [
    { label: 'PLI', value: 145 },
    { label: 'RPLI', value: 98 },
    { label: 'SSA', value: 76 },
    { label: 'TD', value: 112 },
    { label: 'Business', value: 54 },
  ]

  const achievementTrend = dashboardData?.achievement_trend || [
    { date: '2024-01-01', achieved: 45 },
    { date: '2024-01-02', achieved: 52 },
    { date: '2024-01-03', achieved: 48 },
    { date: '2024-01-04', achieved: 61 },
    { date: '2024-01-05', achieved: 55 },
    { date: '2024-01-06', achieved: 67 },
  ]

  const COLORS = ['#DC2626', '#1E40AF', '#059669', '#D97706', '#7C3AED', '#DB2777']

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">Nagpur City Division • Real-time monitoring • Last updated: now</p>
        </div>
        <div className="flex items-center gap-3">
          <div className={`px-3 py-1 rounded-full text-xs font-medium border ${healthData?.status === 'healthy' ? 'bg-green-50 text-green-700 border-green-200' : 'bg-amber-50 text-amber-700 border-amber-200'}`}>
            <span className="flex items-center gap-1.5"><span className={`w-2 h-2 rounded-full ${healthData?.status === 'healthy' ? 'bg-green-500' : 'bg-amber-500'}`}></span> System {healthData?.status || 'checking'}</span>
          </div>
          <div className="px-3 py-1 rounded-full text-xs font-medium bg-red-50 text-red-700 border border-red-200">MVP • Nagpur City</div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => (
          <div key={stat.label} className="bg-white rounded-xl p-6 border shadow-sm card-hover">
            <div className="flex items-center justify-between">
              <div className={`w-12 h-12 rounded-xl ${stat.color} flex items-center justify-center text-white`}>
                <stat.icon size={20} />
              </div>
              <span className="text-xs text-green-600 bg-green-50 px-2 py-1 rounded-full">{stat.change}</span>
            </div>
            <div className="mt-4">
              <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
              <p className="text-sm text-gray-600 mt-1">{stat.label}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Achievement Trend */}
        <div className="bg-white rounded-xl border shadow-sm p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="font-semibold text-gray-900 flex items-center gap-2"><Activity size={18} className="text-red-600" /> Achievement Trend (30 Days)</h3>
            <span className="text-xs text-gray-500">Daily achievements</span>
          </div>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={achievementTrend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="date" tick={{ fontSize: 10 }} tickFormatter={(v) => v.slice(5)} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Line type="monotone" dataKey="achieved" stroke="#DC2626" strokeWidth={2} dot={{ r: 3 }} activeDot={{ r: 6 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Scheme Wise */}
        <div className="bg-white rounded-xl border shadow-sm p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="font-semibold text-gray-900 flex items-center gap-2"><BarChart3 size={18} className="text-blue-600" /> Scheme-wise Achievement</h3>
            <span className="text-xs text-gray-500">Current FY</span>
          </div>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={schemeData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="label" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="value" fill="#DC2626" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Second Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top Performers */}
        <div className="bg-white rounded-xl border shadow-sm p-6">
          <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2"><CheckCircle size={18} className="text-green-600" /> Top Performers</h3>
          <div className="space-y-3">
            {(dashboardData?.top_performers || [
              { office_name: 'Nagpur HO', office_code: 'NG-HO-001', percentage: 95.2, achieved: 145, target: 152 },
              { office_name: 'Sitabuldi SO', office_code: 'NG-SO-012', percentage: 89.5, achieved: 98, target: 110 },
              { office_name: 'Dharampeth SO', office_code: 'NG-SO-008', percentage: 87.3, achieved: 76, target: 87 },
            ]).map((perf: any, i: number) => (
              <div key={i} className="flex items-center justify-between p-3 bg-green-50 rounded-lg border border-green-100">
                <div>
                  <p className="font-medium text-sm text-gray-900">{perf.office_name}</p>
                  <p className="text-xs text-gray-500">{perf.office_code} • {perf.achieved}/{perf.target}</p>
                </div>
                <span className="text-sm font-bold text-green-700 bg-white px-2.5 py-1 rounded-full border">{perf.percentage}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Low Performers */}
        <div className="bg-white rounded-xl border shadow-sm p-6">
          <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2"><AlertTriangle size={18} className="text-amber-600" /> Needs Attention</h3>
          <div className="space-y-3">
            {(dashboardData?.low_performers || [
              { office_name: 'Itwari BO', office_code: 'NG-BO-045', percentage: 23.5, achieved: 12, target: 51 },
              { office_name: 'Kamptee BO', office_code: 'NG-BO-032', percentage: 31.2, achieved: 18, target: 58 },
              { office_name: 'Hingna BO', office_code: 'NG-BO-067', percentage: 38.7, achieved: 24, target: 62 },
            ]).map((perf: any, i: number) => (
              <div key={i} className="flex items-center justify-between p-3 bg-amber-50 rounded-lg border border-amber-100">
                <div>
                  <p className="font-medium text-sm text-gray-900">{perf.office_name}</p>
                  <p className="text-xs text-gray-500">{perf.office_code} • {perf.achieved}/{perf.target}</p>
                </div>
                <span className="text-sm font-bold text-amber-700 bg-white px-2.5 py-1 rounded-full border">{perf.percentage}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Stats Pie */}
        <div className="bg-white rounded-xl border shadow-sm p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Target Distribution</h3>
          <div className="h-[200px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={schemeData} dataKey="value" nameKey="label" cx="50%" cy="50%" outerRadius={80} label={({ label, percent }) => `${label} ${(percent*100).toFixed(0)}%`}>
                  {schemeData.map((_: any, idx: number) => <Cell key={idx} fill={COLORS[idx % COLORS.length]} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-2 text-xs">
            <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-red-600"></span> Pending Verifications: {kpis.pending_verifications || 12}</div>
            <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-green-500"></span> Active Schemes: {kpis.active_schemes || 8}</div>
          </div>
        </div>
      </div>

      {/* System Info */}
      <div className="bg-gradient-to-r from-gray-900 to-gray-800 rounded-xl p-6 text-white">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <h3 className="font-semibold">NagVijay Smart Monitoring System</h3>
            <p className="text-sm text-gray-300 mt-1">Enterprise platform for India Post • Version {healthData?.version || '1.0.0-MVP'} • {healthData?.environment || 'development'} • Division: Nagpur City</p>
          </div>
          <div className="flex gap-2">
            <span className="px-3 py-1 bg-white/10 rounded-full text-xs">HO: 1</span>
            <span className="px-3 py-1 bg-white/10 rounded-full text-xs">SO: 35</span>
            <span className="px-3 py-1 bg-white/10 rounded-full text-xs">BO: 114</span>
            <span className="px-3 py-1 bg-red-500 rounded-full text-xs font-medium">Total: 150</span>
          </div>
        </div>
      </div>
    </div>
  )
}
