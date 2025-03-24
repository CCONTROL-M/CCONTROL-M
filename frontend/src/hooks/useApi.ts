import { useState, useEffect, useCallback } from 'react';
import { AxiosError } from 'axios';
import api from '../services/api';
import { useMock } from '../utils/mock';
import { useLoading } from '../contexts/LoadingContext';
import { useToastUtils } from '../hooks/useToast';

interface UseApiOptions<T, M> {
  endpoint: string;
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  initialData?: T;
  mockData?: M;
  params?: any;
  body?: any;
  autoFetch?: boolean;
  loadingId?: string;
  showSuccessToast?: boolean;
  successMessage?: string;
  showErrorToast?: boolean;
  errorMessage?: string;
  onSuccess?: (data: T) => void;
  onError?: (error: Error | AxiosError) => void;
  transform?: (responseData: any) => T;
}

interface UseApiResult<T> {
  data: T;
  error: Error | AxiosError | null;
  loading: boolean;
  fetch: (customParams?: any, customBody?: any) => Promise<T | null>;
  reset: () => void;
}

/**
 * Hook personalizado para consumo de APIs com gerenciamento de estado, carregamento e erros.
 * Fornece suporte automático para dados mockados.
 * 
 * @param options Opções de configuração da chamada de API
 * @returns Estado atual e funções de controle
 */
export function useApi<T, M = T>(options: UseApiOptions<T, M>): UseApiResult<T> {
  // Valores padrão para as opções
  const {
    endpoint,
    method = 'GET',
    initialData = {} as T,
    mockData,
    params = {},
    body = {},
    autoFetch = true,
    loadingId = `api-${endpoint}-${method}`,
    showSuccessToast = false,
    successMessage = 'Operação realizada com sucesso',
    showErrorToast = true,
    errorMessage = 'Erro ao processar a solicitação',
    onSuccess,
    onError,
    transform = (data: any) => data as T
  } = options;

  // Estados locais
  const [data, setData] = useState<T>(initialData);
  const [error, setError] = useState<Error | AxiosError | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  
  // Hooks
  const isMockEnabled = useMock();
  const { startLoading, stopLoading } = useLoading();
  const { showSuccessToast: showSuccess, showErrorToast: showError } = useToastUtils();

  // Função principal para fazer a chamada à API
  const fetch = useCallback(async (customParams?: any, customBody?: any): Promise<T | null> => {
    // Usar dados mockados se ativados
    if (isMockEnabled && mockData) {
      console.log(`[API Mock] ${method} ${endpoint}`, { params, mockData });
      
      // Simular um atraso para parecer mais real
      await new Promise(resolve => setTimeout(resolve, 300));
      
      setData(mockData as unknown as T);
      setError(null);
      
      if (onSuccess) {
        onSuccess(mockData as unknown as T);
      }
      
      if (showSuccessToast) {
        showSuccess(successMessage);
      }
      
      return mockData as unknown as T;
    }
    
    // Iniciar estado de carregamento
    setLoading(true);
    startLoading(loadingId);
    setError(null);
    
    try {
      // Preparar parâmetros e corpo da requisição
      const requestParams = { ...params, ...customParams };
      const requestBody = { ...body, ...customBody };
      
      // Fazer a requisição com o método apropriado
      let response;
      switch (method) {
        case 'GET':
          response = await api.get(endpoint, { params: requestParams });
          break;
        case 'POST':
          response = await api.post(endpoint, requestBody, { params: requestParams });
          break;
        case 'PUT':
          response = await api.put(endpoint, requestBody, { params: requestParams });
          break;
        case 'DELETE':
          response = await api.delete(endpoint, { params: requestParams });
          break;
        case 'PATCH':
          response = await api.patch(endpoint, requestBody, { params: requestParams });
          break;
        default:
          response = await api.get(endpoint, { params: requestParams });
      }
      
      // Transformar os dados recebidos, se necessário
      const transformedData = transform(response.data);
      
      // Atualizar estado com os dados obtidos
      setData(transformedData);
      
      // Chamar callback de sucesso, se fornecido
      if (onSuccess) {
        onSuccess(transformedData);
      }
      
      // Mostrar toast de sucesso, se configurado
      if (showSuccessToast) {
        showSuccess(successMessage);
      }
      
      return transformedData;
    } catch (err) {
      const axiosError = err as AxiosError;
      setError(axiosError);
      
      // Chamar callback de erro, se fornecido
      if (onError) {
        onError(axiosError);
      }
      
      // Mostrar toast de erro, se configurado
      if (showErrorToast) {
        const errorMsg = axiosError.response?.data && 
          typeof axiosError.response.data === 'object' && 
          'message' in axiosError.response.data
            ? (axiosError.response.data as { message: string }).message
            : errorMessage;
        showError(errorMsg);
      }
      
      console.error(`Erro na chamada API ${method} ${endpoint}:`, axiosError);
      return null;
    } finally {
      // Finalizar estado de carregamento
      setLoading(false);
      stopLoading(loadingId);
    }
  }, [
    endpoint, method, params, body, mockData, isMockEnabled,
    loadingId, startLoading, stopLoading,
    showSuccessToast, successMessage, showSuccess,
    showErrorToast, errorMessage, showError,
    onSuccess, onError, transform
  ]);

  // Resetar estado para valores iniciais
  const reset = useCallback(() => {
    setData(initialData);
    setError(null);
    setLoading(false);
  }, [initialData]);

  // Fazer a chamada automaticamente ao montar o componente, se configurado
  useEffect(() => {
    if (autoFetch) {
      fetch();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return { data, error, loading, fetch, reset };
}

/**
 * Hook especializado para buscar dados de uma API com método GET
 */
export function useFetch<T, M = T>(
  endpoint: string,
  options: Omit<UseApiOptions<T, M>, 'endpoint' | 'method'> = {}
): UseApiResult<T> {
  return useApi<T, M>({ ...options, endpoint, method: 'GET' });
}

/**
 * Hook especializado para enviar dados para uma API com método POST
 */
export function usePost<T, M = T>(
  endpoint: string,
  options: Omit<UseApiOptions<T, M>, 'endpoint' | 'method'> = {}
): UseApiResult<T> {
  return useApi<T, M>({ ...options, endpoint, method: 'POST', autoFetch: false });
}

/**
 * Hook especializado para atualizar dados em uma API com método PUT
 */
export function usePut<T, M = T>(
  endpoint: string,
  options: Omit<UseApiOptions<T, M>, 'endpoint' | 'method'> = {}
): UseApiResult<T> {
  return useApi<T, M>({ ...options, endpoint, method: 'PUT', autoFetch: false });
}

/**
 * Hook especializado para excluir dados em uma API com método DELETE
 */
export function useDelete<T, M = T>(
  endpoint: string,
  options: Omit<UseApiOptions<T, M>, 'endpoint' | 'method'> = {}
): UseApiResult<T> {
  return useApi<T, M>({ ...options, endpoint, method: 'DELETE', autoFetch: false });
}

export default useApi; 