import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Carrega variáveis de ambiente com prefixo "VITE_"
  const env = loadEnv(mode, process.cwd(), '')
  
  console.log('=== Configuração de ambiente ===')
  console.log(`API URL: ${env.VITE_API_URL || 'http://localhost:8000'}`)
  console.log(`Porta: ${env.VITE_PORT || '3000'}`)
  console.log(`Modo de mock: ${env.VITE_MOCK_ENABLED || 'false'}`)
  console.log(`Forçar porta: ${env.VITE_FORCE_PORT || 'false'}`)
  console.log(`Ambiente: ${mode}`)
  console.log('==============================')
  
  // Verifica se deve forçar o uso da porta especificada
  const forcePort = env.VITE_FORCE_PORT === 'true'
  const port = parseInt(env.VITE_PORT || '3000', 10)
  
  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src')
      }
    },
    server: {
      port: port,
      strictPort: forcePort, // Se true, o servidor falhará se a porta já estiver em uso
      proxy: {
        '/api': {
          target: env.VITE_API_URL || 'http://localhost:8000',
          changeOrigin: true,
        }
      }
    },
    // Configurações adicionais para ambiente de produção
    build: {
      outDir: 'dist',
      sourcemap: mode !== 'production',
      minify: mode === 'production',
      chunkSizeWarningLimit: 1600,
    }
  }
}) 