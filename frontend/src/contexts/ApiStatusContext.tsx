import React, { createContext, useState, useContext, useEffect, useCallback, useRef } from 'react';
import { verificarStatusAPI } from '../services/api';
import { AxiosError } from 'axios';
import { useMock } from '../utils/mock';

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

// Intervalo para verificação automática aumentado para 2 minutos
const INTERVALO_VERIFICACAO = 120000;

interface ApiStatusProviderProps {
  children: React.ReactNode;
}

export const ApiStatusProvider: React.FC<ApiStatusProviderProps> = ({ children }) => {
  const [apiOnline, setApiOnline] = useState<boolean>(true);
  const [mensagemErro, setMensagemErro] = useState<string | null>(null);
  const [ultimaVerificacao, setUltimaVerificacao] = useState<Date | null>(null);
  const [verificandoStatus, setVerificandoStatus] = useState<boolean>(false);
  
  // Usar ref para rastrear verificações em andamento
  const verificacaoEmAndamentoRef = useRef<boolean>(false);
  
  // Verificar se o modo mock está ativado
  const isMockEnabled = useMock();

  // Função para verificar o status da API
  const verificarStatus = useCallback(async (origem: 'automático' | 'manual' = 'automático') => {
    // Evitar verificações quando o modo mock está ativado (exceto verificações manuais)
    if (isMockEnabled && origem === 'automático') {
      return { online: true, error: null };
    }
    
    // Evitar múltiplas verificações simultâneas usando uma ref
    if (verificacaoEmAndamentoRef.current) return;
    verificacaoEmAndamentoRef.current = true;
    
    // Apenas definir estado para verificações manuais
    if (origem === 'manual') {
      setVerificandoStatus(true);
    }
    
    try {
      const agora = new Date();
      const resultado = await verificarStatusAPI();
      
      // Prevenir atualizações de estado desnecessárias
      if (resultado.online !== apiOnline) {
        setApiOnline(resultado.online);
      }
      
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
        
        if (mensagemErro !== mensagem) {
          setMensagemErro(mensagem);
        }
      } else if (mensagemErro !== null) {
        setMensagemErro(null);
      }
      
      return resultado;
    } catch (erro) {
      if (apiOnline) {
        setApiOnline(false);
      }
      
      const mensagem = 'Erro ao verificar status da API';
      if (mensagemErro !== mensagem) {
        setMensagemErro(mensagem);
      }
      
      setUltimaVerificacao(new Date());
      
      if (origem === 'manual') {
        console.error('[API Status] Erro ao verificar status', erro);
      }
      
      return { online: false, error: erro };
    } finally {
      verificacaoEmAndamentoRef.current = false;
      if (origem === 'manual') {
        setVerificandoStatus(false);
      }
    }
  }, [isMockEnabled, apiOnline, mensagemErro]);
  
  // Função exposta para forçar verificação manual
  const forcarVerificacao = useCallback(async () => {
    await verificarStatus('manual');
  }, [verificarStatus]);
  
  // Efeito para verificar o status da API ao iniciar e periodicamente
  useEffect(() => {
    // Não fazer verificações automáticas se o mock estiver ativado
    if (isMockEnabled) return;
    
    let isMounted = true;
    let intervalId: number;
    
    // Função segura para verificação
    const checkStatus = async () => {
      if (!isMounted) return;
      await verificarStatus('automático');
    };
    
    // Verificar após um delay inicial para não atrapalhar a renderização
    const timeoutId = setTimeout(() => {
      if (isMounted) {
        checkStatus();
        
        // Iniciar verificações periódicas
        intervalId = window.setInterval(checkStatus, INTERVALO_VERIFICACAO);
      }
    }, 5000); // Aumentar o delay inicial para 5 segundos
    
    // Limpeza ao desmontar
    return () => {
      isMounted = false;
      clearTimeout(timeoutId);
      clearInterval(intervalId);
    };
  }, [verificarStatus, isMockEnabled]);

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

// Hook para usar o contexto
export const useApiStatus = (): ApiStatusContextState => {
  const context = useContext(ApiStatusContext);
  
  if (!context) {
    throw new Error('useApiStatus deve ser usado dentro de um ApiStatusProvider');
  }
  
  return context;
};

export default ApiStatusProvider; 