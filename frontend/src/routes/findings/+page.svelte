<!-- Findings Page with Dynamic Charts -->
<svelte:head>
  <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</svelte:head>

<script>
  import { onMount } from 'svelte';
  import { browser } from '$app/environment';
  import { apiService } from '$lib/services/apiService.js';
  import FilterComponent from '$lib/FilterComponent.svelte';

  // Estado general
  let caseSummary = null;
  let isLoading = true;
  let error = null;

  // Filtros vigentes
  let currentFilters = null;

  // Estado por gráfico (para spinners/errores si quieres mostrarlos)
  let chartStates = {
    representationOutcomes: { loading: false, error: null },
    timeSeriesAnalysis:    { loading: false, error: null },
    chiSquareAnalysis:     { loading: false, error: null },
    outcomePercentages:    { loading: false, error: null },
    countriesChart:        { loading: false, error: null }
  };

  // Prevent duplicate calls
  let isLoadingCharts = false;
  let lastFilterHash = null;

  onMount(() => {
    loadDashboard();
  });

  async function loadDashboard() {
    if (!browser) return;
    isLoading = true;
    error = null;
    
    // Show initial loading states
    showChartLoading('representationChart', 'Initializing Success Rates...');
    showChartLoading('timelineChart', 'Initializing Timeline Trends...');
    showChartLoading('demographicsChart', 'Initializing Outcome Percentages...');
    showChartLoading('chiSquareResults', 'Initializing Statistical Analysis...');
    showChartLoading('countriesChart', 'Initializing Countries Data...');
    
    try {
      await loadSummaryData();
      await loadAllCharts(currentFilters);
      finalizeCharts();
    } catch (err) {
      console.error('Error loading dashboard:', err);
      error = err?.message ?? 'Unexpected error';
    } finally {
      isLoading = false;
    }
  }

  async function loadSummaryData() {
    try {
      caseSummary = await apiService.getBasicStatistics();
      updateKeyStats();
    } catch (err) {
      console.error('Summary data error:', err);
      // When API fails, show large hyphens instead of fallback data
      caseSummary = null;
      showPlaceholderStats();
    }
  }

  function showPlaceholderStats() {
    if (!browser) return;

    const representationStat = document.getElementById('stat-representation');
    const noRepresentationStat = document.getElementById('stat-no-representation');
    const casesStat = document.getElementById('stat-cases');
    const timespanStat = document.getElementById('stat-timespan');

    // Use large hyphens as placeholders when API doesn't work
    if (representationStat) representationStat.textContent = '—';
    if (noRepresentationStat) noRepresentationStat.textContent = '—';
    if (casesStat) casesStat.textContent = '—';
    if (timespanStat) timespanStat.textContent = '—';
  }

  // Cambio de filtros (compatibilidad: por prop o por evento)
  async function handleFilterChange(newFilters) {
    // Create hash of filters to prevent duplicate calls
    const filterHash = JSON.stringify(newFilters);
    if (filterHash === lastFilterHash) {
      return;
    }
    
    // If already loading, wait a bit and try again
    if (isLoadingCharts) {
      setTimeout(() => handleFilterChange(newFilters), 100);
      return;
    }
    
    lastFilterHash = filterHash;
    currentFilters = newFilters;
    isLoadingCharts = true;
    
    // Set loading state for each chart and show loading UI
    Object.keys(chartStates).forEach(k => {
      chartStates[k].loading = true;
      chartStates[k].error = null;
    });
    
    // Show loading state in each chart
    showChartLoading('representationChart', 'Loading Success Rates...');
    showChartLoading('timelineChart', 'Loading Timeline Trends...');
    showChartLoading('demographicsChart', 'Loading Outcome Percentages...');
    showChartLoading('chiSquareResults', 'Loading Statistical Analysis...');
    showChartLoading('countriesChart', 'Loading Countries Data...');
    
    try {
      await loadAllCharts(currentFilters);
    } catch (err) {
      console.error('Error updating charts with filters:', err);
      Object.keys(chartStates).forEach(k => {
        chartStates[k].loading = false;
        chartStates[k].error = err?.message ?? 'Error';
      });
      
      // Show error state for all charts
      showChartError('representationChart', 'Failed to load Success Rates chart');
      showChartError('timelineChart', 'Failed to load Timeline Trends chart');
      showChartError('demographicsChart', 'Failed to load Outcome Percentages chart');
      showChartError('chiSquareResults', 'Failed to load Statistical Analysis');
      showChartError('countriesChart', 'Failed to load Countries chart');
    } finally {
      isLoadingCharts = false;
    }
  }

  async function loadAllCharts(customFilters = null) {
    try {
      const data = await apiService.getAllChartData(customFilters);
      
      // Handle each chart individually with proper error states
      if (data?.representationOutcomes && !data.representationOutcomes.error) {
        renderRepresentationChart(data.representationOutcomes);
        chartStates.representationOutcomes.loading = false;
        chartStates.representationOutcomes.error = null;
      } else {
        chartStates.representationOutcomes.loading = false;
        chartStates.representationOutcomes.error = data?.representationOutcomes?.error || 'Failed to load chart';
        showChartError('representationChart', 'Failed to load Success Rates chart');
      }
      
      if (data?.timeSeriesAnalysis && !data.timeSeriesAnalysis.error) {
        renderTimeSeriesChart(data.timeSeriesAnalysis);
        chartStates.timeSeriesAnalysis.loading = false;
        chartStates.timeSeriesAnalysis.error = null;
      } else {
        chartStates.timeSeriesAnalysis.loading = false;
        chartStates.timeSeriesAnalysis.error = data?.timeSeriesAnalysis?.error || 'Failed to load chart';
        showChartError('timelineChart', 'Failed to load Timeline Trends chart');
      }
      
      if (data?.chiSquareAnalysis && !data.chiSquareAnalysis.error) {
        renderChiSquareResults(data.chiSquareAnalysis);
        chartStates.chiSquareAnalysis.loading = false;
        chartStates.chiSquareAnalysis.error = null;
      } else {
        chartStates.chiSquareAnalysis.loading = false;
        chartStates.chiSquareAnalysis.error = data?.chiSquareAnalysis?.error || 'Failed to load analysis';
        showChartError('chiSquareResults', 'Failed to load Statistical Analysis');
      }
      
      if (data?.outcomePercentages && !data.outcomePercentages.error) {
        renderOutcomePercentagesChart(data.outcomePercentages);
        chartStates.outcomePercentages.loading = false;
        chartStates.outcomePercentages.error = null;
      } else {
        chartStates.outcomePercentages.loading = false;
        chartStates.outcomePercentages.error = data?.outcomePercentages?.error || 'Failed to load chart';
        showChartError('demographicsChart', 'Failed to load Outcome Percentages chart');
      }
      
      if (data?.countriesChart && !data.countriesChart.error) {
        renderCountriesChart(data.countriesChart);
        chartStates.countriesChart.loading = false;
        chartStates.countriesChart.error = null;
      } else {
        chartStates.countriesChart.loading = false;
        chartStates.countriesChart.error = data?.countriesChart?.error || 'Failed to load chart';
        showChartError('countriesChart', 'Failed to load Countries chart');
      }
      
      if (data?.errors?.length) {
        console.warn('Some charts failed:', data.errors);
      }
    } catch (err) {
      console.error('Error loadAllCharts:', err);
      // Set all charts to error state and show error UI
      Object.keys(chartStates).forEach(k => {
        chartStates[k].loading = false;
        chartStates[k].error = err?.message ?? 'Network error';
      });
      
      // Show error state for all charts
      showChartError('representationChart', 'Failed to load Success Rates chart');
      showChartError('timelineChart', 'Failed to load Timeline Trends chart');
      showChartError('demographicsChart', 'Failed to load Outcome Percentages chart');
      showChartError('chiSquareResults', 'Failed to load Statistical Analysis');
      showChartError('countriesChart', 'Failed to load Countries chart');
      
      throw err;
    }
  }

  function updateKeyStats() {
    if (!browser || !caseSummary) return;

    const representationStat = document.getElementById('stat-representation');
    const noRepresentationStat = document.getElementById('stat-no-representation');
    const casesStat = document.getElementById('stat-cases');
    const timespanStat = document.getElementById('stat-timespan');

    if (representationStat && caseSummary.success_with_representation != null) {
      representationStat.textContent = `${Number(caseSummary.success_with_representation).toFixed(1)}%`;
    } else if (representationStat) {
      representationStat.textContent = '—';
    }
    
    if (noRepresentationStat && caseSummary.success_without_representation != null) {
      noRepresentationStat.textContent = `${Number(caseSummary.success_without_representation).toFixed(1)}%`;
    } else if (noRepresentationStat) {
      noRepresentationStat.textContent = '—';
    }
    
    if (casesStat && caseSummary.total_cases_analyzed != null) {
      const n = Number(caseSummary.total_cases_analyzed);
      casesStat.textContent =
        n >= 1_000_000 ? `${(n / 1_000_000).toFixed(1)}M+` :
        n >= 1_000 ? `${(n / 1_000).toFixed(1)}K+` :
        n.toLocaleString();
    } else if (casesStat) {
      casesStat.textContent = '—';
    }
    
    if (timespanStat) {
      timespanStat.textContent = '7';
    }
  }

  // --- Plot helpers ---
  const basePlotConfig = {
    responsive: true,
    displayModeBar: false,
    scrollZoom: false
  };

  const baseLayout = {
    autosize: true,
    margin: { t: 40, b: 40, l: 40, r: 40 },
    font: { size: 12 },
    showlegend: true,
    legend: {
      orientation: "h",
      y: -0.2,
      x: 0.5,
      xanchor: 'center'
    }
  };

  /**
   * Safely trigger a Plotly resize on the chart inside the container `id`.
   * We look for the first element that *actually* has the `js-plotly-plot`
   * class (Plotly adds it to the div passed to `newPlot`).  
   * This prevents early exits when the container itself does not yet hold
   * the Plotly instance and greatly improves responsiveness on window /
   * parent resizes.
   */
  function safeResizeById(id) {
    if (!browser || !window.Plotly || !window.Plotly.Plots) return;

    const container = document.getElementById(id);
    if (!container) return;

    // The real plot element is either the container itself (after newPlot)
    // or a child div with the class `js-plotly-plot`
    const plotEl = container.classList.contains('js-plotly-plot')
      ? container
      : container.querySelector('.js-plotly-plot');

    if (!plotEl) return;

    try {
      window.Plotly.Plots.resize(plotEl);
    } catch (err) {
      console.warn('Failed to resize chart:', id, err);
    }
  }

  function showChartError(elementId, message) {
    const el = document.getElementById(elementId);
    if (!el) return;
    
    el.innerHTML = `
      <div class="flex flex-col items-center justify-center h-full bg-blue-50 rounded-lg border border-blue-200 p-8">
        <div class="text-blue-500 mb-6">
          <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
        </div>
        <div class="text-center mb-6">
          <h4 class="text-gray-700 font-medium mb-3">Chart temporarily unavailable</h4>
          <p class="text-gray-600 text-sm">We're having trouble loading this visualization. No worries - it happens sometimes!</p>
        </div>
        <button onclick="window.location.reload()" class="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm">
          Try again
        </button>
      </div>
    `;
  }

  function showChartLoading(elementId, message = 'Loading...') {
    const el = document.getElementById(elementId);
    if (!el) return;
    
    el.innerHTML = `
      <div class="flex flex-col items-center justify-center h-full bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-8">
        <div class="relative mb-6">
          <div class="w-16 h-16 border-4 border-blue-200 border-t-blue-500 rounded-full animate-spin"></div>
          <div class="absolute inset-0 w-16 h-16 border-4 border-transparent border-r-indigo-300 rounded-full animate-pulse"></div>
        </div>
        <div class="text-center mb-4">
          <p class="text-gray-700 font-medium mb-2">${message}</p>
          <p class="text-gray-500 text-sm">Preparing your visualization...</p>
        </div>
        <div class="flex space-x-1">
          <div class="w-2 h-2 bg-blue-400 rounded-full animate-pulse" style="animation-delay: 0s;"></div>
          <div class="w-2 h-2 bg-blue-400 rounded-full animate-pulse" style="animation-delay: 0.2s;"></div>
          <div class="w-2 h-2 bg-blue-400 rounded-full animate-pulse" style="animation-delay: 0.4s;"></div>
        </div>
      </div>
    `;
  }

  function renderRepresentationChart(payload) {
    try {
      const el = document.getElementById('representationChart');
      if (!browser || !window.Plotly || !payload || !el) return;
      
      // Clear any existing content (including loading messages)
      el.innerHTML = '';
      
      // Merge responsive layout settings
      const layout = { 
        ...baseLayout, 
        ...payload.layout, 
        autosize: true,
        height: undefined // Let container control height
      };
      
      window.Plotly.newPlot(el, payload.data, layout, basePlotConfig);
      chartStates.representationOutcomes.loading = false;
      
      // Force resize after render
      setTimeout(() => safeResizeById('representationChart'), 100);
    } catch (err) {
      console.error('renderRepresentationChart:', err);
      chartStates.representationOutcomes.loading = false;
      chartStates.representationOutcomes.error = err?.message ?? 'Error';
    }
  }

  function renderTimeSeriesChart(payload) {
    try {
      const el = document.getElementById('timelineChart');
      if (!browser || !window.Plotly || !payload || !el) return;
      
      // Clear any existing content (including loading messages)
      el.innerHTML = '';
      
      // Merge responsive layout settings
      const layout = { 
        ...baseLayout, 
        ...payload.layout, 
        autosize: true,
        height: undefined // Let container control height
      };
      
      window.Plotly.newPlot(el, payload.data, layout, basePlotConfig);
      chartStates.timeSeriesAnalysis.loading = false;
      
      // Force resize after render
      setTimeout(() => safeResizeById('timelineChart'), 100);
    } catch (err) {
      console.error('renderTimeSeriesChart:', err);
      chartStates.timeSeriesAnalysis.loading = false;
      chartStates.timeSeriesAnalysis.error = err?.message ?? 'Error';
    }
  }

  function renderOutcomePercentagesChart(payload) {
    try {
      const el = document.getElementById('demographicsChart');
      if (!browser || !window.Plotly || !payload || !el) return;
      
      // Clear any existing content (including loading messages)
      el.innerHTML = '';
      
      // Merge responsive layout settings
      const layout = { 
        ...baseLayout, 
        ...payload.layout, 
        autosize: true,
        height: undefined // Let container control height
      };
      
      window.Plotly.newPlot(el, payload.data, layout, basePlotConfig);
      chartStates.outcomePercentages.loading = false;
      
      // Force resize after render
      setTimeout(() => safeResizeById('demographicsChart'), 100);
    } catch (err) {
      console.error('renderOutcomePercentagesChart:', err);
      chartStates.outcomePercentages.loading = false;
      chartStates.outcomePercentages.error = err?.message ?? 'Error';
    }
  }

  function renderCountriesChart(payload) {
    try {
      const el = document.getElementById('countriesChart');
      if (!browser || !window.Plotly || !payload || !el) return;
      
      // Clear any existing content (including loading messages)
      el.innerHTML = '';
      
      // Merge responsive layout settings
      const layout = { 
        ...baseLayout, 
        ...payload.layout, 
        autosize: true,
        height: undefined // Let container control height
      };
      
      window.Plotly.newPlot(el, payload.data, layout, basePlotConfig);
      chartStates.countriesChart.loading = false;
      
      // Force resize after render
      setTimeout(() => safeResizeById('countriesChart'), 100);
    } catch (err) {
      console.error('renderCountriesChart:', err);
      chartStates.countriesChart.loading = false;
      chartStates.countriesChart.error = err?.message ?? 'Error';
    }
  }

  function renderChiSquareResults(data) {
    try {
      const container = document.getElementById('chiSquareResults');
      if (!container) return;

      const safe = (v) => (v == null ? '—' : v);

      // Clear any existing content (including loading messages)
      container.innerHTML = `
        <div class="space-y-6">
          <!-- Representation by Time Period -->
          <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-200">
            <div class="flex items-center justify-between mb-4">
              <h5 class="text-lg font-bold text-blue-800">👥 Representation by Time Period</h5>
              <span class="px-3 py-1 rounded-full text-sm font-medium ${data?.representation_by_era?.significant ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-600'}">
                ${data?.representation_by_era?.significant ? '✓ Significant' : '✗ Not Significant'}
              </span>
            </div>
            ${data?.representation_by_era ? `
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div class="bg-white p-3 rounded-lg text-center">
                  <div class="font-bold text-lg text-blue-600">${safe(data.representation_by_era.chi_square)}</div>
                  <div class="text-gray-500">Chi-square</div>
                </div>
                <div class="bg-white p-3 rounded-lg text-center">
                  <div class="font-bold text-lg text-blue-600">${safe(Number(data.representation_by_era.p_value).toExponential(2))}</div>
                  <div class="text-gray-500">p-value</div>
                </div>
                <div class="bg-white p-3 rounded-lg text-center">
                  <div class="font-bold text-lg text-blue-600">${safe(data.representation_by_era.cramer_v)}</div>
                  <div class="text-gray-500">Cramer's V</div>
                </div>
                <div class="bg-white p-3 rounded-lg text-center">
                  <div class="font-bold text-lg ${data.representation_by_era.significant ? 'text-red-600' : 'text-gray-400'}">${data.representation_by_era.significant ? 'YES' : 'NO'}</div>
                  <div class="text-gray-500">Significant</div>
                </div>
              </div>
            ` : '<p class="text-gray-500">No data available</p>'}
          </div>

          <!-- Outcomes by Representation -->
          <div class="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-6 border border-green-200">
            <div class="flex items-center justify-between mb-4">
              <h5 class="text-lg font-bold text-green-800">⚖️ Outcomes by Representation</h5>
              <span class="px-3 py-1 rounded-full text-sm font-medium ${data?.outcomes_by_representation?.significant ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-600'}">
                ${data?.outcomes_by_representation?.significant ? '✓ Significant' : '✗ Not Significant'}
              </span>
            </div>
            ${data?.outcomes_by_representation ? `
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-4">
                <div class="bg-white p-3 rounded-lg text-center">
                  <div class="font-bold text-lg text-green-600">${safe(data.outcomes_by_representation.chi_square)}</div>
                  <div class="text-gray-500">Chi-square</div>
                </div>
                <div class="bg-white p-3 rounded-lg text-center">
                  <div class="font-bold text-lg text-green-600">${safe(Number(data.outcomes_by_representation.p_value).toExponential(2))}</div>
                  <div class="text-gray-500">p-value</div>
                </div>
                <div class="bg-white p-3 rounded-lg text-center">
                  <div class="font-bold text-lg text-green-600">${safe(data.outcomes_by_representation.cramer_v)}</div>
                  <div class="text-gray-500">Cramer's V</div>
                </div>
                <div class="bg-white p-3 rounded-lg text-center">
                  <div class="font-bold text-lg text-green-600">${safe(data.outcomes_by_representation.odds_ratio)}x</div>
                  <div class="text-gray-500">Odds Ratio</div>
                </div>
              </div>
              <div class="bg-green-100 border-l-4 border-green-500 p-4 rounded-r-lg">
                <p class="text-green-800 font-medium">
                  Juveniles with legal representation are <strong>${safe(data.outcomes_by_representation.odds_ratio)}x more likely</strong> to receive favorable outcomes.
                </p>
              </div>
            ` : '<p class="text-gray-500">No data available</p>'}
          </div>

          <div class="text-xs text-gray-500 text-center bg-gray-50 p-3 rounded-lg">
            <strong>Note:</strong> p &lt; 0.05 → significant. Cramer's V: 0.1 (small), 0.3 (medium), 0.5 (large).
          </div>
        </div>
      `;

      chartStates.chiSquareAnalysis.loading = false;
    } catch (err) {
      console.error('renderChiSquareResults:', err);
      chartStates.chiSquareAnalysis.loading = false;
      chartStates.chiSquareAnalysis.error = err?.message ?? 'Error';
    }
  }

  // Resize reactivo
  function setupChartResizing() {
    if (!browser || !window.ResizeObserver) return;
    
    const chartIds = ['representationChart', 'timelineChart', 'demographicsChart', 'countriesChart'];
    
    chartIds.forEach((id) => {
      const container = document.getElementById(id);
      if (!container) return;
      
      // Use ResizeObserver for better responsiveness
      const ro = new ResizeObserver((entries) => {
        for (let entry of entries) {
          if (entry.target.id === id) {
            // Debounce resize calls
            clearTimeout(window[`resize_${id}`]);
            window[`resize_${id}`] = setTimeout(() => {
              safeResizeById(id);
            }, 100);
          }
        }
      });
      
      ro.observe(container);
    });
    
    // Window resize backup
    let resizeTimeout;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(() => {
        chartIds.forEach(safeResizeById);
      }, 250);
    });
  }

  function finalizeCharts() {
    setupChartResizing();
    setTimeout(() => {
      ['representationChart', 'timelineChart', 'demographicsChart', 'countriesChart'].forEach(safeResizeById);
    }, 500);
  }

  // Reintento manual
  async function retryDataLoad() {
    try {
      // Clear cache to force fresh data
      apiService.clearCache();
      lastFilterHash = null;
      await loadDashboard();
    } catch (err) {
      console.error('Retry failed:', err);
      error = 'Failed to reload data. Please check your connection.';
    }
  }
</script>

<main class="page-content">
  <!-- Hero -->
  <section class="relative bg-gradient-to-r from-[var(--color-secondary)] to-[var(--color-primary)] text-white py-20">
    <div class="mx-auto max-w-7xl px-6 lg:px-8">
      <div class="text-center">
        <h1 class="text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl mb-6">Research Findings</h1>
        <p class="text-xl leading-8 text-white/90 max-w-4xl mx-auto">
          Interactive dashboards and visualizations revealing the impact of immigration policies on juvenile case outcomes
        </p>
      </div>
    </div>
  </section>

  <!-- Key Findings Overview -->
  <section class="py-16 bg-white">
    <div class="mx-auto max-w-7xl px-6 lg:px-8">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-8 mb-16">
        <div class="bg-gradient-to-br from-[var(--color-accent)] to-[var(--color-secondary)] rounded-2xl p-6 text-white text-center">
          <div class="text-4xl font-bold mb-2" id="stat-representation">—</div>
          <div class="text-sm opacity-90">Success with representation</div>
        </div>
        <div class="bg-gradient-to-br from-[var(--color-primary)] to-[var(--color-secondary)] rounded-2xl p-6 text-white text-center">
          <div class="text-4xl font-bold mb-2" id="stat-no-representation">—</div>
          <div class="text-sm opacity-90">Success without representation</div>
        </div>
        <div class="bg-gradient-to-br from-[var(--color-secondary)] to-[var(--color-accent)] rounded-2xl p-6 text-white text-center">
          <div class="text-4xl font-bold mb-2" id="stat-cases">—</div>
          <div class="text-sm opacity-90">Cases analyzed</div>
        </div>
        <div class="bg-gradient-to-br from-[var(--color-primary)] to-[var(--color-accent)] rounded-2xl p-6 text-white text-center">
          <div class="text-4xl font-bold mb-2" id="stat-timespan">-</div>
          <div class="text-sm opacity-90">Years of data</div>
        </div>
      </div>
    </div>
  </section>

  <!-- Interactive Dashboards -->
  <section class="py-16 bg-gradient-to-br from-[var(--color-background)] to-gray-50">
    <div class="mx-auto max-w-7xl px-6 lg:px-8">
      <div class="text-center mb-12">
        <h2 class="text-3xl font-bold tracking-tight text-[var(--color-primary)] sm:text-4xl mb-4">Interactive Data Visualizations</h2>
        <p class="text-lg text-[var(--color-text-secondary)] max-w-3xl mx-auto">
          Explore our findings through dynamic charts and graphs that reveal patterns in juvenile immigration case outcomes
        </p>
      </div>

      <!-- Filtros -->
      <!-- Soporta prop y/o evento -->
      <FilterComponent onFilterChange={handleFilterChange} on:filterChange={(e) => handleFilterChange(e.detail)} />

      <!-- Chart Grid -->
      <div class="grid grid-cols-1 gap-8">
        <!-- Outcome Percentages Chart -->
        <div class="bg-white rounded-2xl shadow-xl p-8">
          <h3 class="text-xl font-bold text-[var(--color-primary)] mb-6">Outcome Percentages</h3>
          <div class="w-full h-[500px] relative" id="demographicsChart">
            <div class="flex flex-col items-center justify-center h-full bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-8">
              <div class="relative mb-6">
                <div class="w-16 h-16 border-4 border-blue-200 border-t-blue-500 rounded-full animate-spin"></div>
                <div class="absolute inset-0 w-16 h-16 border-4 border-transparent border-r-indigo-300 rounded-full animate-pulse"></div>
              </div>
              <div class="text-center mb-4">
                <p class="text-gray-700 font-medium mb-2">Loading Outcome Percentages...</p>
                <p class="text-gray-500 text-sm">Preparing your visualization...</p>
              </div>
              <div class="flex space-x-1">
                <div class="w-2 h-2 bg-blue-400 rounded-full animate-pulse" style="animation-delay: 0s;"></div>
                <div class="w-2 h-2 bg-blue-400 rounded-full animate-pulse" style="animation-delay: 0.2s;"></div>
                <div class="w-2 h-2 bg-blue-400 rounded-full animate-pulse" style="animation-delay: 0.4s;"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Timeline Trends Chart -->
        <div class="bg-white rounded-2xl shadow-xl p-8">
          <h3 class="text-xl font-bold text-[var(--color-primary)] mb-6">Trends Over Time</h3>
          <div class="w-full h-[500px] relative" id="timelineChart">
            <div class="flex flex-col items-center justify-center h-full bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-8">
              <div class="relative mb-6">
                <div class="w-16 h-16 border-4 border-blue-200 border-t-blue-500 rounded-full animate-spin"></div>
                <div class="absolute inset-0 w-16 h-16 border-4 border-transparent border-r-indigo-300 rounded-full animate-pulse"></div>
              </div>
              <div class="text-center mb-4">
                <p class="text-gray-700 font-medium mb-2">Loading Timeline Trends...</p>
                <p class="text-gray-500 text-sm">Preparing your visualization...</p>
              </div>
              <div class="flex space-x-1">
                <div class="w-2 h-2 bg-blue-400 rounded-full animate-pulse" style="animation-delay: 0s;"></div>
                <div class="w-2 h-2 bg-blue-400 rounded-full animate-pulse" style="animation-delay: 0.2s;"></div>
                <div class="w-2 h-2 bg-blue-400 rounded-full animate-pulse" style="animation-delay: 0.4s;"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Chi-square Results (nuevo contenedor dedicado) -->
        <div class="bg-white rounded-2xl shadow-xl p-8">
          <h3 class="text-xl font-bold text-[var(--color-primary)] mb-6">Statistical Analysis (Chi-square)</h3>
          <div class="w-full min-h-[300px] relative" id="chiSquareResults">
            <div class="flex flex-col items-center justify-center h-full bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-8">
              <div class="relative mb-6">
                <div class="w-16 h-16 border-4 border-blue-200 border-t-blue-500 rounded-full animate-spin"></div>
                <div class="absolute inset-0 w-16 h-16 border-4 border-transparent border-r-indigo-300 rounded-full animate-pulse"></div>
              </div>
              <div class="text-center mb-4">
                <p class="text-gray-700 font-medium mb-2">Loading Statistical Analysis...</p>
                <p class="text-gray-500 text-sm">Preparing your visualization...</p>
              </div>
              <div class="flex space-x-1">
                <div class="w-2 h-2 bg-blue-400 rounded-full animate-pulse" style="animation-delay: 0s;"></div>
                <div class="w-2 h-2 bg-blue-400 rounded-full animate-pulse" style="animation-delay: 0.2s;"></div>
                <div class="w-2 h-2 bg-blue-400 rounded-full animate-pulse" style="animation-delay: 0.4s;"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Top Countries Chart -->
        <div class="bg-white rounded-2xl shadow-xl p-8">
          <h3 class="text-xl font-bold text-[var(--color-primary)] mb-6">Top Countries by Case Volume</h3>
          <div class="w-full h-[500px] relative" id="countriesChart">
            <div class="flex flex-col items-center justify-center h-full bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-8">
              <div class="relative mb-6">
                <div class="w-16 h-16 border-4 border-blue-200 border-t-blue-500 rounded-full animate-spin"></div>
                <div class="absolute inset-0 w-16 h-16 border-4 border-transparent border-r-indigo-300 rounded-full animate-pulse"></div>
              </div>
              <div class="text-center mb-4">
                <p class="text-gray-700 font-medium mb-2">Loading Countries Data...</p>
                <p class="text-gray-500 text-sm">Preparing your visualization...</p>
              </div>
              <div class="flex space-x-1">
                <div class="w-2 h-2 bg-blue-400 rounded-full animate-pulse" style="animation-delay: 0s;"></div>
                <div class="w-2 h-2 bg-blue-400 rounded-full animate-pulse" style="animation-delay: 0.2s;"></div>
                <div class="w-2 h-2 bg-blue-400 rounded-full animate-pulse" style="animation-delay: 0.4s;"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {#if error}
        <div class="text-center mt-8">
          <p class="text-red-600">{error}</p>
          <button on:click={retryDataLoad} class="mt-2 text-blue-600 hover:text-blue-800 text-sm">Retry</button>
        </div>
      {/if}
    </div>
  </section>

  <!-- Key Insights Section -->
  <section class="py-16 bg-white">
    <div class="mx-auto max-w-7xl px-6 lg:px-8">
      <h2 class="text-3xl font-bold tracking-tight text-[var(--color-primary)] sm:text-4xl text-center mb-12">Key Research Insights</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <div class="bg-gradient-to-br from-[var(--color-background)] to-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <h3 class="text-lg font-bold text-[var(--color-primary)] mb-3">Representation is Critical</h3>
          <p class="text-[var(--color-text-secondary)]">Juveniles with legal representation are far more likely to achieve favorable outcomes.</p>
        </div>
        <div class="bg-gradient-to-br from-[var(--color-background)] to-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <h3 class="text-lg font-bold text-[var(--color-primary)] mb-3">Policy Periods Matter</h3>
          <p class="text-[var(--color-text-secondary)]">Administrative periods show distinct patterns in processing times and outcomes.</p>
        </div>
        <div class="bg-gradient-to-br from-[var(--color-background)] to-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <h3 class="text-lg font-bold text-[var(--color-primary)] mb-3">Demographics Influence Outcomes</h3>
          <p class="text-[var(--color-text-secondary)]">Age and country of origin correlate with case outcomes, even controlling for representation.</p>
        </div>
      </div>
    </div>
  </section>
</main>

<style>
  /* Ensure Plotly charts are responsive */

  /* width rules untouched, only height rules removed */

  /* Chart containers */
  #demographicsChart,
  #timelineChart,
  #countriesChart {
    width: 100%;
    height: 500px;
    position: relative;
    overflow: hidden;
  }

  #chiSquareResults {
    width: 100%;
    min-height: 300px;
    position: relative;
  }

  /* Responsive adjustments */
  @media (max-width: 768px) {
    #demographicsChart,
    #timelineChart,
    #countriesChart {
      height: 400px;
    }
  }

  @media (max-width: 640px) {
    #demographicsChart,
    #timelineChart,
    #countriesChart {
      height: 350px;
    }
  }
</style>