import { defineConfig } from 'vite'

export default defineConfig({
  plugins: ['react'],
  root: '.',
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      },
      '/socket.io': {
        target: 'ws://localhost:8000/socket.io',
        changeOrigin: true,
        ws: true
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  },
  resolve: {
    alias: {
      '@': './src'
    }
  }
})
