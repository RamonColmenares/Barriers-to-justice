<!-- Hero Section -->
<section class="relative flex min-h-[60vh] items-center justify-center bg-cover bg-fixed bg-center text-white" style='background-image: linear-gradient(rgba(44, 62, 80, 0.7), rgba(44, 62, 80, 0.7)), url("https://lh3.googleusercontent.com/aida-public/AB6AXuD1dPZXGDzUWSNPDhIolX0qiK_evTpO5NpPSHAJmGVgW8cm7lvwqHyvnNIVjslPo1lDNelkBJcKOMEKOLOamKXKahnRH850tZr_ezZ2MsDujF5-5bshMIYJHFCRxiY0SsCSyI3MVkHJyYdgLbQYpsS2rJR6Wl8mofJoM45bE2-FxejCD4uw8Q2ab4D84vPZr1m1Tq9xI7d8bzWu8g7bRrqfSD-mWtfegJp4T9aqO9bzaJccLcIk1tPkuIhb3JbUop4I2c3mge-m2ls");'>
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
      <h2 class="section-title">Visual Policy Timeline</h2>
      <p class="section-subtitle">A historical overview of key policy changes affecting immigrant juveniles.</p>
    </div>
    <div class="relative wrap overflow-hidden p-10 h-full max-w-5xl mx-auto">
      <div class="border-2-2 absolute border-opacity-20 border-[var(--color-accent)] h-full border" style="left: 50%"></div>
      
      <!-- Timeline Item 1 -->
      <div class="mb-8 flex justify-between items-center w-full right-timeline">
        <div class="order-1 w-5/12"></div>
        <div class="z-20 flex items-center order-1 bg-[var(--color-accent)] shadow-xl w-8 h-8 rounded-full">
          <h3 class="mx-auto font-semibold text-lg text-white">1</h3>
        </div>
        <div class="order-1 bg-white rounded-lg shadow-xl w-5/12 px-6 py-4">
          <h3 class="mb-3 font-bold text-[var(--color-primary)] text-xl">2010: Policy A Enacted</h3>
          <p class="text-sm leading-snug tracking-wide text-[var(--color-text-secondary)]">This policy introduced stricter guidelines for asylum seekers.</p>
        </div>
      </div>
      
      <!-- Timeline Item 2 -->
      <div class="mb-8 flex justify-between flex-row-reverse items-center w-full left-timeline">
        <div class="order-1 w-5/12"></div>
        <div class="z-20 flex items-center order-1 bg-[var(--color-accent)] shadow-xl w-8 h-8 rounded-full">
          <h3 class="mx-auto font-semibold text-lg text-white">2</h3>
        </div>
        <div class="order-1 bg-white rounded-lg shadow-xl w-5/12 px-6 py-4">
          <h3 class="mb-3 font-bold text-[var(--color-primary)] text-xl">2015: Policy B Implemented</h3>
          <p class="text-sm leading-snug tracking-wide text-[var(--color-text-secondary)]">Implementation of this policy led to increased scrutiny of juvenile cases.</p>
        </div>
      </div>
      
      <!-- Timeline Item 3 -->
      <div class="mb-8 flex justify-between items-center w-full right-timeline">
        <div class="order-1 w-5/12"></div>
        <div class="z-20 flex items-center order-1 bg-[var(--color-accent)] shadow-xl w-8 h-8 rounded-full">
          <h3 class="mx-auto font-semibold text-lg text-white">3</h3>
        </div>
        <div class="order-1 bg-white rounded-lg shadow-xl w-5/12 px-6 py-4">
          <h3 class="mb-3 font-bold text-[var(--color-primary)] text-xl">2018: Policy C Revised</h3>
          <p class="text-sm leading-snug tracking-wide text-[var(--color-text-secondary)]">Revisions to this policy aimed to streamline the process but created new challenges.</p>
        </div>
      </div>
      
      <!-- Timeline Item 4 -->
      <div class="mb-8 flex justify-between flex-row-reverse items-center w-full left-timeline">
        <div class="order-1 w-5/12"></div>
        <div class="z-20 flex items-center order-1 bg-[var(--color-accent)] shadow-xl w-8 h-8 rounded-full">
          <h3 class="mx-auto font-semibold text-lg text-white">4</h3>
        </div>
        <div class="order-1 bg-white rounded-lg shadow-xl w-5/12 px-6 py-4">
          <h3 class="mb-3 font-bold text-[var(--color-primary)] text-xl">2022: Current Landscape</h3>
          <p class="text-sm leading-snug tracking-wide text-[var(--color-text-secondary)]">The current landscape presents a complex web of regulations affecting access to justice.</p>
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
      <div class="text-center p-8 rounded-lg shadow-lg hover:shadow-2xl transition-shadow duration-300">
        <div class="text-[var(--color-accent)] mx-auto mb-4">
          <svg fill="currentColor" height="48px" viewBox="0 0 256 256" width="48px" xmlns="http://www.w3.org/2000/svg">
            <path d="M229.66,218.34l-50.07-50.06a88.11,88.11,0,1,0-11.31,11.31l50.06,50.07a8,8,0,0,0,11.32-11.32ZM40,112a72,72,0,1,1,72,72A72.08,72.08,0,0,1,40,112Z"></path>
          </svg>
        </div>
        <h3 class="text-xl font-bold mb-2 text-[var(--color-primary)]">Access to Legal Aid</h3>
        <p class="text-[var(--color-text-secondary)]">Explore the challenges immigrant juveniles face in securing legal representation.</p>
      </div>
      <div class="text-center p-8 rounded-lg shadow-lg hover:shadow-2xl transition-shadow duration-300">
        <div class="text-[var(--color-accent)] mx-auto mb-4">
          <svg fill="currentColor" height="48px" viewBox="0 0 256 256" width="48px" xmlns="http://www.w3.org/2000/svg">
            <path d="M239.43,133l-32-80h0a8,8,0,0,0-9.16-4.84L136,62V40a8,8,0,0,0-16,0V65.58L54.26,80.19A8,8,0,0,0,48.57,85h0v.06L16.57,165a7.92,7.92,0,0,0-.57,3c0,23.31,24.54,32,40,32s40-8.69,40-32a7.92,7.92,0,0,0-.57-3L66.92,93.77,120,82V208H104a8,8,0,0,0,0,16h48a8,8,0,0,0,0-16H136V78.42L187,67.1,160.57,133a7.92,7.92,0,0,0-.57,3c0,23.31,24.54,32,40,32s40-8.69,40-32A7.92,7.92,0,0,0,239.43,133ZM56,184c-7.53,0-22.76-3.61-23.93-14.64L56,109.54l23.93,59.82C78.76,180.39,63.53,184,56,184Zm144-32c-7.53,0-22.76-3.61-23.93-14.64L200,77.54l23.93,59.82C222.76,148.39,207.53,152,200,152Z"></path>
          </svg>
        </div>
        <h3 class="text-xl font-bold mb-2 text-[var(--color-primary)]">Fairness of Proceedings</h3>
        <p class="text-[var(--color-text-secondary)]">Understand how current policies affect the fairness of legal proceedings.</p>
      </div>
      <div class="text-center p-8 rounded-lg shadow-lg hover:shadow-2xl transition-shadow duration-300">
        <div class="text-[var(--color-accent)] mx-auto mb-4">
          <svg fill="currentColor" height="48px" viewBox="0 0 256 256" width="48px" xmlns="http://www.w3.org/2000/svg">
            <path d="M208,40H48A16,16,0,0,0,32,56v58.77c0,89.61,75.82,119.34,91,124.39a15.53,15.53,0,0,0,10,0c15.2-5.05,91-34.78,91-124.39V56A16,16,0,0,0,208,40Zm0,74.79c0,78.42-66.35,104.62-80,109.18-13.53-4.51-80-30.69-80-109.18V56l160,0Z"></path>
          </svg>
        </div>
        <h3 class="text-xl font-bold mb-2 text-[var(--color-primary)]">Protection Mechanisms</h3>
        <p class="text-[var(--color-text-secondary)]">Learn about the effectiveness of existing protection mechanisms for vulnerable youth.</p>
      </div>
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
    <div class="grid md:grid-cols-3 lg:grid-cols-4 gap-8 max-w-6xl mx-auto">
      <div class="card-container flex flex-col items-center text-center group hover:scale-105 transition-transform duration-300">
        <div class="w-32 h-32 mb-4">
          <img src="/team/ammar-osman.jpg" alt="Ammar Osman" 
               class="w-full h-full object-cover rounded-full shadow-lg border-4 border-white"
               style="background: linear-gradient(135deg, var(--color-accent), var(--color-primary))"
               onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" />
          <div class="w-full h-full rounded-full bg-gradient-to-br from-[var(--color-accent)] to-[var(--color-primary)] flex items-center justify-center text-white font-bold text-xl" style="display: none;">
            AO
          </div>
        </div>
        <a href="https://github.com/AmmarIbrahimTech" target="_blank" rel="noopener noreferrer" 
           class="text-lg font-bold text-[var(--color-primary)] hover:text-[var(--color-accent)] transition-colors mb-2">
          Ammar Osman
        </a>
        <p class="text-sm text-[var(--color-text-secondary)] font-medium">Researcher</p>
      </div>
      <div class="card-container flex flex-col items-center text-center group hover:scale-105 transition-transform duration-300">
        <div class="w-32 h-32 mb-4">
          <img src="/team/amro-mohamed.jpg" alt="Amro Mohamed" 
               class="w-full h-full object-cover rounded-full shadow-lg border-4 border-white"
               style="background: linear-gradient(135deg, var(--color-secondary), var(--color-primary))"
               onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" />
          <div class="w-full h-full rounded-full bg-gradient-to-br from-[var(--color-secondary)] to-[var(--color-primary)] flex items-center justify-center text-white font-bold text-xl" style="display: none;">
            AM
          </div>
        </div>
        <a href="https://github.com/Elshikh-Amro" target="_blank" rel="noopener noreferrer" 
           class="text-lg font-bold text-[var(--color-primary)] hover:text-[var(--color-accent)] transition-colors mb-2">
          Amro Mohamed
        </a>
        <p class="text-sm text-[var(--color-text-secondary)] font-medium">Researcher</p>
      </div>
      <div class="card-container flex flex-col items-center text-center group hover:scale-105 transition-transform duration-300">
        <div class="w-32 h-32 mb-4">
          <div class="w-full bg-center bg-no-repeat aspect-square bg-cover rounded-full shadow-lg border-4 border-white" 
               style="background-image: url('/team/azza.jpg'), linear-gradient(135deg, var(--color-accent), var(--color-secondary))">
            <div class="w-full h-full rounded-full bg-gradient-to-br from-[var(--color-accent)] to-[var(--color-secondary)] flex items-center justify-center text-white font-bold text-xl [background-image:none]">
              AZ
            </div>
          </div>
        </div>
        <a href="https://github.com/AzzaOmer1" target="_blank" rel="noopener noreferrer" 
           class="text-lg font-bold text-[var(--color-primary)] hover:text-[var(--color-accent)] transition-colors mb-2">
          Azza
        </a>
        <p class="text-sm text-[var(--color-text-secondary)] font-medium">Researcher</p>
      </div>
      <div class="card-container flex flex-col items-center text-center group hover:scale-105 transition-transform duration-300">
        <div class="w-32 h-32 mb-4">
          <div class="w-full bg-center bg-no-repeat aspect-square bg-cover rounded-full shadow-lg border-4 border-white" 
               style="background-image: url('/team/banu-ozyilmaz.jpg'), linear-gradient(135deg, var(--color-primary), var(--color-accent))">
            <div class="w-full h-full rounded-full bg-gradient-to-br from-[var(--color-primary)] to-[var(--color-accent)] flex items-center justify-center text-white font-bold text-xl [background-image:none]">
              BÖ
            </div>
          </div>
        </div>
        <a href="https://github.com/doctorbanu" target="_blank" rel="noopener noreferrer" 
           class="text-lg font-bold text-[var(--color-primary)] hover:text-[var(--color-accent)] transition-colors mb-2">
          Banu Özyılmaz
        </a>
        <p class="text-sm text-[var(--color-text-secondary)] font-medium">Researcher</p>
      </div>
      <div class="card-container flex flex-col items-center text-center group hover:scale-105 transition-transform duration-300">
        <div class="w-32 h-32 mb-4">
          <div class="w-full bg-center bg-no-repeat aspect-square bg-cover rounded-full shadow-lg border-4 border-white" 
               style="background-image: url('/team/gennadii-ershov.jpg'), linear-gradient(135deg, var(--color-secondary), var(--color-accent))">
            <div class="w-full h-full rounded-full bg-gradient-to-br from-[var(--color-secondary)] to-[var(--color-accent)] flex items-center justify-center text-white font-bold text-xl [background-image:none]">
              GE
            </div>
          </div>
        </div>
        <a href="https://github.com/GennadiiErshov" target="_blank" rel="noopener noreferrer" 
           class="text-lg font-bold text-[var(--color-primary)] hover:text-[var(--color-accent)] transition-colors mb-2">
          Gennadii Ershov
        </a>
        <p class="text-sm text-[var(--color-text-secondary)] font-medium">Researcher</p>
      </div>
      <div class="card-container flex flex-col items-center text-center group hover:scale-105 transition-transform duration-300">
        <div class="w-32 h-32 mb-4">
          <div class="w-full bg-center bg-no-repeat aspect-square bg-cover rounded-full shadow-lg border-4 border-white" 
               style="background-image: url('/team/muhammad-shahroz.jpg'), linear-gradient(135deg, var(--color-accent), var(--color-primary))">
            <div class="w-full h-full rounded-full bg-gradient-to-br from-[var(--color-accent)] to-[var(--color-primary)] flex items-center justify-center text-white font-bold text-xl [background-image:none]">
              MS
            </div>
          </div>
        </div>
        <a href="https://github.com/Shahroz657" target="_blank" rel="noopener noreferrer" 
           class="text-lg font-bold text-[var(--color-primary)] hover:text-[var(--color-accent)] transition-colors mb-2">
          Muhammad Shahroz
        </a>
        <p class="text-sm text-[var(--color-text-secondary)] font-medium">Researcher</p>
      </div>
      <div class="card-container flex flex-col items-center text-center group hover:scale-105 transition-transform duration-300">
        <div class="w-32 h-32 mb-4">
          <div class="w-full bg-center bg-no-repeat aspect-square bg-cover rounded-full shadow-lg border-4 border-white" 
               style="background-image: url('/team/muhammet-isik.jpg'), linear-gradient(135deg, var(--color-primary), var(--color-secondary))">
            <div class="w-full h-full rounded-full bg-gradient-to-br from-[var(--color-primary)] to-[var(--color-secondary)] flex items-center justify-center text-white font-bold text-xl [background-image:none]">
              MI
            </div>
          </div>
        </div>
        <a href="https://github.com/misik-eng" target="_blank" rel="noopener noreferrer" 
           class="text-lg font-bold text-[var(--color-primary)] hover:text-[var(--color-accent)] transition-colors mb-2">
          Muhammet Isik
        </a>
        <p class="text-sm text-[var(--color-text-secondary)] font-medium">Researcher</p>
      </div>
      <div class="card-container flex flex-col items-center text-center group hover:scale-105 transition-transform duration-300">
        <div class="w-32 h-32 mb-4">
          <div class="w-full bg-center bg-no-repeat aspect-square bg-cover rounded-full shadow-lg border-4 border-white" 
               style="background-image: url('/team/niloufar-ahadi.jpg'), linear-gradient(135deg, var(--color-accent), var(--color-secondary))">
            <div class="w-full h-full rounded-full bg-gradient-to-br from-[var(--color-accent)] to-[var(--color-secondary)] flex items-center justify-center text-white font-bold text-xl [background-image:none]">
              NA
            </div>
          </div>
        </div>
        <a href="https://github.com/NiloufarAhadi" target="_blank" rel="noopener noreferrer" 
           class="text-lg font-bold text-[var(--color-primary)] hover:text-[var(--color-accent)] transition-colors mb-2">
          Niloufar Ahadi
        </a>
        <p class="text-sm text-[var(--color-text-secondary)] font-medium">Researcher</p>
      </div>
      <div class="card-container flex flex-col items-center text-center group hover:scale-105 transition-transform duration-300">
        <div class="w-32 h-32 mb-4">
          <div class="w-full bg-center bg-no-repeat aspect-square bg-cover rounded-full shadow-lg border-4 border-white" 
               style="background-image: url('/team/ramon-colmenares.jpg'), linear-gradient(135deg, var(--color-secondary), var(--color-primary))">
            <div class="w-full h-full rounded-full bg-gradient-to-br from-[var(--color-secondary)] to-[var(--color-primary)] flex items-center justify-center text-white font-bold text-xl [background-image:none]">
              RC
            </div>
          </div>
        </div>
        <a href="https://github.com/RamonColmenares" target="_blank" rel="noopener noreferrer" 
           class="text-lg font-bold text-[var(--color-primary)] hover:text-[var(--color-accent)] transition-colors mb-2">
          Ramon Colmenares
        </a>
        <p class="text-sm text-[var(--color-text-secondary)] font-medium">Researcher</p>
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
</script>
