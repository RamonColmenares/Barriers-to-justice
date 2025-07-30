import { error } from '@sveltejs/kit';

// This will make sure all dynamic routes fallback to client-side rendering
export const fallback = 'index.html';
