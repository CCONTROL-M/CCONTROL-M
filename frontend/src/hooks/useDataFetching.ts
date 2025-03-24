import { useState, useEffect, useCallback, useRef } from 'react';
import { useLoading } from '../contexts/LoadingContext';
import { useToastUtils } from './useToast';
import { useMock } from '../utils/mock';
import { verificarStatusAPI } from '../services/api';

interface FetchingOptions<T, M> {
  fetchFunction: () => Promise<T>;
  mockFunction?: () => Promise<M>;
  dependencies?: any[];
  autoFetch?: boolean;
  loadingId?: string;
  showErrorToast?: boolean;
  errorMessage?: string;
  maxRetries?: number;
  useGlobalLoading?: boolean; // Controla se deve usar o overlay global de loading
}

/**
 * Hook personalizado para busca de dados com gerenciamento de estado
 * Especialmente útil para componentes de relatórios e indicadores
 * 
 * @param options Opções de configuração da busca
 * @returns Estado de dados, erro e loading, junto com a função de refetch
 */
export function useDataFetching<T, M = T>(options: FetchingOptions<T, M>) {
  const {
    fetchFunction,
    mockFunction,
    dependencies = [],
    autoFetch = true,
    loadingId = `data-fetch-${Date.now()}`,
    showErrorToast = true,
    errorMessage = 'Erro ao buscar dados',
    maxRetries = 1, // Limitar a 1 tentativa por padrão
    useGlobalLoading = true // Usar loading global por padrão, exceto para relatórios
  } = options;

  // Estados
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<Error | null>(null);
  
  // Usar ref para controlar o loading internamente e evitar estados transitórios
  // que causam flashes - principalmente para relatórios
  const loadingRef = useRef<boolean>(false);
  // Inicializamos o loading como FALSO sempre, para evitar o flash inicial
  const [loading, setLoading] = useState<boolean>(false);
  
  const [apiOffline, setApiOffline] = useState<boolean>(false);
  const [retryCount, setRetryCount] = useState<number>(0);
  const [fetchBlocked, setFetchBlocked] = useState<boolean>(false);
  
  // Refs para controle de chamadas
  const fetchingRef = useRef<boolean>(false);
  const dataIdRef = useRef<string>(`${loadingId}-${Date.now()}`);
  const initialFetchCompletedRef = useRef<boolean>(false);
  const dataCachedRef = useRef<boolean>(false);
  const mountedRef = useRef<boolean>(false);
  const immediateShowDataRef = useRef<boolean>(false);

  // Hooks de sistema
  const { startLoading, stopLoading } = useLoading();
  const { showErrorToast: showError } = useToastUtils();
  const isMockEnabled = useMock();
  
  // Determinar se deve usar o loading global e evitar loading para relatórios
  const isReportComponent = loadingId.includes('dre') || loadingId.includes('ciclo');
  const shouldUseGlobalLoading = useGlobalLoading && !isReportComponent;

  // Marcar componente como montado
  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  // Verificar status da API com debounce para evitar chamadas excessivas
  const verificarApi = useCallback(async () => {
    // Se o modo mock já estiver ativado, não precisa verificar a API
    if (isMockEnabled && mockFunction) {
      console.log(`[${loadingId}] Modo mock já está ativo, não verificando API`);
      return false;
    }
    
    try {
      console.log(`[${loadingId}] Verificando status da API...`);
      const { online } = await verificarStatusAPI();
      console.log(`[${loadingId}] Status da API: ${online ? 'online' : 'offline'}`);
      
      // Atualizar estado apenas se houver mudança
      if (online !== !apiOffline) {
        setApiOffline(!online);
      }
      
      // Não ativamos mais o modo mock automaticamente quando a API está offline
      return online;
    } catch (err) {
      console.error(`[${loadingId}] Erro ao verificar API:`, err);
      
      // Atualizar estado apenas se houver mudança
      if (!apiOffline) {
        setApiOffline(true);
      }
      
      // Não ativamos mais o modo mock automaticamente em caso de erro
      return false;
    }
  }, [isMockEnabled, loadingId, mockFunction, apiOffline]);

  // Função para atualizar o estado loading de forma segura
  const updateLoadingState = useCallback((state: boolean) => {
    // Para relatórios, NUNCA ativamos o loading na montagem inicial
    if (isReportComponent && !mountedRef.current) {
      console.log(`[${loadingId}] Componente ainda não montado, ignorando loading`);
      return;
    }
    
    // Para relatórios, só ativamos o loading se não tivermos dados em cache
    if (isReportComponent && (dataCachedRef.current || immediateShowDataRef.current) && state === true) {
      // Evitar ativar loading para atualizações quando já temos dados
      console.log(`[${loadingId}] Evitando loading para relatório com dados em cache`);
      loadingRef.current = false;
      // Garantir que setLoading seja chamado APENAS se já estivermos montados
      if (mountedRef.current) {
        setLoading(false);
      }
      return;
    }
    
    loadingRef.current = state;
    
    // Atualizar estado React somente se componente estiver montado
    if (mountedRef.current) {
      // Para relatórios, adicionar um pequeno delay para evitar flash durante navegação
      if (isReportComponent && state === true) {
        const hasNoData = !dataCachedRef.current;
        // Se estamos habilitando o loading, usar um delay maior para componentes de relatório
        const timer = setTimeout(() => {
          // Verificar novamente se ainda estamos carregando e montados
          if (loadingRef.current && mountedRef.current && hasNoData && !immediateShowDataRef.current) {
            setLoading(true);
          }
        }, 300); // Aumentar para 300ms para evitar completamente o flash
        return () => clearTimeout(timer);
      } else {
        // Desativar loading de maneira imediata
        setLoading(state);
      }
    }
  }, [loadingId, isReportComponent]);

  // Função principal para buscar dados
  const fetchData = useCallback(async () => {
    // Evitar múltiplas chamadas simultâneas usando ref
    if (fetchingRef.current || loadingRef.current || fetchBlocked) {
      console.log(`[${loadingId}] Busca já em andamento ou bloqueada, ignorando`);
      return;
    }
    fetchingRef.current = true;
    
    console.log(`[${loadingId}] Iniciando busca de dados. Mock: ${isMockEnabled ? 'ativado' : 'desativado'}`);
    
    // Para relatórios com dados em cache, não mostramos o loading
    const shouldShowLoading = !(isReportComponent && (dataCachedRef.current || immediateShowDataRef.current));
    
    // Definir estados iniciais
    if (shouldShowLoading) {
      updateLoadingState(true);
      // Apenas iniciar loading global se permitido para este componente
      if (shouldUseGlobalLoading) {
        startLoading(loadingId);
      }
    } else {
      console.log(`[${loadingId}] Atualizando dados de relatório sem exibir loading`);
    }
    
    setError(null);

    try {
      // Decidir qual função usar - usar mock apenas se ativado explicitamente
      let result;
      
      if (isMockEnabled && mockFunction) {
        console.log(`[${loadingId}] Buscando dados mock...`);
        result = await mockFunction();
        
        // Se for relatório e não tivermos dados em cache, marque para mostrar imediatamente
        if (isReportComponent && !dataCachedRef.current) {
          immediateShowDataRef.current = true;
        }
        
        setData(result as unknown as T);
        dataCachedRef.current = true;
        console.log(`[${loadingId}] Dados mock obtidos com sucesso`);
        // Resetar a contagem de tentativas quando sucesso
        setRetryCount(0);
      } else {
        // Usar API se modo mock não estiver ativado
        console.log(`[${loadingId}] Tentando buscar dados reais...`);
        result = await fetchFunction();
        
        // Se for relatório e não tivermos dados em cache, marque para mostrar imediatamente
        if (isReportComponent && !dataCachedRef.current) {
          immediateShowDataRef.current = true;
        }
        
        setData(result);
        dataCachedRef.current = true;
        console.log(`[${loadingId}] Dados reais obtidos com sucesso`);
        // Resetar a contagem de tentativas quando sucesso
        setRetryCount(0);
      }
      
      // Marcar que a carga inicial foi concluída
      initialFetchCompletedRef.current = true;
      
      // Para relatórios, desativar loading imediatamente após receber dados
      if (isReportComponent) {
        setLoading(false);
      }
    } catch (err) {
      console.error(`[${loadingId}] Erro ao buscar dados:`, err);
      
      setError(err as Error);
      
      // Mostrar toast de erro
      if (showErrorToast && mountedRef.current) {
        showError(errorMessage);
      }
    } finally {
      // Sempre garantir que os indicadores de carregamento sejam desativados
      updateLoadingState(false);
      // Apenas parar loading global se foi iniciado
      if (shouldUseGlobalLoading) {
        stopLoading(loadingId);
      }
      fetchingRef.current = false;
      console.log(`[${loadingId}] Finalizada busca de dados`);
    }
  }, [
    fetchFunction, mockFunction, isMockEnabled, 
    loadingId, startLoading, stopLoading, shouldUseGlobalLoading,
    showErrorToast, errorMessage, showError, retryCount, 
    maxRetries, fetchBlocked, updateLoadingState, isReportComponent
  ]);

  // Efeito especial para garantir que relatórios nunca mostrem loading se tiverem dados
  useEffect(() => {
    // Se temos dados e é um componente de relatório, forçar loading=false
    if (data && isReportComponent) {
      setLoading(false);
    }
  }, [data, isReportComponent]);

  // Fetch data whenever dependencies change
  useEffect(() => {
    // Para evitar o flash em relatórios, não mostramos loading na montagem inicial
    if (autoFetch) {
      if (isReportComponent) {
        // Se for relatório, iniciamos com loading = false e fazemos fetch dos dados
        if (!initialFetchCompletedRef.current) {
          console.log(`[${loadingId}] Iniciando fetch para relatório sem loading inicial`);
          setLoading(false);  // Forçar loading=false inicialmente
          fetchData();
        } else {
          // Se já tivermos feito fetch inicial, seguimos o fluxo normal
          fetchData();
        }
      } else {
        // Se não for relatório, comportamento normal
        fetchData();
      }
    }
    
    // Removida a lógica de forçar mock para relatórios
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, dependencies);

  // Refetch function for manual triggers
  const refetch = useCallback(() => {
    console.log(`[${loadingId}] Refetch solicitado manualmente`);
    // Resetar estados de bloqueio se um refetch manual for solicitado
    setFetchBlocked(false);
    setRetryCount(0);
    return fetchData();
  }, [fetchData, loadingId]);

  return { 
    data, 
    error, 
    loading, 
    fetchData: useCallback(() => {
      if (!fetchingRef.current) fetchData();
    }, [fetchData]), 
    apiOffline 
  };
}

export default useDataFetching; 