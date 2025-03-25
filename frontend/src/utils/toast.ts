import { useToast } from '../hooks/useToast';

// Importar tipo ToastType do componente Toast
import { ToastType } from '../components/Toast';

// Armazenar a função showToast quando disponível
let _showToastFn: ((message: string, type: ToastType, duration?: number) => void) | null = null;

// Função para inicializar o showToast
export const initializeToast = (showToastFn: (message: string, type: ToastType, duration?: number) => void) => {
  _showToastFn = showToastFn;
};

/**
 * Utilitário para mostrar toasts fora de componentes React
 * 
 * @param message Mensagem a ser exibida
 * @param type Tipo do toast ('sucesso', 'erro', 'aviso', 'info')
 * @param duration Duração do toast em ms (opcional)
 */
export const showToast = (message: string, type: ToastType = 'info', duration?: number) => {
  // Se não tivermos a função showToast disponível, logamos um aviso
  if (!_showToastFn) {
    console.warn('Toast não inicializado. Certifique-se que ToastProvider está renderizado.');
    console.log(`[Toast não mostrado]: ${message} (${type})`);
    return;
  }
  
  // Chamar a função real de toast
  _showToastFn(message, type, duration);
};

/**
 * Hook para inicializar o toast no contexto React
 * Deve ser chamado no componente raiz (App ou layout principal)
 */
export const useInitializeToast = () => {
  const { showToast: contextShowToast } = useToast();
  
  // Inicializar o toast global
  initializeToast(contextShowToast);
}; 