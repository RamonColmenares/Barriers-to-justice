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

<div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
  <div class="max-w-md w-full text-center">
    <div class="mb-8">
      <div class="text-6xl font-bold text-indigo-600 mb-4">
        {status || '404'}
      </div>
      <h1 class="text-3xl font-bold text-gray-900 mb-4">
        {#if status === 404}
          Page Not Found
        {:else if status === 500}
          Server Error
        {:else}
          Something went wrong
        {/if}
      </h1>
      <p class="text-gray-600 mb-8">
        {#if status === 404}
          The page you're looking for doesn't exist or has been moved.
        {:else if status === 500}
          We're experiencing some technical difficulties. Please try again later.
        {:else}
          {error?.message || 'An unexpected error occurred.'}
        {/if}
      </p>
    </div>
    
    <div class="space-y-4">
      <button 
        on:click={goHome}
        class="w-full bg-indigo-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-indigo-700 transition-colors duration-200"
      >
        Go Home
      </button>
      
      <button 
        on:click={() => window.history.back()}
        class="w-full border border-gray-300 text-gray-700 py-3 px-6 rounded-lg font-semibold hover:bg-gray-50 transition-colors duration-200"
      >
        Go Back
      </button>
    </div>
    
    <div class="mt-8 text-sm text-gray-500">
      <p>
        If you believe this is an error, please 
        <a href="/contact" class="text-indigo-600 hover:text-indigo-800 underline">
          contact us
        </a>
      </p>
    </div>
  </div>
</div>

<style>
  /* Add some animation to the error number */
  .text-6xl {
    animation: pulse 2s infinite;
  }
  
  @keyframes pulse {
    0%, 100% {
      opacity: 1;
    }
    50% {
      opacity: 0.7;
    }
  }
</style>
