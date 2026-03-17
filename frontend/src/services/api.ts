import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // Handle 401 errors (token expired)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        // Try to refresh the token
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          const response = await axios.post('/api/auth/refresh', {
            refresh_token: refreshToken,
          })
          
          const { access_token } = response.data
          localStorage.setItem('token', access_token)
          api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
          originalRequest.headers['Authorization'] = `Bearer ${access_token}`
          
          return api(originalRequest)
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

export default api

// API methods
export const authApi = {
  login: (email: string, password: string) => 
    api.post('/api/auth/login', { email, password }),
  
  register: (data: { email: string; password: string; first_name: string; last_name: string; company?: string }) =>
    api.post('/api/auth/register', data),
  
  logout: () => 
    api.post('/api/auth/logout'),
  
  forgotPassword: (email: string) => 
    api.post('/api/auth/forgot-password', { email }),
  
  resetPassword: (token: string, password: string) => 
    api.post('/api/auth/reset-password', { token, password }),
  
  verifyEmail: (token: string) => 
    api.post('/api/auth/verify-email', { token }),
}

export const projectsApi = {
  list: (params?: { page?: number; per_page?: number; search?: string; status?: string }) =>
    api.get('/api/projects', { params }),
  
  get: (id: string) => 
    api.get(`/api/projects/${id}`),
  
  create: (data: { 
    name: string
    description?: string
    location_name?: string
    design_storm_years?: number
    runoff_coefficient?: number
    flow_algorithm?: string 
  }) =>
    api.post('/api/projects', data),
  
  update: (id: string, data: { name?: string; description?: string; status?: string }) =>
    api.put(`/api/projects/${id}`, data),
  
  delete: (id: string) => 
    api.delete(`/api/projects/${id}`),
  
  share: (id: string, data: { email: string; permission: string }) =>
    api.post(`/api/projects/${id}/share`, data),
}

export const analysisApi = {
  start: (projectId: string, data?: { analysis_type?: string; parameters?: Record<string, any> }) =>
    api.post(`/api/analysis/start`, { project_id: projectId, ...data }),
  
  getStatus: (jobId: string) => 
    api.get(`/api/analysis/jobs/${jobId}`),
  
  getProjectStatus: (projectId: string) =>
    api.get(`/api/analysis/projects/${projectId}/status`),
  
  getResults: (projectId: string) => 
    api.get(`/api/analysis/projects/${projectId}/results`),
  
  getVisualization: (projectId: string) => 
    `/api/analysis/projects/${projectId}/visualization`,
  
  getComparisonVisualization: (projectId: string) =>
    `/api/analysis/projects/${projectId}/comparison`,
  
  getRawDTMVisualization: (projectId: string) =>
    `/api/analysis/projects/${projectId}/raw-dtm`,
  
  getGeoJSON: (projectId: string) =>
    api.get(`/api/analysis/projects/${projectId}/geojson`),
  
  getReport: (projectId: string) =>
    api.get(`/api/analysis/projects/${projectId}/report`),
  
  cancel: (jobId: string) => 
    api.post(`/api/analysis/jobs/${jobId}/cancel`),
  
  getAlgorithms: () =>
    api.get('/api/analysis/algorithms'),
  
  getDesignStandards: () =>
    api.get('/api/analysis/design-standards'),
}

export const uploadsApi = {
  uploadDTM: (projectId: string, file: File, onProgress?: (progress: number) => void) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('project_id', projectId)
    
    return api.post('/api/uploads/dtm', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      },
    })
  },

  uploadLAS: (projectId: string, file: File, onProgress?: (progress: number) => void) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('project_id', projectId)

    return api.post('/api/uploads/las', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      },
    })
  },

  buildDTMFromLAS: (data: { project_id: string; filename: string; resolution?: number; epsg?: string }) =>
    api.post('/api/uploads/build-dtm', data),
  
  getPreview: (projectId: string) => 
    api.get(`/api/uploads/${projectId}/preview`),
}

export const reportsApi = {
  list: () => 
    api.get('/api/reports'),
  
  generate: (data: { project_id: string; template_type: string; format: string }) =>
    api.post('/api/reports/generate', data),
  
  download: (reportId: string) => 
    api.get(`/api/reports/${reportId}/download`, { responseType: 'blob' }),
}

export const teamsApi = {
  list: () => 
    api.get('/api/teams'),
  
  get: (id: string) => 
    api.get(`/api/teams/${id}`),
  
  create: (data: { name: string; description?: string }) =>
    api.post('/api/teams', data),
  
  addMember: (teamId: string, data: { email: string; role: string }) =>
    api.post(`/api/teams/${teamId}/members`, data),
  
  removeMember: (teamId: string, userId: string) =>
    api.delete(`/api/teams/${teamId}/members/${userId}`),
}
