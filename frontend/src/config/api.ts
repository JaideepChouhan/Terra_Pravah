/**
 * API Configuration
 * Centralizes API endpoints and configuration based on environment
 */

export const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
};

export const API_ENDPOINTS = {
  // Auth
  auth: {
    login: '/api/auth/login',
    register: '/api/auth/register',
    logout: '/api/auth/logout',
    refresh: '/api/auth/refresh',
    verify: '/api/auth/verify',
    userData: '/api/auth/me',
  },

  // Projects
  projects: {
    list: '/api/projects',
    create: '/api/projects',
    getById: (id: string) => `/api/projects/${id}`,
    update: (id: string) => `/api/projects/${id}`,
    delete: (id: string) => `/api/projects/${id}`,
  },

  // Analysis
  analysis: {
    create: '/api/analysis',
    list: '/api/analysis',
    getById: (id: string) => `/api/analysis/${id}`,
    results: (id: string) => `/api/analysis/${id}/results`,
  },

  // File Upload
  upload: {
    file: '/api/upload',
    files: '/api/upload/batch',
  },

  // Processing
  processing: {
    lidar: '/api/process/lidar',
    raster: '/api/process/raster',
    vector: '/api/process/vector',
  },
};

/**
 * Get authorization headers with JWT token
 */
export const getAuthHeaders = (token?: string) => {
  const headers: Record<string, string> = { ...API_CONFIG.headers };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
};

/**
 * Get full API URL
 */
export const getFullUrl = (endpoint: string): string => {
  return `${API_CONFIG.baseURL}${endpoint}`;
};

/**
 * Check if API is accessible
 */
export const isProduction = (): boolean => {
  return import.meta.env.VITE_ENVIRONMENT === 'production';
};

/**
 * Get log level based on environment
 */
export const getLogLevel = (): 'debug' | 'info' | 'warn' | 'error' => {
  const level = import.meta.env.VITE_LOG_LEVEL || 'info';
  return level as 'debug' | 'info' | 'warn' | 'error';
};
