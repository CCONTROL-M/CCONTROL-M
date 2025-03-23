import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useMock, toggleMock } from '../utils/mock';
import { checkCurrentRoute } from '../utils/diagnostics';
import { useApiStatus } from '../contexts/ApiStatusContext';

type ApiStatusType = {
  status: 'online' | 'offline' | 'loading';
  error: string | null;
  timestamp: number;
};

/**
 * Componente para mostrar informações sobre o status de conectividade
 * Útil para diagnosticar problemas de roteamento e conexão com a API
 */
const ConnectivityStatus: React.FC = () => {
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [routeInfo, setRouteInfo] = useState({
    path: '',
    isValid: true,
    suggestion: ''
  });
  
  const navigate = useNavigate();
  const location = useLocation();
  
  // Usar o contexto global de status da API
  const { apiOnline, mensagemErro, ultimaVerificacao, forcarVerificacao } = useApiStatus();
  
  // Converter para o formato local ApiStatusType
  const apiStatus: ApiStatusType = {
    status: apiOnline ? 'online' : 'offline',
    error: mensagemErro,
    timestamp: ultimaVerificacao ? ultimaVerificacao.getTime() : Date.now()
  };
  
  useEffect(() => {
    // Verificar status da rota ao montar e quando a localização mudar
    checkCurrentRouteStatus();
  }, [location.pathname]);
  
  const checkCurrentRouteStatus = () => {
    const result = checkCurrentRoute();
    setRouteInfo({
      path: location.pathname,
      isValid: result.routeStatus === 'registered',
      suggestion: result.routeStatus === 'registered' ? '' : 'Tente ir para a página inicial'
    });
  };
  
  const handleReload = () => {
    window.location.reload();
  };
  
  const handleNavigateHome = () => {
    navigate('/');
    setIsOpen(false);
  };
  
  const handleToggleMockMode = () => {
    toggleMock();
    window.location.reload();
  };
  
  const handleCheckApiStatus = () => {
    forcarVerificacao();
  };
  
  const isMockMode = () => useMock();
  
  const iconClass = `connectivity-icon ${
    isMockMode() 
      ? 'connectivity-mock' 
      : apiStatus.status === 'online' 
        ? 'connectivity-online' 
        : 'connectivity-offline'
  }`;
  
  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString();
  };
  
  return (
    <>
      {!isOpen ? (
        <button 
          className={iconClass}
          onClick={() => setIsOpen(true)}
          title="Status de Conectividade"
        >
          {isMockMode() ? 'M' : apiStatus.status === 'online' ? '✓' : '×'}
        </button>
      ) : (
        <div className="connectivity-panel">
          <div className="connectivity-header">
            <h3>Status do Sistema</h3>
            <button className="connectivity-close" onClick={() => setIsOpen(false)}>×</button>
          </div>
          
          <div className="connectivity-content">
            <div className="connectivity-section">
              <h4>API</h4>
              <div className={`status-indicator ${
                apiStatus.status === 'online' ? 'status-online' : 'status-offline'
              }`}>
                {apiStatus.status === 'online' ? 'Conectado' : 'Desconectado'}
              </div>
              
              {apiStatus.error && (
                <div className="connectivity-error">
                  Erro: {apiStatus.error}
                </div>
              )}
              
              <div className="connectivity-info">
                Última verificação: {formatTimestamp(apiStatus.timestamp)}
              </div>
              
              <button 
                className="btn btn-secondary btn-sm"
                onClick={handleCheckApiStatus}
                style={{ marginTop: '8px' }}
              >
                Verificar Agora
              </button>
            </div>
            
            <div className="connectivity-section">
              <h4>Modo Mock</h4>
              <div className={`status-indicator ${isMockMode() ? 'status-mock' : 'status-normal'}`}>
                {isMockMode() ? 'Ativado' : 'Desativado'}
              </div>
              <div className="connectivity-info">
                {isMockMode() 
                  ? 'O sistema está usando dados simulados.' 
                  : 'O sistema está usando dados reais.'}
              </div>
            </div>
            
            <div className="connectivity-section">
              <h4>Rota Atual</h4>
              <div className={`status-indicator ${routeInfo.isValid ? 'status-ok' : 'status-error'}`}>
                {routeInfo.isValid ? 'Válida' : 'Problema Detectado'}
              </div>
              
              <div className="connectivity-path">
                {routeInfo.path || '/'}
              </div>
              
              {!routeInfo.isValid && routeInfo.suggestion && (
                <div className="connectivity-error">
                  Sugestão: {routeInfo.suggestion}
                </div>
              )}
            </div>
            
            <div className="connectivity-actions">
              <button 
                className="btn btn-secondary btn-sm"
                onClick={handleNavigateHome}
              >
                Ir para Home
              </button>
              
              <button 
                className="btn btn-secondary btn-sm"
                onClick={handleReload}
              >
                Recarregar
              </button>
              
              <button 
                className="btn btn-secondary btn-sm"
                onClick={handleToggleMockMode}
              >
                {isMockMode() ? 'Desativar Mock' : 'Ativar Mock'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ConnectivityStatus; 