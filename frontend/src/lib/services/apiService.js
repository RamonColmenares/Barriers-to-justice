/**
 * API Service for fetching data with filters
 * Handles communication with the backend API endpoints
 */
import { API_BASE_URL } from '$lib/config.js';
import { filterService } from './filterService.js';

class ApiService {
  constructor() {
    // Cache para evitar llamadas duplicadas
    this.pendingRequests = new Map();
    this.requestCache = new Map();
    this.cacheTimeout = 30000; // 30 segundos
  }
  
  /**
   * Build URL with filter query parameters
   */
  buildUrlWithFilters(endpoint, customFilters = null) {
    const filters = customFilters || filterService.getFilters();
    const queryParams = new URLSearchParams();
    
    // Add filters to query params (skip 'all' values)
    Object.entries(filters).forEach(([key, value]) => {
      if (value && value !== 'all') {
        queryParams.append(key, value);
      }
    });
    
    const queryString = queryParams.toString();
    return `${API_BASE_URL}${endpoint}${queryString ? `?${queryString}` : ''}`;
  }

  /**
   * Create cache key for request
   */
  getCacheKey(url, options = {}) {
    return `${url}_${JSON.stringify(options)}`;
  }

  /**
   * Check if request is already pending or cached
   */
  async getFromCacheOrPending(cacheKey, url, options) {
    // Check if request is already pending
    if (this.pendingRequests.has(cacheKey)) {
      console.log(`Request already pending for ${url}, waiting for it...`);
      return this.pendingRequests.get(cacheKey);
    }

    // Check cache
    if (this.requestCache.has(cacheKey)) {
      const cachedData = this.requestCache.get(cacheKey);
      if (Date.now() - cachedData.timestamp < this.cacheTimeout) {
        console.log(`Using cached data for ${url}`);
        return cachedData.data;
      } else {
        this.requestCache.delete(cacheKey);
      }
    }

    return null;
  }

  /**
   * Generic fetch with error handling and duplicate request prevention
   */
  async fetchWithRetry(url, options = {}, retries = 2) {
    const cacheKey = this.getCacheKey(url, options);
    
    // Check cache or pending requests first
    const cachedResult = await this.getFromCacheOrPending(cacheKey, url, options);
    if (cachedResult) {
      return cachedResult;
    }

    // Create promise for this request
    const requestPromise = this._performRequest(url, options, retries);
    
    // Store the promise to prevent duplicate requests
    this.pendingRequests.set(cacheKey, requestPromise);

    try {
      const result = await requestPromise;
      
      // Cache successful results
      this.requestCache.set(cacheKey, {
        data: result,
        timestamp: Date.now()
      });
      
      return result;
    } finally {
      // Remove from pending requests
      this.pendingRequests.delete(cacheKey);
    }
  }

  /**
   * Perform the actual HTTP request with retries
   */
  async _performRequest(url, options, retries) {
    let lastError;
    
    for (let i = 0; i <= retries; i++) {
      try {
        console.log(`Making request to ${url} (attempt ${i + 1})`);
        const response = await fetch(url, {
          ...options,
          headers: {
            'Content-Type': 'application/json',
            ...options.headers
          }
        });
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
      } catch (error) {
        lastError = error;
        console.warn(`Attempt ${i + 1} failed for ${url}:`, error.message);
        
        if (i < retries) {
          // Wait before retrying
          await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
        }
      }
    }
    
    throw lastError;
  }

  /**
   * Clear cache for fresh data
   */
  clearCache() {
    this.requestCache.clear();
    this.pendingRequests.clear();
  }

  /**
   * Get overview statistics (unfiltered)
   */
  async getOverview() {
    const url = `${API_BASE_URL}/overview`;
    return this.fetchWithRetry(url);
  }

  /**
   * Get filtered overview statistics
   */
  async getFilteredOverview(customFilters = null) {
    const url = this.buildUrlWithFilters('/overview/filtered', customFilters);
    return this.fetchWithRetry(url);
  }

  /**
   * Get basic statistics for data page
   */
  async getBasicStatistics(customFilters = null) {
    const url = this.buildUrlWithFilters('/data/basic-stats', customFilters);
    return this.fetchWithRetry(url);
  }

  /**
   * Get representation outcomes chart data
   */
  async getRepresentationOutcomes(customFilters = null) {
    const url = this.buildUrlWithFilters('/findings/representation-outcomes', customFilters);
    return this.fetchWithRetry(url);
  }

  /**
   * Get time series analysis chart data
   */
  async getTimeSeriesAnalysis(customFilters = null) {
    const url = this.buildUrlWithFilters('/findings/time-series', customFilters);
    return this.fetchWithRetry(url);
  }

  /**
   * Get chi-square analysis results
   */
  async getChiSquareAnalysis(customFilters = null) {
    const url = this.buildUrlWithFilters('/findings/chi-square', customFilters);
    return this.fetchWithRetry(url);
  }

  /**
   * Get outcome percentages chart data
   */
  async getOutcomePercentages(customFilters = null) {
    const url = this.buildUrlWithFilters('/findings/outcome-percentages', customFilters);
    return this.fetchWithRetry(url);
  }

  /**
   * Get countries chart data
   */
  async getCountriesChart(customFilters = null) {
    const url = this.buildUrlWithFilters('/findings/countries', customFilters);
    return this.fetchWithRetry(url);
  }

  /**
   * Get filter options from API
   */
  async getFilterOptions() {
    const url = `${API_BASE_URL}/meta/options`;
    return this.fetchWithRetry(url);
  }

  /**
   * Check data loading status
   */
  async getDataStatus() {
    const url = `${API_BASE_URL}/data-status`;
    return this.fetchWithRetry(url);
  }

  /**
   * Force reload data from source
   */
  async forceReloadData() {
    const url = `${API_BASE_URL}/force-reload-data`;
    return this.fetchWithRetry(url);
  }

  /**
   * Load all chart data for findings page
   */
  async getAllChartData(customFilters = null) {
    try {
      const [
        representationOutcomes,
        timeSeriesAnalysis,
        chiSquareAnalysis,
        outcomePercentages,
        countriesChart
      ] = await Promise.allSettled([
        this.getRepresentationOutcomes(customFilters),
        this.getTimeSeriesAnalysis(customFilters),
        this.getChiSquareAnalysis(customFilters),
        this.getOutcomePercentages(customFilters),
        this.getCountriesChart(customFilters)
      ]);

      return {
        representationOutcomes: representationOutcomes.status === 'fulfilled' ? representationOutcomes.value : null,
        timeSeriesAnalysis: timeSeriesAnalysis.status === 'fulfilled' ? timeSeriesAnalysis.value : null,
        chiSquareAnalysis: chiSquareAnalysis.status === 'fulfilled' ? chiSquareAnalysis.value : null,
        outcomePercentages: outcomePercentages.status === 'fulfilled' ? outcomePercentages.value : null,
        countriesChart: countriesChart.status === 'fulfilled' ? countriesChart.value : null,
        errors: [
          ...(representationOutcomes.status === 'rejected' ? [representationOutcomes.reason] : []),
          ...(timeSeriesAnalysis.status === 'rejected' ? [timeSeriesAnalysis.reason] : []),
          ...(chiSquareAnalysis.status === 'rejected' ? [chiSquareAnalysis.reason] : []),
          ...(outcomePercentages.status === 'rejected' ? [outcomePercentages.reason] : []),
          ...(countriesChart.status === 'rejected' ? [countriesChart.reason] : [])
        ]
      };
    } catch (error) {
      console.error('Error loading chart data:', error);
      throw error;
    }
  }

  /**
   * Health check
   */
  async healthCheck() {
    const url = `${API_BASE_URL}/health`;
    return this.fetchWithRetry(url, {}, 0); // No retries for health check
  }
}

// Create singleton instance
export const apiService = new ApiService();

// Export the class for testing
export default ApiService;
