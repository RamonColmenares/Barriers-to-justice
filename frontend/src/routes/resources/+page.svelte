<!-- Resources Page Content -->
<script>
  // Reuse rel attribute for all external links (security best practice)
  const relExternal = "noopener noreferrer";
  const sourceTag = "inline-flex items-center gap-1 text-xs bg-gray-100 text-gray-700 px-2.5 py-1 rounded-full hover:bg-gray-200 hover:text-gray-900 transition-colors";

  // Smooth scroll to in-page targets with focus & brief highlight
  function scrollToTarget(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    // manage focus for accessibility
    el.setAttribute('tabindex', '-1');
    el.focus({ preventScroll: true });
    // flash outline to indicate arrival
    el.classList.add('ring-2', 'ring-[var(--color-accent)]', 'ring-offset-2', 'ring-offset-white');
    setTimeout(() => el.classList.remove('ring-2', 'ring-[var(--color-accent)]', 'ring-offset-2', 'ring-offset-white'), 1200);
  }
</script>
<main class="page-content">
  <!-- Hero Section -->
  <section class="relative bg-gradient-to-br from-[var(--color-secondary)] via-[var(--color-primary)] to-[var(--color-accent)] text-white py-20">
    <div class="mx-auto max-w-7xl px-6 lg:px-8">
      <div class="text-center">
        <h1 class="text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl mb-6">Resources & Documentation</h1>
        <p class="text-xl leading-8 text-white/90 max-w-4xl mx-auto">
          Access our research materials, datasets, methodologies, and tools for understanding juvenile immigration issues
        </p>
      </div>
    </div>
  </section>

  <!-- Resource Categories -->
  <section class="py-16 bg-white">
    <div class="mx-auto max-w-7xl px-6 lg:px-8">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
        <!-- Data & Datasets -->
        <div class="bg-gradient-to-br from-[var(--color-background)] to-white rounded-2xl p-6 shadow-lg border border-gray-100 text-center transform hover:scale-105 transition-transform duration-300">
          <div class="w-16 h-16 bg-[var(--color-accent)] rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-white" aria-hidden="true" fill="currentColor" viewBox="0 0 24 24">
              <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/>
            </svg>
          </div>
          <h3 class="text-xl font-bold text-[var(--color-primary)] mb-2">Data & Datasets</h3>
          <p class="text-[var(--color-text-secondary)] mb-4">Cleaned and processed immigration case data</p>
          <span class="inline-block bg-[var(--color-accent)] text-white px-3 py-1 rounded-full text-sm">4 files</span>
        </div>

        <!-- Research Papers -->
        <div class="bg-gradient-to-br from-[var(--color-background)] to-white rounded-2xl p-6 shadow-lg border border-gray-100 text-center transform hover:scale-105 transition-transform duration-300">
          <div class="w-16 h-16 bg-[var(--color-secondary)] rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-white" aria-hidden="true" fill="currentColor" viewBox="0 0 24 24">
              <path d="M19,3H5C3.9,3 3,3.9 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5C21,3.9 20.1,3 19,3M19,19H5V5H19V19Z"/>
            </svg>
          </div>
          <h3 class="text-xl font-bold text-[var(--color-primary)] mb-2">Research Papers</h3>
          <p class="text-[var(--color-text-secondary)] mb-4">Academic publications and analysis reports</p>
          <span class="inline-block bg-[var(--color-secondary)] text-white px-3 py-1 rounded-full text-sm">1 report</span>
        </div>

        <!-- Code & Tools -->
        <div class="bg-gradient-to-br from-[var(--color-background)] to-white rounded-2xl p-6 shadow-lg border border-gray-100 text-center transform hover:scale-105 transition-transform duration-300">
          <div class="w-16 h-16 bg-[var(--color-primary)] rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-white" aria-hidden="true" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8,3A2,2 0 0,0 6,5V9A2,2 0 0,1 4,11H3V13H4A2,2 0 0,1 6,15V19A2,2 0 0,0 8,21H10V19H8V14A2,2 0 0,0 6,12A2,2 0 0,0 8,10V5H10V3M16,3A2,2 0 0,1 18,5V9A2,2 0 0,0 20,11H21V13H20A2,2 0 0,0 18,15V19A2,2 0 0,1 16,21H14V19H16V14A2,2 0 0,1 18,12A2,2 0 0,1 16,10V5H14V3"/>
            </svg>
          </div>
          <h3 class="text-xl font-bold text-[var(--color-primary)] mb-2">Code & Tools</h3>
          <p class="text-[var(--color-text-secondary)] mb-4">Analysis scripts and data processing tools</p>
          <span class="inline-block bg-[var(--color-primary)] text-white px-3 py-1 rounded-full text-sm">1 repository</span>
        </div>

        <!-- Policy Documents -->
        <div class="bg-gradient-to-br from-[var(--color-background)] to-white rounded-2xl p-6 shadow-lg border border-gray-100 text-center transform hover:scale-105 transition-transform duration-300">
          <div class="w-16 h-16 bg-[var(--color-accent)] rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-white" aria-hidden="true" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
            </svg>
          </div>
          <h3 class="text-xl font-bold text-[var(--color-primary)] mb-2">Policy Documents</h3>
          <p class="text-[var(--color-text-secondary)] mb-4">Immigration policy analysis and reviews</p>
          <span class="inline-block bg-[var(--color-accent)] text-white px-3 py-1 rounded-full text-sm">10 documents</span>
        </div>
      </div>
    </div>
  </section>

  <!-- Featured Resources -->
  <section class="py-16 bg-gradient-to-br from-[var(--color-background)] to-gray-50">
    <div class="mx-auto max-w-7xl px-6 lg:px-8">
      <div class="text-center mb-12">
        <h2 class="text-3xl font-bold tracking-tight text-[var(--color-primary)] sm:text-4xl mb-4">Featured Resources</h2>
        <p class="text-lg text-[var(--color-text-secondary)] max-w-3xl mx-auto">
          Our most important and frequently accessed research materials
        </p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Primary Dataset (Updated) -->
        <div class="bg-white rounded-2xl shadow-xl p-8 flex flex-col h-full">
          <div class="flex items-start justify-between mb-6">
            <div class="flex items-center">
              <div class="w-12 h-12 bg-[var(--color-primary)] rounded-lg flex items-center justify-center mr-4">
                <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/>
                </svg>
              </div>
              <div>
                <h3 class="text-xl font-bold text-[var(--color-primary)]">EOIR Juvenile Datasets (Cleaned)</h3>
                <p class="text-sm text-[var(--color-text-secondary)]">4 cleaned CSV.gz files • Updated January 2025</p>
              </div>
            </div>
            <span class="bg-[var(--color-accent)] text-white px-3 py-1 rounded-full text-sm">Featured</span>
          </div>
          <div class="flex-1 flex flex-col">
            <p class="text-[var(--color-text-secondary)] mb-6">
              Four cleaned EOIR juvenile files: case-level table, event history, proceedings timeline, and assigned representation status (CSV.gz).
            </p>
            <div class="flex flex-wrap gap-2 mb-6 mt-auto">
              <span class="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm">CSV.gz</span>
              <span class="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm">Cleaned</span>
              <span class="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm">4 files</span>
            </div>
          </div>
          <div class="mt-auto flex gap-3 items-stretch">
            <a href="#data-resources"
               role="button"
               aria-label="Jump to Data Resources section"
               on:click|preventDefault={() => scrollToTarget('data-resources')}
               class="bg-[var(--color-primary)] text-white px-4 py-2 rounded-md hover:bg-[var(--color-secondary)] transition-colors flex-1 text-center">
              See Downloads Below
            </a>
            <a href="https://github.com/MIT-Emerging-Talent/ET6-CDSP-group-19-repo"
               target="_blank" rel={relExternal}
               class="border border-[var(--color-primary)] text-[var(--color-primary)] px-4 py-2 rounded-md hover:bg-[var(--color-primary)] hover:text-white transition-colors flex-1 text-center">
              Open Repo
            </a>
          </div>
        </div>

        <!-- Main Analysis Notebook -->
        <div class="bg-white rounded-2xl shadow-xl p-8 flex flex-col h-full">
          <div class="flex items-start justify-between mb-6">
            <div class="flex items-center">
              <div class="w-12 h-12 bg-[var(--color-secondary)] rounded-lg flex items-center justify-center mr-4">
                <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M8,3A2,2 0 0,0 6,5V9A2,2 0 0,1 4,11H3V13H4A2,2 0 0,1 6,15V19A2,2 0 0,0 8,21H10V19H8V14A2,2 0 0,0 6,12A2,2 0 0,0 8,10V5H10V3M16,3A2,2 0 0,1 18,5V9A2,2 0 0,0 20,11H21V13H20A2,2 0 0,0 18,15V19A2,2 0 0,1 16,21H14V19H16V14A2,2 0 0,1 18,12A2,2 0 0,1 16,10V5H14V3"/>
                </svg>
              </div>
              <div>
                <h3 class="text-xl font-bold text-[var(--color-primary)]">Main Analysis Notebook</h3>
                <p class="text-sm text-[var(--color-text-secondary)]">Jupyter Notebook • Python • 145 cells</p>
              </div>
            </div>
            <span class="bg-[var(--color-secondary)] text-white px-3 py-1 rounded-full text-sm">New</span>
          </div>
          <div class="flex-1 flex flex-col">
            <p class="text-[var(--color-text-secondary)] mb-6">
              Complete analysis workflow including data cleaning, exploratory data analysis, statistical testing,
              and visualization generation. Fully reproducible research pipeline.
            </p>
            <div class="flex flex-wrap gap-2 mb-6 mt-auto">
              <span class="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm">Jupyter</span>
              <span class="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm">Python 3.9+</span>
              <span class="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm">Pandas</span>
            </div>
          </div>
          <div class="mt-auto flex gap-3 items-stretch">
            <a href="https://github.com/MIT-Emerging-Talent/ET6-CDSP-group-19-repo/blob/main/4_data_analysis/4_data_analysis.ipynb" 
               target="_blank" rel={relExternal}
               class="bg-[var(--color-secondary)] text-white px-4 py-2 rounded-md hover:bg-[var(--color-primary)] transition-colors flex-1 text-center">
              View on GitHub
            </a>
            <a href="https://colab.research.google.com/github/MIT-Emerging-Talent/ET6-CDSP-group-19-repo/blob/main/4_data_analysis/4_data_analysis.ipynb" 
               target="_blank" rel={relExternal}
               class="border border-[var(--color-secondary)] text-[var(--color-secondary)] px-4 py-2 rounded-md hover:bg-[var(--color-secondary)] hover:text-white transition-colors flex-1 text-center">
              Run in Colab
            </a>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Resource Listings -->
  <section class="py-16 bg-white">
    <div class="mx-auto max-w-7xl px-6 lg:px-8">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-12">
        <!-- Data Resources -->
        <div>
          <h3 id="data-resources" class="text-2xl font-bold text-[var(--color-primary)] mb-8">Data Resources</h3>
          <div class="space-y-4">
            <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div class="flex items-center justify-between mb-2">
                <h4 class="font-semibold text-[var(--color-primary)]">juvenile_cases_cleaned.csv.gz</h4>
                <span class="text-sm text-[var(--color-text-secondary)]">CSV.gz</span>
              </div>
              <p class="text-sm text-[var(--color-text-secondary)] mb-3">
                Cleaned juvenile case-level table.
              </p>
              <div class="flex gap-2">
                <a href="https://drive.google.com/file/d/1XXUKEa9QBCBKAoYSvKWQf19NIsEjWPCo/view?usp=sharing"
                   target="_blank" rel={relExternal}
                   class="text-sm bg-[var(--color-accent)] text-white px-3 py-1 rounded hover:bg-[var(--color-secondary)] transition-colors">
                  Download
                </a>
              </div>
            </div>
            <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div class="flex items-center justify-between mb-2">
                <h4 class="font-semibold text-[var(--color-primary)]">juvenile_reps_assigned.csv.gz</h4>
                <span class="text-sm text-[var(--color-text-secondary)]">CSV.gz</span>
              </div>
              <p class="text-sm text-[var(--color-text-secondary)] mb-3">
                Assigned representation status per case.
              </p>
              <div class="flex gap-2">
                <a href="https://drive.google.com/file/d/1tZiPOZfgaJOpPwW9kuGqCvMWk2PAUAIO/view?usp=sharing"
                   target="_blank" rel={relExternal}
                   class="text-sm bg-[var(--color-accent)] text-white px-3 py-1 rounded hover:bg-[var(--color-secondary)] transition-colors">
                  Download
                </a>
              </div>
            </div>
            <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div class="flex items-center justify-between mb-2">
                <h4 class="font-semibold text-[var(--color-primary)]">juvenile_proceedings_cleaned.csv.gz</h4>
                <span class="text-sm text-[var(--color-text-secondary)]">CSV.gz</span>
              </div>
              <p class="text-sm text-[var(--color-text-secondary)] mb-3">
                Cleaned proceedings timeline (hearing dates, statuses).
              </p>
              <div class="flex gap-2">
                <a href="https://drive.google.com/file/d/1TEAOTFKZrteqrD2u7sb6ilgpiz10hZJC/view?usp=sharing"
                   target="_blank" rel={relExternal}
                   class="text-sm bg-[var(--color-accent)] text-white px-3 py-1 rounded hover:bg-[var(--color-secondary)] transition-colors">
                  Download
                </a>
              </div>
            </div>
            <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div class="flex items-center justify-between mb-2">
                <h4 class="font-semibold text-[var(--color-primary)]">juvenile_history_cleaned.csv.gz</h4>
                <span class="text-sm text-[var(--color-text-secondary)]">CSV.gz</span>
              </div>
              <p class="text-sm text-[var(--color-text-secondary)] mb-3">
                Cleaned event history per case (hearings, decisions, updates).
              </p>
              <div class="flex gap-2">
                <a href="https://drive.google.com/file/d/1iRayX8VCZzh8wkLDJAh7rkzP6IrzUThG/view?usp=sharing"
                   target="_blank" rel={relExternal}
                   class="text-sm bg-[var(--color-accent)] text-white px-3 py-1 rounded hover:bg-[var(--color-secondary)] transition-colors">
                  Download
                </a>
              </div>
            </div>
          </div>
        </div>

        <!-- Code & Documentation -->
        <div>
          <h3 class="text-2xl font-bold text-[var(--color-primary)] mb-8">Code & Documentation</h3>
          <div class="space-y-4">
            <!-- Repo Root -->
            <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div class="flex items-center justify-between mb-2">
                <h4 class="font-semibold text-[var(--color-primary)]">Repository (ET6-CDSP-group-19-repo)</h4>
                <span class="text-sm text-[var(--color-text-secondary)]">GitHub</span>
              </div>
              <p class="text-sm text-[var(--color-text-secondary)] mb-3">Project structure, guides, and all notebooks.</p>
              <div class="flex gap-2">
                <a href="https://github.com/MIT-Emerging-Talent/ET6-CDSP-group-19-repo" target="_blank" rel={relExternal} class="text-sm bg-[var(--color-primary)] text-white px-3 py-1 rounded hover:bg-[var(--color-secondary)] transition-colors">Open Repo</a>
              </div>
            </div>

            <!-- Data Preparation Notebook -->
            <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div class="flex items-center justify-between mb-2">
                <h4 class="font-semibold text-[var(--color-primary)]">02_clean_core_tables.ipynb (Data Preparation)</h4>
                <span class="text-sm text-[var(--color-text-secondary)]">Jupyter</span>
              </div>
              <p class="text-sm text-[var(--color-text-secondary)] mb-3">Cleaning pipeline for core EOIR tables.</p>
              <div class="flex gap-2">
                <a href="https://github.com/MIT-Emerging-Talent/ET6-CDSP-group-19-repo/blob/main/2_data_preparation/notebooks/02_clean_core_tables.ipynb" target="_blank" rel={relExternal} class="text-sm bg-[var(--color-primary)] text-white px-3 py-1 rounded hover:bg-[var(--color-secondary)] transition-colors">GitHub</a>
                <a href="https://colab.research.google.com/github/MIT-Emerging-Talent/ET6-CDSP-group-19-repo/blob/main/2_data_preparation/notebooks/02_clean_core_tables.ipynb" target="_blank" rel={relExternal} class="text-sm border border-gray-300 px-3 py-1 rounded hover:bg-gray-50 transition-colors">Run in Colab</a>
              </div>
            </div>

            <!-- Exploration Notebook -->
            <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div class="flex items-center justify-between mb-2">
                <h4 class="font-semibold text-[var(--color-primary)]">03_eda_juvenile_cases.ipynb (Exploration)</h4>
                <span class="text-sm text-[var(--color-text-secondary)]">Jupyter</span>
              </div>
              <p class="text-sm text-[var(--color-text-secondary)] mb-3">Exploratory analysis of juvenile cases.</p>
              <div class="flex gap-2">
                <a href="https://github.com/MIT-Emerging-Talent/ET6-CDSP-group-19-repo/blob/main/3_data_exploration/notebooks/03_eda_juvenile_cases.ipynb" target="_blank" rel={relExternal} class="text-sm bg-[var(--color-primary)] text-white px-3 py-1 rounded hover:bg-[var(--color-secondary)] transition-colors">GitHub</a>
                <a href="https://colab.research.google.com/github/MIT-Emerging-Talent/ET6-CDSP-group-19-repo/blob/main/3_data_exploration/notebooks/03_eda_juvenile_cases.ipynb" target="_blank" rel={relExternal} class="text-sm border border-gray-300 px-3 py-1 rounded hover:bg-gray-50 transition-colors">Run in Colab</a>
              </div>
            </div>

            <!-- Final Analysis Notebook -->
            <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div class="flex items-center justify-between mb-2">
                <h4 class="font-semibold text-[var(--color-primary)]">4_data_analysis.ipynb (Final Analysis)</h4>
                <span class="text-sm text-[var(--color-text-secondary)]">Jupyter</span>
              </div>
              <p class="text-sm text-[var(--color-text-secondary)] mb-3">Final models, tests, and figures.</p>
              <div class="flex gap-2">
                <a href="https://github.com/MIT-Emerging-Talent/ET6-CDSP-group-19-repo/blob/main/4_data_analysis/4_data_analysis.ipynb" target="_blank" rel={relExternal} class="text-sm bg-[var(--color-primary)] text-white px-3 py-1 rounded hover:bg-[var(--color-secondary)] transition-colors">GitHub</a>
                <a href="https://colab.research.google.com/github/MIT-Emerging-Talent/ET6-CDSP-group-19-repo/blob/main/4_data_analysis/4_data_analysis.ipynb" target="_blank" rel={relExternal} class="text-sm border border-gray-300 px-3 py-1 rounded hover:bg-gray-50 transition-colors">Run in Colab</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Research Question & External Sources -->
  <section class="py-16 bg-gradient-to-br from-[var(--color-background)] to-gray-50">
    <div class="mx-auto max-w-7xl px-6 lg:px-8">
      <div class="text-center mb-12">
        <h2 class="text-3xl font-bold tracking-tight text-[var(--color-primary)] sm:text-4xl mb-4">Research Question & External Sources</h2>
        <p class="text-lg text-[var(--color-text-secondary)] max-w-3xl mx-auto">
          Core question, authoritative data sources, and curated readings connected to juvenile immigration policy and outcomes.
        </p>
      </div>

      <!-- Research Question Card -->
      <div class="bg-white rounded-2xl shadow-xl p-8 mb-10 border border-gray-100">
        <h3 class="text-xl font-bold text-[var(--color-primary)] mb-3">Research Question</h3>
        <p class="text-[var(--color-text-secondary)]">
          <strong>How do changes in U.S. immigration policy under different administrations affect access to legal representation and outcomes for immigrant juveniles seeking protection?</strong>
        </p>
      </div>

      <!-- External Data Sources -->
      <div class="mb-12">
        <h3 class="text-2xl font-bold text-[var(--color-primary)] mb-6">External Data Sources</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <!-- TRAC Immigration -->
          <div class="bg-white rounded-xl p-6 shadow border border-gray-100">
            <div class="flex items-start justify-between mb-2">
              <h4 class="font-semibold text-[var(--color-primary)]">TRAC Immigration – Juvenile Tool</h4>
              <span class="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded">External</span>
            </div>
            <p class="text-sm text-[var(--color-text-secondary)] mb-4">Total numbers of juvenile cases (represented or not) across time and geography.</p>
            <a href="https://tracreports.org/phptools/immigration/juvenile/" target="_blank" rel={relExternal} class={sourceTag}>
              Open Source <span aria-hidden="true">↗</span>
            </a>
          </div>
          <!-- ORR Facts & Data -->
          <div class="bg-white rounded-xl p-6 shadow border border-gray-100">
            <div class="flex items-start justify-between mb-2">
              <h4 class="font-semibold text-[var(--color-primary)]">ORR – Facts & Data (UAC)</h4>
              <span class="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded">External</span>
            </div>
            <p class="text-sm text-[var(--color-text-secondary)] mb-4">Demographics and placements for unaccompanied children (age, sex, location).</p>
            <a href="https://www.acf.hhs.gov/orr/about/ucs/facts-and-data" target="_blank" rel={relExternal} class={sourceTag}>
              Open Source <span aria-hidden="true">↗</span>
            </a>
          </div>
          <!-- EOIR Case Data (FOIA) -->
          <div class="bg-white rounded-xl p-6 shadow border border-gray-100">
            <div class="flex items-start justify-between mb-2">
              <h4 class="font-semibold text-[var(--color-primary)]">EOIR Case Data (FOIA)</h4>
              <span class="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded">External</span>
            </div>
            <p class="text-sm text-[var(--color-text-secondary)] mb-4">Immigration court records incl. juvenile flags, representation, and outcomes.</p>
            <div class="flex gap-2">
              <a href="https://catalog.data.gov/dataset/eoir-case-data" target="_blank" rel={relExternal} class={sourceTag}>
                Open on Data.gov <span aria-hidden="true">↗</span>
              </a>
            </div>
          </div>
        </div>
      </div>


      <!-- Curated Reading: Policy Changes & Outcomes -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Policy Changes -->
        <div class="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
          <div class="flex items-start justify-between mb-4">
            <h3 class="text-xl font-bold text-[var(--color-primary)]">Policy Changes (Articles & News)</h3>
            <span class="bg-[var(--color-accent)] text-white px-3 py-1 rounded-full text-xs">Curated</span>
          </div>
          <ul class="space-y-4 text-sm">
            <!-- A1: Zero Tolerance Policy -->
            <li class="border border-gray-100 rounded-lg p-4">
              <div class="flex items-center justify-between mb-1">
                <span class="font-semibold text-[var(--color-primary)]">Zero Tolerance Policy</span>
                <span class="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded">Trump · 2018</span>
              </div>
              <p class="text-[var(--color-text-secondary)] mb-2">Mandatory criminal prosecution for all border crossers. Led to family separation.</p>
              <a href="https://www.cfr.org/backgrounder/us-detention-child-migrants" target="_blank" rel={relExternal} class={sourceTag}>Council on Foreign Relations <span aria-hidden="true">↗</span></a>
            </li>
            <!-- A1: Family Separation Policy -->
            <li class="border border-gray-100 rounded-lg p-4">
              <div class="flex items-center justify-between mb-1">
                <span class="font-semibold text-[var(--color-primary)]">Family Separation Policy</span>
                <span class="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded">Trump · 2018</span>
              </div>
              <p class="text-[var(--color-text-secondary)] mb-2">De facto separation for families between ports of entry; possible use of military bases for housing.</p>
              <a href="https://www.migrationpolicy.org/article/family-separation-and-zero-tolerance-policies-rolled-out-stem-unwanted-migrants-may-face" target="_blank" rel={relExternal} class={sourceTag}>Migration Policy Institute <span aria-hidden="true">↗</span></a>
            </li>
            <!-- A1: Zero Tolerance Rescission -->
            <li class="border border-gray-100 rounded-lg p-4">
              <div class="flex items-center justify-between mb-1">
                <span class="font-semibold text-[var(--color-primary)]">Zero Tolerance Rescission</span>
                <span class="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded">Biden · 2021</span>
              </div>
              <p class="text-[var(--color-text-secondary)] mb-2">DOJ rescinded the 2018 "Zero Tolerance" policy.</p>
              <a href="https://www.justice.gov/opa/pr/attorney-general-merrick-b-garland-issues-memo-rescinding-zero-tolerance-policy" target="_blank" rel={relExternal} class={sourceTag}>Justice.gov press memo <span aria-hidden="true">↗</span></a>
            </li>
            <!-- A1: DACA Continuation -->
            <li class="border border-gray-100 rounded-lg p-4">
              <div class="flex items-center justify-between mb-1">
                <span class="font-semibold text-[var(--color-primary)]">DACA – Program Guidance</span>
                <span class="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded">Biden · 2021–2024</span>
              </div>
              <p class="text-[var(--color-text-secondary)] mb-2">Continuation and clarifications for childhood arrivals.</p>
              <a href="https://www.uscis.gov/DACA" target="_blank" rel={relExternal} class={sourceTag}>USCIS DACA <span aria-hidden="true">↗</span></a>
            </li>
            <!-- A1: Enhanced Enforcement -->
            <li class="border border-gray-100 rounded-lg p-4">
              <div class="flex items-center justify-between mb-1">
                <span class="font-semibold text-[var(--color-primary)]">Enhanced Enforcement</span>
                <span class="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded">Trump · 2025</span>
              </div>
              <p class="text-[var(--color-text-secondary)] mb-2">ICE arrest rates approximately doubled vs. FY 2024 (≈310 → ≈650/day).</p>
              <a href="https://www.migrationpolicy.org/article/trump-2-immigration-first-100-days" target="_blank" rel={relExternal} class={sourceTag}>Migration Policy Institute <span aria-hidden="true">↗</span></a>
            </li>
            <!-- A1: Detention Capacity Expansion -->
            <li class="border border-gray-100 rounded-lg p-4">
              <div class="flex items-center justify-between mb-1">
                <span class="font-semibold text-[var(--color-primary)]">Detention Capacity Expansion</span>
                <span class="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded">Trump · 2025</span>
              </div>
              <p class="text-[var(--color-text-secondary)] mb-2">ICE detention capacity increased from 41,500 beds (FY 2024) to 54,500 (as of March).</p>
              <a href="https://www.migrationpolicy.org/article/trump-2-immigration-first-100-days" target="_blank" rel={relExternal} class={sourceTag}>Migration Policy Institute <span aria-hidden="true">↗</span></a>
            </li>
            <!-- A1/B1: Unaccompanied Minor Definition Change (consolidated) -->
            <li class="border border-gray-100 rounded-lg p-4">
              <div class="flex items-center justify-between mb-1">
                <span class="font-semibold text-[var(--color-primary)]">Unaccompanied Minor Definition Change</span>
                <span class="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded">Trump · 2025</span>
              </div>
              <p class="text-[var(--color-text-secondary)] mb-2">Changing the legal definition of who qualifies as an unaccompanied minor; may affect eligibility for SIJS/asylum/ORR services.</p>
              <a href="https://www.nycbar.org/wp-content/uploads/2025/03/20221419-TrumpAdminChangesImmigrationLaw.pdf" target="_blank" rel={relExternal} class={sourceTag}>NYC Bar Association report <span aria-hidden="true">↗</span></a>
            </li>
            <!-- B1: Access to Counsel Reduction -->
            <li class="border border-gray-100 rounded-lg p-4">
              <div class="flex items-center justify-between mb-1">
                <span class="font-semibold text-[var(--color-primary)]">Access to Counsel Reduction (Funding Cut Policy)</span>
                <span class="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded">Trump · 2025</span>
              </div>
              <p class="text-[var(--color-text-secondary)] mb-2">Cuts to federally funded legal aid programs for unaccompanied minors; fewer juveniles can access free/low‑cost legal help.</p>
              <a href="https://www.vera.org/explainers/trumps-week-one-orders-on-immigration-law-explained" target="_blank" rel={relExternal} class={sourceTag}>Vera Institute <span aria-hidden="true">↗</span></a>
            </li>
            <!-- B1: Accelerated Docket Expansion -->
            <li class="border border-gray-100 rounded-lg p-4">
              <div class="flex items-center justify-between mb-1">
                <span class="font-semibold text-[var(--color-primary)]">Accelerated Docket Expansion</span>
                <span class="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded">Trump · 2025</span>
              </div>
              <p class="text-[var(--color-text-secondary)] mb-2">Expanded use of fast‑track immigration hearings for minors; less time to obtain counsel; more no‑shows/default removals.</p>
              <a href="https://www.npr.org/" target="_blank" rel={relExternal} class={sourceTag}>NPR (title as cited) <span aria-hidden="true">↗</span></a>
            </li>
            <!-- Refined Table: Public Charge Expansion (2019) -->
            <li class="border border-gray-100 rounded-lg p-4">
              <div class="flex items-center justify-between mb-1">
                <span class="font-semibold text-[var(--color-primary)]">Public Charge Expansion</span>
                <span class="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded">Trump · 2019</span>
              </div>
              <p class="text-[var(--color-text-secondary)] mb-2">Broadened criteria for denying entry/relief based on potential public assistance use; chilling effect on families seeking support.</p>
              <div class="flex flex-wrap gap-2">
                <a href="https://www.kff.org/racial-equity-and-health-policy/fact-sheet/public-charge-policies-for-immigrants-implications-for-health-coverage/" target="_blank" rel={relExternal} class={sourceTag}>KFF <span aria-hidden="true">↗</span></a>
                <a href="https://www.federalregister.gov/documents/2019/08/14/2019-17142/inadmissibility-on-public-charge-grounds" target="_blank" rel={relExternal} class={sourceTag}>Federal Register <span aria-hidden="true">↗</span></a>
              </div>
            </li>
          </ul>
        </div>

        <!-- Outcomes -->
        <div class="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
          <div class="flex items-start justify-between mb-4">
            <h3 class="text-xl font-bold text-[var(--color-primary)]">Outcomes (Articles & Data)</h3>
            <span class="bg-[var(--color-secondary)] text-white px-3 py-1 rounded-full text-xs">Curated</span>
          </div>
          <ul class="space-y-4 text-sm">
            <!-- A2: Unaccompanied Minors Without Court Dates -->
            <li class="border border-gray-100 rounded-lg p-4">
              <div class="flex items-center justify-between mb-1">
                <span class="font-semibold text-[var(--color-primary)]">Unaccompanied Minors Without Court Dates</span>
                <span class="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded">Biden · 2024</span>
              </div>
              <p class="text-[var(--color-text-secondary)] mb-2">&gt;291,000 UACs apprehended without NTAs; ~90,000 from 2021 entries.</p>
              <a href="https://www.oig.dhs.gov/sites/default/files/assets/2024-08/OIG-24-46-Aug24.pdf" target="_blank" rel={relExternal} class={sourceTag}>DHS OIG (2024) <span aria-hidden="true">↗</span></a>
            </li>
            <!-- A2: Court Non-Appearances -->
            <li class="border border-gray-100 rounded-lg p-4">
              <div class="flex items-center justify-between mb-1">
                <span class="font-semibold text-[var(--color-primary)]">Court Non‑Appearances</span>
                <span class="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded">Cross‑Admin · 2019–2023</span>
              </div>
              <p class="text-[var(--color-text-secondary)] mb-2">32,000 UACs did not appear for court hearings.</p>
              <a href="https://immigrationforum.org/article/unaccompanied-alien-children-ucs-or-uacs-2025-update/" target="_blank" rel={relExternal} class={sourceTag}>National Immigration Forum <span aria-hidden="true">↗</span></a>
            </li>
            <!-- A2: Total “Lost” Contact Cases -->
            <li class="border border-gray-100 rounded-lg p-4">
              <div class="flex items-center justify-between mb-1">
                <span class="font-semibold text-[var(--color-primary)]">Total “Lost” Contact Cases</span>
                <span class="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded">Cross‑Admin · 2019–2023</span>
              </div>
              <p class="text-[var(--color-text-secondary)] mb-2">291,000 without NTAs + 32,000 no‑shows ≈ 323,000.</p>
              <a href="https://immigrationforum.org/article/unaccompanied-alien-children-ucs-or-uacs-2025-update/" target="_blank" rel={relExternal} class={sourceTag}>National Immigration Forum <span aria-hidden="true">↗</span></a>
            </li>
            <!-- A2: Overall Immigration Court Backlog -->
            <li class="border border-gray-100 rounded-lg p-4">
              <div class="flex items-center justify-between mb-1">
                <span class="font-semibold text-[var(--color-primary)]">Overall Immigration Court Backlog</span>
                <span class="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded">Cross‑Admin · 2024</span>
              </div>
              <p class="text-[var(--color-text-secondary)] mb-2">Over 3.7M cases pending; 900k+ decided in 2024.</p>
              <a href="https://tracreports.org/whatsnew/email.241021.html" target="_blank" rel={relExternal} class={sourceTag}>TRAC (Oct 2024) <span aria-hidden="true">↗</span></a>
            </li>
            <!-- A2: Deportation Rates -->
            <li class="border border-gray-100 rounded-lg p-4">
              <div class="flex items-center justify-between mb-1">
                <span class="font-semibold text-[var(--color-primary)]">Deportation Rates</span>
                <span class="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded">Biden · 2024</span>
              </div>
              <p class="text-[var(--color-text-secondary)] mb-2">271,000 deportations in FY2024 (vs. 267,000 in 2019).</p>
              <a href="https://www.reuters.com/world/us/us-removals-border-crossings-up-2024-12-03/" target="_blank" rel={relExternal} class={sourceTag}>Reuters <span aria-hidden="true">↗</span></a>
            </li>
            <!-- A2: ICE Arrests Increase -->
            <li class="border border-gray-100 rounded-lg p-4">
              <div class="flex items-center justify-between mb-1">
                <span class="font-semibold text-[var(--color-primary)]">ICE Arrests Increase</span>
                <span class="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded">Trump · 2025</span>
              </div>
              <p class="text-[var(--color-text-secondary)] mb-2">Arrest rate roughly doubled since FY2024 (≈310 → ≈650/day by mid‑March).</p>
              <a href="https://www.migrationpolicy.org/article/trump-2-immigration-first-100-days" target="_blank" rel={relExternal} class={sourceTag}>Migration Policy Institute <span aria-hidden="true">↗</span></a>
            </li>
            <!-- A2: Monthly Deportations -->
            <li class="border border-gray-100 rounded-lg p-4">
              <div class="flex items-center justify-between mb-1">
                <span class="font-semibold text-[var(--color-primary)]">Monthly Deportations</span>
                <span class="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded">Trump · Apr 2025</span>
              </div>
              <p class="text-[var(--color-text-secondary)] mb-2">&gt;17,200 deportations in April 2025 (~29% ↑ vs. April 2024’s &gt;13,300).</p>
              <a href="https://www.yahoo.com/news/ice-deportations-spike-29-amid-124712345.html" target="_blank" rel={relExternal} class={sourceTag}>NBC News (via Yahoo) <span aria-hidden="true">↗</span></a>
            </li>

            <!-- B2: Success Rate with Lawyers -->
            <li class="border border-gray-100 rounded-lg p-4">
              <div class="flex items-center justify-between mb-1">
                <span class="font-semibold text-[var(--color-primary)]">Success Rate with Lawyers</span>
                <span class="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded">Cross‑Admin · 2020–2023</span>
              </div>
              <p class="text-[var(--color-text-secondary)] mb-2">Juveniles with legal representation were 73% more likely to win than those without.</p>
              <a href="https://tracreports.org/tracatwork/detail/A2298.html" target="_blank" rel={relExternal} class={sourceTag}>TRAC summary <span aria-hidden="true">↗</span></a>
            </li>
            <!-- B2: Legal Representation Gap -->
            <li class="border border-gray-100 rounded-lg p-4">
              <div class="flex items-center justify-between mb-1">
                <span class="font-semibold text-[var(--color-primary)]">Legal Representation Gap</span>
                <span class="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded">All periods</span>
              </div>
              <p class="text-[var(--color-text-secondary)] mb-2">Most detained juveniles appear in court without counsel.</p>
              <a href="https://www.americanimmigrationcouncil.org/fact-sheet/children-immigration-court-over-95-percent-represented-attorney-appear-court/" target="_blank" rel={relExternal} class={sourceTag}>AIC — Children in Court <span aria-hidden="true">↗</span></a>
            </li>
            <!-- B2: Case Completion Time -->
            <li class="border border-gray-100 rounded-lg p-4">
              <div class="flex items-center justify-between mb-1">
                <span class="font-semibold text-[var(--color-primary)]">Case Completion Time</span>
                <span class="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded">Cross‑Admin</span>
              </div>
              <p class="text-[var(--color-text-secondary)] mb-2">Represented juvenile cases took longer but had better outcomes.</p>
              <a href="https://tracreports.org/immigration/reports/668/" target="_blank" rel={relExternal} class={sourceTag}>TRAC analysis <span aria-hidden="true">↗</span></a>
            </li>
            <!-- B2: Court Appearance Rate -->
            <li class="border border-gray-100 rounded-lg p-4">
              <div class="flex items-center justify-between mb-1">
                <span class="font-semibold text-[var(--color-primary)]">Court Appearance Rate</span>
                <span class="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded">Cross‑Admin · 2019–2023</span>
              </div>
              <p class="text-[var(--color-text-secondary)] mb-2">Children with lawyers were 95% more likely to attend hearings.</p>
              <a href="https://tracreports.org/phptools/immigration/juvenile/" target="_blank" rel={relExternal} class={sourceTag}>TRAC Data Tool <span aria-hidden="true">↗</span></a>
            </li>
            <!-- B2: Detention Impact on Outcomes -->
            <li class="border border-gray-100 rounded-lg p-4">
              <div class="flex items-center justify-between mb-1">
                <span class="font-semibold text-[var(--color-primary)]">Detention Impact on Outcomes</span>
                <span class="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded">Cross‑Admin</span>
              </div>
              <p class="text-[var(--color-text-secondary)] mb-2">Detained children had worse outcomes than those in shelter/community placements.</p>
              <a href="https://www.americanimmigrationcouncil.org/wp-content/uploads/2025/01/detaining_families_a_study_of_asylum_adjudication_in_family_detention_final.pdf" target="_blank" rel={relExternal} class={sourceTag}>AIC — Family Detention Study <span aria-hidden="true">↗</span></a>
            </li>
            <!-- B2: Backlog Effect on Minors -->
            <li class="border border-gray-100 rounded-lg p-4">
              <div class="flex items-center justify-between mb-1">
                <span class="font-semibold text-[var(--color-primary)]">Backlog Effect on Minors</span>
                <span class="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded">2024–2025</span>
              </div>
              <p class="text-[var(--color-text-secondary)] mb-2">Delays and case overloads reduce consistency and fairness for juveniles.</p>
              <a href="https://time.com/7203665/trump-deportation-immigration-courts/" target="_blank" rel={relExternal} class={sourceTag}>TIME analysis <span aria-hidden="true">↗</span></a>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </section>
  <!-- Usage Guidelines -->
  <section class="py-16 bg-gradient-to-br from-[var(--color-background)] to-gray-50">
    <div class="mx-auto max-w-7xl px-6 lg:px-8">
      <div class="text-center mb-12">
        <h2 class="text-3xl font-bold tracking-tight text-[var(--color-primary)] sm:text-4xl mb-4">Usage Guidelines</h2>
        <p class="text-lg text-[var(--color-text-secondary)] max-w-3xl mx-auto">
          Important information about data usage, licensing, and ethical considerations
        </p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div class="bg-white rounded-lg shadow-lg p-6">
          <div class="w-12 h-12 bg-[var(--color-accent)] rounded-lg flex items-center justify-center mb-4">
            <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 1l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 1z"/>
            </svg>
          </div>
          <h3 class="text-lg font-bold text-[var(--color-primary)] mb-3">Data License</h3>
          <p class="text-[var(--color-text-secondary)] text-sm mb-4">
            All datasets are released under Creative Commons Attribution 4.0 International License. 
            Attribution required for any use.
          </p>
          <span class="text-[var(--color-accent)] hover:text-[var(--color-secondary)] text-sm font-medium cursor-default">
            View License →
          </span>
        </div>

        <div class="bg-white rounded-lg shadow-lg p-6">
          <div class="w-12 h-12 bg-[var(--color-secondary)] rounded-lg flex items-center justify-center mb-4">
            <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
          </div>
          <h3 class="text-lg font-bold text-[var(--color-primary)] mb-3">Privacy Protection</h3>
          <p class="text-[var(--color-text-secondary)] text-sm mb-4">
            All personal identifying information has been removed or anonymized. 
            Data follows privacy-by-design principles.
          </p>
          <span class="text-[var(--color-accent)] hover:text-[var(--color-secondary)] text-sm font-medium cursor-default">
            Privacy Policy →
          </span>
        </div>

        <div class="bg-white rounded-lg shadow-lg p-6">
          <div class="w-12 h-12 bg-[var(--color-primary)] rounded-lg flex items-center justify-center mb-4">
            <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 3c1.93 0 3.5 1.57 3.5 3.5S13.93 13 12 13s-3.5-1.57-3.5-3.5S10.07 6 12 6zm7 13H5v-.23c0-.62.28-1.2.76-1.58C7.47 15.82 9.64 15 12 15s4.53.82 6.24 2.19c.48.38.76.97.76 1.58V19z"/>
            </svg>
          </div>
          <h3 class="text-lg font-bold text-[var(--color-primary)] mb-3">Ethical Use</h3>
          <p class="text-[var(--color-text-secondary)] text-sm mb-4">
            Please use this data responsibly. Consider the impact on vulnerable populations 
            and avoid harmful stereotyping.
          </p>
          <span class="text-[var(--color-accent)] hover:text-[var(--color-secondary)] text-sm font-medium cursor-default">
            Ethics Guidelines →
          </span>
        </div>
      </div>
    </div>
  </section>

  <!-- Getting Started -->
  <section class="py-16 bg-white">
    <div class="mx-auto max-w-7xl px-6 lg:px-8">
      <div class="text-center mb-12">
        <h2 class="text-3xl font-bold tracking-tight text-[var(--color-primary)] sm:text-4xl mb-4">Getting Started</h2>
        <p class="text-lg text-[var(--color-text-secondary)] max-w-3xl mx-auto">
          Quick start guide for researchers and analysts
        </p>
      </div>

      <div class="bg-gradient-to-br from-[var(--color-background)] to-white rounded-2xl p-8 lg:p-12 shadow-lg border border-gray-100">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div>
            <h3 class="text-xl font-bold text-[var(--color-primary)] mb-4">Quick Setup</h3>
            <div class="space-y-3">
              <div class="flex items-center">
                <div class="w-6 h-6 bg-[var(--color-accent)] rounded-full flex items-center justify-center mr-3">
                  <span class="text-white text-xs font-bold">1</span>
                </div>
                <span class="text-[var(--color-text-secondary)]">Download the main dataset</span>
              </div>
              <div class="flex items-center">
                <div class="w-6 h-6 bg-[var(--color-accent)] rounded-full flex items-center justify-center mr-3">
                  <span class="text-white text-xs font-bold">2</span>
                </div>
                <span class="text-[var(--color-text-secondary)]">Install required Python packages</span>
              </div>
              <div class="flex items-center">
                <div class="w-6 h-6 bg-[var(--color-accent)] rounded-full flex items-center justify-center mr-3">
                  <span class="text-white text-xs font-bold">3</span>
                </div>
                <span class="text-[var(--color-text-secondary)]">Run the analysis notebook</span>
              </div>
              <div class="flex items-center">
                <div class="w-6 h-6 bg-[var(--color-accent)] rounded-full flex items-center justify-center mr-3">
                  <span class="text-white text-xs font-bold">4</span>
                </div>
                <span class="text-[var(--color-text-secondary)]">Explore and modify analyses</span>
              </div>
            </div>
          </div>

          <div>
            <h3 class="text-xl font-bold text-[var(--color-primary)] mb-4">Installation</h3>
            <div class="bg-gray-900 rounded-lg p-4 text-white text-sm">
              <pre><code># Clone the repository
git clone https://github.com/MIT-Emerging-Talent/ET6-CDSP-group-19-repo

# Navigate to project directory
cd ET6-CDSP-group-19-repo

# Install dependencies for data analysis
cd 4_data_analysis
pip install -r requirements.txt

# Start Jupyter (multiple notebooks available)
jupyter notebook

# Main analysis notebook:
# 4_data_analysis.ipynb</code></pre>
            </div>
            <div class="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <p class="text-sm text-blue-800">
                <strong>Note:</strong> Each notebook directory contains its own requirements. 
                Install dependencies separately for each analysis you want to run.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</main>
