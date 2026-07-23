import { Settings, Shield, Database, Bot, Link2 } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import api from '@/services/api'

export default function SettingsPage() {
  const { data } = useQuery({
    queryKey: ['settings'],
    queryFn: async () => {
      const res = await api.get('/settings').catch(() => ({ data: { data: {} } }))
      return res.data.data
    }
  })

  const { data: frontendConfig } = useQuery({
    queryKey: ['frontend-config'],
    queryFn: async () => {
      const res = await api.get('/settings/frontend-config').catch(() => ({ data: { data: {} } }))
      return res.data.data
    }
  })

  const { data: integrations } = useQuery({
    queryKey: ['integrations-status'],
    queryFn: async () => {
      const res = await api.get('/integrations/status').catch(() => ({ data: { data: {} } }))
      return res.data.data
    }
  })

  return (
    <div className="space-y-6 max-w-5xl">
      <h1 className="text-3xl font-bold flex items-center gap-3"><Settings className="text-gray-700" /> Settings</h1>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white border rounded-xl p-6">
          <h3 className="font-semibold flex items-center gap-2"><Shield size={18} /> System Info</h3>
          <div className="mt-4 space-y-2 text-sm">
            <div className="flex justify-between"><span className="text-gray-500">App Name</span><span className="font-medium">{data?.app?.name || 'NagVijay NSMS'}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">Version</span><span className="font-medium">{data?.app?.version || '1.0.0-MVP'}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">Environment</span><span className="font-medium">{data?.app?.environment || 'development'}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">Division</span><span className="font-medium">{data?.app?.division || 'Nagpur City'}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">Region</span><span className="font-medium">{data?.app?.region || 'Nagpur'}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">Circle</span><span className="font-medium">{data?.app?.circle || 'Maharashtra'}</span></div>
          </div>
        </div>

        <div className="bg-white border rounded-xl p-6">
          <h3 className="font-semibold flex items-center gap-2"><Database size={18} /> Features</h3>
          <div className="mt-4 space-y-2 text-sm">
            {Object.entries(data?.features || { google_forms_sync: true, google_sheets_sync: true, ai_chatbot: true, notifications: true }).map(([k,v]) => (
              <div key={k} className="flex justify-between"><span className="text-gray-500">{k}</span><span className={`px-2 py-0.5 rounded-full text-xs ${v ? 'bg-green-50 text-green-700 border' : 'bg-gray-100'}`}>{String(v)}</span></div>
            ))}
          </div>
        </div>

        <div className="bg-white border rounded-xl p-6">
          <h3 className="font-semibold flex items-center gap-2"><Bot size={18} /> Integrations Status</h3>
          <div className="mt-4 space-y-3 text-sm">
            <div className="p-3 bg-gray-50 rounded-lg"><p className="font-medium">Supabase</p><p className="text-xs text-gray-600">{integrations?.supabase?.status || data?.integrations?.supabase_configured ? 'Configured' : 'Not configured - set SUPABASE_URL'}</p></div>
            <div className="p-3 bg-gray-50 rounded-lg"><p className="font-medium">Google OAuth</p><p className="text-xs text-gray-600">{data?.integrations?.google_oauth_configured ? 'Configured' : 'Set GOOGLE_CLIENT_ID'}</p></div>
            <div className="p-3 bg-gray-50 rounded-lg"><p className="font-medium">Gemini AI</p><p className="text-xs text-gray-600">{data?.integrations?.gemini_configured ? `Configured (${integrations?.gemini?.model || 'gemini-1.5-flash'})` : 'Set GEMINI_API_KEY'}</p></div>
            <div className="p-3 bg-gray-50 rounded-lg"><p className="font-medium">n8n Workflows</p><p className="text-xs text-gray-600">{data?.integrations?.n8n_configured ? `Enabled: ${data?.integrations?.n8n_enabled}` : 'Set N8N_WEBHOOK_URL'}</p></div>
          </div>
        </div>

        <div className="bg-white border rounded-xl p-6">
          <h3 className="font-semibold flex items-center gap-2"><Link2 size={18} /> Frontend Config</h3>
          <pre className="mt-4 bg-gray-900 text-green-400 p-4 rounded-xl text-xs overflow-auto max-h-[300px]">{JSON.stringify(frontendConfig || {}, null, 2)}</pre>
        </div>
      </div>

      <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-sm text-amber-900">
        <strong>Configuration:</strong> Never hardcode secrets. Copy .env.example to .env and fill values. Values left blank in .env.example. After GitHub upload, add env vars in Railway dashboard, connect Supabase, enable Google OAuth and Sheets/Forms API.
      </div>
    </div>
  )
}
