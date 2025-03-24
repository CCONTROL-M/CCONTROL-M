import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ContaBancaria } from "../types";
import { 
  listarContasBancarias, 
  removerContaBancaria, 
  cadastrarContaBancaria, 
  atualizarContaBancaria 
} from "../services/contaBancariaService";
import { 
  listarContasBancariasMock,
  removerContaBancariaMock, 
  cadastrarContaBancariaMock, 
  atualizarContaBancariaMock 
} from "../services/contaBancariaServiceMock";
import { useMock, adicionarIndicadorMock, toggleMock } from '../utils/mock';
import { useToastUtils } from '../hooks/useToast';
import DataStateHandler from '../components/DataStateHandler';
import Table, { TableColumn } from '../components/Table';
import ConfirmDialog from '../components/ConfirmDialog';
import useConfirmDialog from '../hooks/useConfirmDialog';
import Modal from '../components/Modal';
import ContaBancariaForm from '../components/contaBancaria/ContaBancariaForm';
import { useApiStatus } from '../contexts/ApiStatusContext';
import ApiDiagnostic from '../components/ApiDiagnostic';

/**
 * Página de gerenciamento de contas bancárias
 * 
 * Funcionalidades:
 * - Listagem de contas bancárias
 * - Cadastro de novas contas
 * - Edição de contas existentes
 * - Exclusão de contas
 * - Alternância entre dados mock e reais
 */
export default function ContasBancarias() {
  // Estados
  const [contasBancarias, setContasBancarias] = useState<ContaBancaria[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalAberto, setModalAberto] = useState(false);
  const [contaEmEdicao, setContaEmEdicao] = useState<ContaBancaria | undefined>(undefined);
  
  // Hooks
  const { showSuccessToast, showErrorToast } = useToastUtils();
  const { dialog, confirm, closeDialog } = useConfirmDialog();
  const { apiOnline } = useApiStatus();
  const navigate = useNavigate();

  // Definição das colunas da tabela
  const colunas: TableColumn[] = [
    {
      header: "Nome",
      accessor: "nome"
    },
    {
      header: "Banco",
      accessor: "banco"
    },
    {
      header: "Agência",
      accessor: "agencia"
    },
    {
      header: "Conta",
      accessor: "conta"
    },
    {
      header: "Tipo",
      accessor: "tipo",
      render: (conta: ContaBancaria) => (
        <span>
          {conta.tipo === "corrente" ? "Conta Corrente" : "Conta Poupança"}
        </span>
      )
    },
    {
      header: "Saldo Atual",
      accessor: "saldo_atual",
      render: (conta: ContaBancaria) => (
        <span className={conta.saldo_atual < 0 ? "text-red-600" : "text-green-600"}>
          {conta.saldo_atual.toLocaleString('pt-BR', { 
            style: 'currency', 
            currency: 'BRL' 
          })}
        </span>
      )
    },
    {
      header: "Status",
      accessor: "ativa",
      render: (conta: ContaBancaria) => (
        <span className={conta.ativa ? "text-green-600" : "text-red-600"}>
          {conta.ativa ? "Ativa" : "Inativa"}
        </span>
      )
    },
    {
      header: "Ações",
      accessor: "id_conta",
      render: (conta: ContaBancaria) => (
        <div className="table-actions">
          <button 
            className="btn-icon btn-edit"
            onClick={(e) => {
              e.stopPropagation();
              handleEditarClick(conta);
            }}
            aria-label="Editar conta"
          >
            ✏️
          </button>
          <button 
            className="btn-icon btn-delete"
            onClick={(e) => {
              e.stopPropagation();
              handleExcluirClick(conta);
            }}
            aria-label="Excluir conta"
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

  // Buscar dados das contas bancárias
  const fetchData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Se a API estiver offline e não estiver em modo mock, mostrar erro
      if (!apiOnline && !useMock()) {
        throw new Error('API indisponível. Ative o modo Mock para ver dados simulados.');
      }
      
      // Listar contas bancárias (passar id_empresa = 1 como valor padrão)
      const data = useMock() 
        ? await listarContasBancariasMock() 
        : await listarContasBancarias('1'); // Passando id_empresa
      
      setContasBancarias(data);
    } catch (err) {
      console.error('Erro ao carregar contas bancárias:', err);
      const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar contas bancárias';
      setError(errorMessage);
      showErrorToast(errorMessage);
      
      // Em caso de erro, tentar carregar dados mock
      if (!useMock()) {
        try {
          console.info('Tentando carregar dados mock como fallback');
          const mockData = await listarContasBancariasMock();
          setContasBancarias(mockData);
          setError('API indisponível. Exibindo dados simulados como fallback.');
        } catch (mockErr) {
          console.error('Erro ao carregar dados mock:', mockErr);
        }
      }
    } finally {
      setLoading(false);
    }
  };
  
  // Função para abrir o modal de nova conta
  const handleNovaContaClick = () => {
    setContaEmEdicao(undefined);
    setModalAberto(true);
  };

  // Função para abrir o modal de edição
  const handleEditarClick = (conta: ContaBancaria) => {
    setContaEmEdicao(conta);
    setModalAberto(true);
  };
  
  // Função para fechar o modal
  const handleFecharModal = () => {
    setModalAberto(false);
    setContaEmEdicao(undefined);
  };
  
  // Preparar a exclusão da conta (abre o diálogo)
  const handleExcluirClick = (conta: ContaBancaria) => {
    confirm({
      title: "Excluir conta bancária",
      description: `Tem certeza que deseja excluir a conta "${conta.nome} - ${conta.banco}"? Essa ação não poderá ser desfeita.`,
      confirmText: "Excluir",
      cancelText: "Cancelar",
      type: "danger",
      onConfirm: () => excluirContaBancaria(conta)
    });
  };
  
  // Lidar com salvar conta (nova ou edição)
  const handleSalvarConta = async (contaData: {
    nome: string;
    banco: string;
    agencia: string;
    conta: string;
    tipo: string;
    saldo_inicial: number;
    ativa: boolean;
    mostrar_dashboard: boolean;
  }) => {
    try {
      if (contaEmEdicao) {
        // Atualizar conta existente
        const contaAtualizada = useMock()
          ? await atualizarContaBancariaMock(contaEmEdicao.id_conta, contaData)
          : await atualizarContaBancaria(contaEmEdicao.id_conta, contaData);

        setContasBancarias(prevContas => 
          prevContas.map(conta => 
            conta.id_conta === contaEmEdicao.id_conta ? 
              contaAtualizada : conta
          )
        );
        
        showSuccessToast('Conta bancária atualizada com sucesso!');
      } else {
        // Cadastrar nova conta com ID da empresa
        const contaParaCadastro = {
          ...contaData,
          id_empresa: '1'
        };

        const novaConta = useMock()
          ? await cadastrarContaBancariaMock(contaParaCadastro)
          : await cadastrarContaBancaria(contaParaCadastro);

        setContasBancarias(prevContas => [...prevContas, novaConta]);
        
        showSuccessToast('Conta bancária cadastrada com sucesso!');
      }
      
      setModalAberto(false);
      setContaEmEdicao(undefined);
    } catch (err) {
      console.error('Erro ao salvar conta bancária:', err);
      const operacao = contaEmEdicao ? 'atualizar' : 'cadastrar';
      const errorMessage = err instanceof Error ? err.message : `Não foi possível ${operacao} a conta bancária`;
      showErrorToast(`${errorMessage}. Tente novamente mais tarde.`);
    }
  };
  
  // Função para excluir a conta bancária
  const excluirContaBancaria = async (conta: ContaBancaria) => {
    try {
      // Excluir a conta
      useMock()
        ? await removerContaBancariaMock(conta.id_conta)
        : await removerContaBancaria(conta.id_conta);
      
      // Atualizar a lista de contas (removendo a conta excluída)
      setContasBancarias(prevContas => 
        prevContas.filter(c => c.id_conta !== conta.id_conta)
      );
      
      showSuccessToast('Conta bancária excluída com sucesso!');
    } catch (err) {
      console.error('Erro ao excluir conta bancária:', err);
      const errorMessage = err instanceof Error ? err.message : 'Não foi possível excluir a conta bancária';
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

  // Função para navegar para a página de detalhes
  const handleRowClick = (conta: ContaBancaria) => {
    navigate(`/contas-bancarias/${conta.id_conta}`);
  };

  return (
    <div className="contas-bancarias-page">
      <div className="page-header">
        <h1 className="page-title">Contas Bancárias</h1>
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
            onClick={handleNovaContaClick}
          >
            + Nova Conta
          </button>
        </div>
      </div>
      
      <DataStateHandler
        loading={loading}
        error={error}
        dataLength={contasBancarias.length}
        onRetry={fetchData}
        emptyMessage="Nenhuma conta bancária encontrada."
      >
        <>
          {(!apiOnline && !useMock()) && (
            <div className="mb-6">
              <ApiDiagnostic />
            </div>
          )}
          
          <Table
            columns={colunas}
            data={contasBancarias}
            emptyMessage="Nenhuma conta bancária encontrada."
            onRowClick={handleRowClick}
          />
        </>
      </DataStateHandler>
      
      {/* Modal de cadastro/edição de conta bancária */}
      <Modal
        isOpen={modalAberto}
        onClose={handleFecharModal}
        title={contaEmEdicao ? 'Editar Conta Bancária' : 'Nova Conta Bancária'}
      >
        <ContaBancariaForm
          contaBancaria={contaEmEdicao}
          onSave={handleSalvarConta}
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