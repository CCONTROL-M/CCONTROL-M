import { useState, useEffect, useCallback, useRef } from 'react';
import { useLoading } from '../contexts/LoadingContext';
import { useToastUtils } from './useToast';
import { useMock } from '../utils/mock';
import { verificarStatusAPI } from '../services/api';
import { showToast } from '../utils/toast';

/**
 * Opções para o hook useDataFetching
 */
export interface FetchingOptions<T> {
  /** Função que realiza a busca de dados real */
  fetchFunction: () => Promise<T>;
  
  /** Função para gerar dados simulados (opcional) */
  mockFunction?: () => Promise<T> | T;
  
  /** Dependências que quando alteradas disparam uma nova busca */
  dependencies?: any[];
  
  /** Controla se a busca deve ser automática no mount (default: true) */
  autoFetch?: boolean;
  
  /** ID para identificar esta operação de loading (default: random) */
  loadingId?: string;
  
  /** Exibir toast de erro quando falhar (default: true) */
  showErrorToast?: boolean;
  
  /** Mensagem de erro personalizada para o toast */
  errorMessage?: string;
  
  /** Número máximo de retentativas (default: 0) */
  maxRetries?: number;
  
  /** Usar o indicador de loading global (default: false) */
  useGlobalLoading?: boolean;
  
  /** Intervalo mínimo entre requisições (ms) (default: 0) */
  minRefreshInterval?: number;
}

/**
 * Hook customizado para busca de dados com gerenciamento de estados
 * 
 * Este hook é particularmente útil para componentes de relatório e indicadores.
 * Incorpora estratégias para evitar flickering e melhorar UX.
 */
export function useDataFetching<T>(options: FetchingOptions<T>) {
  const {
    fetchFunction,
    mockFunction,
    dependencies = [],
    autoFetch = true,
    loadingId = `load-${Math.random().toString(36).substr(2, 9)}`,
    showErrorToast = true,
    errorMessage = 'Falha ao carregar dados. Tente novamente.',
    maxRetries = 0,
    useGlobalLoading = false,
    minRefreshInterval = 0
  } = options;

  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [retryCount, setRetryCount] = useState<number>(0);
  
  const mockEnabled = useMock();
  const { startLoading, stopLoading } = useLoading();
  
  // Referências para controle de estado
  const isMountedRef = useRef<boolean>(true);
  const lastFetchTimeRef = useRef<number>(0);
  const hasFetchedRef = useRef<boolean>(false);
  const hasDataRef = useRef<boolean>(false);
  const abortControllerRef = useRef<AbortController | null>(null);
  
  // Determinar se é um componente de relatório pelo loadingId
  const isReportComponent = loadingId.includes('dre') || loadingId.includes('ciclo');
  
  /**
   * Função principal para buscar dados
   * Com otimizações para prevenir flickering e melhorar UX
   */
  const fetchData = useCallback(async () => {
    // Cancelar fetch anterior se existir
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    // Verificar intervalo mínimo entre requisições
    const now = Date.now();
    const timeSinceLastFetch = now - lastFetchTimeRef.current;
    if (timeSinceLastFetch < minRefreshInterval && hasFetchedRef.current) {
      return;
    }
    
    // Criar novo AbortController para este fetch
    abortControllerRef.current = new AbortController();
    
    try {
      // Se já temos dados, não exibir loading para relatórios
      // Esta é uma otimização crucial para prevenir flickering em refreshes
      const shouldShowLoading = !(isReportComponent && hasDataRef.current);
      
      // Antes de iniciar o fetching
      setLoading(true);
      setError(null);
      
      if (shouldShowLoading && useGlobalLoading) {
        startLoading(loadingId);
      }
      
      // Registrar tempo de início do fetch
      lastFetchTimeRef.current = Date.now();
      hasFetchedRef.current = true;
      
      // Usar dados simulados ou dados reais
      let result: T;
      if (mockEnabled && mockFunction) {
        result = await mockFunction();
      } else {
        // Adicionar signal para cancelamento
        result = await fetchFunction();
      }
      
      // Se o componente ainda estiver montado
      if (isMountedRef.current) {
        setData(result);
        hasDataRef.current = true;
        setRetryCount(0);
      }
    } catch (err) {
      if (!isMountedRef.current) return;
      
      // Incrementar contador de retentativas
      const nextRetryCount = retryCount + 1;
      setRetryCount(nextRetryCount);
      
      // Tratar erro
      console.error(`Erro ao buscar dados (${loadingId}):`, err);
      const errorMsg = err instanceof Error ? err.message : String(err);
      setError(errorMsg);
      
      // Exibir toast de erro (mas não para componentes de relatório durante navegação normal)
      if (showErrorToast && !(isReportComponent && window.location.pathname.includes('/relatorios'))) {
        showToast(errorMessage, 'error');
      }
      
      // Tentar novamente automaticamente se dentro do limite
      if (nextRetryCount <= maxRetries) {
        const retryDelay = Math.min(1000 * Math.pow(2, nextRetryCount - 1), 10000);
        console.log(`Tentando novamente em ${retryDelay / 1000}s...`);
        
        setTimeout(() => {
          if (isMountedRef.current) {
            fetchData();
          }
        }, retryDelay);
      }
    } finally {
      // Finalizar loading apenas se o componente ainda estiver montado
      if (isMountedRef.current) {
        setLoading(false);
        
        if (useGlobalLoading) {
          stopLoading(loadingId);
        }
      }
    }
  }, [fetchFunction, mockFunction, mockEnabled, loadingId, showErrorToast, errorMessage, 
      retryCount, maxRetries, useGlobalLoading, startLoading, stopLoading, isReportComponent, 
      minRefreshInterval]);

  // Controle de inicialização e dependências
  useEffect(() => {
    if (autoFetch) {
      // Usando requestAnimationFrame para alinhar com o ciclo de renderização
      // Isso reduz a chance de flickering em relatórios
      const fetchFrame = requestAnimationFrame(() => {
        fetchData();
      });
      
      return () => {
        cancelAnimationFrame(fetchFrame);
      };
    }
  }, [autoFetch, fetchData, ...dependencies]);

  // Limpeza quando componente é desmontado
  useEffect(() => {
    return () => {
      isMountedRef.current = false;
      
      // Cancelar fetch pendente
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      
      // Garantir que loading global seja limpo
      if (useGlobalLoading) {
        stopLoading(loadingId);
      }
    };
  }, [loadingId, useGlobalLoading, stopLoading]);

  // Função para forçar refetch
  const refetch = useCallback(() => {
    fetchData();
  }, [fetchData]);

  return {
    data,
    loading,
    error,
    refetch,
    retryCount
  };
}

export default useDataFetching; 