<header class="sticky top-0 z-50 bg-white/80 backdrop-blur-md shadow-sm">
  <div class="container mx-auto flex items-center justify-between whitespace-nowrap px-10 py-4">
    <div class="flex items-center gap-3 text-[var(--color-primary)]">
      <svg class="h-8 w-8" fill="none" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM12 20C7.59 20 4 16.41 4 12C4 7.59 7.59 4 12 4C16.41 4 20 7.59 20 12C20 16.41 16.41 20 12 20ZM12 6L10 10H14L12 6ZM8.5 12L12 18L15.5 12H8.5Z" fill="currentColor"></path>
      </svg>
      <a href="/" class="text-xl font-bold tracking-tight hover:text-[var(--color-accent)] transition-colors">Barriers to Justice</a>
    </div>
    <nav class="hidden lg:flex items-center gap-8">
      <a class="text-[var(--color-text-primary)] hover:text-[var(--color-accent)] transition-colors text-base font-medium" href="/about">About</a>
      <a class="text-[var(--color-text-primary)] hover:text-[var(--color-accent)] transition-colors text-base font-medium" href="/data">Research</a>
      <a class="text-[var(--color-text-primary)] hover:text-[var(--color-accent)] transition-colors text-base font-medium" href="/findings">Findings</a>
      <a class="text-[var(--color-text-primary)] hover:text-[var(--color-accent)] transition-colors text-base font-medium" href="/resources">Resources</a>
      <a class="text-[var(--color-text-primary)] hover:text-[var(--color-accent)] transition-colors text-base font-medium" href="/team">Team</a>
      <a class="text-[var(--color-text-primary)] hover:text-[var(--color-accent)] transition-colors text-base font-medium" href="/contact">Contact</a>
    </nav>
    <button class="lg:hidden text-[var(--color-primary)]" on:click={toggleMobileMenu} aria-label="Toggle mobile menu">
      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        {#if showMobileMenu}
          <path d="M6 18L18 6M6 6l12 12" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
        {:else}
          <path d="M4 6h16M4 12h16m-7 6h7" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
        {/if}
      </svg>
    </button>
  </div>
  
  <!-- Mobile Menu -->
  {#if showMobileMenu}
    <div class="lg:hidden bg-white/95 backdrop-blur-md border-t border-gray-200">
      <nav class="container mx-auto px-10 py-4 flex flex-col gap-4">
        <a class="text-[var(--color-text-primary)] hover:text-[var(--color-accent)] transition-colors text-base font-medium py-2" href="/about" on:click={() => showMobileMenu = false}>About</a>
        <a class="text-[var(--color-text-primary)] hover:text-[var(--color-accent)] transition-colors text-base font-medium py-2" href="/data" on:click={() => showMobileMenu = false}>Research</a>
        <a class="text-[var(--color-text-primary)] hover:text-[var(--color-accent)] transition-colors text-base font-medium py-2" href="/findings" on:click={() => showMobileMenu = false}>Findings</a>
        <a class="text-[var(--color-text-primary)] hover:text-[var(--color-accent)] transition-colors text-base font-medium py-2" href="/resources" on:click={() => showMobileMenu = false}>Resources</a>
        <a class="text-[var(--color-text-primary)] hover:text-[var(--color-accent)] transition-colors text-base font-medium py-2" href="/team" on:click={() => showMobileMenu = false}>Team</a>
        <a class="text-[var(--color-text-primary)] hover:text-[var(--color-accent)] transition-colors text-base font-medium py-2" href="/contact" on:click={() => showMobileMenu = false}>Contact</a>
      </nav>
    </div>
  {/if}
</header>

<script>
  let showMobileMenu = false;
  
  function toggleMobileMenu() {
    showMobileMenu = !showMobileMenu;
  }
</script>
