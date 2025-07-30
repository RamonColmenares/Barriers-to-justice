<!-- Findings Page with Dynamic Charts -->
<svelte:head>
  <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</svelte:head>

<main class="page-content">
  <!-- Hero Section -->
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
        <div class="bg-gradient-to-br from-[var(--color-accent)] to-[var(--color-secondary)] rounded-2xl p-6 text-white text-center transform hover:scale-105 transition-transform duration-300">
          <div class="text-4xl font-bold mb-2" id="stat-representation">45.3%</div>
          <div class="text-sm opacity-90">Success with representation</div>
        </div>
        <div class="bg-gradient-to-br from-[var(--color-primary)] to-[var(--color-secondary)] rounded-2xl p-6 text-white text-center transform hover:scale-105 transition-transform duration-300">
          <div class="text-4xl font-bold mb-2" id="stat-no-representation">0.8%</div>
          <div class="text-sm opacity-90">Success without representation</div>
        </div>
        <div class="bg-gradient-to-br from-[var(--color-secondary)] to-[var(--color-accent)] rounded-2xl p-6 text-white text-center transform hover:scale-105 transition-transform duration-300">
          <div class="text-4xl font-bold mb-2" id="stat-cases">1.9M+</div>
          <div class="text-sm opacity-90">Cases analyzed</div>
        </div>
        <div class="bg-gradient-to-br from-[var(--color-primary)] to-[var(--color-accent)] rounded-2xl p-6 text-white text-center transform hover:scale-105 transition-transform duration-300">
          <div class="text-4xl font-bold mb-2" id="stat-timespan">7</div>
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

      <!-- Dashboard Controls -->
      <div class="bg-white rounded-lg shadow-lg p-6 mb-8">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label for="timePeriodFilter" class="block text-sm font-medium text-[var(--color-primary)] mb-2">Time Period</label>
            <select id="timePeriodFilter" class="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent">
              <option value="all">All Years (2018-2025)</option>
              <option value="trump1">Trump I (2018-2020)</option>
              <option value="biden">Biden (2021-2024)</option>
              <option value="trump2">Trump II (2025)</option>
            </select>
          </div>
          <div>
            <label for="representationFilter" class="block text-sm font-medium text-[var(--color-primary)] mb-2">Representation Status</label>
            <select id="representationFilter" class="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent">
              <option value="all">All Cases</option>
              <option value="represented">With Representation</option>
              <option value="unrepresented">Without Representation</option>
            </select>
          </div>
          <div>
            <label for="caseTypeFilter" class="block text-sm font-medium text-[var(--color-primary)] mb-2">Case Type</label>
            <select id="caseTypeFilter" class="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent">
              <option value="all">All Types</option>
              <option value="asylum">Asylum</option>
              <option value="removal">Removal</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div class="flex items-end">
            <button id="updateDashboard" class="w-full bg-[var(--color-primary)] text-white px-4 py-2 rounded-md hover:bg-[var(--color-secondary)] transition-colors">
              Update Charts
            </button>
          </div>
        </div>
      </div>

      <!-- Chart Grid -->
      <div class="grid grid-cols-1 gap-8">
        <!-- Representation Success Rate Chart -->
        <div class="bg-white rounded-2xl shadow-xl p-8">
          <h3 class="text-xl font-bold text-[var(--color-primary)] mb-6">Success Rates by Representation Status</h3>
          <div class="min-h-[500px] w-full" id="representationChart">
            <div class="flex items-center justify-center h-full bg-gray-50 rounded-lg">
              <div class="text-center">
                <div class="w-16 h-16 bg-[var(--color-accent)] rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg class="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/>
                  </svg>
                </div>
                <p class="text-[var(--color-text-secondary)]">Loading chart...</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Timeline Trends Chart -->
        <div class="bg-white rounded-2xl shadow-xl p-8">
          <h3 class="text-xl font-bold text-[var(--color-primary)] mb-6">Trends Over Time</h3>
          <div class="min-h-[500px] w-full" id="timelineChart">
            <div class="flex items-center justify-center h-full bg-gray-50 rounded-lg">
              <div class="text-center">
                <div class="w-16 h-16 bg-[var(--color-secondary)] rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg class="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z"/>
                  </svg>
                </div>
                <p class="text-[var(--color-text-secondary)]">Loading chart...</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Demographics Breakdown Chart -->
        <div class="bg-white rounded-2xl shadow-xl p-8">
          <h3 class="text-xl font-bold text-[var(--color-primary)] mb-6">Outcomes by Age Group</h3>
          <div class="min-h-[500px] w-full" id="demographicsChart">
            <div class="flex items-center justify-center h-full bg-gray-50 rounded-lg">
              <div class="text-center">
                <div class="w-16 h-16 bg-[var(--color-primary)] rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg class="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zM7.07 18.28c.43-.9 3.05-1.78 4.93-1.78s4.51.88 4.93 1.78C15.57 19.36 13.86 20 12 20s-3.57-.64-4.93-1.72zm11.29-1.45c-1.43-1.74-4.9-2.33-6.36-2.33s-4.93.59-6.36 2.33C4.62 15.49 4 13.82 4 12c0-4.41 3.59-8 8-8s8 3.59 8 8c0 1.82-.62 3.49-1.64 4.83z"/>
                  </svg>
                </div>
                <p class="text-[var(--color-text-secondary)]">Loading chart...</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Top Countries Chart -->
        <div class="bg-white rounded-2xl shadow-xl p-8">
          <h3 class="text-xl font-bold text-[var(--color-primary)] mb-6">Top Countries by Case Volume</h3>
          <div class="min-h-[500px] w-full" id="countriesChart">
            <div class="flex items-center justify-center h-full bg-gray-50 rounded-lg">
              <div class="text-center">
                <div class="w-16 h-16 bg-[var(--color-accent)] rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg class="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 1l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 1z"/>
                  </svg>
                </div>
                <p class="text-[var(--color-text-secondary)]">Loading chart...</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Key Insights Section -->
  <section class="py-16 bg-white">
    <div class="mx-auto max-w-7xl px-6 lg:px-8">
      <h2 class="text-3xl font-bold tracking-tight text-[var(--color-primary)] sm:text-4xl text-center mb-12">Key Research Insights</h2>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <div class="bg-gradient-to-br from-[var(--color-background)] to-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <div class="w-12 h-12 bg-[var(--color-accent)] rounded-lg flex items-center justify-center mb-4">
            <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z"/>
            </svg>
          </div>
          <h3 class="text-lg font-bold text-[var(--color-primary)] mb-3">Representation is Critical</h3>
          <p class="text-[var(--color-text-secondary)]">Juveniles with legal representation are 56x more likely to achieve favorable case outcomes compared to those without representation.</p>
        </div>

        <div class="bg-gradient-to-br from-[var(--color-background)] to-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <div class="w-12 h-12 bg-[var(--color-secondary)] rounded-lg flex items-center justify-center mb-4">
            <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
          </div>
          <h3 class="text-lg font-bold text-[var(--color-primary)] mb-3">Policy Periods Matter</h3>
          <p class="text-[var(--color-text-secondary)]">Different administrative periods show distinct patterns in case processing times, representation rates, and outcome distributions.</p>
        </div>

        <div class="bg-gradient-to-br from-[var(--color-background)] to-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <div class="w-12 h-12 bg-[var(--color-primary)] rounded-lg flex items-center justify-center mb-4">
            <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 3c1.93 0 3.5 1.57 3.5 3.5S13.93 13 12 13s-3.5-1.57-3.5-3.5S10.07 6 12 6zm7 13H5v-.23c0-.62.28-1.2.76-1.58C7.47 15.82 9.64 15 12 15s4.53.82 6.24 2.19c.48.38.76.97.76 1.58V19z"/>
            </svg>
          </div>
          <h3 class="text-lg font-bold text-[var(--color-primary)] mb-3">Demographics Influence Outcomes</h3>
          <p class="text-[var(--color-text-secondary)]">Age, country of origin, and language spoken significantly correlate with case outcomes, even controlling for representation.</p>
        </div>
      </div>
    </div>
  </section>


</main>

<script>
  import { onMount } from 'svelte';
  import { env } from '$env/dynamic/public';

  // API Configuration
  const API_BASE_URL = env.PUBLIC_API_URL || 'http://localhost:5000/api';

  // Data stores
  let caseSummary = null;
  let isLoading = true;
  let error = null;

  // Chart configuration for responsive behavior
  const chartConfig = {
    responsive: true,
    displayModeBar: false,
    staticPlot: false,
    useResizeHandler: true,
    autosize: true
  };  onMount(() => {
    // Initialize dashboard
    loadDashboard();
    
    // Add event listeners for filters
    document.getElementById('updateDashboard')?.addEventListener('click', updateDashboard);
  });

  async function loadDashboard() {
    isLoading = true;
    error = null;
    
    try {
      // Load summary data first
      await loadSummaryData();
      
      // Load all charts with real notebook analysis
      await Promise.all([
        loadRepresentationOutcomesChart(),
        loadTimeSeriesChart(),
        loadChiSquareResults(),
        loadCountriesChart()
      ]);
      
      // Setup responsive behavior after all charts are loaded
      finalizeCharts();
      
      isLoading = false;
    } catch (err) {
      console.error('Error loading dashboard:', err);
      error = err.message;
      isLoading = false;
    }
  }

  async function loadSummaryData() {
    try {
      const response = await fetch(`${API_BASE_URL}/overview`);
      if (!response.ok) throw new Error('Failed to load summary data');
      caseSummary = await response.json();
      
      // Update the key stats display
      updateKeyStats();
    } catch (err) {
      console.error('Summary data error:', err);
      // Use fallback data
      caseSummary = {
        total_cases: 10000,
        representation_rate: 35.0,
        average_age: 12.5
      };
    }
  }

  function updateKeyStats() {
    if (caseSummary) {
      document.getElementById('stat-cases').textContent = `${Math.round(caseSummary.total_cases / 1000)}K+`;
      document.getElementById('stat-representation').textContent = `${caseSummary.representation_rate}%`;
    }
  }

  async function loadRepresentationOutcomesChart() {
    try {
      const response = await fetch(`${API_BASE_URL}/findings/outcome-percentages`);
      if (!response.ok) throw new Error('Failed to load representation outcomes chart');
      
      const plotlyConfig = await response.json();
      
      // Update layout for responsive behavior
      plotlyConfig.layout.autosize = true;
      plotlyConfig.layout.width = undefined;
      plotlyConfig.layout.height = 500;
      
      // Use the complete Plotly configuration from backend (identical to notebook)
      if (window.Plotly) {
        await window.Plotly.newPlot('representationChart', plotlyConfig.data, plotlyConfig.layout, chartConfig);
        // Add resize listener for this chart
        window.addEventListener('resize', () => {
          window.Plotly.Plots.resize('representationChart');
        });
      }
    } catch (err) {
      console.error('Representation outcomes chart error:', err);
      showChartError('representationChart', 'Failed to load representation outcomes chart');
    }
  }

  async function loadTimeSeriesChart() {
    try {
      const response = await fetch(`${API_BASE_URL}/findings/time-series`);
      if (!response.ok) throw new Error('Failed to load time series chart');
      
      const plotlyConfig = await response.json();
      
      // Update layout for responsive behavior
      plotlyConfig.layout.autosize = true;
      plotlyConfig.layout.width = undefined;
      plotlyConfig.layout.height = 500;
      
      // Use the complete Plotly configuration from backend (identical to notebook)
      if (window.Plotly) {
        await window.Plotly.newPlot('timelineChart', plotlyConfig.data, plotlyConfig.layout, chartConfig);
        // Add resize listener for this chart
        window.addEventListener('resize', () => {
          window.Plotly.Plots.resize('timelineChart');
        });
      }
    } catch (err) {
      console.error('Time series chart error:', err);
      showChartError('timelineChart', 'Failed to load time series chart');
    }
  }

  async function loadChiSquareResults() {
    try {
      const response = await fetch(`${API_BASE_URL}/findings/chi-square`);
      if (!response.ok) throw new Error('Failed to load chi-square analysis');
      
      const data = await response.json();
      
      // Display chi-square results in a more visual format
      const resultsHtml = `
        <div class="space-y-6">
          <!-- Key Finding Header -->
          <div class="text-center mb-8">
            <h4 class="text-2xl font-bold text-[var(--color-primary)] mb-2">Statistical Analysis Results</h4>
            <p class="text-gray-600">Chi-square tests examine relationships between categorical variables</p>
          </div>
          
          <!-- Policy Era Analysis -->
          <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-200">
            <div class="flex items-center justify-between mb-4">
              <h5 class="text-lg font-bold text-blue-800">📊 Representation by Policy Era</h5>
              <span class="px-3 py-1 rounded-full text-sm font-medium ${data.representation_by_era.significant ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-600'}">
                ${data.representation_by_era.significant ? '✓ Significant' : '✗ Not Significant'}
              </span>
            </div>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div class="bg-white p-3 rounded-lg text-center">
                <div class="font-bold text-lg text-blue-600">${data.representation_by_era.chi_square}</div>
                <div class="text-gray-500">Chi-square</div>
              </div>
              <div class="bg-white p-3 rounded-lg text-center">
                <div class="font-bold text-lg text-blue-600">${data.representation_by_era.p_value.toExponential(2)}</div>
                <div class="text-gray-500">p-value</div>
              </div>
              <div class="bg-white p-3 rounded-lg text-center">
                <div class="font-bold text-lg text-blue-600">${data.representation_by_era.cramer_v}</div>
                <div class="text-gray-500">Cramer's V</div>
              </div>
              <div class="bg-white p-3 rounded-lg text-center">
                <div class="font-bold text-lg ${data.representation_by_era.significant ? 'text-red-600' : 'text-gray-400'}">${data.representation_by_era.significant ? 'YES' : 'NO'}</div>
                <div class="text-gray-500">Significant</div>
              </div>
            </div>
          </div>

          <!-- Outcomes Analysis -->
          <div class="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-6 border border-green-200">
            <div class="flex items-center justify-between mb-4">
              <h5 class="text-lg font-bold text-green-800">⚖️ Outcomes by Representation</h5>
              <span class="px-3 py-1 rounded-full text-sm font-medium ${data.outcomes_by_representation.significant ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-600'}">
                ${data.outcomes_by_representation.significant ? '✓ Significant' : '✗ Not Significant'}
              </span>
            </div>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-4">
              <div class="bg-white p-3 rounded-lg text-center">
                <div class="font-bold text-lg text-green-600">${data.outcomes_by_representation.chi_square}</div>
                <div class="text-gray-500">Chi-square</div>
              </div>
              <div class="bg-white p-3 rounded-lg text-center">
                <div class="font-bold text-lg text-green-600">${data.outcomes_by_representation.p_value.toExponential(2)}</div>
                <div class="text-gray-500">p-value</div>
              </div>
              <div class="bg-white p-3 rounded-lg text-center">
                <div class="font-bold text-lg text-green-600">${data.outcomes_by_representation.cramer_v}</div>
                <div class="text-gray-500">Cramer's V</div>
              </div>
              <div class="bg-white p-3 rounded-lg text-center">
                <div class="font-bold text-lg text-green-600">${data.outcomes_by_representation.odds_ratio}x</div>
                <div class="text-gray-500">Odds Ratio</div>
              </div>
            </div>
            <!-- Key Insight -->
            <div class="bg-green-100 border-l-4 border-green-500 p-4 rounded-r-lg">
              <div class="flex items-center">
                <div class="text-green-500 mr-3">
                  <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                  </svg>
                </div>
                <p class="text-green-800 font-medium">
                  Juveniles with legal representation are <strong>${data.outcomes_by_representation.odds_ratio}x more likely</strong> to achieve favorable outcomes
                </p>
              </div>
            </div>
          </div>
          
          <!-- Statistical Note -->
          <div class="text-xs text-gray-500 text-center bg-gray-50 p-3 rounded-lg">
            <strong>Note:</strong> Chi-square tests measure association strength. p-values < 0.05 indicate statistical significance. 
            Cramer's V measures effect size: 0.1 (small), 0.3 (medium), 0.5 (large).
          </div>
        </div>
      `;
      
      document.getElementById('demographicsChart').innerHTML = resultsHtml;
      
    } catch (err) {
      console.error('Chi-square analysis error:', err);
      showChartError('demographicsChart', 'Failed to load statistical analysis');
    }
  }

  async function loadCountriesChart() {
    try {
      const response = await fetch(`${API_BASE_URL}/findings/countries`);
      if (!response.ok) throw new Error('Failed to load countries chart');
      
      const plotlyConfig = await response.json();
      
      // Update layout for responsive behavior
      plotlyConfig.layout.autosize = true;
      plotlyConfig.layout.width = undefined;
      plotlyConfig.layout.height = 500;
      
      // Use the complete Plotly configuration from backend (with enhanced hover)
      if (window.Plotly) {
        await window.Plotly.newPlot('countriesChart', plotlyConfig.data, plotlyConfig.layout, chartConfig);
        // Add resize listener for this chart
        window.addEventListener('resize', () => {
          window.Plotly.Plots.resize('countriesChart');
        });
      }
    } catch (err) {
      console.error('Countries chart error:', err);
      showChartError('countriesChart', 'Failed to load countries chart');
    }
  }

  function showChartError(containerId, message) {
    const container = document.getElementById(containerId);
    if (container) {
      container.innerHTML = `
        <div class="text-center">
          <div class="w-16 h-16 bg-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
            </svg>
          </div>
          <p class="text-red-600 text-sm">${message}</p>
          <button onclick="location.reload()" class="mt-2 text-blue-600 hover:text-blue-800 text-sm">
            Retry
          </button>
        </div>
      `;
    }
  }

  async function updateDashboard() {
    const filters = getFilterValues();
    isLoading = true;
    
    try {
      // For now, just reload the dashboard
      await loadDashboard();
      isLoading = false;
    } catch (err) {
      console.error('Error updating dashboard:', err);
      error = err.message;
      isLoading = false;
    }
  }

  function getFilterValues() {
    return {
      timePeriod: document.getElementById('timePeriodFilter')?.value || 'all',
      representation: document.getElementById('representationFilter')?.value || 'all',
      caseType: document.getElementById('caseTypeFilter')?.value || 'all'
    };
  }

  function setupChartResizing() {
    // Setup ResizeObserver for automatic chart resizing
    if (window.ResizeObserver && window.Plotly) {
      const chartContainers = ['representationChart', 'timelineChart', 'demographicsChart', 'countriesChart'];
      
      chartContainers.forEach(chartId => {
        const container = document.getElementById(chartId);
        if (container) {
          const resizeObserver = new ResizeObserver(() => {
            if (window.Plotly && window.Plotly.Plots) {
              window.Plotly.Plots.resize(chartId);
            }
          });
          resizeObserver.observe(container);
        }
      });
    }
  }

  // Call this after all charts are loaded
  function finalizeCharts() {
    setupChartResizing();
    
    // Force resize all charts after a short delay to ensure they fit their containers
    setTimeout(() => {
      if (window.Plotly && window.Plotly.Plots) {
        ['representationChart', 'timelineChart', 'demographicsChart', 'countriesChart'].forEach(chartId => {
          const container = document.getElementById(chartId);
          if (container) {
            window.Plotly.Plots.resize(chartId);
          }
        });
      }
    }, 500);
  }
</script>
