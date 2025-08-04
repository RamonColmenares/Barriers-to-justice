<script>
  import { onMount, onDestroy } from 'svelte';
  import { filterService } from '$lib/services/filterService.js';

  // Props
  export let showTitle = true;
  export let layout = 'horizontal'; // 'horizontal' | 'vertical'
  export let onFilterChange = null; // Optional callback

  // State
  let filters = filterService.getFilters();
  let availableOptions = null;
  let isLoading = true;
  let debounceTimeout = null;

  // Unsubscribe function
  let unsubscribe = null;

  onMount(async () => {
    // Load filter options from API
    await filterService.loadFilterOptions();
    
    // Subscribe to filter changes with debounce
    unsubscribe = filterService.subscribe((newFilters, options) => {
      filters = newFilters;
      availableOptions = options;
      isLoading = false;
      
      // Debounce the callback to prevent multiple rapid calls
      if (onFilterChange) {
        if (debounceTimeout) {
          clearTimeout(debounceTimeout);
        }
        debounceTimeout = setTimeout(() => {
          onFilterChange(newFilters);
        }, 300); // 300ms debounce
      }
    });
    
    // Initial state
    filters = filterService.getFilters();
    availableOptions = filterService.getAvailableOptions();
    isLoading = false;
  });

  onDestroy(() => {
    if (unsubscribe) {
      unsubscribe();
    }
    if (debounceTimeout) {
      clearTimeout(debounceTimeout);
    }
  });

  // Handle filter changes
  function handleFilterChange(filterType, value) {
    filterService.setFilter(filterType, value);
  }

  function clearAllFilters() {
    filterService.clearFilters();
  }

  function updateCharts() {
    if (onFilterChange) {
      onFilterChange(filters);
    }
  }

  // Get display label for filter value
  function getDisplayLabel(filterType, value) {
    const labels = filterService.getFilterLabels();
    const typeLabels = labels[filterType];
    return typeLabels?.[value] || value;
  }

  // Check if we have active filters
  $: hasActiveFilters = filterService.hasActiveFilters();
</script>

<div class="filter-component">
  {#if showTitle}
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-[var(--color-primary)]">Filter Data</h3>
      {#if hasActiveFilters}
        <button 
          on:click={clearAllFilters}
          class="text-sm text-[var(--color-secondary)] hover:text-[var(--color-primary)] transition-colors"
        >
          Clear All Filters
        </button>
      {/if}
    </div>
  {/if}

  {#if isLoading}
    <div class="flex items-center justify-center p-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-[var(--color-primary)]"></div>
      <span class="ml-3 text-[var(--color-text-secondary)]">Loading filter options...</span>
    </div>
  {:else}
    <div class="filter-controls {layout === 'horizontal' ? 'grid grid-cols-1 md:grid-cols-4 gap-4' : 'space-y-4'}">
      <!-- Time Period Filter -->
      <div class="filter-group">
        <label for="timePeriodFilter" class="block text-sm font-medium text-[var(--color-primary)] mb-2">
          Time Period
        </label>
        <select 
          id="timePeriodFilter" 
          bind:value={filters.time_period}
          on:change={(e) => handleFilterChange('time_period', e.target.value)}
          class="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent transition-colors"
        >
          {#if availableOptions?.time_period}
            {#each availableOptions.time_period as option}
              <option value={option}>
                {getDisplayLabel('time_period', option)}
              </option>
            {/each}
          {/if}
        </select>
      </div>

      <!-- Representation Filter -->
      <div class="filter-group">
        <label for="representationFilter" class="block text-sm font-medium text-[var(--color-primary)] mb-2">
          Representation Status
        </label>
        <select 
          id="representationFilter" 
          bind:value={filters.representation}
          on:change={(e) => handleFilterChange('representation', e.target.value)}
          class="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent transition-colors"
        >
          {#if availableOptions?.representation}
            {#each availableOptions.representation as option}
              <option value={option}>
                {getDisplayLabel('representation', option)}
              </option>
            {/each}
          {/if}
        </select>
      </div>

      <!-- Case Type Filter -->
      <div class="filter-group">
        <label for="caseTypeFilter" class="block text-sm font-medium text-[var(--color-primary)] mb-2">
          Case Type
        </label>
        <select 
          id="caseTypeFilter" 
          bind:value={filters.case_type}
          on:change={(e) => handleFilterChange('case_type', e.target.value)}
          class="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent transition-colors"
        >
          {#if availableOptions?.case_type}
            {#each availableOptions.case_type as option}
              <option value={option}>
                {option === 'all' ? 'All Types' : option}
              </option>
            {/each}
          {/if}
        </select>
      </div>

      <!-- Action Buttons -->
      <div class="filter-actions {layout === 'horizontal' ? 'flex items-end' : ''}">
        {#if layout === 'horizontal'}
          <div class="w-full space-y-2">
            <button 
              on:click={updateCharts}
              class="w-full bg-[var(--color-primary)] text-white px-4 py-2 rounded-md hover:bg-[var(--color-secondary)] transition-colors font-medium"
            >
              Update Charts
            </button>
            {#if hasActiveFilters}
              <button 
                on:click={clearAllFilters}
                class="w-full bg-gray-500 text-white px-4 py-2 rounded-md hover:bg-gray-600 transition-colors text-sm"
              >
                Clear Filters
              </button>
            {/if}
          </div>
        {:else}
          <div class="flex gap-2">
            <button 
              on:click={updateCharts}
              class="flex-1 bg-[var(--color-primary)] text-white px-4 py-2 rounded-md hover:bg-[var(--color-secondary)] transition-colors font-medium"
            >
              Update Charts
            </button>
            {#if hasActiveFilters}
              <button 
                on:click={clearAllFilters}
                class="bg-gray-500 text-white px-4 py-2 rounded-md hover:bg-gray-600 transition-colors"
              >
                Clear
              </button>
            {/if}
          </div>
        {/if}
      </div>
    </div>

    <!-- Active Filters Summary -->
    {#if hasActiveFilters}
      <div class="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <p class="text-sm text-blue-800 font-medium mb-2">Active Filters:</p>
        <div class="flex flex-wrap gap-2">
          {#each filterService.getActiveFiltersSummary() as activeFilter}
            <span class="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
              {activeFilter.label}
              <button 
                on:click={() => handleFilterChange(activeFilter.type, 'all')}
                class="hover:bg-blue-200 rounded-full p-0.5 transition-colors"
                title="Remove filter"
              >
                <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
                </svg>
              </button>
            </span>
          {/each}
        </div>
      </div>
    {/if}
  {/if}
</div>

<style>
  .filter-component {
    background: white;
    border-radius: 0.75rem;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    padding: 1.5rem;
    margin-bottom: 2rem;
  }

  .filter-group select {
    background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e");
    background-position: right 0.5rem center;
    background-repeat: no-repeat;
    background-size: 1.5em 1.5em;
    padding-right: 2.5rem;
  }

  .filter-group select:focus {
    outline: none;
  }
</style>
