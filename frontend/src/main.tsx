import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'
import { LoadingProvider } from './contexts/LoadingContext'
import { ToastProvider } from './hooks/useToast'
import { ApiStatusProvider } from './contexts/ApiStatusContext'

// Suprimir avisos de futuras alterações do React Router
// Isso evita o aviso sobre "Relative route resolution within Splat routes"
// @ts-ignore
window.ROUTER_WARNINGS_DISABLED = true;

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ApiStatusProvider>
      <LoadingProvider>
        <ToastProvider>
          <App />
        </ToastProvider>
      </LoadingProvider>
    </ApiStatusProvider>
  </React.StrictMode>,
) 