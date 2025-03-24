import React, { createContext, useState, useContext, ReactNode, useEffect, useRef, useCallback } from 'react';
import LoadingOverlay from '../components/LoadingOverlay';

// Interface para o contexto de carregamento
interface LoadingContextType {
  isLoading: boolean;
  startLoading: (operationId?: string) => void;
  stopLoading: (operationId?: string) => void;
  setLoadingState: (loading: boolean) => void;
  activeOperationsCount: number;
  activeOperations: Set<string>;
  resetLoadingState: () => void;
}

// Criação do contexto
const LoadingContext = createContext<LoadingContextType | undefined>(undefined);

// Hook personalizado para usar o contexto
export const useLoading = (): LoadingContextType => {
  const context = useContext(LoadingContext);
  
  if (!context) {
    throw new Error('useLoading deve ser usado dentro de um LoadingProvider');
  }
  
  return context;
};

// Tempo de segurança máximo para carregamento (7 segundos - reduzido de 15)
const SAFETY_TIMEOUT = 7000;

// Debounce para atualizações no estado de loading (ms) - reduzido para ser mais responsivo
const DEBOUNCE_TIME = 50;

// Interface para as props do provider
interface LoadingProviderProps {
  children: ReactNode;
}

// Componente Provider
export const LoadingProvider: React.FC<LoadingProviderProps> = ({ children }) => {
  // Usando useRef para valores que não devem causar re-renderizações
  const isLoadingRef = useRef<boolean>(false);
  const activeOperationsRef = useRef<Set<string>>(new Set());
  const loadingCounterRef = useRef<number>(0);
  const safetyTimerIdRef = useRef<number | null>(null);
  const updateTimerRef = useRef<number | null>(null);
  
  // Estados que causarão re-renderizações quando atualizados
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [activeOperations, setActiveOperations] = useState<Set<string>>(new Set());
  const [loadingCounter, setLoadingCounter] = useState<number>(0);
  
  // Função para atualizar o estado de loading com debounce
  const updateLoadingState = useCallback(() => {
    // Limpar qualquer timer pendente
    if (updateTimerRef.current !== null) {
      window.clearTimeout(updateTimerRef.current);
      updateTimerRef.current = null;
    }
    
    // Configurar um timer para atualizar o estado de loading após debounce
    updateTimerRef.current = window.setTimeout(() => {
      // Atualizar state apenas se o valor for diferente para evitar re-renderizações desnecessárias
      if (isLoadingRef.current !== isLoading) {
        setIsLoading(isLoadingRef.current);
      }
      
      // Atualizar outros estados se necessário
      if (loadingCounterRef.current !== loadingCounter) {
        setLoadingCounter(loadingCounterRef.current);
      }
      
      // Atualizar operações ativas apenas se houve mudança
      if (activeOperationsRef.current.size !== activeOperations.size) {
        setActiveOperations(new Set(activeOperationsRef.current));
      }
      
      updateTimerRef.current = null;
    }, DEBOUNCE_TIME);
  }, [isLoading, loadingCounter, activeOperations]);
  
  // Iniciar temporizador de segurança
  const startSafetyTimer = useCallback(() => {
    if (safetyTimerIdRef.current) {
      window.clearTimeout(safetyTimerIdRef.current);
    }
    
    const timerId = window.setTimeout(() => {
      // Se ainda estiver carregando após o timeout
      if (isLoadingRef.current) {
        console.warn(`⚠️ Timeout de segurança atingido após ${SAFETY_TIMEOUT}ms. Operações ativas:`, 
          Array.from(activeOperationsRef.current).join(', '));
        
        // Forçar reset do estado de carregamento
        resetLoadingStateInternal();
      }
      
      safetyTimerIdRef.current = null;
    }, SAFETY_TIMEOUT);
    
    safetyTimerIdRef.current = Number(timerId);
  }, []);
  
  // Parar temporizador de segurança
  const stopSafetyTimer = useCallback(() => {
    if (safetyTimerIdRef.current) {
      window.clearTimeout(safetyTimerIdRef.current);
      safetyTimerIdRef.current = null;
    }
  }, []);

  // Função interna para resetar completamente o estado de carregamento
  const resetLoadingStateInternal = useCallback(() => {
    // Resetar todos os refs
    isLoadingRef.current = false;
    loadingCounterRef.current = 0;
    activeOperationsRef.current.clear();
    
    // Atualizar os estados React
    setIsLoading(false);
    setLoadingCounter(0);
    setActiveOperations(new Set());
    
    // Parar o timer de segurança
    stopSafetyTimer();
    
    console.log("Estado de carregamento resetado completamente");
  }, [stopSafetyTimer]);
  
  // Função exposta para resetar o estado de carregamento
  const resetLoadingState = useCallback(() => {
    resetLoadingStateInternal();
  }, [resetLoadingStateInternal]);
  
  // Ativar/desativar o loading com controle de contagem
  const startLoading = useCallback((operationId?: string) => {
    // Nunca iniciar loading para relatórios específicos
    if (operationId && (operationId.includes('dre') || operationId.includes('ciclo'))) {
      console.log(`[${operationId}] Loading global ignorado para relatório`);
      return;
    }
    
    // Incrementar contador
    loadingCounterRef.current += 1;
    
    // Atualizar estado de loading
    isLoadingRef.current = true;
    
    // Se um ID de operação foi fornecido, rastreá-lo
    if (operationId) {
      activeOperationsRef.current.add(operationId);
    }
    
    // Iniciar timer de segurança se ainda não estiver ativo
    if (safetyTimerIdRef.current === null) {
      startSafetyTimer();
    }
    
    // Atualizar os estados React com debounce
    updateLoadingState();
  }, [startSafetyTimer, updateLoadingState]);
  
  const stopLoading = useCallback((operationId?: string) => {
    // Decrementar contador apenas se for maior que zero
    if (loadingCounterRef.current > 0) {
      loadingCounterRef.current -= 1;
    }
    
    // Atualizar estado de loading se contador chegar a zero
    if (loadingCounterRef.current === 0) {
      isLoadingRef.current = false;
      
      // Parar o timer de segurança
      stopSafetyTimer();
    }
    
    // Se um ID de operação foi fornecido, removê-lo do rastreamento
    if (operationId && activeOperationsRef.current.has(operationId)) {
      activeOperationsRef.current.delete(operationId);
    }
    
    // Atualizar os estados React com debounce
    updateLoadingState();
  }, [stopSafetyTimer, updateLoadingState]);
  
  // Método legado de compatibilidade para componentes existentes
  const setLoadingState = useCallback((loading: boolean) => {
    if (loading) {
      startLoading('legacy');
    } else {
      stopLoading('legacy');
    }
  }, [startLoading, stopLoading]);
  
  // Limpar recursos ao desmontar o componente
  useEffect(() => {
    return () => {
      if (safetyTimerIdRef.current) {
        window.clearTimeout(safetyTimerIdRef.current);
      }
      
      if (updateTimerRef.current) {
        window.clearTimeout(updateTimerRef.current);
      }
    };
  }, []);
  
  // Valor do contexto
  const value = {
    isLoading,
    startLoading,
    stopLoading,
    setLoadingState,
    activeOperationsCount: loadingCounter,
    activeOperations,
    resetLoadingState
  };
  
  return (
    <LoadingContext.Provider value={value}>
      {children}
      <LoadingOverlay 
        visible={isLoading} 
        text={loadingCounter > 1 ? `Carregando... (${loadingCounter} operações)` : "Carregando..."}
      />
    </LoadingContext.Provider>
  );
}; 