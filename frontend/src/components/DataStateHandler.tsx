import React, { ReactNode, useEffect, useRef, useState } from 'react';
import { useLoading } from '../contexts/LoadingContext';
import { useMock } from '../utils/mock';

interface DataStateHandlerProps {
  loading: boolean;
  error?: string | null;
  dataLength?: number;
  onRetry?: () => void;
  emptyMessage?: string;
  children: ReactNode;
  useGlobalLoading?: boolean;
  operationId?: string;
  retryCount?: number;
  maxRetries?: number;
}

/**
 * Componente reutilizável para lidar com os estados de dados
 * 
 * @param loading - Indica se os dados estão carregando
 * @param error - Mensagem de erro, se houver
 * @param dataLength - Tamanho dos dados (para verificar se estão vazios)
 * @param onRetry - Função para tentar novamente em caso de erro
 * @param emptyMessage - Mensagem a ser exibida quando não há dados
 * @param useGlobalLoading - Define se deve usar o overlay global de carregamento
 * @param operationId - ID opcional para identificar a operação de carregamento
 * @param retryCount - Contador de tentativas de carregamento
 * @param maxRetries - Número máximo de tentativas permitidas
 * @param children - Conteúdo a ser renderizado quando não há erros e os dados estão disponíveis
 */
const DataStateHandler: React.FC<DataStateHandlerProps> = ({
  loading,
  error,
  dataLength,
  onRetry,
  emptyMessage = "Nenhum registro encontrado.",
  children,
  useGlobalLoading = false,
  operationId = 'data-fetch',
  retryCount = 0,
  maxRetries = 3
}) => {
  const { startLoading, stopLoading } = useLoading();
  const loadingIdRef = useRef<string>(`${operationId}-${Date.now()}`);
  const isMockEnabled = useMock();
  const [retryDisabled, setRetryDisabled] = useState(false);
  
  // Referências para tracking de dados
  const previousDataLengthRef = useRef<number | undefined>(undefined);
  const contentReadyRef = useRef<boolean>(false);
  
  // Detectar se estamos lidando com um relatório (DRE ou Ciclo Operacional)
  const isReportPage = operationId.includes('dre') || operationId.includes('ciclo');
  
  // Nunca usar loading global para relatórios
  const shouldUseGlobalLoading = useGlobalLoading && !isReportPage;
  
  // Usar estado local para controlar o indicador de loading com debounce inteligente
  const [showLocalLoadingIndicator, setShowLocalLoadingIndicator] = useState<boolean>(false);
  
  // Para relatórios, registrar imediatamente se temos dados
  useEffect(() => {
    // Registrar se já temos dados disponíveis 
    if (dataLength !== undefined && dataLength > 0) {
      contentReadyRef.current = true;
      previousDataLengthRef.current = dataLength;
      
      // Forçar esconder loading imediatamente quando temos dados
      setShowLocalLoadingIndicator(false);
    }
  }, [dataLength]);
  
  // Controle de exibição do loading - com delay muito reduzido para relatórios
  useEffect(() => {
    // Limpar qualquer timer existente
    let loadingTimer: number | undefined;
    
    // Se tivermos dados OU não estamos carregando, não precisamos do indicador
    if ((dataLength && dataLength > 0) || !loading) {
      setShowLocalLoadingIndicator(false);
      return;
    }
    
    // Se estamos carregando e NÃO temos dados
    if (loading && !dataLength) {
      // Usar delay extremamente reduzido para mostrar loading
      // Para relatórios, usar 100ms em vez de 300ms
      const delay = isReportPage ? 100 : 50;
      
      loadingTimer = window.setTimeout(() => {
        // Verificar novamente se ainda estamos carregando e se não temos dados
        if (loading && (!dataLength || dataLength === 0)) {
          setShowLocalLoadingIndicator(true);
        }
      }, delay);
    }
    
    return () => {
      if (loadingTimer) clearTimeout(loadingTimer);
    };
  }, [loading, dataLength, isReportPage]);
  
  // Gerenciar loading global
  useEffect(() => {
    if (!shouldUseGlobalLoading) return;
    
    // Usar um ID consistente durante todo o ciclo de vida do componente
    const loadingId = loadingIdRef.current;
    
    if (loading && !contentReadyRef.current) {
      startLoading(loadingId);
    } else {
      stopLoading(loadingId);
    }
    
    // Limpar o loading global quando o componente for desmontado
    return () => {
      if (shouldUseGlobalLoading) {
        stopLoading(loadingId);
      }
    };
  }, [loading, shouldUseGlobalLoading, startLoading, stopLoading, contentReadyRef]);

  // Desabilitar botão de retry após muitas tentativas
  useEffect(() => {
    if (retryCount >= maxRetries) {
      setRetryDisabled(true);
      
      // Reativar após 1 minuto
      const timer = setTimeout(() => {
        setRetryDisabled(false);
      }, 60000);
      
      return () => clearTimeout(timer);
    }
  }, [retryCount, maxRetries]);

  // Função de retry com proteção
  const handleRetry = () => {
    if (retryDisabled || !onRetry) return;
    
    // Resetar flag de conteúdo pronto quando tentar novamente
    contentReadyRef.current = false;
    onRetry();
  };
  
  // IMPORTANTE: Se temos dados, sempre mostramos o conteúdo, mesmo durante carregamento
  // Isto elimina o problema de flicker quando recarregamos dados
  if (dataLength && dataLength > 0) {
    return <>{children}</>;
  }

  // Exibir mensagem de carregamento com animação suave
  if (loading && showLocalLoadingIndicator) {
    return (
      <div className="data-state-loading" aria-live="polite" role="status">
        <div className="spinner"></div>
        <p>Carregando dados...</p>
      </div>
    );
  }

  // Exibir mensagem de erro, se houver
  if (error && !loading) {
    return (
      <div className="data-state-error">
        <div className="error-icon">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
        </div>
        <h3>Ocorreu um erro ao carregar os dados</h3>
        <p>{error}</p>
        {onRetry && (
          <button
            onClick={handleRetry}
            className="btn btn-sm btn-primary"
            disabled={retryDisabled}
          >
            Tentar novamente
          </button>
        )}
      </div>
    );
  }

  // Exibir mensagem de dados vazios se aplicável
  if (dataLength !== undefined && dataLength === 0 && !loading) {
    return (
      <div className="data-state-empty" aria-live="polite">
        <div className="empty-icon">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M9 17h6M9 12h6M9 7h6" />
            <path d="M5 22h14a2 2 0 002-2V4a2 2 0 00-2-2H5a2 2 0 00-2 2v16a2 2 0 002 2z" />
          </svg>
        </div>
        <p>{emptyMessage}</p>
        {isMockEnabled && (
          <p className="empty-message-detail">
            Modo de demonstração ativo: Exibindo dados simulados.
          </p>
        )}
      </div>
    );
  }

  // Renderizar o conteúdo sem delay se nenhum estado especial acima
  // Esta mudança é crucial para evitar telas em branco durante o carregamento inicial
  return <>{children}</>;
};

export default DataStateHandler; 