/**
 * Filter Service for managing filter options and state
 * Handles communication with the new /api/meta/options endpoint
 */
import { API_BASE_URL } from '$lib/config.js';

// Default filter state
const DEFAULT_FILTERS = {
  time_period: 'all',
  representation: 'all',
  case_type: 'all'
};

class FilterService {
  constructor() {
    this.filters = { ...DEFAULT_FILTERS };
    this.availableOptions = null;
    this.listeners = new Set();
  }

  /**
   * Load available filter options from the API
   */
  async loadFilterOptions() {
    try {
      const response = await fetch(`${API_BASE_URL}/meta/options`);
      if (!response.ok) {
        throw new Error(`Failed to load filter options: ${response.statusText}`);
      }
      
      const data = await response.json();
      this.availableOptions = data.options;
      
      // Notify listeners
      this.notifyListeners();
      
      return this.availableOptions;
    } catch (error) {
      console.error('Error loading filter options:', error);
      
      // Fallback to default options
      this.availableOptions = {
        time_period: ['all', 'trump1', 'biden', 'trump2'],
        representation: ['all', 'represented', 'unrepresented'],
        case_type: ['all']
      };
      
      return this.availableOptions;
    }
  }

  /**
   * Get current filter state
   */
  getFilters() {
    return { ...this.filters };
  }

  /**
   * Update a specific filter
   */
  setFilter(filterKey, value) {
    if (filterKey in this.filters && this.filters[filterKey] !== value) {
      this.filters[filterKey] = value;
      this.notifyListeners();
    }
  }

  /**
   * Update multiple filters at once
   */
  setFilters(newFilters) {
    let changed = false;
    
    for (const [key, value] of Object.entries(newFilters)) {
      if (key in this.filters && this.filters[key] !== value) {
        this.filters[key] = value;
        changed = true;
      }
    }
    
    if (changed) {
      this.notifyListeners();
    }
  }

  /**
   * Reset all filters to default values
   */
  clearFilters() {
    this.filters = { ...DEFAULT_FILTERS };
    this.notifyListeners();
  }

  /**
   * Get available options for all filters
   */
  getAvailableOptions() {
    return this.availableOptions;
  }

  /**
   * Convert filters to URL query parameters
   */
  toQueryParams() {
    const params = new URLSearchParams();
    
    for (const [key, value] of Object.entries(this.filters)) {
      if (value !== 'all') {
        params.append(key, value);
      }
    }
    
    return params.toString();
  }

  /**
   * Load filters from URL query parameters
   */
  fromQueryParams(searchParams) {
    const newFilters = { ...DEFAULT_FILTERS };
    
    // Support both snake_case and camelCase
    const paramMap = {
      'time_period': ['time_period', 'timePeriod'],
      'representation': ['representation'],
      'case_type': ['case_type', 'caseType']
    };
    
    for (const [filterKey, paramNames] of Object.entries(paramMap)) {
      for (const paramName of paramNames) {
        const value = searchParams.get(paramName);
        if (value && filterKey in newFilters) {
          newFilters[filterKey] = value;
          break;
        }
      }
    }
    
    this.setFilters(newFilters);
  }

  /**
   * Subscribe to filter changes
   */
  subscribe(callback) {
    this.listeners.add(callback);
    
    // Return unsubscribe function
    return () => {
      this.listeners.delete(callback);
    };
  }

  /**
   * Notify all listeners of filter changes
   */
  notifyListeners() {
    this.listeners.forEach(callback => {
      try {
        callback(this.getFilters(), this.availableOptions);
      } catch (error) {
        console.error('Error in filter listener:', error);
      }
    });
  }

  /**
   * Get display labels for filter values
   */
  getFilterLabels() {
    return {
      time_period: {
        all: 'All Years (2018-2025)',
        trump1: 'Trump I Era (2018-2020)',
        biden: 'Biden Era (2021-2024)',
        trump2: 'Trump II Era (2025+)'
      },
      representation: {
        all: 'All Cases',
        represented: 'With Legal Representation',
        unrepresented: 'Without Representation'
      },
      case_type: {
        all: 'All Types'
        // Additional case types will be added dynamically
      }
    };
  }

  /**
   * Get the display label for a specific filter value
   */
  getFilterLabel(filterType, value) {
    const labels = this.getFilterLabels();
    const typeLabels = labels[filterType];
    return typeLabels?.[value] || value;
  }

  /**
   * Check if any filters are active (not default)
   */
  hasActiveFilters() {
    return Object.entries(this.filters).some(([key, value]) => DEFAULT_FILTERS[key] !== value);
  }

  /**
   * Get summary of active filters for display
   */
  getActiveFiltersSummary() {
    const active = [];
    const labels = this.getFilterLabels();
    
    for (const [key, value] of Object.entries(this.filters)) {
      if (DEFAULT_FILTERS[key] !== value) {
        const typeLabels = labels[key];
        const label = typeLabels?.[value] || value;
        active.push({
          type: key,
          value: value,
          label: label
        });
      }
    }
    
    return active;
  }
}

// Create singleton instance
export const filterService = new FilterService();

// Export the class for testing
export default FilterService;
