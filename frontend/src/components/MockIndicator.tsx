import React from 'react';
import { useMock } from '../utils/mock';

/**
 * Componente leve para mostrar um indicador discreto de modo mock ativo
 * Aparece apenas quando o modo mock está ativado
 */
const MockIndicator: React.FC = () => {
  const isMockEnabled = useMock();
  
  // Não renderizar nada se o mock não estiver ativo
  if (!isMockEnabled) return null;
  
  return (
    <div 
      className="fixed top-1 right-1 bg-orange-500 text-white text-xs px-2 py-0.5 rounded-sm shadow-sm opacity-70 z-50"
      title="Usando dados simulados (modo mock ativo)"
    >
      MOCK
    </div>
  );
};

export default MockIndicator; 