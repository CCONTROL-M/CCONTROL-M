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
  // Novo método para loading silencioso (sem overlay)
  startSilentLoading: (operationId: string) => void;
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

// Tempo de segurança máximo para carregamento (5 segundos - reduzido de 7)
const SAFETY_TIMEOUT = 5000;

// Debounce para atualizações no estado de loading (ms) - reduzido para ser mais responsivo
const DEBOUNCE_TIME = 30;

// Interface para as props do provider
interface LoadingProviderProps {
  children: ReactNode;
}

// Componente Provider
export const LoadingProvider: React.FC<LoadingProviderProps> = ({ children }) => {
  // Usando useRef para valores que não devem causar re-renderizações
  const isLoadingRef = useRef<boolean>(false);
  const activeOperationsRef = useRef<Set<string>>(new Set());
  const silentOperationsRef = useRef<Set<string>>(new Set());
  const loadingCounterRef = useRef<number>(0);
  const safetyTimerIdRef = useRef<number | null>(null);
  const updateTimerRef = useRef<number | null>(null);
  const lastTransitionTimeRef = useRef<number>(0);
  
  // Estados que causarão re-renderizações quando atualizados
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [activeOperations, setActiveOperations] = useState<Set<string>>(new Set());
  const [loadingCounter, setLoadingCounter] = useState<number>(0);
  
  // Função para atualizar o estado de loading com debounce inteligente
  const updateLoadingState = useCallback(() => {
    // Limpar qualquer timer pendente
    if (updateTimerRef.current !== null) {
      window.clearTimeout(updateTimerRef.current);
      updateTimerRef.current = null;
    }
    
    // Calcular o tempo desde a última transição
    const now = Date.now();
    const timeSinceLastTransition = now - lastTransitionTimeRef.current;
    
    // Usar debounce mais curto se estivermos ativando o loading
    // e um debounce mais longo se estivermos desativando
    const delayTime = isLoadingRef.current && !isLoading 
      ? DEBOUNCE_TIME  // Ativar loading rapidamente
      : Math.max(DEBOUNCE_TIME, Math.min(300, timeSinceLastTransition)); // Desativar com delay proporcional
    
    // Configurar um timer para atualizar o estado de loading após debounce
    updateTimerRef.current = window.setTimeout(() => {
      // Verificar se temos operações silenciosas e nenhuma operação regular
      const hasOnlySilentOperations = silentOperationsRef.current.size > 0 && 
        (activeOperationsRef.current.size === silentOperationsRef.current.size);
      
      // Se todas as operações são silenciosas, não mostrar loading global
      const shouldShowLoading = isLoadingRef.current && !hasOnlySilentOperations;
      
      // Atualizar state apenas se o valor for diferente para evitar re-renderizações desnecessárias
      if (shouldShowLoading !== isLoading) {
        setIsLoading(shouldShowLoading);
        // Registrar quando ocorreu a última transição
        lastTransitionTimeRef.current = Date.now();
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
    }, delayTime);
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
    silentOperationsRef.current.clear();
    
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
  
  // Iniciar loading silencioso (sem overlay)
  const startSilentLoading = useCallback((operationId: string) => {
    // Incrementar contador
    loadingCounterRef.current += 1;
    
    // Atualizar estado de loading
    isLoadingRef.current = true;
    
    // Rastrear como operação ativa e silenciosa
    activeOperationsRef.current.add(operationId);
    silentOperationsRef.current.add(operationId);
    
    // Iniciar timer de segurança se ainda não estiver ativo
    if (safetyTimerIdRef.current === null) {
      startSafetyTimer();
    }
    
    // Atualizar os estados React com debounce
    updateLoadingState();
  }, [startSafetyTimer, updateLoadingState]);
  
  // Ativar o loading com controle de contagem
  const startLoading = useCallback((operationId?: string) => {
    // Detectar loading para relatórios e torná-lo silencioso automaticamente
    if (operationId && (operationId.includes('dre') || operationId.includes('ciclo'))) {
      startSilentLoading(operationId);
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
  }, [startSilentLoading, startSafetyTimer, updateLoadingState]);
  
  const stopLoading = useCallback((operationId?: string) => {
    // Decrementar contador apenas se for maior que zero
    if (loadingCounterRef.current > 0) {
      loadingCounterRef.current -= 1;
    }
    
    // Remover da lista de operações silenciosas se aplicável
    if (operationId && silentOperationsRef.current.has(operationId)) {
      silentOperationsRef.current.delete(operationId);
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
    startSilentLoading,
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
        theme="light"
        blur={false}
      />
    </LoadingContext.Provider>
  );
}; 