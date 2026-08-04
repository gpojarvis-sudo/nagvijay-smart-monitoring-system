import { todayIST, timeIST } from "@/utils/date"
import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '@/services/api'
import { Building2, Users, Target, TrendingUp, AlertTriangle, CheckCircle, BarChart3, Activity, Calendar, DollarSign, FileText } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, CartesianGrid } from 'recharts'
import { dashboardService } from '@/services/dashboardService'


const downloadExcel = async (date: string) => {
  try {
    const token = sessionStorage.getItem('access_token');
    const res = await fetch(`/api/v1/daily-reports/export?report_date=${date}&format=excel`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!res.ok) throw new Error('Download failed');
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `daily_report_${date}.xlsx`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  } catch (err) {
    alert('Failed to download Excel: ' + (err as any).message);
  }
};

export default function DashboardPage() {
  const today = todayIST()
  const [selectedDate, setSelectedDate] = useState(today)
  const [lastUpdated, setLastUpdated] = useState(timeIST())

  useEffect(() => {
    const timer = setInterval(() => {
      setLastUpdated(timeIST())

      const d = todayIST()
      setSelectedDate(prev => prev === d ? prev : d)
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  // Analytics dashboard
  const { data: dashboardData, isLoading: analyticsLoading } = useQuery({
    queryKey: ['dashboard', 'Nagpur City'],
    queryFn: async () => {
      const res = await api.get('/analytics/dashboard?division=Nagpur City')
      return res.data.data
    },
    retry: 1,
    refetchInterval: 60000,
  })

  // Daily summary for selected date
  const { data: dailySummary, isLoading: dailyLoading } = useQuery({
    queryKey: ['dailySummary', selectedDate],
    queryFn: async () => {
      const res = await api.get('/daily-reports/summary', { params: { report_date: selectedDate } })
      return res.data
    },
    retry: 1,
    refetchInterval: 60000,
  })

  // Non-reporting offices
  const { data: nonReporting, isLoading: nonReportingLoading } = useQuery({
    queryKey: ['nonReporting', selectedDate],
    queryFn: async () => {
      const res = await api.get('/daily-reports/non-reporting', { params: { report_date: selectedDate } })
      return res.data
    },
    retry: 1,
    refetchInterval: 60000,
  })


  // Daily reports
  const { data: reports } = useQuery({
    queryKey: ["dailyReports", selectedDate],
    queryFn: async () => {
      const res = await api.get("/daily-reports/", {
        params: { report_date: selectedDate }
      })
      return res.data
    },
    retry: 1,
    refetchInterval: 60000,
  })

  // Duplicate errors (Feature 1)
  const { data: syncErrors, isLoading: syncErrorsLoading } = useQuery({
    queryKey: ['syncErrors'],
    queryFn: async () => {
      const res = await api.get('/sync-errors/recent?limit=5&error_type=WEBHOOK')
      return res.data
    },
    retry: 1,
    refetchInterval: 60000,
  })

  const { data: officeStats } = useQuery({
    queryKey: ['officeStats'],
    queryFn: async () => {
      const res = await api.get('/offices/stats');
      return res.data;
    },
    retry: 1,
    refetchInterval: 60000,
  });

  const { data: healthData } = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const res = await api.get('/health')
      return res.data
    }
  })

  const isLoading = analyticsLoading || dailyLoading || nonReportingLoading || syncErrorsLoading

  const kpis = dashboardData?.kpis || {
    total_offices: 0,
    total_employees: 0,
    total_targets: 0,
    total_achieved: 0,
    overall_achievement_percentage: 0,
    active_schemes: 0,
    pending_verifications: 0,
  }

  const daily = dailySummary || {
    total_offices: 0,
    total_sb_opened: 0,
    total_sb_closed: 0,
    total_net_accounts: 0,
    total_pli_policies: 0,
    total_sum_assured: 0,
    total_premium: 0,
    total_revenue: 0,
    report_date: selectedDate,
  }

  const reportingCount = reports?.length || 0;
  const nonReportingCount = nonReporting?.non_reporting_offices?.length || 0;
  const totalOffices = officeStats?.total || 66;

  const reportingPercentage =
    totalOffices > 0
      ? ((reportingCount / totalOffices) * 100).toFixed(1)
      : "0";

  const pendingPercentage =
    totalOffices > 0
      ? ((nonReportingCount / totalOffices) * 100).toFixed(1)
      : "0";



  const stats = [
    {
      label: 'Total Offices',
      value: totalOffices,
      icon: Building2,
      color: 'bg-blue-500',
      change: 'Nagpur City Division'
    },
    {
      label: 'Reporting Offices',
      value: reportingCount,
      icon: Users,
      color: 'bg-green-500',
      change: `${reportingPercentage}% Submitted`
    },
    {
      label: 'Daily SB Opened',
      value: daily.total_sb_opened || 0,
      icon: FileText,
      color: 'bg-purple-500',
      change: `Closed: ${daily.total_sb_closed || 0}`
    },
    {
      label: 'Pending Offices',
      value: nonReportingCount,
      icon: AlertTriangle,
      color: 'bg-orange-500',
      change: `${pendingPercentage}% Pending`
    },
  ]

  const schemeData = dashboardData?.scheme_wise || []

  const achievementTrend = dashboardData?.achievement_trend || []

  const COLORS = ['#DC2626', '#1E40AF', '#059669', '#D97706', '#7C3AED', '#DB2777']

  const topReportingOffices = (reports || []).slice(0,5);
  const pendingOffices = nonReporting?.non_reporting_offices || [];


  return (
    <div className="space-y-6">
      {/* Header with Date Picker */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">Nagpur City Division • Real-time monitoring • Last updated: {lastUpdated}</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 bg-white px-4 py-2 rounded-xl border shadow-sm">
            <Calendar size={18} className="text-gray-500" />
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="border-0 focus:ring-0 text-sm font-medium text-gray-700 bg-transparent"
            />
          </div>
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


      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        <div className="bg-white rounded-xl border shadow-sm p-6">
          <h3 className="text-lg font-semibold mb-4">
            Top Reporting Offices
          </h3>

          {topReportingOffices.length === 0 ? (
            <p className="text-gray-500">No reports submitted.</p>
          ) : (
            <div className="space-y-3">
              {topReportingOffices.map((o:any)=>(
                <div key={o.office_id} className="flex justify-between border-b pb-2">
                  <span>{o.office_name}</span>
                  <span className="font-semibold text-green-700">
                    Submitted
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-white rounded-xl border shadow-sm p-6">
          <h3 className="text-lg font-semibold mb-4">
            Non Reporting Offices
          </h3>

          {pendingOffices.length === 0 ? (
            <p className="text-green-600">
              All offices have reported.
            </p>
          ) : (
            <div className="space-y-3 max-h-72 overflow-auto">
              {pendingOffices.slice(0,10).map((o:any)=>(
                <div key={o.office_id} className="flex justify-between border-b pb-2">
                  <span>{o.office_name}</span>
                  <span className="text-red-600 font-medium">
                    Pending
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>

      {/* Charts Row */}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
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

      {/* Daily Office Report Summary */}
      <div className="bg-white rounded-xl border shadow-sm p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="font-semibold text-gray-900 flex items-center gap-2"><Calendar size={18} className="text-indigo-600" /> Daily Office Report Summary</h3>
          <span className="text-xs text-gray-500">{daily.report_date || selectedDate}</span>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-4 bg-blue-50 rounded-lg">
            <p className="text-xs text-blue-600 font-medium">SB Opened</p>
            <p className="text-2xl font-bold text-blue-800">{daily.total_sb_opened || 0}</p>
          </div>
          <div className="p-4 bg-red-50 rounded-lg">
            <p className="text-xs text-red-600 font-medium">SB Closed</p>
            <p className="text-2xl font-bold text-red-800">{daily.total_sb_closed || 0}</p>
          </div>
          <div className="p-4 bg-green-50 rounded-lg">
            <p className="text-xs text-green-600 font-medium">Net Accounts</p>
            <p className="text-2xl font-bold text-green-800">{daily.total_net_accounts || 0}</p>
          </div>
          <div className="p-4 bg-purple-50 rounded-lg">
            <p className="text-xs text-purple-600 font-medium">PLI Policies</p>
            <p className="text-2xl font-bold text-purple-800">{daily.total_pli_policies || 0}</p>
          </div>
          <div className="p-4 bg-amber-50 rounded-lg">
            <p className="text-xs text-amber-600 font-medium">Total Premium (₹)</p>
            <p className="text-2xl font-bold text-amber-800">₹{(daily.total_premium || 0).toLocaleString()}</p>
          </div>
          <div className="p-4 bg-indigo-50 rounded-lg">
            <p className="text-xs text-indigo-600 font-medium">Sum Assured (₹)</p>
            <p className="text-2xl font-bold text-indigo-800">₹{(daily.total_sum_assured || 0).toLocaleString()}</p>
          </div>
          <div className="p-4 bg-teal-50 rounded-lg">
            <p className="text-xs text-teal-600 font-medium">Aadhaar Transactions</p>
            <p className="text-2xl font-bold text-teal-800">{daily.aadhaar_transactions || 0}</p>
          </div>
          <div className="p-4 bg-rose-50 rounded-lg">
            <p className="text-xs text-rose-600 font-medium">Total Revenue (₹)</p>
            <p className="text-2xl font-bold text-rose-800">₹{(daily.total_revenue || 0).toLocaleString()}</p>
          </div>
        </div>
      </div>

      {/* Non-Reporting Offices */}
      <div className="bg-white rounded-xl border shadow-sm p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="font-semibold text-gray-900 flex items-center gap-2"><AlertTriangle size={18} className="text-amber-600" /> Non-Reporting Offices</h3>
          <span className="text-xs text-gray-500">{nonReporting?.report_date || selectedDate}</span>
        </div>
        <div className="space-y-3 max-h-64 overflow-y-auto">
          {nonReporting?.non_reporting_offices?.length > 0 ? (
            nonReporting.non_reporting_offices.slice(0, 10).map((office: any, i: number) => (
              <div key={i} className="flex items-center justify-between p-3 bg-red-50 rounded-lg border border-red-100">
                <div>
                  <p className="font-medium text-sm text-gray-900">{office.office_name}</p>
                  <p className="text-xs text-gray-500">{office.office_code} • {office.office_type}</p>
                </div>
                <span className="text-xs font-medium text-red-600 bg-white px-2.5 py-1 rounded-full border">No Report</span>
              </div>
            ))
          ) : (
            <div className="text-center py-8 text-green-600">
              <CheckCircle size={40} className="mx-auto mb-2" />
              <p className="font-medium">All offices have reported!</p>
              <p className="text-sm text-gray-500">Complete data for {nonReporting?.report_date || selectedDate}</p>
            </div>
          )}
          {nonReporting?.non_reporting_offices?.length > 10 && (
            <p className="text-xs text-gray-500 text-center">+ {nonReporting.non_reporting_offices.length - 10} more</p>
          )}
        </div>
      </div>

      {/* 🔹 Duplicate Alerts Card (Feature 1) */}
      <div className="bg-white rounded-xl border shadow-sm p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="font-semibold text-gray-900 flex items-center gap-2"><AlertTriangle size={18} className="text-orange-600" /> Duplicate Submission Alerts</h3>
          <span className="text-xs text-gray-500">Recent duplicates</span>
        </div>
        <div className="space-y-3 max-h-64 overflow-y-auto">
          {syncErrors?.length > 0 ? (
            syncErrors.slice(0, 5).map((err: any, i: number) => (
              <div key={i} className="flex items-center justify-between p-3 bg-orange-50 rounded-lg border border-orange-100">
                <div>
                  <p className="font-medium text-sm text-gray-900">{err.office_name || err.office_code}</p>
                  <p className="text-xs text-gray-500">Date: {err.error_date} • {err.error_type}</p>
                </div>
                <span className="text-xs font-medium text-orange-700 bg-white px-2.5 py-1 rounded-full border">{err.error_message.slice(0, 30)}...</span>
              </div>
            ))
          ) : (
            <div className="text-center py-8 text-green-600">
              <CheckCircle size={40} className="mx-auto mb-2" />
              <p className="font-medium">No duplicate alerts</p>
              <p className="text-sm text-gray-500">All submissions are unique</p>
            </div>
          )}
        </div>
      </div>

      {/* Second Row - Top and Low Performers */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl border shadow-sm p-6">
          <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2"><CheckCircle size={18} className="text-green-600" /> Top Performers</h3>
          <div className="space-y-3">
            {(dashboardData?.top_performers || []).map((perf: any, i: number) => (
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

        <div className="bg-white rounded-xl border shadow-sm p-6">
          <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2"><AlertTriangle size={18} className="text-amber-600" /> Needs Attention</h3>
          <div className="space-y-3">
            {(dashboardData?.low_performers || []).map((perf: any, i: number) => (
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
            <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-red-600"></span> Pending Verifications: {kpis.pending_verifications || 0}</div>
            <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-green-500"></span> Active Schemes: {kpis.active_schemes || 0}</div>
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
            <span className="px-3 py-1 bg-white/10 rounded-full text-xs">HO: {officeStats?.head_office || 0}</span>
            <span className="px-3 py-1 bg-white/10 rounded-full text-xs">SO: {(officeStats?.sub_office || 0) + (officeStats?.other || 0)}</span>
            <span className="px-3 py-1 bg-white/10 rounded-full text-xs">BO: {officeStats?.branch_office || 0}</span>
            <span className="px-3 py-1 bg-red-500 rounded-full text-xs font-medium">Total: {officeStats?.total || 0}</span>
          </div>
        </div>
      </div>
    </div>
  )
}
