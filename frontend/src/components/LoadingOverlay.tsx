import React, { useEffect, useState } from 'react';

interface LoadingOverlayProps {
  visible: boolean;
  text?: string;
  theme?: 'light' | 'dark';
  blur?: boolean;
}

/**
 * Overlay de carregamento para toda a aplicação
 * 
 * @param visible Determina se o overlay está visível
 * @param text Texto a ser exibido (padrão: "Carregando...")
 * @param theme Tema do overlay ('light' | 'dark')
 * @param blur Se deve aplicar efeito de desfoque no fundo
 */
const LoadingOverlay: React.FC<LoadingOverlayProps> = ({ 
  visible, 
  text = "Carregando...", 
  theme = 'dark',
  blur = false // Nunca usar blur por padrão para melhorar desempenho
}) => {
  const [show, setShow] = useState(visible);
  const [isExiting, setIsExiting] = useState(false);
  
  useEffect(() => {
    let timer: number;
    if (visible) {
      setShow(true);
      setIsExiting(false);
    } else {
      setIsExiting(true);
      // Aguardar a animação terminar antes de remover o componente do DOM
      // Reduzido para 150ms para ser mais rápido
      timer = window.setTimeout(() => {
        setShow(false);
      }, 150);
    }
    
    // Limpar timer para evitar problemas de memória
    return () => {
      if (timer) window.clearTimeout(timer);
    };
  }, [visible]);
  
  // Se não está visível nem em animação de saída, não renderizar
  if (!show) return null;
  
  // Definir classes com base nas props
  const overlayClasses = [
    'loading-overlay',
    theme === 'light' ? 'loading-overlay--light' : 'loading-overlay--dark',
    blur ? 'loading-overlay--blur' : '',
    isExiting ? 'loading-overlay--exiting' : 'loading-overlay--entering',
    'loading-overlay--transparent' // Tornar o overlay mais transparente para ser menos intrusivo
  ].filter(Boolean).join(' ');

  return (
    <div 
      className={overlayClasses}
      aria-hidden={!visible || isExiting}
      role="dialog"
      aria-live="assertive"
      aria-busy={visible}
      data-testid="loading-overlay"
    >
      <div className="loading-content">
        <div className="loading-spinner"></div>
        <div className="loading-text">{text}</div>
      </div>
    </div>
  );
};

export default LoadingOverlay; 