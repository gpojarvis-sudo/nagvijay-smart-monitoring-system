import { Bell } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import api from '@/services/api'

export default function NotificationsPage() {
  const { data } = useQuery({
    queryKey: ['notifications'],
    queryFn: async () => {
      const res = await api.get('/notifications').catch(() => ({ data: { data: [] } }))
      return res.data.data
    }
  })

  const notifs = data || [
    { id: '1', title: 'Target Achieved', message: 'Nagpur HO achieved 100% PLI target', type: 'SUCCESS', is_read: false, created_at: new Date().toISOString() },
    { id: '2', title: 'Pending Verification', message: '12 achievements pending verification from yesterday', type: 'WARNING', is_read: false, created_at: new Date().toISOString() },
    { id: '3', title: 'Weekly Report', message: 'Weekly DPR generated for Nagpur City Division', type: 'INFO', is_read: true, created_at: new Date().toISOString() },
  ]

  return (
    <div className="space-y-6 max-w-3xl">
      <h1 className="text-3xl font-bold flex items-center gap-3"><Bell className="text-red-600" /> Notifications</h1>
      
      <div className="bg-white border rounded-xl">
        {notifs.map((n: any) => (
          <div key={n.id} className={`p-5 border-b last:border-0 flex gap-4 ${!n.is_read ? 'bg-red-50/50' : ''}`}>
            <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${n.type === 'SUCCESS' ? 'bg-green-500' : n.type === 'WARNING' ? 'bg-amber-500' : 'bg-blue-500'}`}></div>
            <div className="flex-1">
              <div className="flex justify-between">
                <h3 className="font-medium text-sm">{n.title}</h3>
                <span className="text-xs text-gray-500">{new Date(n.created_at).toLocaleString()}</span>
              </div>
              <p className="text-sm text-gray-600 mt-1">{n.message}</p>
              <span className="inline-flex mt-2 px-2 py-0.5 rounded-full text-[10px] border bg-white">{n.type}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
