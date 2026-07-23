import { BarChart3 } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import api from '@/services/api'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

export default function AnalyticsPage() {
  const { data } = useQuery({
    queryKey: ['analytics-dashboard'],
    queryFn: async () => {
      const res = await api.get('/analytics/dashboard').catch(() => ({ data: { data: null } }))
      return res.data.data
    }
  })

  const officeWise = data?.office_wise || [
    { label: 'NG-HO-001 Nagpur HO', value: 145, percentage: 95 },
    { label: 'NG-SO-012 Sitabuldi', value: 98, percentage: 89 },
    { label: 'NG-SO-008 Dharampeth', value: 76, percentage: 87 },
    { label: 'NG-BO-045 Itwari', value: 12, percentage: 23 },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold flex items-center gap-3"><BarChart3 className="text-indigo-600" /> Analytics</h1>
      
      <div className="grid lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border p-6">
          <h3 className="font-semibold mb-4">Office-wise Performance</h3>
          <div className="h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={officeWise} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="label" type="category" width={140} tick={{ fontSize: 10 }} />
                <Tooltip />
                <Bar dataKey="value" fill="#4F46E5" radius={[0,6,6,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-white rounded-xl border p-6">
            <h3 className="font-semibold mb-4">Filters</h3>
            <div className="grid grid-cols-2 gap-4">
              <select className="border rounded-lg p-2.5 text-sm"><option>FY 2024-25</option><option>FY 2023-24</option></select>
              <select className="border rounded-lg p-2.5 text-sm"><option>Nagpur City Division</option></select>
              <select className="border rounded-lg p-2.5 text-sm"><option>All Schemes</option><option>PLI</option><option>SSA</option></select>
              <select className="border rounded-lg p-2.5 text-sm"><option>All Office Types</option><option>BO</option><option>SO</option></select>
            </div>
            <button className="mt-4 w-full py-2.5 bg-indigo-600 text-white rounded-xl text-sm font-medium">Apply Filters</button>
          </div>

          <div className="bg-gradient-to-br from-indigo-50 to-purple-50 border border-indigo-200 rounded-xl p-6">
            <h3 className="font-semibold text-indigo-900">AI Insights</h3>
            <p className="text-sm text-indigo-800 mt-2">Low performing BOs in North Nagpur need support. Top 3 offices contributing 45% of total achievement. SSA scheme lagging by 12% - consider incentive.</p>
            <button className="mt-3 px-3 py-1.5 bg-indigo-600 text-white rounded-lg text-xs">Ask AI Assistant</button>
          </div>
        </div>
      </div>
    </div>
  )
}
