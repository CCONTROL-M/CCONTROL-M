import React, { useEffect, useRef, useState } from 'react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  size?: 'small' | 'medium' | 'large' | 'full';
  /**
   * Ajusta o modal para ocupar a tela inteira em dispositivos móveis
   * @default true
   */
  fullScreenOnMobile?: boolean;
  /**
   * Tipo de posicionamento do modal na tela
   * - 'center': centralizado na tela (padrão)
   * - 'bottom': inicia na parte inferior e slide para cima (ideal para mobile)
   */
  position?: 'center' | 'bottom';
}

/**
 * Componente de Modal padronizado e responsivo
 * Usa os tokens visuais do sistema para garantir consistência
 * Adapta-se automaticamente para dispositivos móveis
 */
const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'medium',
  fullScreenOnMobile = true,
  position = 'center'
}) => {
  const modalRef = useRef<HTMLDivElement>(null);
  const [windowWidth, setWindowWidth] = useState(window.innerWidth);
  const isMobile = windowWidth <= 768;
  
  // Monitor de tamanho da janela para responsividade
  useEffect(() => {
    const handleResize = () => {
      setWindowWidth(window.innerWidth);
    };
    
    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);
  
  // Fechar o modal ao pressionar a tecla ESC
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    
    document.addEventListener('keydown', handleKeyDown);
    
    // Prevenir o scroll da página quando o modal estiver aberto
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    }
    
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'auto';
    };
  }, [isOpen, onClose]);
  
  // Fechar o modal ao clicar fora dele
  const handleOverlayClick = (e: React.MouseEvent) => {
    if (modalRef.current && !modalRef.current.contains(e.target as Node)) {
      onClose();
    }
  };
  
  if (!isOpen) return null;
  
  // Definir largura máxima com base no tamanho
  const sizeStyles: Record<string, React.CSSProperties> = {
    small: { maxWidth: '400px' },
    medium: { maxWidth: '600px' },
    large: { maxWidth: '800px' },
    full: { maxWidth: '100%', width: '100%', height: '100%' }
  };
  
  // Em modo mobile com fullScreenOnMobile, força o tamanho 'full'
  const effectiveSize = (isMobile && fullScreenOnMobile) ? 'full' : size;
  
  // Determinar classes para posicionamento
  const overlayClasses = [
    'modal-overlay',
    position === 'bottom' ? 'modal-overlay-bottom' : ''
  ].filter(Boolean).join(' ');
  
  const contentClasses = [
    'modal-content',
    position === 'bottom' ? 'modal-content-bottom' : '',
    isMobile && fullScreenOnMobile ? 'modal-content-fullscreen-mobile' : ''
  ].filter(Boolean).join(' ');
  
  return (
    <div 
      className={overlayClasses} 
      onClick={handleOverlayClick}
      aria-modal="true"
      role="dialog"
    >
      <div 
        ref={modalRef}
        className={contentClasses}
        onClick={(e) => e.stopPropagation()} // Previne que o modal feche ao clicar dentro dele
        style={sizeStyles[effectiveSize]}
      >
        <div className="modal-header">
          <h2>{title}</h2>
          <button 
            className="modal-close-button" 
            onClick={onClose} 
            aria-label="Fechar"
          >
            &times;
          </button>
        </div>
        <div className="modal-body">
          {children}
        </div>
        
        {/* Adicionar um botão de fechar no rodapé em telas pequenas */}
        {isMobile && (
          <div className="modal-footer-mobile">
            <button 
              className="btn btn-secondary modal-close-button-mobile" 
              onClick={onClose}
            >
              Fechar
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Modal; 