import { useState, useEffect } from 'react';

// Definir os nomes dos eventos personalizados
export const CONFIRM_DIALOG_EVENTS = {
  OPENED: 'confirm-dialog-opened',
  CLOSED: 'confirm-dialog-closed'
};

export type ConfirmDialogState = {
  isOpen: boolean;
  title: string;
  description: string;
  onConfirm: () => void;
  confirmText?: string;
  cancelText?: string;
  type?: 'danger' | 'warning' | 'info';
};

/**
 * Hook para gerenciar o estado e funcionamento do ConfirmDialog
 * 
 * @returns Métodos para controlar o diálogo de confirmação
 */
export function useConfirmDialog() {
  const [dialog, setDialog] = useState<ConfirmDialogState>({
    isOpen: false,
    title: '',
    description: '',
    onConfirm: () => {},
    confirmText: 'Confirmar',
    cancelText: 'Cancelar',
    type: 'danger'
  });

  // Emitir eventos quando o estado do diálogo mudar
  useEffect(() => {
    // Quando o diálogo é aberto, emitir o evento OPENED
    if (dialog.isOpen) {
      const event = new CustomEvent(CONFIRM_DIALOG_EVENTS.OPENED, {
        detail: dialog
      });
      document.dispatchEvent(event);
    } else {
      // Quando o diálogo é fechado, emitir o evento CLOSED
      const event = new CustomEvent(CONFIRM_DIALOG_EVENTS.CLOSED);
      document.dispatchEvent(event);
    }
  }, [dialog.isOpen]);

  /**
   * Abre o diálogo de confirmação
   */
  const confirm = (options: Omit<ConfirmDialogState, 'isOpen'>) => {
    setDialog({
      ...options,
      isOpen: true
    });

    // Retorna uma promessa que será resolvida quando o usuário confirmar ou rejeitada quando cancelar
    return new Promise<void>((resolve, reject) => {
      setDialog({
        ...options,
        isOpen: true,
        onConfirm: () => {
          options.onConfirm?.();
          resolve();
          closeDialog();
        }
      });
    });
  };

  /**
   * Fecha o diálogo de confirmação
   */
  const closeDialog = () => {
    setDialog({
      ...dialog,
      isOpen: false
    });
  };

  return {
    dialog,
    confirm,
    closeDialog
  };
}

export default useConfirmDialog; 