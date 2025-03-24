import React, { useEffect, useState, useRef } from 'react';
import { useMock } from '../utils/mock';
import { useApiStatus } from '../contexts/ApiStatusContext';

// Interface para controlar o estado do banner
interface BannerState {
  show: boolean;
  type: 'error' | 'success' | 'warning';
  message: string;
}

const APIStatusBanner: React.FC = () => {
  // Estado para controlar a visibilidade e tipo do banner
  const [bannerState, setBannerState] = useState<BannerState>({
    show: false,
    type: 'error',
    message: ''
  });

  // Estado para rastrear se a API estava offline anteriormente
  const [wasOffline, setWasOffline] = useState<boolean>(false);
  
  // Referência para o timer de esconder o banner
  const hideTimerRef = useRef<number | null>(null);
  
  // Verificar se o modo mock está ativado
  const mockEnabled = useMock();
  
  // Usar o contexto global de status da API
  const { apiOnline, mensagemErro } = useApiStatus();

  useEffect(() => {
    // Limpar qualquer timer existente
    if (hideTimerRef.current) {
      clearTimeout(hideTimerRef.current);
      hideTimerRef.current = null;
    }
    
    // Se o modo mock está ativado, mostrar um banner informativo
    if (mockEnabled) {
      // Evitar atualizações desnecessárias do estado
      if (!bannerState.show || bannerState.type !== 'warning' || 
          bannerState.message !== '⚠️ Usando dados de exemplo (modo simulado)') {
        setBannerState({
          show: true,
          type: 'warning',
          message: '⚠️ Usando dados de exemplo (modo simulado)'
        });
      }
      return;
    }
    
    // Gerenciar estado do banner baseado no status da API
    if (!apiOnline) {
      // API está offline - Evitar atualizações desnecessárias
      const newMessage = mensagemErro ? `🔴 ${mensagemErro}` : '🔴 Servidor indisponível. Usando dados locais...';
      if (!bannerState.show || bannerState.type !== 'error' || bannerState.message !== newMessage) {
        setBannerState({
          show: true,
          type: 'error',
          message: newMessage
        });
      }
      setWasOffline(true);
    } else if (apiOnline && wasOffline) {
      // API estava offline e agora está online novamente
      setBannerState({
        show: true,
        type: 'success',
        message: '🟢 Conectado com sucesso!'
      });
      
      // Esconder o banner de sucesso após 3 segundos
      hideTimerRef.current = window.setTimeout(() => {
        setBannerState(prev => ({ ...prev, show: false }));
        hideTimerRef.current = null;
      }, 3000);
      
      setWasOffline(false);
    } else if (apiOnline && !wasOffline) {
      // API está online desde o início, não mostrar banner
      // Evitar atualizações desnecessárias do estado
      if (bannerState.show) {
        setBannerState({ show: false, type: 'success', message: '' });
      }
    }
    
    // Limpeza do efeito
    return () => {
      if (hideTimerRef.current) {
        clearTimeout(hideTimerRef.current);
        hideTimerRef.current = null;
      }
    };
  }, [apiOnline, mensagemErro, wasOffline, mockEnabled, bannerState]);

  // Memo para classes CSS com base no tipo de banner
  const bannerClass = `api-status-banner ${
    bannerState.type === 'error' 
      ? 'api-status-error' 
      : bannerState.type === 'success'
        ? 'api-status-success'
        : 'api-status-warning'
  }`;

  // Não renderizar nada se o banner não deve ser mostrado
  if (!bannerState.show) {
    return null;
  }

  return (
    <div className={bannerClass}>
      {bannerState.message}
    </div>
  );
};

export default APIStatusBanner; 