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
  const previousDataLengthRef = useRef<number | undefined>(undefined);
  const showLoadingRef = useRef<boolean>(false);
  const mountedTimeRef = useRef<number>(Date.now());
  const contentReadyRef = useRef<boolean>(false);
  
  // Identificar se é um relatório para tratamento especial
  const isReportComponent = operationId.includes('dre') || operationId.includes('ciclo-operacional');
  
  // Nunca usar loading global para relatórios
  const shouldUseGlobalLoading = useGlobalLoading && !isReportComponent;
  
  // Usar estado local apenas para debounce do loading
  const [shouldShowLoadingIndicator, setShouldShowLoadingIndicator] = useState<boolean>(false);
  
  // Para relatórios, registrar imediatamente se temos dados
  useEffect(() => {
    // Registrar se já temos dados disponíveis 
    if (dataLength !== undefined && dataLength > 0) {
      contentReadyRef.current = true;
      previousDataLengthRef.current = dataLength;
    }
    
    // Para relatórios, NUNCA mostrar loading se já temos dados ou estamos em montagem inicial
    if (isReportComponent) {
      if (previousDataLengthRef.current && previousDataLengthRef.current > 0) {
        // Se já tínhamos dados anteriormente, não mostrar loading para relatórios
        showLoadingRef.current = false;
      } else {
        // Para primeira carga, só mostrar loading após um tempo mínimo
        const isInitialMount = Date.now() - mountedTimeRef.current < 300;
        showLoadingRef.current = loading && !isInitialMount;
      }
    } else {
      // Para componentes normais, seguir o loading normalmente
      showLoadingRef.current = loading;
    }
  }, [loading, dataLength, isReportComponent]);
  
  // Controlar o debounce para exibição do loading - evitar flash
  useEffect(() => {
    // Limpar qualquer timer existente
    let loadingTimer: number | undefined;
    
    // Se tivermos dados OU não estamos carregando, não precisamos do indicador
    if (contentReadyRef.current || !loading) {
      setShouldShowLoadingIndicator(false);
      return;
    }
    
    // Se estamos carregando e NÃO temos o indicador ativo ainda
    if (loading && !shouldShowLoadingIndicator && showLoadingRef.current) {
      // Relatórios precisam de mais tempo antes de mostrar loading
      const delay = isReportComponent ? 300 : 150;
      
      loadingTimer = window.setTimeout(() => {
        // Só mostrar o indicador se ainda estivermos carregando e não tivermos dados
        if (loading && !contentReadyRef.current) {
          setShouldShowLoadingIndicator(true);
        }
      }, delay);
    }
    
    return () => {
      if (loadingTimer) clearTimeout(loadingTimer);
    };
  }, [loading, shouldShowLoadingIndicator, isReportComponent]);
  
  // Ativar o loading global se necessário
  useEffect(() => {
    if (!shouldUseGlobalLoading) return;
    
    // Usar um ID consistente durante todo o ciclo de vida do componente
    const loadingId = loadingIdRef.current;
    
    if (loading) {
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
  }, [loading, shouldUseGlobalLoading, startLoading, stopLoading]);

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

  // Detectar quando temos dados disponíveis e cancelar o loading imediatamente
  useEffect(() => {
    // Se tiver dados disponíveis, marcar como pronto e esconder loading
    if (dataLength && dataLength > 0) {
      console.log(`[${operationId}] Dados disponíveis (${dataLength} itens), interrompendo loading`);
      
      // Parar loading global se necessário
      if (shouldUseGlobalLoading && loading) {
        stopLoading(loadingIdRef.current);
      }
      
      // Marcar que temos conteúdo pronto
      contentReadyRef.current = true;
      
      // Forçar esconder o indicador de loading imediatamente
      setShouldShowLoadingIndicator(false);
    }
  }, [dataLength, loading, operationId, stopLoading, shouldUseGlobalLoading]);

  // Função de retry com proteção
  const handleRetry = () => {
    if (retryDisabled || !onRetry) return;
    
    // Resetar flag de conteúdo pronto quando tentar novamente
    contentReadyRef.current = false;
    onRetry();
  };

  // Verificar se deve realmente mostrar o loading
  const shouldRenderLoadingUI = loading && 
                            (!shouldUseGlobalLoading || !useGlobalLoading) && 
                            !dataLength && 
                            showLoadingRef.current &&
                            shouldShowLoadingIndicator;
  
  // Se temos dados, sempre mostramos o conteúdo, mesmo durante carregamento
  if (dataLength && dataLength > 0) {
    return <>{children}</>;
  }

  // Exibir mensagem de carregamento
  if (shouldRenderLoadingUI) {
    return (
      <div className="p-6 flex flex-col items-center justify-center" aria-live="polite" role="status">
        <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500"></div>
        <p className="mt-3 text-sm text-gray-600">Carregando dados...</p>
      </div>
    );
  }

  // Exibir mensagem de erro, se houver
  if (error && !loading) {
    return (
      <div className="p-6 text-center">
        <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Ocorreu um erro ao carregar os dados</h3>
              <div className="mt-2 text-sm text-red-700">
                <p>{error}</p>
              </div>
            </div>
          </div>
        </div>
        {onRetry && (
          <button
            onClick={handleRetry}
            className="mt-2 px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
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
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 text-center m-2" aria-live="polite">
        <svg 
          className="mx-auto h-12 w-12 text-gray-400" 
          xmlns="http://www.w3.org/2000/svg" 
          fill="none" 
          viewBox="0 0 24 24" 
          stroke="currentColor"
        >
          <path 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            strokeWidth={1.5} 
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" 
          />
        </svg>
        <p className="mt-2 text-gray-600">{emptyMessage}</p>
        {isMockEnabled && (
          <p className="mt-2 text-sm text-orange-600">
            Modo de demonstração ativo: Exibindo dados simulados.
          </p>
        )}
        {!isMockEnabled && error && (
          <p className="mt-2 text-sm text-red-600">
            Erro de conexão com a API. Verifique se o servidor está online.
          </p>
        )}
      </div>
    );
  }

  // Renderizar o conteúdo se não estivermos mostrando nenhum dos estados acima
  return <>{children}</>;
};

export default DataStateHandler; 