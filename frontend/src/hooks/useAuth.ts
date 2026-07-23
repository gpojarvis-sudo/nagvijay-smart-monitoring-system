import { useAuthStore } from '@/services/authStore'

export function useAuth() {
  const store = useAuthStore()
  return store
}
