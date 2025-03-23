import React, { useEffect } from 'react';
import ReactDOM from 'react-dom';

interface ConfirmDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  description: string;
  confirmText?: string;
  cancelText?: string;
  type?: 'danger' | 'warning' | 'info';
}

/**
 * Componente de diálogo para confirmação de ações críticas ou destrutivas
 * 
 * @param isOpen - Controla se o diálogo está visível
 * @param onClose - Função chamada ao fechar/cancelar
 * @param onConfirm - Função chamada ao confirmar a ação
 * @param title - Título do diálogo
 * @param description - Descrição da ação a ser confirmada
 * @param confirmText - Texto do botão de confirmação (padrão: "Confirmar")
 * @param cancelText - Texto do botão de cancelamento (padrão: "Cancelar")
 * @param type - Tipo do diálogo: 'danger', 'warning' ou 'info' (padrão: 'danger')
 */
const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  description,
  confirmText = "Confirmar",
  cancelText = "Cancelar",
  type = "danger"
}) => {
  // Evitar scroll da página quando o diálogo estiver aberto
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'auto';
    }
    
    return () => {
      document.body.style.overflow = 'auto';
    };
  }, [isOpen]);
  
  // Fechar diálogo ao pressionar ESC
  useEffect(() => {
    const handleEsc = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    
    window.addEventListener('keydown', handleEsc);
    
    return () => {
      window.removeEventListener('keydown', handleEsc);
    };
  }, [isOpen, onClose]);
  
  // Retornar null quando fechado
  if (!isOpen) return null;
  
  // Determinar a classe baseada no tipo
  const getDialogClass = () => {
    switch (type) {
      case 'danger':
        return 'confirm-dialog-danger';
      case 'warning':
        return 'confirm-dialog-warning';
      case 'info':
        return 'confirm-dialog-info';
      default:
        return 'confirm-dialog-danger';
    }
  };
  
  // Ícone baseado no tipo
  const getIcon = () => {
    switch (type) {
      case 'danger':
        return '⚠️';
      case 'warning':
        return '⚠️';
      case 'info':
        return 'ℹ️';
      default:
        return '⚠️';
    }
  };
  
  // Criar portal para o diálogo
  const dialogContent = (
    <div className="dialog-overlay" onClick={onClose}>
      <div 
        className={`confirm-dialog ${getDialogClass()}`} 
        onClick={(e) => e.stopPropagation()}
      >
        <div className="confirm-dialog-header">
          <span className="confirm-dialog-icon">{getIcon()}</span>
          <h3>{title}</h3>
          <button 
            className="confirm-dialog-close" 
            onClick={onClose}
            aria-label="Fechar"
          >
            &times;
          </button>
        </div>
        
        <div className="confirm-dialog-content">
          <p>{description}</p>
        </div>
        
        <div className="confirm-dialog-actions">
          <button 
            className="btn-secondary" 
            onClick={onClose}
          >
            {cancelText}
          </button>
          <button 
            className={`btn-${type === 'info' ? 'primary' : type}`} 
            onClick={() => {
              onConfirm();
              onClose();
            }}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
  
  // Renderizar usando Portal para evitar problemas de z-index
  return ReactDOM.createPortal(
    dialogContent,
    document.body
  );
};

export default ConfirmDialog; 