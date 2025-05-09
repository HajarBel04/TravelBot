// hooks/useRagApi.js
import { useState, useCallback } from 'react';
import apiService from '../services/apiService';

/**
 * Custom hook for processing email with the RAG system
 */
export function useEmailProcessor() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [processingTime, setProcessingTime] = useState(null);

  const processEmail = useCallback(async (email) => {
    setLoading(true);
    setError(null);
    
    const startTime = Date.now();
    
    try {
      const data = await apiService.processEmail(email);
      setResult(data);
      setProcessingTime(Date.now() - startTime);
      return data;
    } catch (err) {
      setError(err.message || 'An error occurred while processing the email');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    processEmail,
    loading,
    error,
    result,
    processingTime
  };
}

/**
 * Custom hook for fetching system statistics
 */
export function useSystemStats() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);

  const fetchStats = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await apiService.getStats();
      setStats(data);
      return data;
    } catch (err) {
      setError(err.message || 'An error occurred while fetching stats');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    fetchStats,
    loading,
    error,
    stats
  };
}

/**
 * Custom hook for fetching destinations
 */
export function useDestinations() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [destinations, setDestinations] = useState([]);

  const fetchDestinations = useCallback(async (filters = {}) => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await apiService.getDestinations(filters);
      setDestinations(data);
      return data;
    } catch (err) {
      setError(err.message || 'An error occurred while fetching destinations');
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchDestination = useCallback(async (id) => {
    setLoading(true);
    setError(null);
    
    try {
      return await apiService.getDestination(id);
    } catch (err) {
      setError(err.message || 'An error occurred while fetching the destination');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    fetchDestinations,
    fetchDestination,
    loading,
    error,
    destinations
  };
}