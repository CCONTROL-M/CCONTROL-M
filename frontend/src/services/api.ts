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

// Obter a URL da API das variáveis de ambiente ou usar caminho relativo
const API_URL = ''; // URL vazia para usar caminhos relativos com o proxy do Vite

console.log("API configurada para usar proxy do Vite");

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
const MIN_CHECK_INTERVAL = 10000; // Mínimo de 10 segundos entre verificações de status

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
    
    // Log de requisição para debugging
    console.log(`Requisição para: ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`, {
      url: config.url,
      params: config.params,
      withCredentials: config.withCredentials,
      headers: config.headers,
      retryCount: config.retryCount
    });
    
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
    // Log de resposta bem-sucedida
    console.log(`Resposta de ${response.config.url}:`, {
      status: response.status,
      hasData: !!response.data,
      dataType: response.data ? (Array.isArray(response.data) ? 'array' : typeof response.data) : null,
    });
    
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
    
    // Se é um erro que podemos tentar novamente e não excedemos o número máximo de tentativas
    if (isRetryableError(error) && originalConfig.retryCount !== undefined && originalConfig.retryCount < 3) {
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
      console.error("🔴 API parece estar offline após 3 tentativas", {
        url: originalConfig.url,
        error: error.message
      });
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
  
  // Limitar a frequência de verificações para reduzir logs e requisições
  if (now - lastCheckTime < MIN_CHECK_INTERVAL) {
    return { online: !isAPIOffline, error: lastServerError };
  }
  
  lastCheckTime = now;
  
  try {
    await api.get('/api/v1/health', { timeout: 3000 });
    
    // Se estava offline e agora está online, logar a informação
    if (isAPIOffline) {
      console.info("🟢 Conexão com a API restaurada");
    }
    
    isAPIOffline = false;
    return { online: true, error: null };
  } catch (error) {
    // Se não estava offline antes, logar o erro apenas uma vez
    if (!isAPIOffline) {
      console.error("🔴 API não está respondendo. Usando dados mockados.", error);
    }
    
    isAPIOffline = true;
    lastServerError = error as Error | AxiosError;
    return { online: false, error: lastServerError };
  }
};

// Método para obter o status atual da conexão com a API
export const getStatusAPI = (): APIStatus => {
  return {
    online: !isAPIOffline,
    lastError: lastServerError
  };
};

export default api; 