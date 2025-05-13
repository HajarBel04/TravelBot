// src/hooks/useRagApi.js
import { useState, useCallback } from 'react';
import apiService from '../services/apiService';

/**
 * Hook for processing email through the RAG system
 */
export function useEmailProcessor() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const processEmail = useCallback(async (email) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiService.processEmail(email);
      setResult(response);
      return response;
    } catch (err) {
      setError(err.message || 'Failed to process email');
      console.error('Error in useEmailProcessor:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return { processEmail, loading, result, error };
}

/**
 * Hook for fetching system statistics
 */
export function useSystemStats() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchStats = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiService.getStats();
      setStats(response);
      return response;
    } catch (err) {
      setError(err.message || 'Failed to fetch stats');
      console.error('Error in useSystemStats:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return { fetchStats, stats, loading, error };
}

/**
 * Hook for fetching destinations
 */
export function useDestinations() {
  const [destinations, setDestinations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchDestinations = useCallback(async (filters = {}) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiService.getDestinations(filters);
      setDestinations(response);
      return response;
    } catch (err) {
      setError(err.message || 'Failed to fetch destinations');
      console.error('Error in useDestinations:', err);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  return { fetchDestinations, destinations, loading, error };
}