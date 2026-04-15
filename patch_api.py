import re
import os

with open('frontend/src/services/api.ts', 'r', encoding='utf-8') as f:
    content = f.read()

if 'const isDemo' not in content:
    content = content.replace('export const authApi =', 'const isDemo = () => localStorage.getItem("token") === "demo-token-123";\n\nconst demoDelay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));\n\nexport const authApi =')

projects_replacement = """export const projectsApi = {
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
      return { data: { id, name: 'Demo Project', status: 'completed', design_storm_years: 10, runoff_coefficient: 0.5, flow_algorithm: 'd8' } };
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
}"""
content = re.sub(r'export const projectsApi = \{[\s\S]*?(?=\nexport const analysisApi =)', projects_replacement, content)

uploads_replacement = """export const uploadsApi = {
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
}"""
content = re.sub(r'export const uploadsApi = \{[\s\S]*?(?=\nexport const reportsApi =)', uploads_replacement, content)

analysis_replacement = """export const analysisApi = {
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
      return { data: { url: '/demo-report.pdf' } };
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
}"""
content = re.sub(r'export const analysisApi = \{[\s\S]*?(?=\nexport const uploadsApi =)', analysis_replacement, content)

with open('frontend/src/services/api.ts', 'w', encoding='utf-8') as f:
    f.write(content)
