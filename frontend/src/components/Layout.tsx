import React, { useState, useEffect } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import APIStatusBanner from './APIStatusBanner';
import ConnectivityStatus from './ConnectivityStatus';
import { useMock } from '../utils/mock';
import { checkCurrentRoute, runDiagnostics } from '../utils/diagnostics';
import ConfirmDialogStatus from './ConfirmDialogStatus';
import { useApiStatus } from '../contexts/ApiStatusContext';

const Layout: React.FC = () => {
  const [routeError, setRouteError] = useState<string | null>(null);
  const [layoutError, setLayoutError] = useState<Error | null>(null);
  const location = useLocation();
  const navigate = useNavigate();
  
  // Verificar se o modo mock está ativado
  const mockEnabled = useMock();
  
  // Usar o contexto global de status da API
  const { apiOnline } = useApiStatus();
  
  // Determinar se o container precisa de ajuste para o banner
  const isApiOffline = !apiOnline || mockEnabled;

  // Error Boundary para o layout
  useEffect(() => {
    const handleError = (error: ErrorEvent) => {
      console.error("Layout Error Boundary capturou:", error);
      setLayoutError(error.error);
    };

    window.addEventListener('error', handleError);
    return () => window.removeEventListener('error', handleError);
  }, []);

  // Verificar o status da rota atual
  useEffect(() => {
    try {
      const routeDiagnostic = checkCurrentRoute();
      console.log('Diagnóstico de rota:', routeDiagnostic);
      
      // Se houver problemas com a rota, registrar no estado
      if (routeDiagnostic.routeStatus === 'not_found') {
        setRouteError(`Rota não encontrada: ${routeDiagnostic.path}`);
        // Podemos redirecionar para uma página de erro ou para a página inicial
        // navigate('/');
      } else {
        setRouteError(null);
      }
      
      // Executar diagnóstico completo e salvar no localStorage
      runDiagnostics().then(result => {
        console.log('Diagnóstico completo:', result);
      }).catch(err => {
        console.error('Erro ao executar diagnóstico:', err);
      });
    } catch (error) {
      console.error('Erro ao verificar rota:', error);
      setRouteError('Erro ao verificar rota');
    }
  }, [location.pathname, navigate]);

  // Adicionar classe condicional com base no status da API ou modo mock
  const containerClass = `app-container${isApiOffline ? ' with-banner' : ''}`;
  
  // Renderizar mensagem de erro do layout se houver
  if (layoutError) {
    return (
      <div className="layout-error-container">
        <h1>Erro na Aplicação</h1>
        <p>Ocorreu um erro inesperado no layout da aplicação.</p>
        <p>Detalhes: {layoutError.message}</p>
        <button 
          className="btn-primary" 
          onClick={() => {
            setLayoutError(null);
            window.location.reload();
          }}
        >
          Recarregar Aplicação
        </button>
      </div>
    );
  }

  return (
    <>
      <APIStatusBanner />
      <div className={containerClass}>
        <Sidebar />
        <div className="main-content">
          <Header />
          <main className="page-container">
            {routeError ? (
              <div className="route-error-message">
                <h2>Problema ao acessar a página</h2>
                <p>{routeError}</p>
                <p>Verifique se a URL está correta ou se a API está disponível.</p>
                <button 
                  className="btn-primary" 
                  onClick={() => navigate('/')}
                >
                  Voltar para o Dashboard
                </button>
              </div>
            ) : (
              // Envolver o Outlet em um ErrorBoundary para evitar que erros no conteúdo quebrem o layout
              <React.Suspense fallback={<div>Carregando...</div>}>
                <ErrorBoundary>
                  <Outlet />
                </ErrorBoundary>
              </React.Suspense>
            )}
          </main>
        </div>
      </div>
      <ConnectivityStatus />
      <ConfirmDialogStatus />
    </>
  );
};

// Componente ErrorBoundary para capturar erros de renderização
class ErrorBoundary extends React.Component<{children: React.ReactNode}, {hasError: boolean, error: Error | null}> {
  constructor(props: {children: React.ReactNode}) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("Erro capturado pelo Error Boundary:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary-message">
          <h3>Erro no Carregamento da Página</h3>
          <p>Ocorreu um erro ao carregar esta página.</p>
          {this.state.error && (
            <p className="error-details">Detalhes: {this.state.error.message}</p>
          )}
          <button 
            className="btn-primary" 
            onClick={() => this.setState({ hasError: false, error: null })}
          >
            Tentar Novamente
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default Layout; 