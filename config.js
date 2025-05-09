// config.js
// This file contains configuration for connecting to the RAG backend

const config = {
    // Backend API configuration
    api: {
      // Base URL for the RAG backend API
      baseUrl: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000',
      
      // API endpoints
      endpoints: {
        processEmail: '/api/process-email',
        getStats: '/api/stats',
        getDestinations: '/api/destinations',
        getSingleDestination: (id) => `/api/destinations/${id}`
      },
      
      // Request timeout in milliseconds
      timeout: 30000,
      
      // Enable mock responses for development
      useMocks: process.env.NEXT_PUBLIC_USE_MOCKS === 'true' || true
    },
    
    // UI configuration
    ui: {
      // Theme colors
      colors: {
        primary: {
          light: '#3B82F6', // blue-500
          DEFAULT: '#2563EB', // blue-600
          dark: '#1D4ED8'    // blue-700
        },
        secondary: {
          light: '#06B6D4', // cyan-500
          DEFAULT: '#0891B2', // cyan-600
          dark: '#0E7490'  // cyan-700
        },
        accent: {
          light: '#F59E0B', // amber-500
          DEFAULT: '#D97706', // amber-600
          dark: '#B45309'  // amber-700
        }
      },
      
      // Default pagination settings
      pagination: {
        itemsPerPage: 10
      },
      
      // Animation settings
      animations: {
        enabled: true,
        duration: 300
      }
    },
    
    // Feature flags
    features: {
      shareItinerary: true,
      exportPDF: true,
      showProcessingMetrics: true,
      realTimeWeather: false,
      userAccounts: false
    }
  };
  
  export default config;