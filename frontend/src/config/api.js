// API Configuration
const API_CONFIG = {
  // Base URL - can be overridden by environment variables
  BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  
  // API Endpoints
  ENDPOINTS: {
    AQI: '/aqi/aqi',
    CHARTS: '/aqi/charts',
    YEARLY_CHARTS: '/aqi/charts',
    SUGGEST: '/suggest/ask-vayu'
  },
  
  // External APIs
  EXTERNAL: {
    WAQI_TOKEN: import.meta.env.VITE_WAQI_TOKEN || '674c86ddb4615f8667355f4c52e8446cef910b3b',
    NOMINATIM: 'https://nominatim.openstreetmap.org/search'
  }
};

// Helper function to build API URLs
export const buildApiUrl = (endpoint) => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};

// Helper function to get external API URL
export const getExternalApiUrl = (apiName) => {
  return API_CONFIG.EXTERNAL[apiName];
};

export default API_CONFIG; 