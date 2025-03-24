import { useEffect, useState } from "react";
import { listarLogs, filtrarLogs } from "../services/logService";
import { Log } from "../types";
import Table, { TableColumn } from "../components/Table";
import DataStateHandler from "../components/DataStateHandler";
import { useToastUtils } from "../hooks/useToast";
import FormField from "../components/FormField";
import Modal from "../components/Modal";
import LogDetalhesModal from "../components/logs/LogDetalhesModal";

// Interface para filtros
interface FiltrosLog {
  dataInicio?: string;
  dataFim?: string;
  usuario?: string;
  acao?: string;
  entidade?: string;
}

// Configurações de paginação
interface PaginacaoConfig {
  paginaAtual: number;
  itensPorPagina: number;
  totalItens: number;
}

export default function AuditoriaLogs() {
  // Estados principais
  const [logs, setLogs] = useState<Log[]>([]);
  const [logsFiltrados, setLogsFiltrados] = useState<Log[]>([]);
  const [logsExibidos, setLogsExibidos] = useState<Log[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // Estados para filtros
  const [filtrosAbertos, setFiltrosAbertos] = useState(false);
  const [filtros, setFiltros] = useState<FiltrosLog>({});
  
  // Estado para modal de detalhes
  const [modalDetalhesAberto, setModalDetalhesAberto] = useState(false);
  const [logSelecionado, setLogSelecionado] = useState<Log | null>(null);
  
  // Estado para paginação
  const [paginacao, setPaginacao] = useState<PaginacaoConfig>({
    paginaAtual: 1,
    itensPorPagina: 10,
    totalItens: 0
  });
  
  // Hooks para notificações toast
  const { showSuccessToast, showErrorToast, showInfoToast } = useToastUtils();

  // Definição das colunas da tabela
  const columns: TableColumn[] = [
    {
      header: "ID",
      accessor: "id_log",
    },
    {
      header: "Data/Hora",
      accessor: "data",
      render: (item: Log) => {
        const data = new Date(item.data);
        return data.toLocaleString("pt-BR");
      }
    },
    {
      header: "Usuário",
      accessor: "usuario",
    },
    {
      header: "Ação",
      accessor: "acao",
      render: (item: Log) => {
        const corAcao = getTipoAcaoCor(item.acao);
        return (
          <span className={`badge ${corAcao}`}>
            {item.acao}
          </span>
        );
      }
    },
    {
      header: "Detalhes",
      accessor: "detalhes",
      render: (item: Log) => {
        // Exibe apenas parte dos detalhes para não ocupar muito espaço
        const detalhesResumidos = item.detalhes.length > 50 
          ? `${item.detalhes.substring(0, 50)}...` 
          : item.detalhes;
        
        return (
          <span className="hover:underline cursor-pointer" onClick={(e) => {
            e.stopPropagation();
            abrirModalDetalhes(item);
          }}>
            {detalhesResumidos}
          </span>
        );
      }
    },
  ];

  // Funções auxiliares
  const getTipoAcaoCor = (acao: string): string => {
    const tiposAcao: Record<string, string> = {
      "Cadastro": "badge-success",
      "Atualização": "badge-warning",
      "Exclusão": "badge-danger",
      "Login": "badge-info",
      "Logout": "badge-secondary",
      "Configuração": "badge-primary",
      "Venda": "badge-success",
      "Transferência": "badge-warning"
    };
    
    return tiposAcao[acao] || "badge-secondary";
  };
  
  const abrirModalDetalhes = (log: Log) => {
    setLogSelecionado(log);
    setModalDetalhesAberto(true);
  };

  // Efeito para carregar logs quando componente montar
  useEffect(() => {
    buscarLogs();
  }, []);
  
  // Efeito para paginar logs quando a lista filtrada ou configuração de paginação mudar
  useEffect(() => {
    paginarLogs();
  }, [logsFiltrados, paginacao.paginaAtual, paginacao.itensPorPagina]);

  // Função para buscar logs do serviço
  async function buscarLogs() {
    setLoading(true);
    setError(null);
    
    try {
      const response = await listarLogs();
      setLogs(response);
      setLogsFiltrados(response);
      setPaginacao(prev => ({
        ...prev,
        totalItens: response.length
      }));
      
      showSuccessToast("Logs carregados com sucesso");
    } catch (err) {
      console.error("Erro ao carregar logs:", err);
      setError("Erro ao carregar logs. Tente novamente.");
      showErrorToast("Falha ao carregar logs");
    } finally {
      setLoading(false);
    }
  }
  
  // Função para buscar logs com filtros aplicados
  async function buscarLogsFiltrados() {
    setLoading(true);
    setError(null);
    
    try {
      // Remover filtros vazios
      const filtrosLimpos: any = {};
      if (filtros.dataInicio) filtrosLimpos.dataInicio = filtros.dataInicio;
      if (filtros.dataFim) filtrosLimpos.dataFim = filtros.dataFim;
      if (filtros.usuario) filtrosLimpos.usuario = filtros.usuario;
      if (filtros.acao) filtrosLimpos.acao = filtros.acao;
      
      const response = await filtrarLogs(filtrosLimpos);
      
      // Se houver filtro por entidade (que não existe na API), filtrar no client-side
      let resultado = [...response];
      if (filtros.entidade && filtros.entidade.trim() !== '') {
        resultado = resultado.filter(log => 
          log.detalhes.toLowerCase().includes(filtros.entidade!.toLowerCase())
        );
      }
      
      setLogsFiltrados(resultado);
      setPaginacao(prev => ({
        ...prev,
        paginaAtual: 1,
        totalItens: resultado.length
      }));
      
      showInfoToast(`${resultado.length} logs encontrados`);
    } catch (err) {
      console.error("Erro ao filtrar logs:", err);
      setError("Erro ao filtrar logs. Tente novamente mais tarde.");
      showErrorToast("Erro ao aplicar filtros");
    } finally {
      setLoading(false);
    }
  }
  
  // Função para paginar logs
  function paginarLogs() {
    const inicio = (paginacao.paginaAtual - 1) * paginacao.itensPorPagina;
    const fim = inicio + paginacao.itensPorPagina;
    
    const logsPaginados = logsFiltrados.slice(inicio, fim);
    setLogsExibidos(logsPaginados);
  }
  
  // Manipulador para alterar os filtros
  const handleFiltroChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFiltros(prev => ({ ...prev, [name]: value || undefined }));
  };
  
  // Aplicar filtros
  const aplicarFiltros = (e: React.FormEvent) => {
    e.preventDefault();
    buscarLogsFiltrados();
    setFiltrosAbertos(false);
  };
  
  // Limpar filtros
  const limparFiltros = () => {
    setFiltros({});
    setLogsFiltrados(logs);
    setPaginacao(prev => ({
      ...prev,
      paginaAtual: 1,
      totalItens: logs.length
    }));
    setFiltrosAbertos(false);
  };
  
  // Navegação de páginas
  const irParaPagina = (numeroPagina: number) => {
    if (numeroPagina < 1 || numeroPagina > calcularTotalPaginas()) return;
    
    setPaginacao(prev => ({
      ...prev,
      paginaAtual: numeroPagina
    }));
  };
  
  const calcularTotalPaginas = () => {
    return Math.ceil(paginacao.totalItens / paginacao.itensPorPagina);
  };
  
  // Extrai entidades únicas dos logs para o filtro
  const extrairAcoesUnicas = (): string[] => {
    const acoes = new Set<string>();
    logs.forEach(log => acoes.add(log.acao));
    return Array.from(acoes).sort();
  };
  
  // Extrai usuários únicos dos logs para o filtro
  const extrairUsuariosUnicos = (): string[] => {
    const usuarios = new Set<string>();
    logs.forEach(log => usuarios.add(log.usuario));
    return Array.from(usuarios).sort();
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Auditoria de Logs</h1>
        <div className="page-actions">
          <button
            className="btn-secondary"
            onClick={() => setFiltrosAbertos(!filtrosAbertos)}
          >
            {filtrosAbertos ? 'Ocultar Filtros' : 'Filtrar Logs'}
          </button>
        </div>
      </div>
      
      {/* Seção de filtros */}
      {filtrosAbertos && (
        <div className="filtro-container">
          <h2 className="filtro-titulo">Filtrar Logs</h2>
          <form onSubmit={aplicarFiltros} className="filtro-form">
            <div className="filtro-grid">
              <div className="filtro-col">
                <FormField
                  label="Data Inicial"
                  name="dataInicio"
                  type="date"
                  value={filtros.dataInicio || ''}
                  onChange={handleFiltroChange}
                />
              </div>
              <div className="filtro-col">
                <FormField
                  label="Data Final"
                  name="dataFim"
                  type="date"
                  value={filtros.dataFim || ''}
                  onChange={handleFiltroChange}
                />
              </div>
              <div className="filtro-col">
                <div className="form-group">
                  <label htmlFor="usuario">Usuário:</label>
                  <select
                    id="usuario"
                    name="usuario"
                    value={filtros.usuario || ''}
                    onChange={handleFiltroChange}
                  >
                    <option value="">Todos</option>
                    {extrairUsuariosUnicos().map(usuario => (
                      <option key={usuario} value={usuario}>{usuario}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="filtro-col">
                <div className="form-group">
                  <label htmlFor="acao">Ação:</label>
                  <select
                    id="acao"
                    name="acao"
                    value={filtros.acao || ''}
                    onChange={handleFiltroChange}
                  >
                    <option value="">Todas</option>
                    {extrairAcoesUnicas().map(acao => (
                      <option key={acao} value={acao}>{acao}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
            <div className="filtro-buttons">
              <button type="submit" className="btn-primary">
                Aplicar Filtros
              </button>
              <button type="button" className="btn-secondary" onClick={limparFiltros}>
                Limpar Filtros
              </button>
            </div>
          </form>
        </div>
      )}
      
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Logs do Sistema</h2>
          <div className="card-tools">
            <span className="text-sm">
              Total de registros: <strong>{paginacao.totalItens}</strong>
            </span>
          </div>
        </div>
        <div className="card-body">
          <DataStateHandler
            loading={loading}
            error={error}
            dataLength={logsExibidos.length}
            emptyMessage="Nenhum log encontrado."
            onRetry={buscarLogs}
          >
            <Table 
              data={logsExibidos} 
              columns={columns}
              emptyMessage="Nenhum log encontrado"
            />
          </DataStateHandler>
          
          {/* Paginação */}
          {logsExibidos.length > 0 && (
            <div className="pagination-container">
              <div className="pagination-controls">
                <button
                  className="pagination-button"
                  onClick={() => irParaPagina(1)}
                  disabled={paginacao.paginaAtual === 1}
                >
                  &laquo;
                </button>
                <button
                  className="pagination-button"
                  onClick={() => irParaPagina(paginacao.paginaAtual - 1)}
                  disabled={paginacao.paginaAtual === 1}
                >
                  &lsaquo;
                </button>
                
                <span className="pagination-info">
                  Página {paginacao.paginaAtual} de {calcularTotalPaginas()}
                </span>
                
                <button
                  className="pagination-button"
                  onClick={() => irParaPagina(paginacao.paginaAtual + 1)}
                  disabled={paginacao.paginaAtual >= calcularTotalPaginas()}
                >
                  &rsaquo;
                </button>
                <button
                  className="pagination-button"
                  onClick={() => irParaPagina(calcularTotalPaginas())}
                  disabled={paginacao.paginaAtual >= calcularTotalPaginas()}
                >
                  &raquo;
                </button>
              </div>
              
              <div className="pagination-select">
                <label>Itens por página:</label>
                <select
                  value={paginacao.itensPorPagina}
                  onChange={(e) => setPaginacao(prev => ({
                    ...prev,
                    itensPorPagina: Number(e.target.value),
                    paginaAtual: 1
                  }))}
                >
                  <option value={5}>5</option>
                  <option value={10}>10</option>
                  <option value={20}>20</option>
                  <option value={50}>50</option>
                </select>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Modal para visualizar detalhes do log */}
      <LogDetalhesModal
        isOpen={modalDetalhesAberto}
        onClose={() => setModalDetalhesAberto(false)}
        log={logSelecionado}
      />
    </div>
  );
} 