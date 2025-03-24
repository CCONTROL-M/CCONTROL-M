import { useEffect, useState } from "react";
import { listarParcelas, atualizarParcela, marcarComoPaga, filtrarParcelas } from "../services/parcelaService";
import { Parcela } from "../types";
import { formatarData, formatarMoeda } from "../utils/formatters";
import Table, { TableColumn } from "../components/Table";
import DataStateHandler from "../components/DataStateHandler";
import Modal from "../components/Modal";
import FormField from "../components/FormField";
import { useToastUtils } from "../hooks/useToast";

// Estendendo a interface para adicionar campos de exibição
interface ParcelaExibicao extends Parcela {
  numero: number;
  tipo: 'receber' | 'pagar';
  dias_atraso?: number;
}

// Interface para filtros
interface FiltrosParcela {
  dataInicio?: string;
  dataFim?: string;
  status?: string;
  tipo?: string;
}

export default function Parcelas() {
  // Estados principais
  const [parcelas, setParcelas] = useState<ParcelaExibicao[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // Estados para filtros
  const [filtrosAbertos, setFiltrosAbertos] = useState(false);
  const [filtros, setFiltros] = useState<FiltrosParcela>({});
  
  // Estados para modal de alteração de status
  const [modalStatusAberto, setModalStatusAberto] = useState(false);
  const [parcelaSelecionada, setParcelaSelecionada] = useState<ParcelaExibicao | null>(null);
  const [dataPagamento, setDataPagamento] = useState(new Date().toISOString().split('T')[0]);
  const [alterandoStatus, setAlterandoStatus] = useState(false);
  
  // Hooks para notificações toast
  const { showSuccessToast, showErrorToast, showInfoToast } = useToastUtils();

  // Definição das colunas da tabela
  const columns: TableColumn[] = [
    {
      header: "Venda",
      accessor: "id_venda",
      render: (item: ParcelaExibicao) => item.id_venda.length > 8 ? `${item.id_venda.slice(0, 8)}...` : item.id_venda,
    },
    {
      header: "Nº Parcela",
      accessor: "numero",
    },
    {
      header: "Tipo",
      accessor: "tipo",
      render: (item: ParcelaExibicao) => (
        <span className={`badge ${item.tipo === 'receber' ? 'badge-success' : 'badge-danger'}`}>
          {item.tipo === 'receber' ? 'A Receber' : 'A Pagar'}
        </span>
      ),
    },
    {
      header: "Valor",
      accessor: "valor",
      render: (item: ParcelaExibicao) => formatarMoeda(item.valor),
    },
    {
      header: "Vencimento",
      accessor: "data_vencimento",
      render: (item: ParcelaExibicao) => formatarData(item.data_vencimento),
    },
    {
      header: "Status",
      accessor: "status",
      render: (item: ParcelaExibicao) => (
        <span className={`badge ${item.status === 'Paga' ? 'badge-success' : (
          new Date(item.data_vencimento) < new Date() && item.status !== 'Paga' 
            ? 'badge-danger' : 'badge-warning'
        )}`}>
          {item.status === 'Paga' ? 'Paga' : (
            new Date(item.data_vencimento) < new Date() ? 'Atrasada' : 'Pendente'
          )}
        </span>
      ),
    },
    {
      header: "Atraso",
      accessor: "dias_atraso",
      render: (item: ParcelaExibicao) => {
        if (item.status === 'Paga') return '-';
        
        const hoje = new Date();
        const vencimento = new Date(item.data_vencimento);
        
        if (vencimento > hoje) return 'Em dia';
        
        // Calcular dias de atraso
        const diffTempo = Math.abs(hoje.getTime() - vencimento.getTime());
        const diasAtraso = Math.ceil(diffTempo / (1000 * 60 * 60 * 24));
        
        return `${diasAtraso} dias`;
      },
    },
    {
      header: "Ações",
      accessor: "acoes",
      render: (item: ParcelaExibicao) => (
        <div className="flex space-x-2">
          {item.status !== 'Paga' && (
            <button 
              className="btn-small btn-success"
              onClick={() => handleAbrirModalStatus(item)}
            >
              <i className="fas fa-check-circle mr-1"></i> Pagar
            </button>
          )}
        </div>
      ),
    },
  ];

  // Carregar parcelas ao montar componente
  useEffect(() => {
    buscarParcelas();
  }, []);

  // Função para buscar todas as parcelas
  async function buscarParcelas() {
    setLoading(true);
    setError(null);
    try {
      const response = await listarParcelas();
      
      // Processar as parcelas
      const parcelasProcessadas = processarParcelas(response);
      
      setParcelas(parcelasProcessadas);
    } catch (err) {
      console.error("Erro ao carregar parcelas:", err);
      setError("Erro ao carregar as parcelas. Tente novamente mais tarde.");
      showErrorToast("Erro ao carregar parcelas");
    } finally {
      setLoading(false);
    }
  }
  
  // Função para processar parcelas (adicionar numeração, calcular atrasos)
  function processarParcelas(parcelasOriginais: Parcela[]): ParcelaExibicao[] {
    // Agrupar parcelas por venda
    const vendasMap: Record<string, ParcelaExibicao[]> = {};
    
    // Primeiro passo: converter e agrupar
    parcelasOriginais.forEach(parcela => {
      if (!vendasMap[parcela.id_venda]) {
        vendasMap[parcela.id_venda] = [];
      }
      
      // Usar algum critério para definir tipo (a receber ou a pagar)
      // Aqui estamos usando um exemplo simplificado baseado no ID da venda
      // Na versão real, isso seria determinado pelo tipo de transação ou por um campo específico
      const tipo = parcela.id_venda.includes('venda') ? 'receber' : 'pagar';
      
      vendasMap[parcela.id_venda].push({
        ...parcela,
        numero: 0, // Valor temporário
        tipo
      });
    });
    
    // Segundo passo: processar cada grupo de venda
    const parcelasProcessadas: ParcelaExibicao[] = [];
    
    Object.values(vendasMap).forEach(vendaParcelas => {
      // Ordenar parcelas por data de vencimento
      vendaParcelas.sort((a, b) => 
        new Date(a.data_vencimento).getTime() - new Date(b.data_vencimento).getTime()
      );
      
      // Atribuir número sequencial
      vendaParcelas.forEach((parcela, index) => {
        parcela.numero = index + 1;
        
        // Calcular dias de atraso se for parcela não paga e vencida
        if (parcela.status !== 'Paga') {
          const hoje = new Date();
          const vencimento = new Date(parcela.data_vencimento);
          
          if (vencimento < hoje) {
            const diffTempo = Math.abs(hoje.getTime() - vencimento.getTime());
            parcela.dias_atraso = Math.ceil(diffTempo / (1000 * 60 * 60 * 24));
          }
        }
        
        parcelasProcessadas.push(parcela);
      });
    });
    
    return parcelasProcessadas;
  }
  
  // Função para buscar parcelas com filtros
  async function buscarParcelasFiltradas() {
    setLoading(true);
    setError(null);
    
    try {
      // Remover filtros vazios
      const filtrosLimpos: FiltrosParcela = {};
      if (filtros.dataInicio) filtrosLimpos.dataInicio = filtros.dataInicio;
      if (filtros.dataFim) filtrosLimpos.dataFim = filtros.dataFim;
      if (filtros.status) filtrosLimpos.status = filtros.status;
      
      const response = await filtrarParcelas(filtrosLimpos);
      
      // Filtrar pelo tipo aqui no front-end já que o backend não suporta esse filtro
      let parcelasFiltradas = processarParcelas(response);
      
      if (filtros.tipo && filtros.tipo !== 'todos') {
        parcelasFiltradas = parcelasFiltradas.filter(p => p.tipo === filtros.tipo);
      }
      
      setParcelas(parcelasFiltradas);
      showInfoToast(`${parcelasFiltradas.length} parcela(s) encontrada(s)`);
    } catch (err) {
      console.error("Erro ao filtrar parcelas:", err);
      setError("Erro ao filtrar parcelas. Tente novamente mais tarde.");
      showErrorToast("Erro ao filtrar parcelas");
    } finally {
      setLoading(false);
    }
  }
  
  // Manipulador para alterar os filtros
  const handleFiltroChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFiltros(prev => ({ ...prev, [name]: value || undefined }));
  };
  
  // Aplicar filtros
  const aplicarFiltros = (e: React.FormEvent) => {
    e.preventDefault();
    buscarParcelasFiltradas();
    setFiltrosAbertos(false);
  };
  
  // Limpar filtros
  const limparFiltros = () => {
    setFiltros({});
    buscarParcelas();
    setFiltrosAbertos(false);
  };
  
  // Abrir modal para alterar status da parcela
  const handleAbrirModalStatus = (parcela: ParcelaExibicao) => {
    setParcelaSelecionada(parcela);
    setDataPagamento(new Date().toISOString().split('T')[0]);
    setModalStatusAberto(true);
  };
  
  // Marcar parcela como paga
  const handleMarcarComoPaga = async () => {
    if (!parcelaSelecionada) return;
    
    setAlterandoStatus(true);
    
    try {
      await marcarComoPaga(parcelaSelecionada.id_parcela, dataPagamento);
      
      // Atualizar a lista de parcelas
      setParcelas(prev => 
        prev.map(p => 
          p.id_parcela === parcelaSelecionada.id_parcela 
            ? { ...p, status: 'Paga' } 
            : p
        )
      );
      
      // Fechar modal e mostrar mensagem de sucesso
      setModalStatusAberto(false);
      showSuccessToast(`Parcela ${parcelaSelecionada.numero} marcada como paga!`);
    } catch (err) {
      console.error("Erro ao marcar parcela como paga:", err);
      showErrorToast("Erro ao atualizar status da parcela");
    } finally {
      setAlterandoStatus(false);
    }
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Parcelas a Receber/Pagar</h1>
        <div className="page-actions">
          <button
            className="btn-secondary mr-2"
            onClick={() => setFiltrosAbertos(!filtrosAbertos)}
          >
            <i className="fas fa-filter"></i> Filtros
          </button>
          <button
            className="btn-primary"
            onClick={buscarParcelas}
            disabled={loading}
          >
            <i className="fas fa-sync"></i> Atualizar
          </button>
        </div>
      </div>
      
      {/* Painel de Filtros */}
      {filtrosAbertos && (
        <div className="card mb-4">
          <div className="card-header">
            <h2 className="card-title">Filtros</h2>
          </div>
          <div className="card-body">
            <form onSubmit={aplicarFiltros}>
              <div className="form-grid">
                <FormField
                  label="Data Início"
                  name="dataInicio"
                  type="date"
                  value={filtros.dataInicio || ''}
                  onChange={handleFiltroChange}
                />
                
                <FormField
                  label="Data Fim"
                  name="dataFim"
                  type="date"
                  value={filtros.dataFim || ''}
                  onChange={handleFiltroChange}
                />
                
                <div className="form-group">
                  <label htmlFor="tipo">Tipo</label>
                  <select
                    id="tipo"
                    name="tipo"
                    value={filtros.tipo || 'todos'}
                    onChange={handleFiltroChange}
                  >
                    <option value="todos">Todos</option>
                    <option value="receber">A Receber</option>
                    <option value="pagar">A Pagar</option>
                  </select>
                </div>
                
                <div className="form-group">
                  <label htmlFor="status">Status</label>
                  <select
                    id="status"
                    name="status"
                    value={filtros.status || ''}
                    onChange={handleFiltroChange}
                  >
                    <option value="">Todos</option>
                    <option value="Pendente">Pendentes</option>
                    <option value="Paga">Pagas</option>
                  </select>
                </div>
              </div>
              
              <div className="form-actions">
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={limparFiltros}
                >
                  Limpar
                </button>
                <button
                  type="submit"
                  className="btn-primary"
                >
                  Aplicar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      
      {/* Listagem de Parcelas */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Lista de Parcelas</h2>
          <div className="card-tools">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <span className="badge badge-success">A Receber</span>
                <span className="text-xs">{parcelas.filter(p => p.tipo === 'receber').length}</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="badge badge-danger">A Pagar</span>
                <span className="text-xs">{parcelas.filter(p => p.tipo === 'pagar').length}</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="badge badge-warning">Pendentes</span>
                <span className="text-xs">{parcelas.filter(p => p.status !== 'Paga').length}</span>
              </div>
            </div>
          </div>
        </div>
        <div className="card-body">
          <DataStateHandler
            loading={loading}
            error={error}
            dataLength={parcelas.length}
            emptyMessage="Nenhuma parcela encontrada."
            onRetry={buscarParcelas}
          >
            <Table 
              data={parcelas} 
              columns={columns}
              emptyMessage="Nenhuma parcela encontrada"
            />
          </DataStateHandler>
        </div>
      </div>
      
      {/* Modal para marcar parcela como paga */}
      <Modal
        isOpen={modalStatusAberto}
        onClose={() => setModalStatusAberto(false)}
        title="Marcar Parcela como Paga"
        size="small"
      >
        {parcelaSelecionada && (
          <div>
            <div className="mb-4">
              <p><strong>Venda:</strong> {parcelaSelecionada.id_venda}</p>
              <p><strong>Parcela:</strong> {parcelaSelecionada.numero}</p>
              <p><strong>Valor:</strong> {formatarMoeda(parcelaSelecionada.valor)}</p>
              <p><strong>Vencimento:</strong> {formatarData(parcelaSelecionada.data_vencimento)}</p>
            </div>
            
            <FormField
              label="Data de Pagamento"
              name="dataPagamento"
              type="date"
              value={dataPagamento}
              onChange={(e) => setDataPagamento(e.target.value)}
              required
            />
            
            <div className="form-actions">
              <button
                type="button"
                className="btn-secondary"
                onClick={() => setModalStatusAberto(false)}
                disabled={alterandoStatus}
              >
                Cancelar
              </button>
              <button
                type="button"
                className="btn-success"
                onClick={handleMarcarComoPaga}
                disabled={alterandoStatus}
              >
                {alterandoStatus ? 'Salvando...' : 'Confirmar Pagamento'}
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
} 