/**
 * Centralized API configuration service
 * Manages all API endpoints and base URL configuration
 */

// Base API URL - configured via environment variables
//const API_BASE_URL = 'http://localhost:8000/api';
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://company-scraper-backend-90mt.onrender.com/api';

export { API_BASE_URL };

// API endpoints configuration
export const API_ENDPOINTS = {
  // File management endpoints
  files: {
    validateHeaders: (sessionId) => `${API_BASE_URL}/files/validate-headers?session_id=${sessionId}`,
    downloadProcessed: (fileId, sessionId) => `${API_BASE_URL}/files/download-processed/${fileId}?session_id=${sessionId}`,
    viewData: (fileId, sessionId, limit = 100, offset = 0) => `${API_BASE_URL}/files/view-data/${fileId}?session_id=${sessionId}&limit=${limit}&offset=${offset}`,
    editRecord: (recordId, sessionId) => `${API_BASE_URL}/files/edit-data/${recordId}?session_id=${sessionId}`,
    deleteRecord: (recordId, sessionId) => `${API_BASE_URL}/files/delete-record/${recordId}?session_id=${sessionId}`,
    reprocess: (fileId, sessionId) => `${API_BASE_URL}/files/process/${fileId}?session_id=${sessionId}`,
  },
  
  // Template endpoints
  templates: {
    sample: `${API_BASE_URL}/sample-template`,
  },
  
  // User management endpoints
  auth: {
    getUsers: (sessionId) => `${API_BASE_URL}/auth/users?session_id=${sessionId}`,
    updateUser: (sessionId) => `${API_BASE_URL}/auth/users?session_id=${sessionId}`,
    deleteUser: (sessionId, userId) => `${API_BASE_URL}/auth/users/${userId}?session_id=${sessionId}`,
    createUser: (sessionId) => `${API_BASE_URL}/auth/users?session_id=${sessionId}`,
  }
};

// Configuration for axios instances
export const API_CONFIG = {
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
};

// Export the base URL for backward compatibility
export default API_BASE_URL;