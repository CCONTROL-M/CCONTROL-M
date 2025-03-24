import React, { useState, useEffect } from 'react';
import { useToastUtils } from '../hooks/useToast';
import useConfirmDialog from '../hooks/useConfirmDialog';
import { Inadimplente } from '../types';
import DataStateHandler from '../components/DataStateHandler';
import Table, { TableColumn } from '../components/Table';
import InadimplenciaFiltro from '../components/inadimplencia/InadimplenciaFiltro';
import AcaoInadimplenciaModal from '../components/inadimplencia/AcaoInadimplenciaModal';
import { buscarInadimplencia } from '../services/relatorioService';
import { obterRelatorioInadimplencia } from '../services/relatoriosService';
import { marcarComoPaga, registrarAcaoInadimplencia } from '../services/parcelaService';

/**
 * Interface para o formulário de filtro
 */
interface InadimplenciaFiltroForm {
  dataInicio: string;
  dataFim: string;
  id_cliente?: string;
}

/**
 * Interface para dados da ação de inadimplência
 */
interface DadosAcaoInadimplencia {
  observacao: string;
  dataNovoVencimento?: string;
  valorNovo?: number;
  dataContato: string;
  meioComunicacao: string;
  responsavel: string;
}

/**
 * Página de Inadimplência - Exibe parcelas em atraso e permite ações de cobrança/renegociação
 */
export default function Inadimplencia() {
  // Estados
  const [inadimplentes, setInadimplentes] = useState<Inadimplente[]>([]);
  const [inadimplentesFiltrados, setInadimplentesFiltrados] = useState<Inadimplente[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [parcelaSelecionada, setParcelaSelecionada] = useState<Inadimplente | null>(null);
  const [salvandoAcao, setSalvandoAcao] = useState(false);
  
  // Estado para filtros
  const [filtrosAtivos, setFiltrosAtivos] = useState<InadimplenciaFiltroForm>({
    dataInicio: new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0],
    dataFim: new Date().toISOString().split('T')[0]
  });
  
  // Hooks
  const { showSuccessToast, showErrorToast } = useToastUtils();
  const { confirm } = useConfirmDialog();
  
  // Carregar dados ao montar o componente
  useEffect(() => {
    buscarDadosInadimplencia();
  }, []);
  
  // Colunas da tabela
  const columns: TableColumn[] = [
    {
      header: "Cliente",
      accessor: "cliente",
    },
    {
      header: "Valor Devido",
      accessor: "valor",
      render: (item: Inadimplente) => (
        <span className="font-medium text-red-600">
          {item.valor.toLocaleString('pt-BR', {
            style: 'currency',
            currency: 'BRL'
          })}
        </span>
      )
    },
    {
      header: "Vencimento",
      accessor: "vencimento",
      render: (item: Inadimplente) => (
        <span>
          {new Date(item.vencimento).toLocaleDateString('pt-BR')}
        </span>
      )
    },
    {
      header: "Dias em Atraso",
      accessor: "dias_em_atraso",
      render: (item: Inadimplente) => (
        <span className="font-medium text-red-600">
          {item.dias_em_atraso} dias
        </span>
      )
    },
    {
      header: "Ações",
      accessor: "id_parcela",
      render: (item: Inadimplente) => (
        <div className="flex space-x-2">
          <button
            onClick={() => handleAbrirModal(item)}
            className="btn-primary px-3 py-1 text-sm rounded-md"
          >
            Gerenciar
          </button>
          <button
            onClick={() => handleMarcarComoPaga(item)}
            className="btn-success px-3 py-1 text-sm rounded-md"
          >
            Pagar
          </button>
        </div>
      )
    }
  ];
  
  // Função para buscar dados de inadimplência
  const buscarDadosInadimplencia = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await obterRelatorioInadimplencia();
      setInadimplentes(Array.isArray(data) ? data : []);
      setInadimplentesFiltrados(Array.isArray(data) ? data : []);
      showSuccessToast('Dados de inadimplência carregados com sucesso');
    } catch (err) {
      console.error('Erro ao buscar dados de inadimplência:', err);
      setError('Não foi possível carregar os dados de inadimplência. Tente novamente.');
      showErrorToast('Erro ao carregar dados de inadimplência');
      // Inicializar com arrays vazios em caso de erro
      setInadimplentes([]);
      setInadimplentesFiltrados([]);
    } finally {
      setLoading(false);
    }
  };
  
  // Função para filtrar inadimplentes
  const handleFiltrar = (filtros: InadimplenciaFiltroForm) => {
    setFiltrosAtivos(filtros);
    
    if (!inadimplentes || !Array.isArray(inadimplentes) || inadimplentes.length === 0) {
      setInadimplentesFiltrados([]);
      return;
    }
    
    const dataInicio = new Date(filtros.dataInicio);
    const dataFim = new Date(filtros.dataFim);
    dataFim.setHours(23, 59, 59, 999); // Ajustar para final do dia
    
    const resultadoFiltrado = inadimplentes.filter(inadimplente => {
      if (!inadimplente || !inadimplente.vencimento) return false;
      
      const dataVencimento = new Date(inadimplente.vencimento);
      
      // Verificar intervalo de datas
      const dentroDoPeriodo = dataVencimento >= dataInicio && dataVencimento <= dataFim;
      
      // Verificar cliente se filtro de cliente estiver presente
      const clienteCorreto = !filtros.id_cliente || 
        (inadimplente.cliente && inadimplente.cliente.includes(filtros.id_cliente));
      
      return dentroDoPeriodo && clienteCorreto;
    });
    
    setInadimplentesFiltrados(resultadoFiltrado);
    showSuccessToast(`Filtro aplicado: ${resultadoFiltrado.length} resultados encontrados`);
  };
  
  // Função para abrir o modal de ação com a parcela selecionada
  const handleAbrirModal = (parcela: Inadimplente) => {
    if (!parcela) return;
    setParcelaSelecionada(parcela);
  };
  
  // Função para fechar o modal
  const handleFecharModal = () => {
    setParcelaSelecionada(null);
  };
  
  // Função para salvar a ação (cobrança ou renegociação)
  const handleSalvarAcao = async (dados: DadosAcaoInadimplencia, tipoAcao: 'cobranca' | 'renegociacao') => {
    if (!parcelaSelecionada) return;
    
    // Confirmar operação com usuário
    const mensagemConfirmacao = tipoAcao === 'cobranca'
      ? 'Deseja registrar esta cobrança para a parcela em atraso?'
      : 'Deseja renegociar esta parcela com os novos termos?';
    
    try {
      await confirm({
        title: tipoAcao === 'cobranca' ? 'Confirmar Cobrança' : 'Confirmar Renegociação',
        description: mensagemConfirmacao,
        confirmText: 'Confirmar',
        cancelText: 'Cancelar',
        onConfirm: () => {}
      });
      
      // Se chegarmos aqui, o usuário confirmou
      setSalvandoAcao(true);
      
      try {
        // Chamar o serviço para registrar a ação
        await registrarAcaoInadimplencia({
          id_parcela: parcelaSelecionada.id_parcela,
          tipo_acao: tipoAcao,
          observacao: dados.observacao,
          dataNovoVencimento: dados.dataNovoVencimento,
          valorNovo: dados.valorNovo,
          dataContato: dados.dataContato,
          meioComunicacao: dados.meioComunicacao,
          responsavel: dados.responsavel
        });
        
        // Recarregar dados após salvar
        await buscarDadosInadimplencia();
        
        // Fechar modal e mostrar mensagem de sucesso
        handleFecharModal();
        
        const mensagemSucesso = tipoAcao === 'cobranca'
          ? 'Cobrança registrada com sucesso'
          : 'Parcela renegociada com sucesso';
        
        showSuccessToast(mensagemSucesso);
      } catch (err) {
        console.error(`Erro ao ${tipoAcao === 'cobranca' ? 'registrar cobrança' : 'renegociar parcela'}:`, err);
        
        const mensagemErro = tipoAcao === 'cobranca'
          ? 'Erro ao registrar cobrança'
          : 'Erro ao renegociar parcela';
        
        showErrorToast(mensagemErro);
      } finally {
        setSalvandoAcao(false);
      }
    } catch (err) {
      // O usuário cancelou a operação
      console.log('Operação cancelada pelo usuário');
    }
  };
  
  // Função para marcar uma parcela como paga
  const handleMarcarComoPaga = async (parcela: Inadimplente) => {
    try {
      await confirm({
        title: 'Confirmar Pagamento',
        description: `Deseja marcar a parcela do cliente ${parcela.cliente} como paga?`,
        confirmText: 'Confirmar',
        cancelText: 'Cancelar',
        onConfirm: () => {}
      });
      
      // Se chegarmos aqui, o usuário confirmou
      setSalvandoAcao(true);
      
      try {
        const dataPagamento = new Date().toISOString().split('T')[0];
        await marcarComoPaga(parcela.id_parcela, dataPagamento);
        
        // Recarregar dados após salvar
        await buscarDadosInadimplencia();
        showSuccessToast('Parcela marcada como paga com sucesso');
      } catch (err) {
        console.error('Erro ao marcar parcela como paga:', err);
        showErrorToast('Erro ao marcar parcela como paga');
      } finally {
        setSalvandoAcao(false);
      }
    } catch (err) {
      // O usuário cancelou a operação
      console.log('Operação cancelada pelo usuário');
    }
  };
  
  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Gerenciamento de Inadimplência</h1>
      </div>
      
      {/* Componente de filtro */}
      <InadimplenciaFiltro onFiltrar={handleFiltrar} />
      
      {/* Tabela de inadimplentes */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Parcelas em Atraso</h2>
          <div className="card-tools">
            <button
              onClick={buscarDadosInadimplencia}
              className="btn-secondary px-3 py-1 text-sm rounded-md"
              disabled={loading}
            >
              Atualizar
            </button>
          </div>
        </div>
        <div className="card-body">
          <DataStateHandler
            loading={loading}
            error={error}
            dataLength={inadimplentesFiltrados.length}
            emptyMessage="Nenhuma parcela inadimplente encontrada."
            onRetry={buscarDadosInadimplencia}
          >
            <Table
              data={inadimplentesFiltrados}
              columns={columns}
              emptyMessage="Nenhuma parcela inadimplente encontrada."
            />
          </DataStateHandler>
        </div>
        <div className="card-footer">
          <div className="text-sm text-gray-500">
            Total de parcelas em atraso: <span className="font-semibold">{inadimplentesFiltrados.length}</span>
          </div>
        </div>
      </div>
      
      {/* Modal de ação para parcela selecionada */}
      <AcaoInadimplenciaModal
        parcela={parcelaSelecionada}
        onClose={handleFecharModal}
        onSalvar={handleSalvarAcao}
        isLoading={salvandoAcao}
      />
    </div>
  );
} 