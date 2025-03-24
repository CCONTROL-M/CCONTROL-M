import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useMock, setUseMock } from '../utils/mock';

interface MockToggleProps {
  className?: string;
}

/**
 * Componente para alternar entre modos de dados reais e mockados
 * IMPORTANTE: Este componente só deve ser usado em ambiente de desenvolvimento.
 * Em produção, o sistema sempre operará com dados reais.
 */
const MockToggle: React.FC<MockToggleProps> = ({ className = '' }) => {
  // Se não estiver em ambiente de desenvolvimento, não renderiza nada
  if (!import.meta.env.DEV) {
    return null;
  }
  
  // Estado local para o modo mock
  const [isMockEnabled, setIsMockEnabled] = useState<boolean>(useMock());
  
  // Referência para verificar se o estado mudou
  const lastMockStateRef = useRef<boolean>(useMock());
  
  // Referência para acompanhar se estamos em transição de modo
  const isTransitioningRef = useRef<boolean>(false);

  // Sincronizar o estado local com o estado global
  useEffect(() => {
    // Verificar localStorage diretamente para garantir sincronização
    const checkMockState = () => {
      try {
        const currentMockState = useMock();
        if (currentMockState !== isMockEnabled) {
          setIsMockEnabled(currentMockState);
        }
        lastMockStateRef.current = currentMockState;
      } catch (error) {
        console.error('Erro ao sincronizar estado de mock:', error);
      }
    };
    
    // Verificar estado imediatamente
    checkMockState();
    
    // Verificar periodicamente (a cada 2 segundos)
    const interval = setInterval(checkMockState, 2000);
    
    // Limpar intervalo ao desmontar
    return () => {
      clearInterval(interval);
    };
  }, [isMockEnabled]);
  
  // Manipulador de alternância otimizado
  const handleToggle = useCallback(() => {
    // Evitar múltiplas transições simultâneas
    if (isTransitioningRef.current) {
      console.log('Transição já em andamento, ignorando clique');
      return;
    }
    
    try {
      isTransitioningRef.current = true;
      console.log('Iniciando transição de modo mock...');
      
      // Determinar o novo estado (inverso do atual)
      const newState = !isMockEnabled;
      console.log(`Alterando modo de ${isMockEnabled ? 'mock' : 'real'} para ${newState ? 'mock' : 'real'}`);
      
      // Atualizar estado local
      setIsMockEnabled(newState);
      
      // Atualizar estado global e localStorage
      setUseMock(newState);
      
      // Verificar se localStorage foi atualizado corretamente
      const savedValue = localStorage.getItem('modoMockAtivo');
      console.log(`Valor salvo no localStorage: ${savedValue}`);
      
      // Mostrar uma notificação
      const message = document.createElement('div');
      message.className = 'fixed top-4 right-4 z-50 bg-blue-600 text-white py-2 px-4 rounded shadow-lg';
      message.textContent = `Alterando para ${newState ? 'dados simulados' : 'dados reais'}...`;
      document.body.appendChild(message);
      
      // Forçar um hard reload após um breve atraso
      setTimeout(() => {
        try {
          console.log('Recarregando página após troca de modo...');
          // Usar location.reload(true) para forçar recarga sem cache
          window.location.href = window.location.pathname + '?t=' + Date.now();
        } catch (error) {
          console.error('Erro ao recarregar página:', error);
          // Fallback se o redirecionamento falhar
          window.location.reload();
        }
      }, 800);
    } catch (error) {
      console.error('Erro ao alternar modo mock:', error);
      isTransitioningRef.current = false;
      alert('Erro ao alternar modo. Tente recarregar a página manualmente.');
    }
  }, [isMockEnabled]);
  
  return (
    <div 
      className={`fixed bottom-4 left-4 z-50 bg-white rounded-lg border border-gray-200 shadow-md p-3 transition-opacity duration-200 ${
        isTransitioningRef.current ? 'opacity-50' : 'opacity-100'
      } ${className}`}
    >
      <div className="flex flex-col items-center gap-2">
        <div className="text-center">
          <div className={`font-bold ${isMockEnabled ? 'text-orange-600' : 'text-green-600'}`}>
            {isMockEnabled ? 'MODO MOCK ATIVO' : 'DADOS REAIS'}
          </div>
          <p className="text-xs text-gray-500">
            {isMockEnabled 
              ? 'Usando dados simulados para teste' 
              : 'Conectado ao servidor de API'}
          </p>
        </div>
        
        <div className="flex items-center">
          <span className="text-xs mr-2">API</span>
          <button
            onClick={handleToggle}
            disabled={isTransitioningRef.current}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ${
              isMockEnabled ? 'bg-gray-200' : 'bg-green-600'
            } ${isTransitioningRef.current ? 'cursor-not-allowed opacity-70' : ''}`}
            role="switch"
            aria-checked={!isMockEnabled}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                isMockEnabled ? 'translate-x-1' : 'translate-x-6'
              }`}
            />
          </button>
          <span className="text-xs ml-2">MOCK</span>
        </div>
        
        <button
          onClick={handleToggle}
          disabled={isTransitioningRef.current}
          className={`text-xs py-1 px-3 rounded ${
            isMockEnabled
              ? 'bg-green-100 text-green-700 hover:bg-green-200'
              : 'bg-orange-100 text-orange-700 hover:bg-orange-200'
          } ${isTransitioningRef.current ? 'cursor-not-allowed opacity-70' : ''}`}
        >
          {isMockEnabled ? 'Usar dados reais' : 'Usar dados mockados'}
        </button>
        
        <div className="text-xs text-gray-500 mt-1 text-center">
          <em>Apenas para ambiente de desenvolvimento</em>
        </div>
      </div>
    </div>
  );
};

export default MockToggle; 