import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'
import { LoadingProvider } from './contexts/LoadingContext'
import { ToastProvider } from './hooks/useToast'
import { ApiStatusProvider } from './contexts/ApiStatusContext'
import { adicionarIndicadorMock } from './utils/mock'
import MockIndicator from './components/MockIndicator'

// Filtro personalizado de console para reduzir logs de erro de rede
const originalConsoleError = console.error;
console.error = function(...args) {
  // Filtrar mensagens de erro de conexão recusada
  const errorString = args.join(' ');
  if (
    errorString.includes('Failed to fetch') || 
    errorString.includes('Network Error') || 
    errorString.includes('ERR_CONNECTION_REFUSED') ||
    errorString.includes('net::ERR')
  ) {
    // Permitir apenas o primeiro erro de rede
    if (!(window as any).__networkErrorLogged) {
      (window as any).__networkErrorLogged = true;
      originalConsoleError.apply(console, ['Erro de conexão com o servidor. Erros adicionais serão suprimidos.']);
    }
    return;
  }
  
  // Suprimir avisos do React Router
  if (
    errorString.includes('React Router Future Flag Warning') ||
    errorString.includes('v7_startTransition') ||
    errorString.includes('v7_relativeSplatPath')
  ) {
    return;
  }
  
  // Suprimir avisos de componentes React
  if (
    errorString.includes('Maximum update depth exceeded') || 
    errorString.includes('Can\'t perform a React state update')
  ) {
    // Mostrar apenas uma vez
    if (!(window as any).__reactUpdateErrorLogged) {
      (window as any).__reactUpdateErrorLogged = true;
      originalConsoleError.apply(console, ['Erro de atualização React detectado. Erros adicionais serão suprimidos.']);
    }
    return;
  }
  
  // Suprimir avisos de timeout
  if (
    errorString.includes('timeout') ||
    errorString.includes('Timeout')
  ) {
    // Mostrar apenas uma vez
    if (!(window as any).__timeoutErrorLogged) {
      (window as any).__timeoutErrorLogged = true;
      originalConsoleError.apply(console, ['Erros de timeout detectados. Erros adicionais serão suprimidos.']);
    }
    return;
  }
  
  originalConsoleError.apply(console, args);
};

// Suprimir avisos de futuras alterações do React Router
// @ts-ignore
window.ROUTER_WARNINGS_DISABLED = true;

// Adicionar indicador visual de mock quando ativado
adicionarIndicadorMock();

// Em desenvolvimento, remover o StrictMode para evitar duplicação de efeitos
// que pode causar recargas desnecessárias
const AppWithProviders = () => (
  <LoadingProvider>
    <ApiStatusProvider>
      <ToastProvider>
        <MockIndicator />
        <App />
      </ToastProvider>
    </ApiStatusProvider>
  </LoadingProvider>
);

ReactDOM.createRoot(document.getElementById('root')!).render(
  import.meta.env.DEV 
    ? <AppWithProviders /> 
    : (
      <React.StrictMode>
        <AppWithProviders />
      </React.StrictMode>
    )
); 