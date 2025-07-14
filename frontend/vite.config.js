// vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/process_video': 'http://localhost:8000',
      '/chat': 'http://localhost:8000'
    }
  }
});