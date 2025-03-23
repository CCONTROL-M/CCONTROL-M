import React, { ReactNode } from 'react';
import { useLoading } from '../contexts/LoadingContext';

interface DataStateHandlerProps {
  loading: boolean;
  error?: string | null;
  dataLength?: number;
  onRetry?: () => void;
  emptyMessage?: string;
  children: ReactNode;
  useGlobalLoading?: boolean;
}

/**
 * Componente reutilizável para lidar com os estados de dados
 * 
 * @param loading - Indica se os dados estão carregando
 * @param error - Mensagem de erro, se houver
 * @param dataLength - Tamanho dos dados (para verificar se estão vazios)
 * @param onRetry - Função para tentar novamente em caso de erro
 * @param emptyMessage - Mensagem a ser exibida quando não há dados
 * @param useGlobalLoading - Define se deve usar o overlay global de carregamento
 * @param children - Conteúdo a ser renderizado quando não há erros e os dados estão disponíveis
 */
const DataStateHandler: React.FC<DataStateHandlerProps> = ({
  loading,
  error,
  dataLength,
  onRetry,
  emptyMessage = "Nenhum registro encontrado.",
  children,
  useGlobalLoading = false
}) => {
  const { setLoading } = useLoading();
  
  // Ativar o loading global se necessário
  React.useEffect(() => {
    if (useGlobalLoading) {
      setLoading(loading);
    }
    // Limpar o loading global quando o componente for desmontado
    return () => {
      if (useGlobalLoading) {
        setLoading(false);
      }
    };
  }, [loading, useGlobalLoading, setLoading]);

  // Exibir mensagem de carregamento se useGlobalLoading for false
  if (loading && !useGlobalLoading) {
    return <p className="placeholder-text">Carregando...</p>;
  }

  // Exibir mensagem de erro se houver
  if (error) {
    return (
      <div className="data-state-error">
        <p className="placeholder-text">{error}</p>
        {onRetry && (
          <button className="btn-primary" onClick={onRetry}>
            Tentar Novamente
          </button>
        )}
      </div>
    );
  }

  // Exibir mensagem de dados vazios se aplicável
  if (dataLength !== undefined && dataLength === 0 && !loading) {
    return <p className="placeholder-text">{emptyMessage}</p>;
  }

  // Renderizar o conteúdo normal
  return <>{children}</>;
};

export default DataStateHandler; 