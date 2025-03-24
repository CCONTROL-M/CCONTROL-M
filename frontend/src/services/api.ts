import axios, { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from "axios";

// Estender a configuração do Axios para incluir o contador de tentativas
interface CustomAxiosRequestConfig extends InternalAxiosRequestConfig {
  retryCount?: number;
}

// Definir tipo para o status da API
interface APIStatus {
  online: boolean;
  lastError: Error | AxiosError | null;
}

// Função para obter o token de autenticação do localStorage
const getAuthToken = () => {
  return localStorage.getItem('token');
};

// Obter a URL da API das variáveis de ambiente
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

console.log("API configurada para URL:", API_URL);

const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Habilitar envio de cookies para requisições CORS
  timeout: 15000 // Definir timeout de 15 segundos para evitar travamentos
});

// Variáveis para controle de status da API
let isAPIOffline = false;
let lastServerError: Error | AxiosError | null = null;
let lastCheckTime = 0;
const MIN_CHECK_INTERVAL = 30000; // Reduzir para 30 segundos entre verificações (antes 120000)
let healthCheckAttempts = 0;
const MAX_HEALTH_CHECK_ATTEMPTS = 5; // Aumentar para 5 tentativas (antes 2)
let healthCheckBlocked = false;
let errorLogged = false; // Evitar logs de erros repetidos

// Interceptor para adicionar token de autenticação a todas as requisições
api.interceptors.request.use(
  (config: CustomAxiosRequestConfig) => {
    const token = getAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Inicializar contador de tentativas se não existir
    if (!config.retryCount) {
      config.retryCount = 0;
    }
    
    // Log de requisição apenas em desenvolvimento
    if (import.meta.env.DEV) {
      console.log(`Requisição: ${config.method?.toUpperCase()} ${config.url}`, {
        params: config.params,
        retryCount: config.retryCount
      });
    }
    
    return config;
  },
  (error: AxiosError) => {
    console.error("Erro ao configurar requisição:", error);
    return Promise.reject(error);
  }
);

// Função para verificar se o erro é elegível para retry
const isRetryableError = (error: AxiosError): boolean => {
  // Retry em erros de rede (offline, conexão recusada, etc)
  if (!error.response) {
    return true;
  }
  
  // Retry em erros 5xx (problemas no servidor)
  const status = error.response.status;
  return status >= 500 && status < 600;
};

// Calcula o tempo de espera para o próximo retry com backoff exponencial
const getRetryDelay = (retryCount: number): number => {
  return Math.min(1000 * Math.pow(2, retryCount), 10000); // Entre 1s e 10s
};

// Interceptor para tratar erros de resposta com retry
api.interceptors.response.use(
  (response: AxiosResponse) => {
    // Log de resposta bem-sucedida em desenvolvimento
    if (import.meta.env.DEV) {
      console.log(`Resposta de ${response.config.url}:`, {
        status: response.status,
        hasData: !!response.data,
        dataType: response.data ? (Array.isArray(response.data) ? 'array' : typeof response.data) : null,
      });
    }
    
    // Se a API estava offline e agora respondeu, resetar o status
    if (isAPIOffline) {
      console.info("🟢 Conexão com a API restaurada");
      isAPIOffline = false;
      lastServerError = null;
    }
    
    return response;
  },
  async (error: AxiosError) => {
    // Obter a configuração da requisição original
    const originalConfig = error.config as CustomAxiosRequestConfig;
    
    // Verificar se a requisição tem a flag X-No-Retry
    const noRetry = originalConfig.headers && 'X-No-Retry' in originalConfig.headers;
    
    // Se é um erro que podemos tentar novamente e não excedemos o número máximo de tentativas
    // e não tem a flag de no-retry
    if (!noRetry && isRetryableError(error) && originalConfig.retryCount !== undefined && originalConfig.retryCount < 3) {
      // Incrementar o contador de tentativas
      originalConfig.retryCount++;
      
      // Calcular o tempo de espera
      const delayTime = getRetryDelay(originalConfig.retryCount);
      
      if (originalConfig.retryCount === 1) {
        // Na primeira tentativa, avisar no console uma mensagem mais detalhada
        console.warn(`⚠️ Erro de comunicação com o servidor. Tentando novamente (${originalConfig.retryCount}/3) após ${delayTime}ms...`, {
          url: originalConfig.url,
          metodo: originalConfig.method,
          erro: error.message
        });
      } else {
        // Nas tentativas seguintes, mensagem mais simples
        console.warn(`⚠️ Servidor não respondeu. Nova tentativa (${originalConfig.retryCount}/3) após ${delayTime}ms...`);
      }
      
      // Esperar antes de tentar novamente (backoff exponencial)
      await new Promise(resolve => setTimeout(resolve, delayTime));
      
      // Tentar a requisição novamente
      return api(originalConfig);
    }
    
    // Detecção de API offline (após todas as tentativas)
    if (isRetryableError(error) && originalConfig.retryCount !== undefined && originalConfig.retryCount >= 3) {
      isAPIOffline = true;
      lastServerError = error;
      // Logar erro apenas se não for uma requisição de health check
      if (!originalConfig.url?.includes('/health')) {
        console.error("🔴 API parece estar offline após 3 tentativas", {
          url: originalConfig.url,
          error: error.message
        });
      }
    }
    
    // Tratamento específico por tipo de erro
    if (error.response) {
      // O servidor respondeu com um status code fora do intervalo 2xx
      const { status, data } = error.response;
      const url = originalConfig.url;
      
      console.error(`Erro na API (${status}) na requisição para ${url}:`, data);
      
      // Se o erro for 401 (não autorizado), redirecionar para login
      if (status === 401) {
        console.warn("Token expirado ou inválido. Redirecionando para login.");
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
      
      // Se o erro for 403 (acesso negado), pode ser um problema com o id_empresa
      if (status === 403) {
        console.warn("Acesso negado. Verifique se o usuário tem permissão para esta operação.");
      }
    } else if (error.request) {
      // A requisição foi feita mas não houve resposta
      console.error("Sem resposta do servidor:", {
        url: originalConfig.url,
        method: originalConfig.method?.toUpperCase(),
        tentativas: originalConfig.retryCount,
        mensagem: error.message
      });
    } else {
      // Erro ao configurar a requisição
      console.error("Erro de configuração da requisição:", error.message);
    }
    
    return Promise.reject(error);
  }
);

// Método para verificar o status atual da API
export const verificarStatusAPI = async (): Promise<{ online: boolean; error: Error | AxiosError | null }> => {
  const now = Date.now();
  
  // Se as verificações estiverem bloqueadas, retorne o status offline imediatamente
  if (healthCheckBlocked) {
    console.log("Verificação de API bloqueada, assumindo offline");
    return { online: false, error: lastServerError };
  }
  
  // Limitar a frequência de verificações para reduzir logs e requisições
  if (now - lastCheckTime < MIN_CHECK_INTERVAL) {
    console.log(`Verificação muito recente, usando cache: ${!isAPIOffline ? 'online' : 'offline'}`);
    return { online: !isAPIOffline, error: lastServerError };
  }
  
  // Se já atingiu o número máximo de tentativas, bloquear por 2 minutos (antes 5 minutos)
  if (healthCheckAttempts >= MAX_HEALTH_CHECK_ATTEMPTS) {
    if (!errorLogged) {
      console.warn(`🔒 Verificação de API bloqueada após ${MAX_HEALTH_CHECK_ATTEMPTS} tentativas. Aguardando 2 minutos.`);
      errorLogged = true;
    }
    
    healthCheckBlocked = true;
    
    // Desbloquear após 2 minutos (antes 5 minutos - 300000)
    setTimeout(() => {
      healthCheckBlocked = false;
      healthCheckAttempts = 0;
      errorLogged = false;
      console.info("🔓 Verificação de API desbloqueada. Novas tentativas serão permitidas.");
    }, 120000); // 2 minutos
    
    return { online: false, error: lastServerError };
  }
  
  lastCheckTime = now;
  console.log("Iniciando verificação de API...");
  
  try {
    // Criar uma Promise com timeout manual para evitar mensagens de erro repetidas
    const timeoutPromise = new Promise<{ data: any }>((_, reject) => {
      setTimeout(() => {
        reject(new Error('⏱️ Timeout ao verificar API'));
      }, 3000); // Aumentado para 3s (antes 800ms)
    });
    
    // Criar a Promise da requisição real
    const fetchPromise = api.get('/v1/health', { 
      timeout: 5000,  // Aumentado para 5s (antes 1000ms)
      headers: {
        'X-No-Retry': 'true'
      }
    });
    
    // Usar race para pegar o que completar primeiro
    await Promise.race([fetchPromise, timeoutPromise]);
    
    // Se chegou aqui, a requisição foi bem-sucedida
    if (isAPIOffline) {
      console.info("🟢 Conexão com a API restaurada");
      errorLogged = false;
    }
    
    // Resetar contadores
    isAPIOffline = false;
    healthCheckAttempts = 0;
    return { online: true, error: null };
  } catch (err) {
    // Incrementar contador de tentativas
    healthCheckAttempts++;
    
    // Tratar erro como Error ou AxiosError para tipagem
    const error = err as Error | AxiosError;
    
    // Verificar se é um erro de timeout e tratar especificamente
    const axiosError = error as AxiosError;
    const isTimeout = axiosError.code === 'ECONNABORTED' || 
                     (axiosError.message && axiosError.message.includes('timeout')) ||
                     error.message === '⏱️ Timeout ao verificar API';
    
    // Se não estava offline antes, logar o erro apenas uma vez
    if (!isAPIOffline && !errorLogged) {
      // Mensagem amigável para timeout
      if (isTimeout) {
        console.warn(`⏱️ Timeout ao verificar API (${healthCheckAttempts}/${MAX_HEALTH_CHECK_ATTEMPTS})`);
      } else {
        console.error(`🔴 API não está respondendo (${healthCheckAttempts}/${MAX_HEALTH_CHECK_ATTEMPTS})`);
      }
      errorLogged = true;
    } else if (healthCheckAttempts === MAX_HEALTH_CHECK_ATTEMPTS && !errorLogged) {
      console.warn(`⚠️ Atingido limite de tentativas (${MAX_HEALTH_CHECK_ATTEMPTS}). Pausando verificações.`);
      errorLogged = true;
    }
    
    isAPIOffline = true;
    // Só atualizar lastServerError se não for um timeout, para evitar mensagens genéricas
    if (!isTimeout) {
      lastServerError = error as Error | AxiosError;
    }
    return { online: false, error: isTimeout ? new Error('Timeout ao verificar API') : lastServerError };
  }
};

// Método para obter o status atual da conexão com a API
export const getStatusAPI = (): APIStatus => {
  return {
    online: !isAPIOffline,
    lastError: lastServerError
  };
};

// Função utilitária para verificação segura de arrays
export function safeArray<T>(input: any): T[] {
  if (Array.isArray(input) && input.length > 0) {
    return input;
  }
  return [];
}

// Função utilitária para verificação segura de objetos
export function safeObject<T>(input: any, defaultValue: T): T {
  if (input && typeof input === 'object' && !Array.isArray(input)) {
    return input as T;
  }
  return defaultValue;
}

export default api; 