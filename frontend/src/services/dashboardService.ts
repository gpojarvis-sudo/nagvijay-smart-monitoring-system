import api from './api'

export const dashboardService = {
  getStats: async (filters?: any) => {
    const res = await api.get('/analytics/dashboard', { params: filters })
    return res.data.data
  },
  getKpis: async () => {
    const res = await api.get('/analytics/kpis')
    return res.data.data
  }
}
