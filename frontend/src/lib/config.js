// API Configuration - Dynamic URL based on environment
import { env } from '$env/dynamic/public';

// Use the PUBLIC_API_URL environment variable set by deploy.sh
// If not set (development), fallback to localhost
export const API_BASE_URL = env.PUBLIC_API_URL || 'http://localhost:5000/api';
