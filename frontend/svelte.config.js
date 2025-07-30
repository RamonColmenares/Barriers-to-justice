import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';
import adapter from '@sveltejs/adapter-static';
import preprocess from 'svelte-preprocess';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  // Consult https://kit.svelte.dev/docs/integrations#preprocessors
  // for more information about preprocessors
  preprocess: [
    vitePreprocess(),
    preprocess({
      postcss: true,
    }),
  ],

  kit: {
    // adapter-static generates static files for S3/CDN deployment
    adapter: adapter({
      fallback: 'index.html',
      precompress: false,
      strict: false
    }),
    prerender: {
      handleHttpError: 'warn'
    },
  },
};

export default config;
