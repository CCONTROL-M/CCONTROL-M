import React, { createContext, useState, useContext, useEffect, useCallback } from 'react';
import { verificarStatusAPI } from '../services/api';
import { AxiosError } from 'axios';

// Interface para o estado do contexto
interface ApiStatusContextState {
  apiOnline: boolean;
  mensagemErro: string | null;
  ultimaVerificacao: Date | null;
  forcarVerificacao: () => Promise<void>;
  verificandoStatus: boolean;
}

// Criação do contexto com valor padrão
const ApiStatusContext = createContext<ApiStatusContextState>({
  apiOnline: true,
  mensagemErro: null,
  ultimaVerificacao: null,
  forcarVerificacao: async () => {},
  verificandoStatus: false
});

// Intervalo para verificação automática (30 segundos)
const INTERVALO_VERIFICACAO = 30000;

interface ApiStatusProviderProps {
  children: React.ReactNode;
}

export const ApiStatusProvider: React.FC<ApiStatusProviderProps> = ({ children }) => {
  const [apiOnline, setApiOnline] = useState<boolean>(true);
  const [mensagemErro, setMensagemErro] = useState<string | null>(null);
  const [ultimaVerificacao, setUltimaVerificacao] = useState<Date | null>(null);
  const [verificandoStatus, setVerificandoStatus] = useState<boolean>(false);

  // Função para verificar o status da API
  const verificarStatus = useCallback(async (origem: 'automático' | 'manual' = 'automático') => {
    // Evitar múltiplas verificações simultâneas
    if (verificandoStatus) return;
    
    setVerificandoStatus(true);
    
    try {
      const agora = new Date();
      const resultado = await verificarStatusAPI();
      
      setApiOnline(resultado.online);
      setUltimaVerificacao(agora);
      
      // Formatar mensagem de erro se houver
      if (!resultado.online && resultado.error) {
        const erro = resultado.error;
        let mensagem = 'Erro de conexão com o servidor';
        
        if (erro instanceof AxiosError && erro.response) {
          mensagem = `Erro ${erro.response.status}: ${erro.response.statusText}`;
        } else if (erro instanceof Error) {
          mensagem = erro.message;
        }
        
        setMensagemErro(mensagem);
      } else {
        setMensagemErro(null);
      }
      
      // Log de status
      console.log(
        `[API Status] ${resultado.online ? '🟢 Online' : '🔴 Offline'} | ${agora.toLocaleTimeString()} | Origem: ${origem}`,
        resultado.online ? '' : `\nErro: ${mensagemErro}`
      );
    } catch (erro) {
      setApiOnline(false);
      setMensagemErro('Erro ao verificar status da API');
      setUltimaVerificacao(new Date());
      
      console.error('[API Status] Erro ao verificar status', erro);
    } finally {
      setVerificandoStatus(false);
    }
  }, [verificandoStatus, mensagemErro]);

  // Função para forçar a verificação do status
  const forcarVerificacao = useCallback(async () => {
    await verificarStatus('manual');
  }, [verificarStatus]);

  // Efeito para verificar o status da API ao iniciar e periodicamente
  useEffect(() => {
    // Verificação inicial
    verificarStatus('automático');
    
    // Configurar verificação periódica
    const intervalo = setInterval(() => {
      verificarStatus('automático');
    }, INTERVALO_VERIFICACAO);
    
    // Limpeza ao desmontar
    return () => {
      clearInterval(intervalo);
    };
  }, [verificarStatus]);

  // Valor do contexto
  const contextValue: ApiStatusContextState = {
    apiOnline,
    mensagemErro,
    ultimaVerificacao,
    forcarVerificacao,
    verificandoStatus
  };

  return (
    <ApiStatusContext.Provider value={contextValue}>
      {children}
    </ApiStatusContext.Provider>
  );
};

// Hook para usar o estado da API
export const useApiStatus = (): ApiStatusContextState => {
  const context = useContext(ApiStatusContext);
  
  if (context === undefined) {
    throw new Error('useApiStatus deve ser usado dentro de um ApiStatusProvider');
  }
  
  return context;
};

export default ApiStatusProvider; 