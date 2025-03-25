import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import { configDefaults } from 'vitest/config'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Carrega variáveis de ambiente com prefixo "VITE_"
  const env = loadEnv(mode, process.cwd(), '')
  
  // Logs apenas em ambiente de desenvolvimento
  if (mode === 'development') {
    console.log('=== Configuração de ambiente ===')
    console.log(`API URL: ${env.VITE_API_URL || 'http://127.0.0.1:8002/api/v1'}`)
    console.log(`Forçar porta: ${env.VITE_FORCE_PORT || 'false'}`)
    console.log(`Ambiente: ${mode}`)
    console.log('==============================')
  }
  
  // Porta para o servidor de desenvolvimento
  const port = parseInt(env.VITE_PORT || '3001', 10)
  
  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src')
      }
    },
    server: {
      port: port,
      strictPort: false, // Permitir que o Vite procure outra porta se a configurada estiver em uso
      proxy: {
        '/api': {
          target: env.VITE_API_URL || 'http://127.0.0.1:8002/api/v1',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
          configure: (proxy, _options) => {
            proxy.on('error', (err, _req, _res) => {
              if (mode === 'development') {
                console.log('Erro de proxy:', err);
              }
            });
            proxy.on('proxyReq', (proxyReq, req, _res) => {
              if (mode === 'development') {
                console.log('Requisição de proxy:', req.method, req.url);
              }
            });
          }
        }
      }
    },
    // Configurações adicionais para ambiente de produção
    build: {
      outDir: 'dist',
      sourcemap: mode !== 'production',
      minify: mode === 'production' ? 'terser' : false,
      terserOptions: {
        compress: {
          drop_console: mode === 'production', // Remove console.log em produção
          drop_debugger: mode === 'production' // Remove debugger statements em produção
        }
      },
      chunkSizeWarningLimit: 1600,
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom', 'react-router-dom'],
            charts: ['recharts'],
            ui: ['react-bootstrap', 'bootstrap']
          }
        }
      }
    },
    // Configuração para testes com Vitest
    test: {
      globals: true,
      environment: 'jsdom',
      setupFiles: ['./src/setupTests.ts'],
      css: false, // Ignorar importações de CSS durante os testes
      coverage: {
        provider: 'v8',
        reporter: ['text', 'html'],
        exclude: [
          'node_modules/**',
          'dist/**',
          '**/*.d.ts',
          '**/*.test.{ts,tsx}',
          'src/vite-env.d.ts',
        ],
      },
      include: ['src/**/*.{test,spec}.{ts,tsx}'],
      exclude: [...configDefaults.exclude, 'e2e/**', '.next/**', 'node_modules/**'],
    }
  }
}) 