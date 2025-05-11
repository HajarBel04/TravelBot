// services/apiService.js
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiService = {
  /**
   * Process an email with the RAG system
   */
  async processEmail(email) {
    try {
      // FIXED: Added /api/ prefix to match FastAPI endpoint
      const response = await fetch(`${API_URL}/api/process-email`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Failed to process email');
      }

      return await response.json();
    } catch (error) {
      console.error('Error processing email:', error);
      throw error;
    }
  },

  /**
   * Get system statistics
   */
  async getStats() {
    try {
      // FIXED: Added /api/ prefix to match FastAPI endpoint
      const response = await fetch(`${API_URL}/api/stats`);

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Failed to fetch stats');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching stats:', error);
      throw error;
    }
  },

  /**
   * Get destinations with optional filters
   */
  async getDestinations(filters = {}) {
    try {
      // Create query string from filters
      const queryParams = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) queryParams.append(key, value);
      });

      // FIXED: Added /api/ prefix to match FastAPI endpoint
      const response = await fetch(`${API_URL}/api/destinations?${queryParams}`);

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Failed to fetch destinations');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching destinations:', error);
      throw error;
    }
  },

  /**
   * Get a specific destination by ID
   */
  async getDestination(id) {
    try {
      // FIXED: Added /api/ prefix to match FastAPI endpoint
      const response = await fetch(`${API_URL}/api/destinations/${id}`);

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Failed to fetch destination');
      }

      return await response.json();
    } catch (error) {
      console.error(`Error fetching destination ${id}:`, error);
      throw error;
    }
  }
};

export default apiService;