/**
 * Utilitário para gerenciar o uso de mocks em todo o sistema
 */

// Chave para armazenamento no localStorage
const MOCK_STORAGE_KEY = 'modoMockAtivo';

// Verifica se deve usar mock baseado em variável de ambiente ou localStorage
const ENV_USE_MOCK = import.meta.env.VITE_MOCK_ENABLED === 'true';

// Log das variáveis de ambiente para diagnóstico
console.info('🔧 Iniciando frontend com as seguintes configurações:');
console.info(`- API URL: ${import.meta.env.VITE_API_URL || 'http://localhost:8000'}`);
console.info(`- Porta: ${import.meta.env.VITE_PORT || '3000'} (Forçar porta: ${import.meta.env.VITE_FORCE_PORT === 'true' ? 'Sim' : 'Não'})`);
console.info(`- Modo mock: ${ENV_USE_MOCK ? 'Ativado' : 'Desativado'}`);
console.info(`- Ambiente: ${import.meta.env.MODE}`);

// Recupera preferência do usuário do localStorage (se existir)
const getSavedMockPreference = (): boolean => {
  if (typeof window !== 'undefined' && window.localStorage) {
    const saved = localStorage.getItem(MOCK_STORAGE_KEY);
    if (saved !== null) {
      return saved === 'true';
    }
  }
  return false; // Padrão é FALSE (modo real)
};

// Estado global para ativar/desativar mocks em todo o sistema
// Por padrão, usa modo real (false), a menos que forçado por env ou localStorage
let GLOBAL_USE_MOCK = ENV_USE_MOCK || getSavedMockPreference();

// Exibe mensagem no console sobre o modo inicial
if (process.env.NODE_ENV === 'development') {
  if (GLOBAL_USE_MOCK) {
    console.warn("🟠 Sistema iniciado no modo mock (dados simulados).");
  } else {
    console.info("🟢 Sistema usando dados reais (API ativa).");
  }
}

/**
 * Verifica se deve usar mock no sistema
 * 
 * @param forceValue Se informado, sobrescreve a configuração global
 * @returns true se deve usar mock, false caso contrário
 */
export function useMock(forceValue?: boolean): boolean {
  // Se um valor específico foi informado, retorna ele
  if (forceValue !== undefined) {
    return forceValue;
  }
  
  // Verificar se o mock está explicitamente ativado nas variáveis de ambiente
  if (import.meta.env.VITE_MOCK_ENABLED === 'true') {
    return true;
  }
  
  // Caso contrário, retorna o valor global
  return GLOBAL_USE_MOCK;
}

/**
 * Ativa ou desativa o uso de mocks em todo o sistema
 * 
 * @param value true para ativar, false para desativar
 */
export function setUseMock(value: boolean): void {
  GLOBAL_USE_MOCK = value;
  
  // Salvar no localStorage
  if (typeof window !== 'undefined' && window.localStorage) {
    localStorage.setItem(MOCK_STORAGE_KEY, value.toString());
  }
  
  // Exibe mensagem no console para depuração
  if (process.env.NODE_ENV === 'development') {
    if (value) {
      console.warn("🟠 Modo mock ativado (dados simulados).");
    } else {
      console.info("🟢 Usando dados reais (API ativa).");
    }
  }
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

export default {
  useMock,
  setUseMock,
  toggleMock
}; 