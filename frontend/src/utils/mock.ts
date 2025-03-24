/**
 * Utilitário para gerenciar o uso de mocks em todo o sistema
 */

// Chave para armazenamento no localStorage
const MOCK_STORAGE_KEY = 'modoMockAtivo';

// Log das variáveis de ambiente para diagnóstico
console.info('🔧 Iniciando frontend com as seguintes configurações:');
console.info(`- API URL: ${import.meta.env.VITE_API_URL || 'http://localhost:8000'}`);
console.info(`- Porta: ${import.meta.env.VITE_PORT || '3000'} (Forçar porta: ${import.meta.env.VITE_FORCE_PORT === 'true' ? 'Sim' : 'Não'})`);
console.info(`- Modo mock: Desativado (padrão)`);
console.info(`- Ambiente: ${import.meta.env.MODE}`);

// Recupera preferência do usuário do localStorage (se existir)
const getSavedMockPreference = (): boolean => {
  try {
    if (typeof window !== 'undefined' && window.localStorage) {
      const savedPreference = localStorage.getItem(MOCK_STORAGE_KEY);
      // Verificação rígida: apenas retorna true se o valor for exatamente 'true'
      if (savedPreference === 'true') {
        return true;
      }
      // Em todos os outros casos, incluindo valores inválidos, nulos ou undefined
      return false;
    }
  } catch (error) {
    console.error('Erro ao ler preferência de mock do localStorage:', error);
  }
  // Padrão é SEMPRE false (dados reais)
  return false;
}

// Configura o modo de mock global com base apenas em preferências salvas
// Inicializar explicitamente como false no início e depois verificar o localStorage
let GLOBAL_USE_MOCK = false;

// Agora verifica o localStorage
try {
  GLOBAL_USE_MOCK = getSavedMockPreference();
} catch (error) {
  console.error('Erro ao inicializar modo mock:', error);
  // Em caso de erro, manterá como false
}

// Rastreia os erros de API para diagnóstico
interface ApiErrorRecord {
  count: number;
  lastMessage: string;
  timestamp: number;
}

const apiErrors: Record<string, ApiErrorRecord> = {};

// Exibe mensagem no console sobre o modo inicial
if (import.meta.env.DEV) {
  if (GLOBAL_USE_MOCK) {
    console.warn("🟠 Sistema iniciado no modo mock (dados simulados).");
  } else {
    console.info("🟢 Sistema iniciado com dados reais (API ativa).");
  }
}

/**
 * Verifica se deve usar mock no sistema
 * 
 * @param forceValue Se informado, sobrescreve a configuração global
 * @returns true se deve usar mock, false caso contrário
 */
export function useMock(forceValue?: boolean): boolean {
  // Se um valor específico foi passado, retorná-lo
  if (forceValue !== undefined) {
    return forceValue;
  }
  
  // Verificar novamente o localStorage para garantir sincronização
  // Isso evita que mudanças em outras abas ou componentes não sejam refletidas
  if (typeof window !== 'undefined' && window.localStorage) {
    try {
      // Apenas atualiza GLOBAL_USE_MOCK se o localStorage tiver um valor diferente
      const savedPreference = localStorage.getItem(MOCK_STORAGE_KEY) === 'true';
      if (savedPreference !== GLOBAL_USE_MOCK) {
        GLOBAL_USE_MOCK = savedPreference;
      }
    } catch (error) {
      // Em caso de erro, ignora e mantém o valor atual
      console.error('Erro ao acessar localStorage em useMock():', error);
    }
  }
  
  return GLOBAL_USE_MOCK;
}

/**
 * Ativa ou desativa o uso de mocks em todo o sistema
 * 
 * @param value true para ativar, false para desativar
 */
export function setUseMock(value: boolean): void {
  // Certifique-se de que o valor seja um booleano
  const boolValue = Boolean(value);
  
  // Atualizar a variável global
  GLOBAL_USE_MOCK = boolValue;
  
  // Persistir no localStorage
  saveUserMockPreference(boolValue);
  
  // Exibir status
  logMockStatus();
}

/**
 * Registra um erro da API para diagnóstico
 * 
 * @param endpoint Endpoint que gerou o erro
 * @param error Objeto de erro
 */
export function registerApiError(endpoint: string, error: any): void {
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
  
  // Apenas registrar erros sem sugerir modo mock
  if (apiErrors[endpoint].count >= 3) {
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
  setUseMock(!GLOBAL_USE_MOCK);
}

// Função que adiciona um indicador visual de que estamos em modo mock
export function adicionarIndicadorMock() {
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

// Salva a preferência do usuário no localStorage
function saveUserMockPreference(value: boolean): void {
  try {
    if (typeof window !== 'undefined' && window.localStorage) {
      // Log de diagnóstico para identificar quem está chamando
      console.log('[Mock] modoMockAtivo setado como:', value, '- Stack trace:', new Error().stack);
      
      // Importante: sempre converter para string
      localStorage.setItem(MOCK_STORAGE_KEY, value.toString());
      
      // Verificar se foi salvo corretamente
      const checkSaved = localStorage.getItem(MOCK_STORAGE_KEY);
      if (checkSaved !== value.toString()) {
        console.error(`Falha ao salvar preferência de mock: valor esperado "${value}" mas obteve "${checkSaved}"`);
      }
    }
  } catch (error) {
    console.error('Erro ao salvar preferência de mock no localStorage:', error);
  }
}

// Exibe o status atual do mock no console
function logMockStatus(): void {
  if (import.meta.env.DEV) {
    if (GLOBAL_USE_MOCK) {
      console.warn("🟠 Modo mock ativado (dados simulados).");
    } else {
      console.info("🟢 Usando dados reais (API ativa).");
    }
  }
  
  // Reseta os erros de API quando alternar para modo mock
  if (GLOBAL_USE_MOCK) {
    resetApiErrors();
  }
}

export default {
  useMock,
  setUseMock,
  toggleMock,
  registerApiError,
  getApiErrorReport
}; 