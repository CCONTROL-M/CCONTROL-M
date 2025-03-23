import React, { useEffect, useState } from 'react';
import { Fornecedor } from "../types";
import { 
  listarFornecedores, 
  removerFornecedor, 
  cadastrarFornecedor, 
  atualizarFornecedor 
} from "../services/fornecedorService";
import { 
  listarFornecedoresMock,
  removerFornecedorMock, 
  cadastrarFornecedorMock, 
  atualizarFornecedorMock 
} from "../services/fornecedorServiceMock";
import { useMock, adicionarIndicadorMock, toggleMock } from '../utils/mock';
import { useToastUtils } from '../hooks/useToast';
import DataStateHandler from '../components/DataStateHandler';
import Table, { TableColumn } from '../components/Table';
import ConfirmDialog from '../components/ConfirmDialog';
import useConfirmDialog from '../hooks/useConfirmDialog';
import Modal from '../components/Modal';
import FornecedorForm from '../components/fornecedor/FornecedorForm';

/**
 * Página de gerenciamento de fornecedores
 * 
 * Funcionalidades:
 * - Listagem de fornecedores
 * - Cadastro de novos fornecedores
 * - Edição de fornecedores existentes
 * - Exclusão de fornecedores
 * - Alternância entre dados mock e reais
 */
export default function Fornecedores() {
  // Estados
  const [fornecedores, setFornecedores] = useState<Fornecedor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalAberto, setModalAberto] = useState(false);
  const [fornecedorEmEdicao, setFornecedorEmEdicao] = useState<Fornecedor | undefined>(undefined);
  
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
      header: "CNPJ",
      accessor: "cnpj"
    },
    {
      header: "Contato",
      accessor: "contato"
    },
    {
      header: "Avaliação",
      accessor: "avaliacao"
    },
    {
      header: "Ações",
      accessor: "id_fornecedor",
      render: (fornecedor: Fornecedor) => (
        <div className="table-actions">
          <button 
            className="btn-icon btn-edit"
            onClick={(e) => {
              e.stopPropagation();
              handleEditarClick(fornecedor);
            }}
            aria-label="Editar fornecedor"
          >
            ✏️
          </button>
          <button 
            className="btn-icon btn-delete"
            onClick={(e) => {
              e.stopPropagation();
              handleExcluirClick(fornecedor);
            }}
            aria-label="Excluir fornecedor"
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

  // Buscar dados dos fornecedores
  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = useMock() 
        ? await listarFornecedoresMock() 
        : await listarFornecedores();
      setFornecedores(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar fornecedores';
      setError(errorMessage);
      showErrorToast(errorMessage);
    } finally {
      setLoading(false);
    }
  };
  
  // Função para abrir o modal de novo fornecedor
  const handleNovoFornecedorClick = () => {
    setFornecedorEmEdicao(undefined);
    setModalAberto(true);
  };

  // Função para abrir o modal de edição
  const handleEditarClick = (fornecedor: Fornecedor) => {
    setFornecedorEmEdicao(fornecedor);
    setModalAberto(true);
  };
  
  // Função para fechar o modal
  const handleFecharModal = () => {
    setModalAberto(false);
    setFornecedorEmEdicao(undefined);
  };
  
  // Preparar a exclusão do fornecedor (abre o diálogo)
  const handleExcluirClick = (fornecedor: Fornecedor) => {
    confirm({
      title: "Excluir fornecedor",
      description: `Tem certeza que deseja excluir o fornecedor "${fornecedor.nome}"? Essa ação não poderá ser desfeita.`,
      confirmText: "Excluir",
      cancelText: "Cancelar",
      type: "danger",
      onConfirm: () => excluirFornecedor(fornecedor)
    });
  };
  
  // Lidar com salvar fornecedor (novo ou edição)
  const handleSalvarFornecedor = async (fornecedorData: Omit<Fornecedor, 'id_fornecedor' | 'created_at' | 'avaliacao'>) => {
    try {
      if (fornecedorEmEdicao) {
        // Atualizar fornecedor existente
        const fornecedorAtualizado = useMock()
          ? await atualizarFornecedorMock(fornecedorEmEdicao.id_fornecedor, fornecedorData)
          : await atualizarFornecedor(fornecedorEmEdicao.id_fornecedor, fornecedorData);

        setFornecedores(prevFornecedores => 
          prevFornecedores.map(fornecedor => 
            fornecedor.id_fornecedor === fornecedorEmEdicao.id_fornecedor ? 
              fornecedorAtualizado : fornecedor
          )
        );
        
        showSuccessToast('Fornecedor atualizado com sucesso!');
      } else {
        // Cadastrar novo fornecedor
        const fornecedorParaCadastro = {
          ...fornecedorData,
          avaliacao: "Novo",
          created_at: new Date().toISOString()
        };

        const novoFornecedor = useMock()
          ? await cadastrarFornecedorMock(fornecedorParaCadastro)
          : await cadastrarFornecedor(fornecedorParaCadastro);

        setFornecedores(prevFornecedores => [...prevFornecedores, novoFornecedor]);
        
        showSuccessToast('Fornecedor cadastrado com sucesso!');
      }
      
      setModalAberto(false);
      setFornecedorEmEdicao(undefined);
    } catch (err) {
      console.error('Erro ao salvar fornecedor:', err);
      const operacao = fornecedorEmEdicao ? 'atualizar' : 'cadastrar';
      const errorMessage = err instanceof Error ? err.message : `Não foi possível ${operacao} o fornecedor`;
      showErrorToast(`${errorMessage}. Tente novamente mais tarde.`);
    }
  };
  
  // Função para excluir o fornecedor
  const excluirFornecedor = async (fornecedor: Fornecedor) => {
    try {
      // Excluir o fornecedor
      useMock()
        ? await removerFornecedorMock(fornecedor.id_fornecedor)
        : await removerFornecedor(fornecedor.id_fornecedor);
      
      // Atualizar a lista de fornecedores (removendo o fornecedor excluído)
      setFornecedores(prevFornecedores => 
        prevFornecedores.filter(f => f.id_fornecedor !== fornecedor.id_fornecedor)
      );
      
      showSuccessToast('Fornecedor excluído com sucesso!');
    } catch (err) {
      console.error('Erro ao excluir fornecedor:', err);
      const errorMessage = err instanceof Error ? err.message : 'Não foi possível excluir o fornecedor';
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
    <div className="fornecedores-page">
      <div className="page-header">
        <h1 className="page-title">Fornecedores</h1>
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
            onClick={handleNovoFornecedorClick}
          >
            + Novo Fornecedor
          </button>
        </div>
      </div>
      
      <DataStateHandler
        loading={loading}
        error={error}
        dataLength={fornecedores.length}
        onRetry={fetchData}
        emptyMessage="Nenhum fornecedor encontrado."
      >
        <Table
          columns={colunas}
          data={fornecedores}
          emptyMessage="Nenhum fornecedor encontrado."
        />
      </DataStateHandler>
      
      {/* Modal de cadastro/edição de fornecedor */}
      <Modal
        isOpen={modalAberto}
        onClose={handleFecharModal}
        title={fornecedorEmEdicao ? 'Editar Fornecedor' : 'Novo Fornecedor'}
      >
        <FornecedorForm
          fornecedor={fornecedorEmEdicao}
          onSave={handleSalvarFornecedor}
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