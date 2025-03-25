/**
 * Utilitário para gerenciar o uso de mocks em todo o sistema
 * 
 * IMPORTANTE: O modo mock está desabilitado por padrão e não deve ser ativado automaticamente.
 * O sistema deve sempre tentar usar dados reais da API.
 */

// Chave para armazenamento no localStorage
const MOCK_STORAGE_KEY = 'modoMockAtivo';

// Verificar se logs de debug estão habilitados
const ENABLE_DEBUG_LOGS = import.meta.env.VITE_ENABLE_DEBUG_LOGS !== 'false';

// Log das variáveis de ambiente para diagnóstico apenas em desenvolvimento
if (import.meta.env.DEV && ENABLE_DEBUG_LOGS) {
  console.info('🔧 Iniciando frontend com as seguintes configurações:');
  console.info(`- API URL: ${import.meta.env.VITE_API_URL || 'http://localhost:8002/api/v1'}`);
  console.info(`- Porta: ${import.meta.env.VITE_PORT || '3000'} (Forçar porta: ${import.meta.env.VITE_FORCE_PORT === 'true' ? 'Sim' : 'Não'})`);
  console.info(`- Modo mock: Desativado (padrão)`);
  console.info(`- Ambiente: ${import.meta.env.MODE}`);
}

// Verificação mais robusta de ambiente de produção
const isProduction = import.meta.env.MODE === 'production' || import.meta.env.PROD === true;

// Configuração do modo mock - SEMPRE INICIA COMO FALSE
let GLOBAL_USE_MOCK = false;

// Rastreia os erros de API para diagnóstico
interface ApiErrorRecord {
  count: number;
  lastMessage: string;
  timestamp: number;
}

const apiErrors: Record<string, ApiErrorRecord> = {};

/**
 * Verifica se deve usar mock no sistema
 * 
 * IMPORTANTE: Por padrão, sempre retorna false. O modo mock só será ativado
 * se explicitamente configurado pelo usuário via localStorage.
 * 
 * @returns false para garantir uso de dados reais
 */
export function useMock(): boolean {
  // Em produção, SEMPRE retornar false
  if (isProduction) return false;
  
  // Em desenvolvimento, verificar localStorage, mas com muito cuidado
  if (typeof window !== 'undefined' && window.localStorage) {
    try {
      // Verificação estrita - só retorna true se explicitamente salvo como 'true'
      return localStorage.getItem(MOCK_STORAGE_KEY) === 'true';
    } catch (error) {
      // Em caso de erro, retorna false para segurança
      if (ENABLE_DEBUG_LOGS) {
        console.warn('Erro ao verificar modo mock, usando dados reais:', error);
      }
    }
  }
  
  // Por segurança, sempre retorna false em caso de dúvida
  return false;
}

/**
 * Ativa ou desativa o uso de mocks em todo o sistema
 * 
 * @param value true para ativar, false para desativar
 */
export function setUseMock(value: boolean): void {
  // Em produção, não permitir ativar o modo mock
  if (isProduction && value === true) {
    if (ENABLE_DEBUG_LOGS) {
      console.warn("Tentativa de ativar modo mock em produção ignorada");
    }
    return;
  }
  
  // Certifique-se de que o valor seja um booleano
  const boolValue = Boolean(value);
  
  // Persistir no localStorage
  try {
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.setItem(MOCK_STORAGE_KEY, boolValue.toString());
      
      if (ENABLE_DEBUG_LOGS) {
        console.log(`[Mock] Modo mock ${boolValue ? 'ativado' : 'desativado'} manualmente pelo usuário`);
      }
    }
  } catch (error) {
    if (ENABLE_DEBUG_LOGS) {
      console.error('Erro ao salvar preferência de mock:', error);
    }
  }
}

/**
 * Registra um erro da API para diagnóstico
 * 
 * @param endpoint Endpoint que gerou o erro
 * @param error Objeto de erro
 */
export function registerApiError(endpoint: string, error: any): void {
  // Em produção, não registrar erros detalhados
  if (isProduction) return;
  
  const errorMessage = error?.message || 'Erro desconhecido';
  const now = Date.now();
  
  if (!apiErrors[endpoint]) {
    apiErrors[endpoint] = {
      count: 0,
      lastMessage: '',
      timestamp: 0
    };
  }
  
  apiErrors[endpoint].count++;
  apiErrors[endpoint].lastMessage = errorMessage;
  apiErrors[endpoint].timestamp = now;
  
  // Log diagnóstico, sem sugerir ativação do modo mock
  if (apiErrors[endpoint].count >= 3 && ENABLE_DEBUG_LOGS) {
    console.error(`⚠️ Detectados ${apiErrors[endpoint].count} erros no endpoint ${endpoint}. Verifique a conexão com a API.`);
  }
}

/**
 * Limpa o registro de erros de API
 */
export function resetApiErrors(): void {
  Object.keys(apiErrors).forEach(key => {
    delete apiErrors[key];
  });
}

/**
 * Obtém um relatório de erros da API
 */
export function getApiErrorReport(): Record<string, ApiErrorRecord> {
  return { ...apiErrors };
}

/**
 * Alterna o estado atual de uso de mocks
 */
export function toggleMock(): void {
  // Em produção, não permitir alternar para modo mock
  if (isProduction) {
    if (ENABLE_DEBUG_LOGS) {
      console.warn("Tentativa de alternar modo mock em produção ignorada");
    }
    return;
  }
  
  // Verifica o valor atual e o inverte
  const currentValue = useMock();
  setUseMock(!currentValue);
}

// Função que adiciona um indicador visual de que estamos em modo mock
export function adicionarIndicadorMock() {
  // Em produção, nunca mostrar o indicador
  if (isProduction) return;
  
  if (!useMock()) return; // Se não estiver em modo mock, não faz nada
  
  // Verifica se o indicador já existe para não duplicar
  if (document.getElementById('mock-indicator')) return;
  
  // Cria o elemento indicador
  const mockIndicator = document.createElement('div');
  mockIndicator.id = 'mock-indicator';
  mockIndicator.style.position = 'fixed';
  mockIndicator.style.bottom = '10px';
  mockIndicator.style.left = '10px';
  mockIndicator.style.backgroundColor = '#f59e0b'; // Cor de alerta amarela
  mockIndicator.style.color = '#7c2d12'; // Texto em marrom escuro
  mockIndicator.style.padding = '4px 8px';
  mockIndicator.style.borderRadius = '4px';
  mockIndicator.style.fontSize = '12px';
  mockIndicator.style.fontWeight = 'bold';
  mockIndicator.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.1)';
  mockIndicator.style.zIndex = '9999';
  mockIndicator.innerText = 'MODO MOCK';
  
  // Adiciona ao documento
  document.body.appendChild(mockIndicator);
}

export default {
  useMock,
  setUseMock,
  toggleMock,
  registerApiError,
  getApiErrorReport
}; 