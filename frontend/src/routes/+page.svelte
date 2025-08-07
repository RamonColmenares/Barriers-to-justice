<!-- Hero Section -->
<section class="relative flex min-h-[65vh] lg:min-h-[70vh] items-center justify-center bg-cover bg-fixed bg-center text-white pt-4" style='background-image: linear-gradient(rgba(44, 62, 80, 0.7), rgba(44, 62, 80, 0.7)), url("https://lh3.googleusercontent.com/aida-public/AB6AXuD1dPZXGDzUWSNPDhIolX0qiK_evTpO5NpPSHAJmGVgW8cm7lvwqHyvnNIVjslPo1lDNelkBJcKOMEKOLOamKXKahnRH850tZr_ezZ2MsDujF5-5bshMIYJHFCRxiY0SsCSyI3MVkHJyYdgLbQYpsS2rJR6Wl8mofJoM45bE2-FxejCD4uw8Q2ab4D84vPZr1m1Tq9xI7d8bzWu8g7bRrqfSD-mWtfegJp4T9aqO9bzaJccLcIk1tPkuIhb3JbUop4I2c3mge-m2ls");'>
  <div class="container mx-auto px-10 text-center">
    <h1 class="text-4xl md:text-6xl font-bold leading-tight drop-shadow-md">Barriers to Justice</h1>
    <p class="mt-4 max-w-3xl mx-auto text-lg md:text-xl font-light">
      Our research illuminates how immigration policies impact immigrant juveniles seeking protection. A staggering
      <span class="font-bold text-[var(--color-accent)]">75%</span> face significant obstacles in accessing legal aid.
    </p>
    <button class="mt-8 btn-primary text-lg px-8 py-3" on:click={scrollToFindings}>Learn More</button>
  </div>
  <div class="absolute bottom-0 left-0 w-full h-20 bg-gradient-to-t from-[var(--color-background)] to-transparent"></div>
</section>

<!-- Policy Timeline Section -->
<section class="section-spacing bg-[var(--color-background)]" bind:this={timelineSection}>
  <div class="section-container">
    <div class="text-container mb-12">
      <h2 class="section-title">Policy Timeline (2018–2025)</h2>
      <p class="section-subtitle">Key U.S. immigration policy shifts that affected immigrant juveniles and access to counsel.</p>
    </div>
    <div class="relative wrap overflow-hidden p-10 h-full max-w-5xl mx-auto">
      <div class="border-2-2 absolute border-opacity-20 border-[var(--color-accent)] h-full border" style="left: 50%"></div>

      <!-- 2018: Zero Tolerance -->
      <div class="mb-8 flex justify-between items-center w-full right-timeline">
        <div class="order-1 w-5/12"></div>
        <div class="z-20 flex items-center order-1 bg-[var(--color-accent)] shadow-xl w-8 h-8 rounded-full">
          <h3 class="mx-auto font-semibold text-lg text-white">1</h3>
        </div>
        <div class="order-1 bg-white rounded-lg shadow-xl w-5/12 px-6 py-4">
          <h3 class="mb-3 font-bold text-[var(--color-primary)] text-xl">2018 · “Zero Tolerance”</h3>
          <p class="text-sm leading-snug tracking-wide text-[var(--color-text-secondary)]">Mandatory prosecution of all border crossers led to widespread family separation and a surge of unaccompanied minors entering the system.</p>
        </div>
      </div>

      <!-- 2019: Public Charge Rule -->
      <div class="mb-8 flex justify-between flex-row-reverse items-center w-full left-timeline">
        <div class="order-1 w-5/12"></div>
        <div class="z-20 flex items-center order-1 bg-[var(--color-accent)] shadow-xl w-8 h-8 rounded-full">
          <h3 class="mx-auto font-semibold text-lg text-white">2</h3>
        </div>
        <div class="order-1 bg-white rounded-lg shadow-xl w-5/12 px-6 py-4">
          <h3 class="mb-3 font-bold text-[var(--color-primary)] text-xl">2019 · Public Charge Expansion</h3>
          <p class="text-sm leading-snug tracking-wide text-[var(--color-text-secondary)]">Broadened denial criteria based on potential public-benefit use, discouraging families from seeking legal and social services for children.</p>
        </div>
      </div>

      <!-- 2021: Rescission of Zero Tolerance -->
      <div class="mb-8 flex justify-between items-center w-full right-timeline">
        <div class="order-1 w-5/12"></div>
        <div class="z-20 flex items-center order-1 bg-[var(--color-accent)] shadow-xl w-8 h-8 rounded-full">
          <h3 class="mx-auto font-semibold text-lg text-white">3</h3>
        </div>
        <div class="order-1 bg-white rounded-lg shadow-xl w-5/12 px-6 py-4">
          <h3 class="mb-3 font-bold text-[var(--color-primary)] text-xl">2021 · Zero Tolerance Rescinded</h3>
          <p class="text-sm leading-snug tracking-wide text-[var(--color-text-secondary)]">The DOJ ended the policy, halting systematic family separation while reunification challenges persisted.</p>
        </div>
      </div>

      <!-- 2021–2024: DACA Maintained/Strengthened -->
      <div class="mb-8 flex justify-between flex-row-reverse items-center w-full left-timeline">
        <div class="order-1 w-5/12"></div>
        <div class="z-20 flex items-center order-1 bg-[var(--color-accent)] shadow-xl w-8 h-8 rounded-full">
          <h3 class="mx-auto font-semibold text-lg text-white">4</h3>
        </div>
        <div class="order-1 bg-white rounded-lg shadow-xl w-5/12 px-6 py-4">
          <h3 class="mb-3 font-bold text-[var(--color-primary)] text-xl">2021–2024 · DACA Maintained</h3>
          <p class="text-sm leading-snug tracking-wide text-[var(--color-text-secondary)]">Protections for childhood arrivals were maintained and clarified, supporting continued relief eligibility for many youths.</p>
        </div>
      </div>

      <!-- 2025: Enforcement & Detention Expansion -->
      <div class="mb-8 flex justify-between items-center w-full right-timeline">
        <div class="order-1 w-5/12"></div>
        <div class="z-20 flex items-center order-1 bg-[var(--color-accent)] shadow-xl w-8 h-8 rounded-full">
          <h3 class="mx-auto font-semibold text-lg text-white">5</h3>
        </div>
        <div class="order-1 bg-white rounded-lg shadow-xl w-5/12 px-6 py-4">
          <h3 class="mb-3 font-bold text-[var(--color-primary)] text-xl">2025 · Enhanced Enforcement & Detention</h3>
          <p class="text-sm leading-snug tracking-wide text-[var(--color-text-secondary)]">ICE arrest rates and detention capacity expanded sharply, heightening detention and separation risks for mixed‑status families with juveniles.</p>
        </div>
      </div>

      <!-- 2025: UAC Redefinition & Accelerated Dockets -->
      <div class="mb-8 flex justify-between flex-row-reverse items-center w-full left-timeline">
        <div class="order-1 w-5/12"></div>
        <div class="z-20 flex items-center order-1 bg-[var(--color-accent)] shadow-xl w-8 h-8 rounded-full">
          <h3 class="mx-auto font-semibold text-lg text-white">6</h3>
        </div>
        <div class="order-1 bg-white rounded-lg shadow-xl w-5/12 px-6 py-4">
          <h3 class="mb-3 font-bold text-[var(--color-primary)] text-xl">2025 · UAC Redefinition & Fast‑Track Dockets</h3>
          <p class="text-sm leading-snug tracking-wide text-[var(--color-text-secondary)]">Proposals to narrow who counts as an unaccompanied minor and expanded accelerated dockets reduce time to secure counsel and may lower appearance rates.</p>
        </div>
      </div>

      <!-- 2025: Funding Cut Policy -->
      <div class="mb-8 flex justify-between items-center w-full right-timeline">
        <div class="order-1 w-5/12"></div>
        <div class="z-20 flex items-center order-1 bg-[var(--color-accent)] shadow-xl w-8 h-8 rounded-full">
          <h3 class="mx-auto font-semibold text-lg text-white">7</h3>
        </div>
        <div class="order-1 bg-white rounded-lg shadow-xl w-5/12 px-6 py-4">
          <h3 class="mb-3 font-bold text-[var(--color-primary)] text-xl">2025 · Access to Counsel Reduction</h3>
          <p class="text-sm leading-snug tracking-wide text-[var(--color-text-secondary)]">Cuts to federally funded legal aid programs for unaccompanied minors mean fewer juveniles can access free or low-cost legal help, creating a wider representation gap.</p>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Key Findings Section -->
<section class="py-20 bg-white" bind:this={findingsSection}>
  <div class="container mx-auto px-10">
    <div class="text-center mb-12">
      <h2 class="text-3xl md:text-4xl font-bold text-[var(--color-primary)]">Key Findings</h2>
      <p class="text-[var(--color-text-secondary)] mt-2">Quick access to the most critical insights from our research.</p>
    </div>
    <div class="grid md:grid-cols-3 gap-8">
      <!-- Access to Legal Aid Card -->
      <a href="/findings#legal-aid" 
         class="text-center p-8 rounded-lg shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:scale-105 cursor-pointer group block border-2 border-transparent hover:border-[var(--color-accent)]/20">
        <div class="text-[var(--color-accent)] mx-auto mb-4 group-hover:text-[var(--color-primary)] transition-colors">
          <svg fill="currentColor" height="48px" viewBox="0 0 256 256" width="48px" xmlns="http://www.w3.org/2000/svg">
            <path d="M229.66,218.34l-50.07-50.06a88.11,88.11,0,1,0-11.31,11.31l50.06,50.07a8,8,0,0,0,11.32-11.32ZM40,112a72,72,0,1,1,72,72A72.08,72.08,0,0,1,40,112Z"></path>
          </svg>
        </div>
        <h3 class="text-xl font-bold mb-2 text-[var(--color-primary)] group-hover:text-[var(--color-accent)] transition-colors">Access to Legal Aid</h3>
        <p class="text-[var(--color-text-secondary)] group-hover:text-[var(--color-primary)] transition-colors">Explore the challenges immigrant juveniles face in securing legal representation.</p>
        <div class="mt-4 text-sm text-[var(--color-accent)] font-medium opacity-0 group-hover:opacity-100 transition-opacity">
          Click to explore findings →
        </div>
      </a>
      
      <!-- Fairness of Proceedings Card -->
      <a href="/findings#proceedings" 
         class="text-center p-8 rounded-lg shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:scale-105 cursor-pointer group block border-2 border-transparent hover:border-[var(--color-accent)]/20">
        <div class="text-[var(--color-accent)] mx-auto mb-4 group-hover:text-[var(--color-primary)] transition-colors">
          <svg fill="currentColor" height="48px" viewBox="0 0 256 256" width="48px" xmlns="http://www.w3.org/2000/svg">
            <path d="M239.43,133l-32-80h0a8,8,0,0,0-9.16-4.84L136,62V40a8,8,0,0,0-16,0V65.58L54.26,80.19A8,8,0,0,0,48.57,85h0v.06L16.57,165a7.92,7.92,0,0,0-.57,3c0,23.31,24.54,32,40,32s40-8.69,40-32a7.92,7.92,0,0,0-.57-3L66.92,93.77,120,82V208H104a8,8,0,0,0,0,16h48a8,8,0,0,0,0-16H136V78.42L187,67.1,160.57,133a7.92,7.92,0,0,0-.57,3c0,23.31,24.54,32,40,32s40-8.69,40-32A7.92,7.92,0,0,0,239.43,133ZM56,184c-7.53,0-22.76-3.61-23.93-14.64L56,109.54l23.93,59.82C78.76,180.39,63.53,184,56,184Zm144-32c-7.53,0-22.76-3.61-23.93-14.64L200,77.54l23.93,59.82C222.76,148.39,207.53,152,200,152Z"></path>
          </svg>
        </div>
        <h3 class="text-xl font-bold mb-2 text-[var(--color-primary)] group-hover:text-[var(--color-accent)] transition-colors">Fairness of Proceedings</h3>
        <p class="text-[var(--color-text-secondary)] group-hover:text-[var(--color-primary)] transition-colors">Understand how current policies affect the fairness of legal proceedings.</p>
        <div class="mt-4 text-sm text-[var(--color-accent)] font-medium opacity-0 group-hover:opacity-100 transition-opacity">
          Click to explore findings →
        </div>
      </a>

      <!-- Add the third card here in the same format, updating href and content as needed -->
      <!-- Example: -->
      <a href="/findings#outcomes" 
         class="text-center p-8 rounded-lg shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:scale-105 cursor-pointer group block border-2 border-transparent hover:border-[var(--color-accent)]/20">
        <div class="text-[var(--color-accent)] mx-auto mb-4 group-hover:text-[var(--color-primary)] transition-colors">
          <svg fill="currentColor" height="48px" viewBox="0 0 256 256" width="48px" xmlns="http://www.w3.org/2000/svg">
            <path d="M208,40H48A16,16,0,0,0,32,56v58.77c0,89.61,75.82,119.34,91,124.39a15.53,15.53,0,0,0,10,0c15.2-5.05,91-34.78,91-124.39V56A16,16,0,0,0,208,40Zm0,74.79c0,78.42-66.35,104.62-80,109.18-13.53-4.51-80-30.69-80-109.18V56l160,0Z"></path>
          </svg>
        </div>
        <h3 class="text-xl font-bold mb-2 text-[var(--color-primary)] group-hover:text-[var(--color-accent)] transition-colors">Outcomes & Impact</h3>
        <p class="text-[var(--color-text-secondary)] group-hover:text-[var(--color-primary)] transition-colors">See the real-world impact of legal decisions on immigrant juveniles.</p>
        <div class="mt-4 text-sm text-[var(--color-accent)] font-medium opacity-0 group-hover:opacity-100 transition-opacity">
          Click to explore findings →
        </div>
      </a>
    </div>
  </div>
</section>

<!-- Research Team Section -->
<section class="section-spacing bg-white">
  <div class="section-container">
    <div class="text-container mb-16">
      <h2 class="section-title">Meet the Research Team</h2>
      <p class="section-subtitle">MIT Emerging Talent students dedicated to uncovering barriers to justice.</p>
    </div>
    <div class="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
      <!-- Team Page Link Card (a nifoula removed) -->
      <div class="bg-gradient-to-br from-[var(--color-primary)] to-[var(--color-accent)] rounded-2xl shadow-lg overflow-hidden text-white group hover:scale-105 transition-transform duration-300">
        <div class="p-8 text-center">
          <div class="w-24 h-24 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg class="w-12 h-12 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
            </svg>
          </div>
          <h3 class="text-2xl font-bold mb-4">Research Team</h3>
          <p class="text-white/90 font-medium mb-6">Meet Our Researchers</p>
          <p class="text-white/80 text-sm mb-6">
            Discover our team of dedicated researchers working to understand barriers to justice in the U.S. immigration system.
          </p>
          <a href="/team" 
             class="inline-flex items-center px-6 py-3 bg-white text-[var(--color-primary)] font-bold rounded-lg hover:bg-gray-100 transition-colors">
            Meet the Team
            <svg class="w-4 h-4 ml-2" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
            </svg>
          </a>
        </div>
      </div>
      
      <!-- MIT Emerging Talent Card -->
      <div class="bg-gradient-to-br from-[var(--color-secondary)] to-[var(--color-accent)] rounded-2xl shadow-lg overflow-hidden text-white group hover:scale-105 transition-transform duration-300">
        <div class="p-8 text-center">
          <div class="w-24 h-24 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg class="w-12 h-12 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
            </svg>
          </div>
          <h3 class="text-2xl font-bold mb-4">MIT Emerging Talent</h3>
          <p class="text-white/90 font-medium mb-6">Program Support & Guidance</p>
          <p class="text-white/80 text-sm mb-6">
            This research is conducted as part of the MIT Emerging Talent program, which provides support and guidance to help us develop innovative approaches to critical social challenges.
          </p>
          <a href="https://emergingtalent.mit.edu" target="_blank" rel="noopener noreferrer"
             class="inline-flex items-center px-6 py-3 bg-white text-[var(--color-secondary)] font-bold rounded-lg hover:bg-gray-100 transition-colors">
            Learn More
            <svg class="w-4 h-4 ml-2" fill="currentColor" viewBox="0 0 24 24">
              <path d="M19 19H5V5h7V3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.11 0 2-.9 2-2v-7h-2v7zM14 3v2h3.59l-9.83 9.83 1.41 1.41L19 6.41V10h2V3h-7z"/>
            </svg>
          </a>
        </div>
      </div>
    </div>
  </div>
</section>

<script>
  let timelineSection;
  let findingsSection;
  
  function scrollToFindings() {
    findingsSection.scrollIntoView({ behavior: 'smooth' });
  }

  function handleImageError(event) {
    event.target.style.display = 'none';
    event.target.nextElementSibling.style.display = 'flex';
  }
</script>
