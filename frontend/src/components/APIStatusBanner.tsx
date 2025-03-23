import React, { useEffect, useState } from 'react';
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
  
  // Verificar se o modo mock está ativado
  const mockEnabled = useMock();
  
  // Usar o contexto global de status da API
  const { apiOnline, mensagemErro } = useApiStatus();

  useEffect(() => {
    // Se o modo mock está ativado, mostrar um banner informativo
    if (mockEnabled) {
      console.log('Mock ativado - exibindo banner de aviso');
      setBannerState({
        show: true,
        type: 'warning',
        message: '⚠️ Usando dados de exemplo (modo simulado)'
      });
      return;
    }
    
    // Gerenciar estado do banner baseado no status da API
    if (!apiOnline) {
      // API está offline
      console.log('API offline - exibindo banner de erro');
      setBannerState({
        show: true,
        type: 'error',
        message: mensagemErro ? `🔴 ${mensagemErro}` : '🔴 Servidor indisponível. Usando dados locais...'
      });
      setWasOffline(true);
    } else if (apiOnline && wasOffline) {
      // API estava offline e agora está online novamente
      console.log('API restaurada - exibindo banner de sucesso');
      setBannerState({
        show: true,
        type: 'success',
        message: '🟢 Conectado com sucesso!'
      });
      
      // Esconder o banner de sucesso após 3 segundos
      setTimeout(() => {
        setBannerState(prev => ({ ...prev, show: false }));
      }, 3000);
      
      setWasOffline(false);
    } else if (apiOnline && !wasOffline) {
      // API está online desde o início, não mostrar banner
      setBannerState({ show: false, type: 'success', message: '' });
    }
  }, [apiOnline, mensagemErro, wasOffline, mockEnabled]);

  // Não renderizar nada se o banner não deve ser mostrado
  if (!bannerState.show) {
    return null;
  }

  // Classes CSS com base no tipo de banner
  const bannerClass = `api-status-banner ${
    bannerState.type === 'error' 
      ? 'api-status-error' 
      : bannerState.type === 'success'
        ? 'api-status-success'
        : 'api-status-warning'
  }`;

  return (
    <div className={bannerClass}>
      {bannerState.message}
    </div>
  );
};

export default APIStatusBanner; 