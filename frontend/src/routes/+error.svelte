<script>
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  
  // Get the error status from the page store
  $: status = $page.status;
  $: error = $page.error;
  
  function goHome() {
    goto('/');
  }
</script>

<div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4 py-8">
  <div class="max-w-md w-full text-center">
    <div class="mb-12">
      <div class="text-6xl font-bold text-indigo-500 mb-6">
        {status || '404'}
      </div>
      <h1 class="text-3xl font-bold text-gray-800 mb-6">
        {#if status === 404}
          Page Not Found
        {:else if status === 500}
          Temporary Issue
        {:else}
          Something's Not Right
        {/if}
      </h1>
      <p class="text-gray-600 mb-8 px-4">
        {#if status === 404}
          The page you're looking for seems to have moved or doesn't exist.
        {:else if status === 500}
          We're experiencing some technical difficulties. We'll have this fixed soon!
        {:else}
          {error?.message || 'Don\'t worry, these things happen sometimes.'}
        {/if}
      </p>
    </div>
    
    <div class="space-y-4 mb-8">
      <button 
        on:click={goHome}
        class="w-full bg-indigo-500 text-white py-3 px-6 rounded-lg font-semibold hover:bg-indigo-600 transition-colors duration-200"
      >
        Take Me Home
      </button>
      
      <button 
        on:click={() => window.history.back()}
        class="w-full border border-gray-300 text-gray-700 py-3 px-6 rounded-lg font-semibold hover:bg-gray-50 transition-colors duration-200"
      >
        Go Back
      </button>
    </div>
    
    <div class="text-sm text-gray-500 px-4">
      <p>
        Need help? Feel free to 
        <a href="/contact" class="text-indigo-500 hover:text-indigo-700 underline">
          get in touch
        </a>
      </p>
    </div>
  </div>
</div>

<style>
  /* Add some smooth animation to the error number */
  .text-6xl {
    animation: gentlePulse 3s ease-in-out infinite;
  }
  
  @keyframes gentlePulse {
    0%, 100% {
      opacity: 1;
      transform: scale(1);
    }
    50% {
      opacity: 0.8;
      transform: scale(1.02);
    }
  }
</style>
