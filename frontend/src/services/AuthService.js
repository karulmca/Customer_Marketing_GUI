import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    
    // Handle 401 Unauthorized - session expired
    if (error.response?.status === 401) {
      // Clear stored session data
      localStorage.removeItem('sessionId');
      localStorage.removeItem('userInfo');
      
      // Reload the page to force re-authentication
      if (window.location.pathname !== '/') {
        window.location.href = '/';
      }
    }
    
    throw error;
  }
);

export const AuthService = {
  async login(credentials) {
    try {
      const response = await api.post('/auth/login', credentials);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  },

  async register(userData) {
    try {
      const response = await api.post('/auth/register', userData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Registration failed');
    }
  },

  async logout(sessionId) {
    try {
      const response = await api.post('/auth/logout', null, {
        params: { session_id: sessionId }
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Logout failed');
    }
  }
};

export const FileService = {
  async uploadFile(sessionId, file) {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/files/upload', formData, {
        params: { session_id: sessionId },
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'File upload failed');
    }
  },

  async processFile(sessionId, fileId, options = {}) {
    try {
      const response = await api.post(`/files/process/${fileId}`, null, {
        params: { 
          session_id: sessionId,
          scraping_enabled: options.scrapingEnabled || true,
          ai_analysis_enabled: options.aiAnalysisEnabled || false
        }
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'File processing failed');
    }
  },

  async getProcessingStatus(sessionId, fileId) {
    try {
      const response = await api.get(`/files/status/${fileId}`, {
        params: { session_id: sessionId }
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Status check failed');
    }
  },

  async downloadProcessedFile(sessionId, fileId) {
    try {
      const response = await api.get(`/files/download/${fileId}`, {
        params: { session_id: sessionId },
        responseType: 'blob'
      });
      
      // Create blob link to download file
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      // Get filename from response headers or use default
      const contentDisposition = response.headers['content-disposition'];
      let filename = 'processed_file.xlsx';
      if (contentDisposition) {
        const match = contentDisposition.match(/filename="(.+)"/);
        if (match) filename = match[1];
      }
      
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      return { success: true, filename };
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Download failed');
    }
  },

  // New methods matching original GUI workflow
  async uploadFileAsJson(sessionId, file) {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/files/upload-json', formData, {
        params: { session_id: sessionId },
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'JSON upload failed');
    }
  },

  async uploadAndProcessFile(sessionId, file) {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/files/upload-and-process', formData, {
        params: { session_id: sessionId },
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Upload and process failed');
    }
  },

  async getUploadedFiles(sessionId) {
    try {
      const response = await api.get('/files/uploads', {
        params: { session_id: sessionId }
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get uploaded files');
    }
  }
};

export const DatabaseService = {
  async getStatus(sessionId) {
    try {
      const response = await api.get('/database/status', {
        params: { session_id: sessionId }
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Database status check failed');
    }
  }
};