import api from './api'

export const dashboardService = {
  getStats: async (filters?: any) => {
    const res = await api.get('/analytics/dashboard', { params: filters })
    return res.data.data
  },
  getKpis: async () => {
    const res = await api.get('/analytics/kpis')
    return res.data.data
  },
  getDailySummary: async (date?: string) => {
    const params = { report_date: date || new Date().toISOString().split('T')[0] }
    const res = await api.get('/daily-reports/summary', { params })
    return res.data
  }
}
