import React, { useState, useEffect } from "react";
import { CONFIRM_DIALOG_EVENTS } from "../hooks/useConfirmDialog";

/**
 * Componente que mostra um indicador visual quando um diálogo de confirmação está ativo
 * Este indicador aparece no canto inferior direito da tela
 */
const ConfirmDialogStatus = () => {
  // Estado para controlar a visibilidade do indicador
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Função para lidar com o evento de abertura do diálogo
    const handleDialogOpened = () => {
      setIsVisible(true);
    };

    // Função para lidar com o evento de fechamento do diálogo
    const handleDialogClosed = () => {
      setIsVisible(false);
    };

    // Adicionar os event listeners
    document.addEventListener(CONFIRM_DIALOG_EVENTS.OPENED, handleDialogOpened);
    document.addEventListener(CONFIRM_DIALOG_EVENTS.CLOSED, handleDialogClosed);

    // Cleanup: remover os event listeners quando o componente for desmontado
    return () => {
      document.removeEventListener(CONFIRM_DIALOG_EVENTS.OPENED, handleDialogOpened);
      document.removeEventListener(CONFIRM_DIALOG_EVENTS.CLOSED, handleDialogClosed);
    };
  }, []);

  // Se não estiver visível, não renderizar nada
  if (!isVisible) return null;

  return (
    <div className="confirm-dialog-status">
      <span role="img" aria-label="Cadeado">🔒</span> Confirmação ativa
    </div>
  );
};

export default ConfirmDialogStatus; 