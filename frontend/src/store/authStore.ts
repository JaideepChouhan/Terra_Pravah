import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import api from '../services/api'

interface User {
  id: string
  email: string
  firstName: string
  lastName: string
  role: string
  avatar?: string
  company?: string
  createdAt: string
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  
  // Actions
  login: (email: string, password: string) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  logout: () => void
  updateUser: (data: Partial<User>) => void
  setUser: (user: Partial<User>) => void
  checkAuth: () => Promise<void>
  clearError: () => void
}

interface RegisterData {
  email: string
  password: string
  firstName: string
  lastName: string
  company?: string
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: true,
      error: null,

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null })
        try {
          const response = await api.post('/api/auth/login', { email, password })
          const { user, access_token } = response.data
          
          localStorage.setItem('token', access_token)
          api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
          
          set({
            user: {
              id: user.id,
              email: user.email,
              firstName: user.first_name,
              lastName: user.last_name,
              role: user.role,
              avatar: user.avatar_url,
              company: user.company,
              createdAt: user.created_at,
            },
            token: access_token,
            isAuthenticated: true,
            isLoading: false,
          })
        } catch (error: any) {
          set({
            error: error.response?.data?.error || 'Failed to login',
            isLoading: false,
          })
          throw error
        }
      },

      register: async (data: RegisterData) => {
        set({ isLoading: true, error: null })
        try {
          const response = await api.post('/api/auth/register', {
            email: data.email,
            password: data.password,
            first_name: data.firstName,
            last_name: data.lastName,
            company: data.company,
          })
          const { user, access_token } = response.data
          
          localStorage.setItem('token', access_token)
          api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
          
          set({
            user: {
              id: user.id,
              email: user.email,
              firstName: user.first_name,
              lastName: user.last_name,
              role: user.role,
              avatar: user.avatar_url,
              company: user.company,
              createdAt: user.created_at,
            },
            token: access_token,
            isAuthenticated: true,
            isLoading: false,
          })
        } catch (error: any) {
          set({
            error: error.response?.data?.error || 'Failed to register',
            isLoading: false,
          })
          throw error
        }
      },

      logout: () => {
        localStorage.removeItem('token')
        delete api.defaults.headers.common['Authorization']
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
        })
      },

      updateUser: (data: Partial<User>) => {
        const { user } = get()
        if (user) {
          set({ user: { ...user, ...data } })
        }
      },

      setUser: (data: Partial<User>) => {
        const { user } = get()
        if (user) {
          set({ user: { ...user, ...data } })
        }
      },

      checkAuth: async () => {
        const token = localStorage.getItem('token')
        if (!token) {
          set({ isLoading: false, isAuthenticated: false })
          return
        }

        set({ isLoading: true })
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`

        try {
          const response = await api.get('/api/users/me')
          const user = response.data
          
          set({
            user: {
              id: user.id,
              email: user.email,
              firstName: user.first_name,
              lastName: user.last_name,
              role: user.role,
              avatar: user.avatar_url,
              company: user.company,
              createdAt: user.created_at,
            },
            token,
            isAuthenticated: true,
            isLoading: false,
          })
        } catch (error) {
          localStorage.removeItem('token')
          delete api.defaults.headers.common['Authorization']
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
          })
        }
      },

      clearError: () => {
        set({ error: null })
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token }),
    }
  )
)

// Initialize auth check on app load
if (typeof window !== 'undefined') {
  useAuthStore.getState().checkAuth()
}
