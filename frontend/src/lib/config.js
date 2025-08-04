// API Configuration - Dynamic URL based on environment
import { env } from '$env/dynamic/public';

// Use the PUBLIC_API_URL environment variable set by deploy.sh
// If not set (development), fallback to localhost
export const API_BASE_URL = env.PUBLIC_API_URL || 'http://localhost:5000/api';

// Log configuration in development
if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
  console.log('API Configuration:', {
    API_BASE_URL,
    PUBLIC_API_URL: env.PUBLIC_API_URL
  });
}
