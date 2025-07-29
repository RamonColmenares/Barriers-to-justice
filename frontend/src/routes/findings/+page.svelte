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
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Representation Success Rate Chart -->
        <div class="bg-white rounded-2xl shadow-xl p-6">
          <h3 class="text-xl font-bold text-[var(--color-primary)] mb-4">Success Rates by Representation Status</h3>
          <div class="h-80" id="representationChart">
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
        <div class="bg-white rounded-2xl shadow-xl p-6">
          <h3 class="text-xl font-bold text-[var(--color-primary)] mb-4">Trends Over Time</h3>
          <div class="h-80" id="timelineChart">
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
        <div class="bg-white rounded-2xl shadow-xl p-6">
          <h3 class="text-xl font-bold text-[var(--color-primary)] mb-4">Outcomes by Age Group</h3>
          <div class="h-80" id="demographicsChart">
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
        <div class="bg-white rounded-2xl shadow-xl p-6">
          <h3 class="text-xl font-bold text-[var(--color-primary)] mb-4">Top Countries by Case Volume</h3>
          <div class="h-80" id="countriesChart">
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

      <!-- Courts Analysis Chart (Full Width) -->
      <div class="mt-8">
        <div class="bg-white rounded-2xl shadow-xl p-6">
          <h3 class="text-xl font-bold text-[var(--color-primary)] mb-4">Court Performance Analysis</h3>
          <div class="h-96" id="courtsChart">
            <div class="flex items-center justify-center h-full bg-gray-50 rounded-lg">
              <div class="text-center">
                <div class="w-16 h-16 bg-[var(--color-secondary)] rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg class="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 1z"/>
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

  // Chart configuration
  const chartConfig = {
    responsive: true,
    displayModeBar: false,
    staticPlot: false
  };

  onMount(() => {
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
      
      // Load all charts
      await Promise.all([
        loadRepresentationChart(),
        loadTimeSeriesChart(),
        loadOddsRatioChart(),
        loadOutcomePercentagesChart(),
        loadTrendsChart(),
        loadDemographicsChart(),
        loadCountriesChart(),
        loadCourtsChart()
      ]);
      
      isLoading = false;
    } catch (err) {
      console.error('Error loading dashboard:', err);
      error = err.message;
      isLoading = false;
    }
  }

  async function loadSummaryData() {
    try {
      const response = await fetch(`${API_BASE_URL}/cases/summary`);
      if (!response.ok) throw new Error('Failed to load summary data');
      caseSummary = await response.json();
    } catch (err) {
      console.error('Summary data error:', err);
      // Use fallback data
      caseSummary = {
        total_cases: 10000,
        juvenile_cases: 3000,
        representation_rate: 35.0,
        avg_days_to_resolution: 485
      };
    }
  }

  async function loadRepresentationChart() {
    try {
      const response = await fetch(`${API_BASE_URL}/charts/representation`);
      if (!response.ok) throw new Error('Failed to load representation chart');
      
      const data = await response.json();
      
      // Render chart using Plotly
      if (window.Plotly) {
        window.Plotly.newPlot('representationChart', data.chart.data, data.chart.layout, chartConfig);
      }
    } catch (err) {
      console.error('Representation chart error:', err);
      showChartError('representationChart', 'Failed to load representation chart');
    }
  }

  async function loadTrendsChart() {
    try {
      const response = await fetch(`${API_BASE_URL}/charts/trends`);
      if (!response.ok) throw new Error('Failed to load trends chart');
      
      const data = await response.json();
      
      if (window.Plotly) {
        window.Plotly.newPlot('timelineChart', data.chart.data, data.chart.layout, chartConfig);
      }
    } catch (err) {
      console.error('Trends chart error:', err);
      showChartError('timelineChart', 'Failed to load trends chart');
    }
  }

  async function loadDemographicsChart() {
    try {
      const response = await fetch(`${API_BASE_URL}/charts/demographics`);
      if (!response.ok) throw new Error('Failed to load demographics chart');
      
      const data = await response.json();
      
      if (window.Plotly) {
        window.Plotly.newPlot('demographicsChart', data.chart.data, data.chart.layout, chartConfig);
      }
    } catch (err) {
      console.error('Demographics chart error:', err);
      showChartError('demographicsChart', 'Failed to load demographics chart');
    }
  }

  async function loadCountriesChart() {
    try {
      const response = await fetch(`${API_BASE_URL}/charts/countries`);
      if (!response.ok) throw new Error('Failed to load countries chart');
      
      const data = await response.json();
      
      if (window.Plotly) {
        window.Plotly.newPlot('countriesChart', data.chart.data, data.chart.layout, chartConfig);
      }
    } catch (err) {
      console.error('Countries chart error:', err);
      showChartError('countriesChart', 'Failed to load countries chart');
    }
  }

  async function loadCourtsChart() {
    try {
      const response = await fetch(`${API_BASE_URL}/charts/courts`);
      if (!response.ok) throw new Error('Failed to load courts chart');
      
      const data = await response.json();
      
      if (window.Plotly) {
        window.Plotly.newPlot('courtsChart', data.chart.data, data.chart.layout, chartConfig);
      }
    } catch (err) {
      console.error('Courts chart error:', err);
      showChartError('courtsChart', 'Failed to load courts chart');
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
      // Build query parameters
      const params = new URLSearchParams();
      if (filters.startDate) params.append('start_date', filters.startDate);
      if (filters.endDate) params.append('end_date', filters.endDate);
      if (filters.court && filters.court !== 'all') params.append('court', filters.court);
      if (filters.representation && filters.representation !== 'all') {
        if (filters.representation === 'represented') params.append('representation', 'Represented');
        if (filters.representation === 'unrepresented') params.append('representation', 'Pro Se');
      }
      if (filters.ageGroup && filters.ageGroup !== 'all') params.append('age_group', filters.ageGroup);
      
      const queryString = params.toString();
      
      // Reload all charts with filters
      await Promise.all([
        loadRepresentationChartWithFilters(queryString),
        loadTrendsChartWithFilters(queryString),
        loadDemographicsChartWithFilters(queryString),
        loadCountriesChartWithFilters(queryString),
        loadCourtsChartWithFilters(queryString)
      ]);
      
      isLoading = false;
    } catch (err) {
      console.error('Error updating dashboard:', err);
      error = err.message;
      isLoading = false;
    }
  }

  async function loadRepresentationChartWithFilters(queryString) {
    const response = await fetch(`${API_BASE_URL}/charts/representation?${queryString}`);
    if (!response.ok) throw new Error('Failed to load representation chart');
    
    const data = await response.json();
    if (window.Plotly) {
      window.Plotly.react('representationChart', data.chart.data, data.chart.layout, chartConfig);
    }
  }

  async function loadTrendsChartWithFilters(queryString) {
    const response = await fetch(`${API_BASE_URL}/charts/trends?${queryString}`);
    if (!response.ok) throw new Error('Failed to load trends chart');
    
    const data = await response.json();
    if (window.Plotly) {
      window.Plotly.react('timelineChart', data.chart.data, data.chart.layout, chartConfig);
    }
  }

  async function loadDemographicsChartWithFilters(queryString) {
    const response = await fetch(`${API_BASE_URL}/charts/demographics?${queryString}`);
    if (!response.ok) throw new Error('Failed to load demographics chart');
    
    const data = await response.json();
    if (window.Plotly) {
      window.Plotly.react('demographicsChart', data.chart.data, data.chart.layout, chartConfig);
    }
  }

  async function loadCountriesChartWithFilters(queryString) {
    const response = await fetch(`${API_BASE_URL}/charts/countries?${queryString}`);
    if (!response.ok) throw new Error('Failed to load countries chart');
    
    const data = await response.json();
    if (window.Plotly) {
      window.Plotly.react('countriesChart', data.chart.data, data.chart.layout, chartConfig);
    }
  }

  async function loadCourtsChartWithFilters(queryString) {
    const response = await fetch(`${API_BASE_URL}/charts/courts?${queryString}`);
    if (!response.ok) throw new Error('Failed to load courts chart');
    
    const data = await response.json();
    if (window.Plotly) {
      window.Plotly.react('courtsChart', data.chart.data, data.chart.layout, chartConfig);
    }
  }

  async function loadTimeSeriesChart() {
    try {
      const response = await fetch(`${API_BASE_URL}/charts/time-series`);
      if (!response.ok) throw new Error('Failed to load time series chart');
      
      const data = await response.json();
      
      if (window.Plotly) {
        window.Plotly.newPlot('timeSeriesChart', data.chart.data, data.chart.layout, chartConfig);
      }
    } catch (err) {
      console.error('Time series chart error:', err);
      showChartError('timeSeriesChart', 'Failed to load time series chart');
    }
  }

  async function loadOddsRatioChart() {
    try {
      const response = await fetch(`${API_BASE_URL}/charts/odds-ratio`);
      if (!response.ok) throw new Error('Failed to load odds ratio chart');
      
      const data = await response.json();
      
      if (window.Plotly) {
        window.Plotly.newPlot('oddsRatioChart', data.chart.data, data.chart.layout, chartConfig);
      }
    } catch (err) {
      console.error('Odds ratio chart error:', err);
      showChartError('oddsRatioChart', 'Failed to load odds ratio chart');
    }
  }

  async function loadOutcomePercentagesChart() {
    try {
      const response = await fetch(`${API_BASE_URL}/charts/outcome-percentages`);
      if (!response.ok) throw new Error('Failed to load outcome percentages chart');
      
      const data = await response.json();
      
      if (window.Plotly) {
        window.Plotly.newPlot('outcomePercentagesChart', data.chart.data, data.chart.layout, chartConfig);
      }
    } catch (err) {
      console.error('Outcome percentages chart error:', err);
      showChartError('outcomePercentagesChart', 'Failed to load outcome percentages chart');
    }
  }

  function getFilterValues() {
    return {
      startDate: document.getElementById('startDateFilter')?.value || '',
      endDate: document.getElementById('endDateFilter')?.value || '',
      court: document.getElementById('courtFilter')?.value || 'all',
      representation: document.getElementById('representationFilter')?.value || 'all',
      ageGroup: document.getElementById('ageGroupFilter')?.value || 'all'
    };
  }
</script>
