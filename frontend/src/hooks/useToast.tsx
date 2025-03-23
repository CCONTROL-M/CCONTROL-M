import React, { createContext, useContext, useState, ReactNode } from 'react';
import Toast, { ToastType } from '../components/Toast';

interface ToastContextData {
  showToast: (mensagem: string, tipo: ToastType, duracao?: number) => void;
  closeToast: () => void;
}

interface ToastProviderProps {
  children: ReactNode;
}

const ToastContext = createContext<ToastContextData>({} as ToastContextData);

export function ToastProvider({ children }: ToastProviderProps) {
  const [visible, setVisible] = useState(false);
  const [message, setMessage] = useState('');
  const [type, setType] = useState<ToastType>('info');
  const [duration, setDuration] = useState(3000);

  const showToast = (mensagem: string, tipo: ToastType, duracao = 3000) => {
    setMessage(mensagem);
    setType(tipo);
    setDuration(duracao);
    setVisible(true);
  };

  const closeToast = () => {
    setVisible(false);
  };

  return (
    <ToastContext.Provider value={{ showToast, closeToast }}>
      {children}
      {visible && (
        <Toast
          mensagem={message}
          tipo={type}
          duracao={duration}
          onClose={closeToast}
        />
      )}
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  
  if (!context) {
    throw new Error('useToast deve ser usado dentro de um ToastProvider');
  }
  
  return context;
}

export function useToastUtils() {
  const { showToast } = useToast();
  
  return {
    showSuccessToast: (mensagem: string, duracao?: number) => 
      showToast(mensagem, 'sucesso', duracao),
    
    showErrorToast: (mensagem: string, duracao?: number) => 
      showToast(mensagem, 'erro', duracao),
    
    showWarningToast: (mensagem: string, duracao?: number) => 
      showToast(mensagem, 'aviso', duracao),
    
    showInfoToast: (mensagem: string, duracao?: number) => 
      showToast(mensagem, 'info', duracao)
  };
} 