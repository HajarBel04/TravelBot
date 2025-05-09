// services/apiService.js
import config from '../config';

/**
 * Service to handle API requests to the RAG backend
 */
class ApiService {
  constructor() {
    this.baseUrl = config.api.baseUrl;
    this.timeout = config.api.timeout;
    this.useMocks = config.api.useMocks;
  }

  /**
   * Process an email and generate a travel proposal
   * 
   * @param {string} email - The email content
   * @returns {Promise<Object>} - The processed result with proposal
   */
  async processEmail(email) {
    if (this.useMocks) {
      // Return from the local Next.js API route
      return this.fetchWithTimeout('/api/process-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });
    } else {
      // Make a direct call to the RAG backend
      return this.fetchWithTimeout(`${this.baseUrl}${config.api.endpoints.processEmail}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });
    }
  }

  /**
   * Get system statistics
   * 
   * @returns {Promise<Object>} - System statistics
   */
  async getStats() {
    if (this.useMocks) {
      return this.fetchWithTimeout('/api/stats');
    } else {
      return this.fetchWithTimeout(`${this.baseUrl}${config.api.endpoints.getStats}`);
    }
  }

  /**
   * Get destinations
   * 
   * @param {Object} filters - Optional filters for destinations
   * @returns {Promise<Array>} - List of destinations
   */
  async getDestinations(filters = {}) {
    const params = new URLSearchParams();
    
    // Add filters to query params
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        params.append(key, value);
      }
    });
    
    const queryString = params.toString() ? `?${params.toString()}` : '';
    
    if (this.useMocks) {
      return this.fetchWithTimeout(`/api/destinations${queryString}`);
    } else {
      return this.fetchWithTimeout(`${this.baseUrl}${config.api.endpoints.getDestinations}${queryString}`);
    }
  }

  /**
   * Get a single destination by ID
   * 
   * @param {string|number} id - Destination ID
   * @returns {Promise<Object>} - Destination details
   */
  async getDestination(id) {
    if (this.useMocks) {
      return this.fetchWithTimeout(`/api/destinations/${id}`);
    } else {
      return this.fetchWithTimeout(`${this.baseUrl}${config.api.endpoints.getSingleDestination(id)}`);
    }
  }

  /**
   * Helper method to fetch with timeout
   * 
   * @param {string} url - URL to fetch
   * @param {Object} options - Fetch options
   * @returns {Promise<any>} - Parsed JSON response
   */
  async fetchWithTimeout(url, options = {}) {
    const controller = new AbortController();
    const { signal } = controller;
    
    // Set timeout
    const timeout = setTimeout(() => {
      controller.abort();
    }, this.timeout);
    
    try {
      const response = await fetch(url, {
        ...options,
        signal,
      });
      
      clearTimeout(timeout);
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      clearTimeout(timeout);
      
      if (error.name === 'AbortError') {
        throw new Error(`Request timeout after ${this.timeout}ms`);
      }
      
      throw error;
    }
  }
}

// Export as singleton
export default new ApiService();