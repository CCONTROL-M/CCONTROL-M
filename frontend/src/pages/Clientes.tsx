import React, { useEffect, useState } from 'react';
import { Cliente } from "../types";
import { 
  listarClientes, 
  removerCliente, 
  cadastrarCliente, 
  atualizarCliente,
  buscarCliente
} from "../services/clienteService";
import { 
  listarClientesMock,
  removerClienteMock, 
  cadastrarClienteMock, 
  atualizarClienteMock,
  buscarClienteMock
} from "../services/clienteServiceMock";
import { useMock, adicionarIndicadorMock, toggleMock } from '../utils/mock';
import { useToastUtils } from '../hooks/useToast';
import DataStateHandler from '../components/DataStateHandler';
import Table, { TableColumn } from '../components/Table';
import ConfirmDialog from '../components/ConfirmDialog';
import useConfirmDialog from '../hooks/useConfirmDialog';
import Modal from '../components/Modal';
import ClienteForm from '../components/cliente/ClienteForm';
import CadastroFiltro from '../components/CadastroFiltro';

/**
 * Página de gerenciamento de clientes
 * 
 * Funcionalidades:
 * - Listagem de clientes
 * - Cadastro de novos clientes
 * - Edição de clientes existentes
 * - Exclusão de clientes
 * - Alternância entre dados mock e reais
 * - Filtro por nome/código
 * - Paginação
 */
export default function Clientes() {
  // Estados
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [clientesFiltrados, setClientesFiltrados] = useState<Cliente[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalAberto, setModalAberto] = useState(false);
  const [clienteEmEdicao, setClienteEmEdicao] = useState<Cliente | undefined>(undefined);
  const [termoBusca, setTermoBusca] = useState<string>("");
  
  // Estados para paginação
  const [paginaAtual, setPaginaAtual] = useState<number>(1);
  const itensPorPagina = 10;
  const [totalPaginas, setTotalPaginas] = useState<number>(1);
  const [clientesPaginados, setClientesPaginados] = useState<Cliente[]>([]);
  
  // Hooks
  const { showSuccessToast, showErrorToast } = useToastUtils();
  const { dialog, confirm, closeDialog } = useConfirmDialog();

  // Definição das colunas da tabela
  const colunas: TableColumn[] = [
    {
      header: "Nome",
      accessor: "nome"
    },
    {
      header: "CPF/CNPJ",
      accessor: "cpf_cnpj"
    },
    {
      header: "Contato",
      accessor: "contato"
    },
    {
      header: "Ações",
      accessor: "id_cliente",
      render: (cliente: Cliente) => (
        <div className="table-actions">
          <button 
            className="btn-icon btn-edit"
            onClick={(e) => {
              e.stopPropagation();
              handleEditarClick(cliente);
            }}
            aria-label="Editar cliente"
          >
            ✏️
          </button>
          <button 
            className="btn-icon btn-delete"
            onClick={(e) => {
              e.stopPropagation();
              handleExcluirClick(cliente);
            }}
            aria-label="Excluir cliente"
          >
            🗑️
          </button>
        </div>
      )
    }
  ];

  // Efeito para carregar dados e configurar indicador de mock
  useEffect(() => {
    fetchData();
    adicionarIndicadorMock();
  }, []);
  
  // Efeito para filtrar os clientes quando o termo de busca mudar
  useEffect(() => {
    filtrarClientes();
  }, [termoBusca, clientes]);
  
  // Efeito para paginar os clientes filtrados
  useEffect(() => {
    paginarClientes();
  }, [clientesFiltrados, paginaAtual]);

  // Buscar dados dos clientes
  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = useMock() 
        ? await listarClientesMock() 
        : await listarClientes();
      setClientes(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar clientes';
      setError(errorMessage);
      showErrorToast(errorMessage);
    } finally {
      setLoading(false);
    }
  };
  
  // Filtrar clientes com base no termo de busca
  const filtrarClientes = () => {
    if (!termoBusca) {
      setClientesFiltrados(clientes);
    } else {
      const termo = termoBusca.toLowerCase();
      const filtrados = clientes.filter(cliente => 
        cliente.nome.toLowerCase().includes(termo) || 
        cliente.cpf_cnpj.toLowerCase().includes(termo) ||
        cliente.id_cliente.toLowerCase().includes(termo)
      );
      setClientesFiltrados(filtrados);
    }
    
    // Resetar para a primeira página quando filtrar
    setPaginaAtual(1);
  };
  
  // Buscar clientes com base no termo de busca
  const buscarClientes = (termo: string) => {
    setTermoBusca(termo);
  };
  
  // Limpar filtros
  const limparFiltros = () => {
    setTermoBusca("");
    setPaginaAtual(1);
  };
  
  // Paginar clientes filtrados
  const paginarClientes = () => {
    // Calcular total de páginas
    const total = Math.ceil(clientesFiltrados.length / itensPorPagina);
    setTotalPaginas(total);
    
    // Obter itens da página atual
    const inicio = (paginaAtual - 1) * itensPorPagina;
    const fim = inicio + itensPorPagina;
    const itensPaginados = clientesFiltrados.slice(inicio, fim);
    setClientesPaginados(itensPaginados);
  };
  
  // Função para mudar de página
  const mudarPagina = (pagina: number) => {
    setPaginaAtual(pagina);
  };
  
  // Função para abrir o modal de novo cliente
  const handleNovoClienteClick = () => {
    setClienteEmEdicao(undefined);
    setModalAberto(true);
  };

  // Função para abrir o modal de edição
  const handleEditarClick = (cliente: Cliente) => {
    setClienteEmEdicao(cliente);
    setModalAberto(true);
  };
  
  // Função para fechar o modal
  const handleFecharModal = () => {
    setModalAberto(false);
    setClienteEmEdicao(undefined);
  };
  
  // Preparar a exclusão do cliente (abre o diálogo)
  const handleExcluirClick = (cliente: Cliente) => {
    confirm({
      title: "Excluir cliente",
      description: `Tem certeza que deseja excluir o cliente "${cliente.nome}"? Essa ação não poderá ser desfeita.`,
      confirmText: "Excluir",
      cancelText: "Cancelar",
      type: "danger",
      onConfirm: () => excluirCliente(cliente)
    });
  };
  
  // Lidar com salvar cliente (novo ou edição)
  const handleSalvarCliente = async (clienteData: Omit<Cliente, 'id_cliente' | 'created_at'>) => {
    try {
      if (clienteEmEdicao) {
        // Atualizar cliente existente
        const clienteAtualizado = useMock()
          ? await atualizarClienteMock(clienteEmEdicao.id_cliente, clienteData)
          : await atualizarCliente(clienteEmEdicao.id_cliente, clienteData);

        setClientes(prevClientes => 
          prevClientes.map(cliente => 
            cliente.id_cliente === clienteEmEdicao.id_cliente ? 
              clienteAtualizado : cliente
          )
        );
        
        showSuccessToast('Cliente atualizado com sucesso!');
      } else {
        // Cadastrar novo cliente 
        const clienteParaCadastro = {
          ...clienteData,
          created_at: new Date().toISOString()
        };

        const novoCliente = useMock()
          ? await cadastrarClienteMock(clienteParaCadastro)
          : await cadastrarCliente(clienteParaCadastro);

        setClientes(prevClientes => [...prevClientes, novoCliente]);
        
        showSuccessToast('Cliente cadastrado com sucesso!');
      }
      
      setModalAberto(false);
      setClienteEmEdicao(undefined);
    } catch (err) {
      console.error('Erro ao salvar cliente:', err);
      const operacao = clienteEmEdicao ? 'atualizar' : 'cadastrar';
      const errorMessage = err instanceof Error ? err.message : `Não foi possível ${operacao} o cliente`;
      showErrorToast(`${errorMessage}. Tente novamente mais tarde.`);
    }
  };
  
  // Função para excluir o cliente
  const excluirCliente = async (cliente: Cliente) => {
    try {
      // Excluir o cliente
      useMock()
        ? await removerClienteMock(cliente.id_cliente)
        : await removerCliente(cliente.id_cliente);
      
      // Atualizar a lista de clientes (removendo o cliente excluído)
      setClientes(prevClientes => 
        prevClientes.filter(c => c.id_cliente !== cliente.id_cliente)
      );
      
      showSuccessToast('Cliente excluído com sucesso!');
    } catch (err) {
      console.error('Erro ao excluir cliente:', err);
      const errorMessage = err instanceof Error ? err.message : 'Não foi possível excluir o cliente';
      showErrorToast(`${errorMessage}. Tente novamente mais tarde.`);
    }
  };

  // Alternar entre modo real e mock
  const handleToggleMock = () => {
    toggleMock();
    // Recarrega os dados após alternar o modo
    fetchData();
    // Recria o indicador se necessário
    adicionarIndicadorMock();
  };

  return (
    <div className="clientes-page">
      <div className="page-header">
        <h1 className="page-title">Clientes</h1>
        <div className="page-actions">
          <button 
            className="btn-secondary"
            onClick={handleToggleMock}
            title={useMock() ? "Mudar para modo real" : "Mudar para modo mock"}
          >
            {useMock() ? "🔄 Modo Real" : "🔄 Modo Mock"}
          </button>
          <button 
            className="btn-primary"
            onClick={handleNovoClienteClick}
          >
            + Novo Cliente
          </button>
        </div>
      </div>
      
      {/* Adicionar filtro de busca */}
      <CadastroFiltro
        onBuscar={buscarClientes}
        onLimpar={limparFiltros}
        totalPaginas={totalPaginas}
        paginaAtual={paginaAtual}
        onMudarPagina={mudarPagina}
        placeholder="Buscar por nome, CPF/CNPJ ou código..."
        isLoading={loading}
      />
      
      <DataStateHandler
        loading={loading}
        error={error}
        dataLength={clientesFiltrados.length}
        onRetry={fetchData}
        emptyMessage="Nenhum cliente encontrado."
      >
        <Table
          columns={colunas}
          data={clientesPaginados}
          emptyMessage="Nenhum cliente encontrado."
        />
        
        {clientesFiltrados.length > 0 && clientesPaginados.length === 0 && (
          <p className="text-gray-600 text-center mt-4">
            Não há clientes nesta página. Tente uma página diferente.
          </p>
        )}
      </DataStateHandler>
      
      {/* Modal de cadastro/edição de cliente */}
      <Modal
        isOpen={modalAberto}
        onClose={handleFecharModal}
        title={clienteEmEdicao ? 'Editar Cliente' : 'Novo Cliente'}
      >
        <ClienteForm
          cliente={clienteEmEdicao}
          onSave={handleSalvarCliente}
          onCancel={handleFecharModal}
        />
      </Modal>
      
      {/* Diálogo de confirmação de exclusão */}
      <ConfirmDialog 
        isOpen={dialog.isOpen}
        onClose={closeDialog}
        onConfirm={dialog.onConfirm}
        title={dialog.title}
        description={dialog.description}
        confirmText={dialog.confirmText}
        cancelText={dialog.cancelText}
        type={dialog.type}
      />
    </div>
  );
} 