import React, { useEffect } from 'react';

export type ToastType = 'sucesso' | 'erro' | 'aviso' | 'info';

export interface ToastProps {
  mensagem: string;
  tipo: ToastType;
  duracao?: number;
  onClose: () => void;
}

const Toast: React.FC<ToastProps> = ({ 
  mensagem, 
  tipo, 
  duracao = 5000, 
  onClose 
}) => {
  // Fechar automaticamente após o tempo definido
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, duracao);

    return () => {
      clearTimeout(timer);
    };
  }, [duracao, onClose]);

  // Mapear tipo para classe CSS e ícone
  const getToastClass = () => {
    switch (tipo) {
      case 'sucesso':
        return 'toast-sucesso';
      case 'erro':
        return 'toast-erro';
      case 'aviso':
        return 'toast-aviso';
      case 'info':
        return 'toast-info';
      default:
        return 'toast-info';
    }
  };

  // Ícone baseado no tipo
  const getToastIcon = () => {
    switch (tipo) {
      case 'sucesso':
        return '✓';
      case 'erro':
        return '✗';
      case 'aviso':
        return '⚠';
      case 'info':
        return 'ℹ';
      default:
        return 'ℹ';
    }
  };

  return (
    <div className={`toast ${getToastClass()}`}>
      <div className="toast-icon">{getToastIcon()}</div>
      <div className="toast-content">{mensagem}</div>
      <button 
        className="toast-close" 
        onClick={onClose}
        aria-label="Fechar"
      >
        ×
      </button>
    </div>
  );
};

export default Toast; 