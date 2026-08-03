import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import api from './api'

export interface User {
  id: string
  email: string
  full_name: string
  avatar_url?: string
  role: string
  is_active: boolean
  office_id?: string
  employee_id?: string
  permissions: string[]
}

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (idToken: string) => Promise<void>
  loginWithPassword: (username: string, password: string) => Promise<any>
  logout: () => void
  checkAuth: () => Promise<void>
  hasPermission: (permission: string) => boolean
  hasRole: (roles: string | string[]) => boolean
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (idToken: string) => {
        set({ isLoading: true })
        try {
          const res = await api.post('/auth/google', { id_token: idToken })
          const { access_token, refresh_token, user } = res.data.data

          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', refresh_token)

          set({
            user,
            accessToken: access_token,
            refreshToken: refresh_token,
            isAuthenticated: true,
            isLoading: false,
          })

          return user
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      loginWithPassword: async (username: string, password: string) => {
        set({ isLoading: true })

        try {
          const res = await api.post('/auth/login', {
            username: username,
            password,
          })

          const { access_token, refresh_token, user } = res.data.data

          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', refresh_token)

          set({
            user,
            accessToken: access_token,
            refreshToken: refresh_token,
            isAuthenticated: true,
            isLoading: false,
          })

          return user
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      logout: () => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        })
        window.location.href = '/login'
      },

      checkAuth: async () => {
        const token = localStorage.getItem('access_token')
        if (!token) {
          set({ isAuthenticated: false, user: null })
          return
        }

        try {
          const res = await api.get('/auth/me')
          const user = res.data.data
          set({ user, isAuthenticated: true, accessToken: token })
        } catch {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          set({ isAuthenticated: false, user: null })
        }
      },

      hasPermission: (permission: string) => {
        const { user } = get()
        if (!user) return false
        if (user.role === 'SUPER_ADMIN') return true
        return user.permissions.includes(permission)
      },

      hasRole: (roles: string | string[]) => {
        const { user } = get()
        if (!user) return false
        const roleList = Array.isArray(roles) ? roles : [roles]
        return roleList.includes(user.role)
      },
    }),
    {
      name: 'nsms-auth',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
