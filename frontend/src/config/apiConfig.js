/**
 * Centralized API configuration service
 * Manages all API endpoints and base URL configuration
 */

// Base API URL - configured via environment variables
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://company-scraper-backend.onrender.com/api';

export { API_BASE_URL };

// API endpoints configuration
export const API_ENDPOINTS = {
  // File management endpoints
  files: {
    validateHeaders: (sessionId) => `${API_BASE_URL}/files/validate-headers?session_id=${sessionId}`,
    downloadProcessed: (fileId, sessionId) => `${API_BASE_URL}/files/download-processed/${fileId}?session_id=${sessionId}`,
  },
  
  // Template endpoints
  templates: {
    sample: `${API_BASE_URL}/sample-template`,
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