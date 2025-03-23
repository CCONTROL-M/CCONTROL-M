import React, { useEffect, useState } from 'react';
import { Cliente } from "../types";
import { 
  listarClientes, 
  removerCliente, 
  cadastrarCliente, 
  atualizarCliente 
} from "../services/clienteService";
import { 
  listarClientesMock,
  removerClienteMock, 
  cadastrarClienteMock, 
  atualizarClienteMock 
} from "../services/clienteServiceMock";
import { useMock, adicionarIndicadorMock, toggleMock } from '../utils/mock';
import { useToastUtils } from '../hooks/useToast';
import DataStateHandler from '../components/DataStateHandler';
import Table, { TableColumn } from '../components/Table';
import ConfirmDialog from '../components/ConfirmDialog';
import useConfirmDialog from '../hooks/useConfirmDialog';
import Modal from '../components/Modal';
import ClienteForm from '../components/cliente/ClienteForm';

/**
 * Página de gerenciamento de clientes
 * 
 * Funcionalidades:
 * - Listagem de clientes
 * - Cadastro de novos clientes
 * - Edição de clientes existentes
 * - Exclusão de clientes
 * - Alternância entre dados mock e reais
 */
export default function Clientes() {
  // Estados
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalAberto, setModalAberto] = useState(false);
  const [clienteEmEdicao, setClienteEmEdicao] = useState<Cliente | undefined>(undefined);
  
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
      
      <DataStateHandler
        loading={loading}
        error={error}
        dataLength={clientes.length}
        onRetry={fetchData}
        emptyMessage="Nenhum cliente encontrado."
      >
        <Table
          columns={colunas}
          data={clientes}
          emptyMessage="Nenhum cliente encontrado."
        />
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