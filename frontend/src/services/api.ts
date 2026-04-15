import axios from 'axios'

const PROD_API_FALLBACK = 'https://terrapravah-production.up.railway.app'
const DEMO_ENABLED = import.meta.env.VITE_ENABLE_DEMO === 'true'

const api = axios.create({
  baseURL:
    import.meta.env.VITE_API_URL || (import.meta.env.PROD ? PROD_API_FALLBACK : ''),
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
          const refreshUrl = api.defaults.baseURL
            ? `${api.defaults.baseURL}/api/auth/refresh`
            : '/api/auth/refresh'

          const response = await axios.post(refreshUrl, {
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
const isDemo = () => DEMO_ENABLED && localStorage.getItem("token") === "demo-token-123";

const demoDelay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

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
  list: async (params?: { page?: number; per_page?: number; search?: string; status?: string }) => {
    if (isDemo()) {
      await demoDelay(500);
      return { data: { projects: [{id: 'demo-1', name: 'Demo Project', status: 'completed'}], total: 1 } };
    }
    return api.get('/api/projects', { params });
  },

  get: async (id: string) => {
    if (isDemo()) {
      await demoDelay(500);
      return { data: { project: { id, name: 'Demo Project', status: 'completed', design_storm_years: 10, runoff_coefficient: 0.5, flow_algorithm: 'd8', dtm_file_path: 'mock/path', visualization_path: 'mock/path' } } };
    }
    return api.get(`/api/projects/${id}`);
  },

  create: async (data: {
    name: string
    description?: string
    location_name?: string
    design_storm_years?: number
    runoff_coefficient?: number
    flow_algorithm?: string
  }) => {
    if (isDemo()) {
      await demoDelay(1000);
      return { data: { project: { id: 'demo-proj-' + Date.now(), ...data, status: 'created' } } };
    }
    return api.post('/api/projects', data);
  },

  update: async (id: string, data: { name?: string; description?: string; status?: string }) => {
    if (isDemo()) return { data: { id, ...data } };
    return api.put(`/api/projects/${id}`, data);
  },

  delete: async (id: string) => {
    if (isDemo()) return { data: { success: true } };
    return api.delete(`/api/projects/${id}`);
  },

  share: async (id: string, data: { email: string; permission: string }) => {
    if (isDemo()) return { data: { success: true } };
    return api.post(`/api/projects/${id}/share`, data);
  },
}
export const analysisApi = {
  start: async (projectId: string, data?: { analysis_type?: string; parameters?: Record<string, any> }) => {
    if (isDemo()) {
      await demoDelay(500);
      return { data: { job_id: 'demo-job-' + Date.now() } };
    }
    return api.post(`/api/analysis/start`, { project_id: projectId, ...data });
  },

  getStatus: async (jobId: string) => {
    if (isDemo()) {
      await demoDelay(500);
      return { data: { status: 'completed', progress: 100 } };
    }
    return api.get(`/api/analysis/jobs/${jobId}`);
  },

  getProjectStatus: async (projectId: string) => {
    if (isDemo()) {
      await demoDelay(500);
      return { data: { status: 'completed', message: 'Analysis complete.' } };
    }
    return api.get(`/api/analysis/projects/${projectId}/status`);
  },

  getResults: async (projectId: string) => {
    if (isDemo()) {
      await demoDelay(500);
      return { data: { 
        stats: { totalArea: 100, catchments: 5, channels: 10 },
        results: []
      } };
    }
    return api.get(`/api/analysis/projects/${projectId}/results`);
  },

  getVisualization: (projectId: string) => {
    if (isDemo()) return `/demo-visualization.png`;
    return `/api/analysis/projects/${projectId}/visualization`;
  },

  getComparisonVisualization: (projectId: string) => {
    if (isDemo()) return `/demo-comparison.png`;
    return `/api/analysis/projects/${projectId}/comparison`;
  },

  getRawDTMVisualization: (projectId: string) => {
    if (isDemo()) return `/demo-raw-dtm.png`;
    return `/api/analysis/projects/${projectId}/raw-dtm`;
  },

  getGeoJSON: async (projectId: string) => {
    if (isDemo()) {
      await demoDelay(500);
      return { data: { type: 'FeatureCollection', features: [] } };
    }
    return api.get(`/api/analysis/projects/${projectId}/geojson`);
  },

  getReport: async (projectId: string) => {
    if (isDemo()) {
      await demoDelay(500);
      return { data: { report: {
          project: { terrain_file: 'test.las', design_storm_return_years: 10, runoff_coefficient: 0.5 },
          terrain: { dimensions: '1000x1000', resolution_m: 1, elevation_min: 10, elevation_max: 50, elevation_range: 40 },
          network_summary: { total_channels: 15, primary_channels: 2, secondary_channels: 5, tertiary_channels: 8, total_length_m: 5000, total_length_km: 5, outlets: 1 },
          hydraulics: { design_method: 'Rational', flow_routing: 'Manning', pipe_sizing: 'Automatic', total_design_flow_m3s: 1.5 },
          channels: []
      } } };
    }
    return api.get(`/api/analysis/projects/${projectId}/report`);
  },

  cancel: async (jobId: string) => {
    if (isDemo()) return { data: { success: true } };
    return api.post(`/api/analysis/jobs/${jobId}/cancel`);
  },

  getAlgorithms: async () => {
    if (isDemo()) return { data: { algorithms: ['d8', 'dinf'] } };
    return api.get('/api/analysis/algorithms');
  },

  getDesignStandards: async () => {
    if (isDemo()) return { data: { standards: [] } };
    return api.get('/api/analysis/design-standards');
  },
}
export const uploadsApi = {
  uploadDTM: async (projectId: string, file: File, onProgress?: (progress: number) => void) => {
    if (isDemo()) {
      if (onProgress) {
        for(let i=10; i<=100; i+=10) {
          await demoDelay(100);
          onProgress(i);
        }
      }
      return { data: { file: { name: file.name } } };
    }
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

  uploadLAS: async (projectId: string, file: File, onProgress?: (progress: number) => void) => {
    if (isDemo()) {
      if (onProgress) {
        for(let i=10; i<=100; i+=10) {
          await demoDelay(100);
          onProgress(i);
        }
      }
      return { data: { file: { name: file.name } } };
    }
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

  buildDTMFromLAS: async (data: { project_id: string; filename: string; resolution?: number; epsg?: string }) => {
    if (isDemo()) {
      await demoDelay(1000);
      return { data: { success: true } };
    }
    return api.post('/api/uploads/build-dtm', data);
  },

  getPreview: async (projectId: string) => {
    if (isDemo()) return { data: { preview_url: null } };
    return api.get(`/api/uploads/${projectId}/preview`);
  },
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
