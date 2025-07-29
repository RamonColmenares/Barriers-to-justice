<script>
  import Header from '$lib/Header.svelte';
  import '../app.css';
</script>

<div class="relative flex size-full min-h-screen flex-col group/design-root overflow-x-hidden bg-[var(--color-background)]">
  <div class="layout-container flex h-full grow flex-col">
    <Header />
    
    <main class="flex-1">
      <slot></slot>
    </main>
    
    <footer class="bg-[var(--color-primary)] text-white">
      <div class="container mx-auto py-12 px-10">
        <div class="flex flex-col md:flex-row justify-between items-center text-center md:text-left">
          <div class="mb-6 md:mb-0">
            <h3 class="text-lg font-bold">Barriers to Justice</h3>
            <p class="text-sm text-gray-300">© 2025. All rights reserved.</p>
          </div>
          <div class="flex flex-wrap justify-center gap-6">
            <a class="hover:text-[var(--color-accent)] transition-colors" href="/about">About</a>
            <a class="hover:text-[var(--color-accent)] transition-colors" href="/data">Research</a>
            <a class="hover:text-[var(--color-accent)] transition-colors" href="/findings">Findings</a>
            <a class="hover:text-[var(--color-accent)] transition-colors" href="/resources">Resources</a>
            <a class="hover:text-[var(--color-accent)] transition-colors" href="/team">Team</a>
            <a class="hover:text-[var(--color-accent)] transition-colors" href="/contact">Contact</a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</div>
