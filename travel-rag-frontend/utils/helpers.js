// utils/helpers.js

/**
 * Format a timestamp to a readable date string
 * 
 * @param {string|Date} timestamp - The timestamp to format
 * @param {Object} options - Formatting options
 * @returns {string} - Formatted date string
 */
export function formatDate(timestamp, options = {}) {
    if (!timestamp) return 'N/A';
    
    const date = typeof timestamp === 'string' ? new Date(timestamp) : timestamp;
    
    // Default formatting options
    const defaultOptions = {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      ...options
    };
    
    try {
      return date.toLocaleDateString(undefined, defaultOptions);
    } catch (error) {
      console.error('Error formatting date:', error);
      return 'Invalid date';
    }
  }
  
  /**
   * Format a number with commas as thousands separators
   * 
   * @param {number} number - The number to format
   * @param {number} decimals - Number of decimal places
   * @returns {string} - Formatted number
   */
  export function formatNumber(number, decimals = 0) {
    if (number === null || number === undefined) return 'N/A';
    
    try {
      return Number(number).toLocaleString(undefined, { 
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
      });
    } catch (error) {
      console.error('Error formatting number:', error);
      return 'Error';
    }
  }
  
  /**
   * Format milliseconds to a readable time string
   * 
   * @param {number} ms - Time in milliseconds
   * @returns {string} - Formatted time string
   */
  export function formatTime(ms) {
    if (!ms && ms !== 0) return 'N/A';
    
    if (ms < 1000) {
      return `${ms}ms`;
    } else if (ms < 60000) {
      return `${(ms / 1000).toFixed(2)}s`;
    } else {
      const minutes = Math.floor(ms / 60000);
      const seconds = ((ms % 60000) / 1000).toFixed(2);
      return `${minutes}m ${seconds}s`;
    }
  }
  
  /**
   * Calculate percentage and format it
   * 
   * @param {number} value - The value
   * @param {number} total - The total
   * @param {number} decimals - Number of decimal places
   * @returns {string} - Formatted percentage
   */
  export function formatPercentage(value, total, decimals = 1) {
    if (value === null || value === undefined || total === null || total === undefined || total === 0) {
      return 'N/A';
    }
    
    try {
      const percentage = (value / total) * 100;
      return `${percentage.toFixed(decimals)}%`;
    } catch (error) {
      console.error('Error calculating percentage:', error);
      return 'Error';
    }
  }
  
  /**
   * Truncate a string to a specified length
   * 
   * @param {string} text - The text to truncate
   * @param {number} length - Maximum length
   * @param {string} suffix - Suffix to add when truncated
   * @returns {string} - Truncated text
   */
  export function truncateText(text, length = 100, suffix = '...') {
    if (!text) return '';
    
    return text.length > length ? `${text.substring(0, length)}${suffix}` : text;
  }
  
  /**
   * Extract destination information from an email
   * This is a simple implementation for demo purposes
   * 
   * @param {string} email - The email text
   * @returns {Object} - Extracted information
   */
  export function extractDestinationFromEmail(email) {
    if (!email) return null;
    
    // Simple regex patterns to extract basic information
    const destinationPattern = /(?:to|in|for)\s+([A-Za-z\s]+)(?:for|in|\.)/i;
    const durationPattern = /(\d+)\s*(?:day|days|week|weeks)/i;
    const travelersPattern = /(?:family of|with|for)\s+(\d+)/i;
    const budgetPattern = /budget.*?(\$?\d[\d,]*)/i;
    
    const destinationMatch = email.match(destinationPattern);
    const durationMatch = email.match(durationPattern);
    const travelersMatch = email.match(travelersPattern);
    const budgetMatch = email.match(budgetPattern);
    
    return {
      destination: destinationMatch ? destinationMatch[1].trim() : null,
      duration: durationMatch ? `${durationMatch[1]} days` : null,
      travelers: travelersMatch ? travelersMatch[1] : null,
      budget: budgetMatch ? budgetMatch[1] : null
    };
  }
  
  /**
   * Generate a list of dates between start and end
   * 
   * @param {Date} startDate - Start date
   * @param {Date} endDate - End date
   * @returns {Array<Date>} - Array of dates
   */
  export function getDatesBetween(startDate, endDate) {
    const dates = [];
    let currentDate = new Date(startDate);
    
    while (currentDate <= endDate) {
      dates.push(new Date(currentDate));
      currentDate.setDate(currentDate.getDate() + 1);
    }
    
    return dates;
  }