import axios from 'axios';

// Create axios instance with base configuration
const API = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000',
  timeout: 120000, // 2 minutes for large file processing
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging and auth (if needed later)
API.interceptors.request.use(
  (config) => {
    // Log requests in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`);
    }
    return config;
  },
  (error) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
API.interceptors.response.use(
  (response) => {
    if (process.env.NODE_ENV === 'development') {
      console.log(`[API Response] ${response.config.url}`, response.status);
    }
    return response;
  },
  (error) => {
    // Handle specific error cases
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      
      switch (status) {
        case 400:
          console.error('[API Error 400] Bad Request:', data.error || data.message);
          break;
        case 404:
          console.error('[API Error 404] Not Found:', error.config.url);
          break;
        case 500:
          console.error('[API Error 500] Server Error:', data.error || data.message);
          break;
        default:
          console.error(`[API Error ${status}]`, data.error || data.message);
      }
    } else if (error.request) {
      // Request made but no response received
      console.error('[API Error] No response received:', error.message);
    } else {
      // Something else happened
      console.error('[API Error]', error.message);
    }
    
    return Promise.reject(error);
  }
);

// API endpoint functions with retry logic
const apiClient = {
  // Upload and analyze files
  analyzeFiles: async (formData, config = {}) => {
    try {
      const response = await API.post('/api/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        ...config,
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get analysis results with retry
  getResults: async (analysisId, retries = 3) => {
    let lastError;
    
    for (let i = 0; i < retries; i++) {
      try {
        const response = await API.get(`/api/results/${analysisId}`);
        return response.data;
      } catch (error) {
        lastError = error;
        
        // Don't retry on 404 or 400 errors
        if (error.response && [400, 404].includes(error.response.status)) {
          throw error;
        }
        
        // Wait before retrying (exponential backoff)
        if (i < retries - 1) {
          const delay = Math.min(1000 * Math.pow(2, i), 5000);
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }
    }
    
    throw lastError;
  },

  // Download results
  downloadResults: async (analysisId, format = 'json') => {
    try {
      const response = await API.get(`/api/download/${analysisId}`, {
        params: { format },
        responseType: 'blob',
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get all analyses (for dashboard)
  getAllAnalyses: async () => {
    try {
      const response = await API.get('/api/analyses');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Delete analysis
  deleteAnalysis: async (analysisId) => {
    try {
      const response = await API.delete(`/api/analysis/${analysisId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Health check
  healthCheck: async () => {
    try {
      const response = await API.get('/api/health');
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};

export default apiClient;
export { API };