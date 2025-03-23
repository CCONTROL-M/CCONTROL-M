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
  const location = useLocation();
  const navigate = useNavigate();
  
  // Verificar se o modo mock está ativado
  const mockEnabled = useMock();
  
  // Usar o contexto global de status da API
  const { apiOnline } = useApiStatus();
  
  // Determinar se o container precisa de ajuste para o banner
  const isApiOffline = !apiOnline || mockEnabled;

  // Verificar o status da rota atual
  useEffect(() => {
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
    });
  }, [location.pathname, navigate]);

  // Adicionar classe condicional com base no status da API ou modo mock
  const containerClass = `app-container${isApiOffline ? ' with-banner' : ''}`;

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
              <Outlet />
            )}
          </main>
        </div>
      </div>
      <ConnectivityStatus />
      <ConfirmDialogStatus />
    </>
  );
};

export default Layout; 