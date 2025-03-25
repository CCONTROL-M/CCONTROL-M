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

// Intervalo para verificação automática - reduzido para 60 segundos
const INTERVALO_VERIFICACAO = 60000;

interface ApiStatusProviderProps {
  children: React.ReactNode;
}

export const ApiStatusProvider: React.FC<ApiStatusProviderProps> = ({ children }) => {
  // Forçar sempre como online para ambiente de desenvolvimento
  const [apiOnline, setApiOnline] = useState<boolean>(true);
  const [mensagemErro, setMensagemErro] = useState<string | null>(null);
  const [ultimaVerificacao, setUltimaVerificacao] = useState<Date | null>(new Date()); // Já definir uma data inicial
  const [verificandoStatus, setVerificandoStatus] = useState<boolean>(false);
  
  // Usar ref para rastrear verificações em andamento
  const verificacaoEmAndamentoRef = useRef<boolean>(false);
  
  // Verificar se o modo mock está ativado
  const isMockEnabled = useMock();

  // Função para verificar o status da API
  const verificarStatus = useCallback(async (origem: 'automático' | 'manual' = 'automático') => {
    // Em ambiente de desenvolvimento, sempre retornar online=true
    if (import.meta.env.DEV) {
      console.log("[API Status] Forçando status como ONLINE para ambiente de desenvolvimento");
      
      // Atualizar a data da verificação se for verificação manual
      if (origem === 'manual') {
        setUltimaVerificacao(new Date());
        
        // Garantir que o status seja true e sem mensagem de erro
        if (!apiOnline) setApiOnline(true);
        if (mensagemErro) setMensagemErro(null);
      }
      
      // Sempre retornar como online em desenvolvimento
      return { online: true, error: null };
    }
    
    // Resto do código original para ambientes de produção
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
      
      // Tentar a verificação real da API (mesmo em desenvolvimento, tentamos - mas não alteramos o estado)
      const resultado = await verificarStatusAPI();
      
      // Em ambiente não-desenvolvimento, atualizar o estado conforme o resultado real
      if (!import.meta.env.DEV) {
        // Prevenir atualizações de estado desnecessárias
        if (resultado.online !== apiOnline) {
          setApiOnline(resultado.online);
        }
        
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
      } else {
        // Em DEV, logar resultado mas não alterar estado
        console.log(`[API Status] Verificação real: ${resultado.online ? 'online' : 'offline'}, mas mantendo forçado como online`);
      }
      
      // Sempre atualizar a data de verificação
      setUltimaVerificacao(agora);
      
      // Em DEV, forçar resultado como online ignorando o resultado real
      return import.meta.env.DEV ? { online: true, error: null } : resultado;
    } catch (erro) {
      // Em DEV, ignorar erro e manter online
      if (import.meta.env.DEV) {
        console.error('[API Status] Erro ao verificar status, mas mantendo forçado como online:', erro);
        setUltimaVerificacao(new Date());
        return { online: true, error: null };
      }
      
      // Em produção, tratar normalmente
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
    
    // Verificar imediatamente na inicialização
    checkStatus();
    
    // Iniciar verificações periódicas
    intervalId = window.setInterval(checkStatus, INTERVALO_VERIFICACAO);
    
    // Limpeza ao desmontar
    return () => {
      isMounted = false;
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