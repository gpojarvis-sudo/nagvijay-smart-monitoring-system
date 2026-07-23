import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '@/services/api'
import { Target, Plus, TrendingUp } from 'lucide-react'

export default function TargetsPage() {
  const [activeTab, setActiveTab] = useState<'schemes' | 'targets' | 'allocations' | 'achievements'>('targets')

  const { data: schemes } = useQuery({
    queryKey: ['schemes'],
    queryFn: async () => {
      const res = await api.get('/targets/schemes').catch(() => ({ data: { data: [] } }))
      return res.data.data
    }
  })

  const { data: targets } = useQuery({
    queryKey: ['targets'],
    queryFn: async () => {
      const res = await api.get('/targets').catch(() => ({ data: { data: [] } }))
      return res.data.data
    }
  })

  return (
    <div className="space-y-6">
      <div className="flex justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3"><Target className="text-purple-600" /> Target Engine</h1>
          <p className="text-gray-600 mt-1">Scheme master, allocation, achievement tracking with Forms/Sheets sync</p>
        </div>
        <button className="h-fit px-4 py-2.5 bg-purple-600 text-white rounded-xl flex items-center gap-2"><Plus size={18} /> New Target</button>
      </div>

      <div className="bg-white rounded-xl border shadow-sm">
        <div className="border-b px-2 flex gap-2 overflow-x-auto">
          {[
            { id: 'schemes', label: 'Schemes (PLI, RPLI, SSA...)' },
            { id: 'targets', label: 'Division Targets' },
            { id: 'allocations', label: 'Office Allocation' },
            { id: 'achievements', label: 'Achievements' },
          ].map(tab => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id as any)} className={`px-4 py-3 text-sm font-medium border-b-2 whitespace-nowrap ${activeTab === tab.id ? 'border-purple-600 text-purple-700' : 'border-transparent text-gray-500 hover:text-gray-700'}`}>
              {tab.label}
            </button>
          ))}
        </div>

        <div className="p-6">
          {activeTab === 'schemes' && (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {(schemes && schemes.length ? schemes : [
                { scheme_code: 'PLI', scheme_name: 'Postal Life Insurance', scheme_type: 'PLI', financial_year: '2024-25', unit: 'Policies' },
                { scheme_code: 'RPLI', scheme_name: 'Rural PLI', scheme_type: 'RPLI', financial_year: '2024-25', unit: 'Policies' },
                { scheme_code: 'SSA', scheme_name: 'Sukanya Samriddhi', scheme_type: 'SSA', financial_year: '2024-25', unit: 'Accounts' },
                { scheme_code: 'TD', scheme_name: 'Time Deposit', scheme_type: 'TD', financial_year: '2024-25', unit: 'Amount in Lakhs' },
              ]).map((s: any) => (
                <div key={s.scheme_code} className="border rounded-xl p-4 hover:shadow-md">
                  <div className="flex justify-between">
                    <span className="px-2 py-1 bg-purple-50 text-purple-700 rounded-full text-xs font-bold border">{s.scheme_code}</span>
                    <span className="text-xs text-gray-500">{s.financial_year}</span>
                  </div>
                  <h3 className="font-semibold mt-3">{s.scheme_name}</h3>
                  <p className="text-xs text-gray-500 mt-1">Type: {s.scheme_type} • Unit: {s.unit}</p>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'targets' && (
            <div className="space-y-4">
              {(targets && targets.length ? targets : [
                { id: '1', scheme_id: 'PLI', division: 'Nagpur City', total_target: 500, total_achieved: 345, achievement_percentage: 69, financial_year: '2024-25' },
                { id: '2', scheme_id: 'SSA', division: 'Nagpur City', total_target: 300, total_achieved: 210, achievement_percentage: 70, financial_year: '2024-25' },
              ]).map((t: any) => (
                <div key={t.id} className="border rounded-xl p-5 flex items-center justify-between">
                  <div>
                    <p className="font-semibold flex items-center gap-2"><Target size={16} /> {t.scheme_id} • {t.division} • {t.financial_year}</p>
                    <p className="text-sm text-gray-600 mt-1">Target: {t.total_target} | Achieved: {t.total_achieved} | {t.achievement_percentage}%</p>
                    <div className="w-48 h-2 bg-gray-100 rounded-full mt-2"><div className="h-2 bg-purple-600 rounded-full" style={{ width: `${t.achievement_percentage}%` }}></div></div>
                  </div>
                  <button className="px-3 py-1.5 bg-purple-50 text-purple-700 rounded-lg text-xs border">Allocate</button>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'achievements' && (
            <div className="bg-green-50 border border-green-200 rounded-xl p-4">
              <h4 className="font-medium text-green-900 flex items-center gap-2"><TrendingUp size={16} /> Recent Achievements (Google Forms/Sheets Sync)</h4>
              <p className="text-sm text-green-800 mt-2">Real-time sync from field staff via Google Forms. Webhook: /api/v1/integrations/forms/webhook</p>
              <div className="mt-4 space-y-2">
                <div className="bg-white rounded-lg p-3 flex justify-between text-sm"><span>NG-BO-045 • PLI • 2 policies</span><span className="text-green-600">Verified</span></div>
                <div className="bg-white rounded-lg p-3 flex justify-between text-sm"><span>NG-SO-012 • SSA • 1 account</span><span className="text-amber-600">Pending</span></div>
              </div>
            </div>
          )}

          {activeTab === 'allocations' && (
            <div className="text-center py-12 text-gray-500">
              <Target size={48} className="mx-auto text-gray-300 mb-3" />
              <p>Office-wise allocation view</p>
              <p className="text-sm">Allocate division targets to offices and employees</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
