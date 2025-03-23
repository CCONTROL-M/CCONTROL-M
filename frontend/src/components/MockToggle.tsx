import React from 'react';
import { toggleMock, useMock } from '../utils/mock';

/**
 * Exibe um indicador no canto da tela para mostrar e alternar entre dados reais e mock
 * Útil durante o desenvolvimento e para testes sem backend
 */
export function MockToggle() {
  const isMockEnabled = useMock();
  
  const handleToggle = () => {
    toggleMock();
    // Recarregar a página para aplicar as alterações em todos os componentes
    window.location.reload();
  };
  
  // Só exibe o botão em ambiente de desenvolvimento
  if (process.env.NODE_ENV !== 'development' && !isMockEnabled) {
    return null;
  }
  
  return (
    <button
      onClick={handleToggle}
      title={isMockEnabled ? "Clique para usar dados reais" : "Clique para usar dados simulados"}
      style={{
        position: 'fixed',
        bottom: '50px',
        right: '20px',
        zIndex: 9999,
        padding: '8px 12px',
        backgroundColor: isMockEnabled ? '#F97316' : '#10B981',
        color: 'white',
        border: 'none',
        borderRadius: '8px',
        cursor: 'pointer',
        fontSize: '14px',
        fontWeight: 'bold',
        display: 'flex',
        alignItems: 'center',
        gap: '6px',
        boxShadow: '0 2px 5px rgba(0,0,0,0.2)',
        opacity: 0.9,
        transition: 'all 0.2s ease'
      }}
      onMouseOver={(e) => {
        e.currentTarget.style.opacity = '1';
        e.currentTarget.style.transform = 'translateY(-2px)';
      }}
      onMouseOut={(e) => {
        e.currentTarget.style.opacity = '0.9';
        e.currentTarget.style.transform = 'translateY(0)';
      }}
    >
      <span role="img" aria-label={isMockEnabled ? "Modo mock" : "Modo real"}>
        {isMockEnabled ? '🟠' : '🟢'}
      </span>
      {isMockEnabled ? 'Modo Simulado' : 'Modo Real'}
    </button>
  );
}

export default MockToggle; 