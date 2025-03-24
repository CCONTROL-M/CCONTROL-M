import { useEffect, useState } from "react";
import { 
  listarEmpresas, 
  EmpresaCompleta, 
  cadastrarEmpresa, 
  atualizarEmpresa, 
  removerEmpresa
} from "../services/empresaService";
import Table, { TableColumn } from "../components/Table";
import DataStateHandler from "../components/DataStateHandler";
import Modal from "../components/Modal";
import ConfirmDialog from "../components/ConfirmDialog";
import { useToastUtils } from "../hooks/useToast";
import useConfirmDialog from "../hooks/useConfirmDialog";
import EmpresaForm, { EmpresaFormData } from "../components/empresa/EmpresaForm";

export default function Empresas() {
  // Estados
  const [empresas, setEmpresas] = useState<EmpresaCompleta[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");
  const [modalAberto, setModalAberto] = useState<boolean>(false);
  const [empresaEmEdicao, setEmpresaEmEdicao] = useState<EmpresaCompleta | null>(null);
  
  // Hooks
  const { showSuccessToast, showErrorToast } = useToastUtils();
  const { dialog, confirm, closeDialog } = useConfirmDialog();

  // Definição das colunas da tabela
  const colunas: TableColumn[] = [
    {
      header: "Razão Social",
      accessor: "razao_social"
    },
    {
      header: "Nome Fantasia",
      accessor: "nome_fantasia",
      render: (item: EmpresaCompleta) => item.nome_fantasia || '-'
    },
    {
      header: "CNPJ",
      accessor: "cnpj"
    },
    {
      header: "Cidade/UF",
      accessor: "cidade",
      render: (item: EmpresaCompleta) => {
        return item.cidade && item.estado 
          ? `${item.cidade}/${item.estado}`
          : item.cidade || item.estado || '-';
      }
    },
    {
      header: "Status",
      accessor: "ativo",
      render: (item: EmpresaCompleta) => item.ativo ? "Ativa" : "Inativa"
    },
    {
      header: "Ações",
      accessor: "id_empresa",
      render: (empresa: EmpresaCompleta) => (
        <div className="flex space-x-2">
          <button 
            className="btn-icon-small"
            onClick={() => handleEditarClick(empresa)}
            aria-label="Editar empresa"
          >
            ✏️
          </button>
          <button 
            className="btn-icon-small text-red-500"
            onClick={() => handleExcluirClick(empresa)}
            aria-label="Excluir empresa"
          >
            🗑️
          </button>
        </div>
      )
    }
  ];

  useEffect(() => {
    fetchEmpresas();
  }, []);

  /**
   * Busca a lista de empresas
   */
  async function fetchEmpresas() {
    try {
      setLoading(true);
      const data = await listarEmpresas();
      setEmpresas(data);
      setError("");
    } catch (err) {
      console.error("Erro ao carregar empresas:", err);
      setError("Erro ao carregar empresas. Verifique a conexão com o servidor.");
    } finally {
      setLoading(false);
    }
  }

  /**
   * Abre o modal para adicionar uma nova empresa
   */
  const handleNovaEmpresa = () => {
    setEmpresaEmEdicao(null);
    setModalAberto(true);
  };

  /**
   * Abre o modal para editar uma empresa existente
   */
  const handleEditarClick = (empresa: EmpresaCompleta) => {
    setEmpresaEmEdicao(empresa);
    setModalAberto(true);
  };

  /**
   * Solicita confirmação para excluir uma empresa
   */
  const handleExcluirClick = (empresa: EmpresaCompleta) => {
    confirm({
      title: "Excluir Empresa",
      description: `Tem certeza que deseja excluir a empresa "${empresa.razao_social}"? Esta ação não pode ser desfeita.`,
      confirmText: "Excluir",
      cancelText: "Cancelar",
      type: "danger",
      onConfirm: () => excluirEmpresa(empresa.id_empresa)
    });
  };

  /**
   * Exclui uma empresa
   */
  const excluirEmpresa = async (id: string) => {
    try {
      setLoading(true);
      
      await removerEmpresa(id);
      
      setEmpresas(prevEmpresas => 
        prevEmpresas.filter(e => e.id_empresa !== id)
      );
      
      showSuccessToast("Empresa excluída com sucesso!");
    } catch (err) {
      console.error('Erro ao excluir empresa:', err);
      showErrorToast("Não foi possível excluir a empresa. Tente novamente.");
    } finally {
      setLoading(false);
    }
  };

  /**
   * Salva a empresa (nova ou editada)
   */
  const handleSalvar = async (formData: EmpresaFormData) => {    
    try {
      setLoading(true);
      
      const empresaData = {
        nome: formData.nome,
        razao_social: formData.razao_social,
        nome_fantasia: formData.nome_fantasia,
        cnpj: formData.cnpj,
        contato: formData.contato,
        cidade: formData.cidade,
        estado: formData.estado,
        ativo: formData.ativo,
        created_at: new Date().toISOString().split('T')[0] // Adicionar campo created_at
      };
      
      if (empresaEmEdicao) {
        // Editando empresa existente
        const empresaAtualizada = await atualizarEmpresa(empresaEmEdicao.id_empresa, empresaData);
        
        // Atualiza a lista local
        setEmpresas(prevEmpresas => 
          prevEmpresas.map(e => 
            e.id_empresa === empresaEmEdicao.id_empresa 
              ? empresaAtualizada
              : e
          )
        );
        
        showSuccessToast("Empresa atualizada com sucesso!");
      } else {
        // Cadastrando nova empresa
        const novaEmpresa = await cadastrarEmpresa(empresaData);
        
        // Adiciona à lista local
        setEmpresas(prevEmpresas => [...prevEmpresas, novaEmpresa]);
        
        showSuccessToast("Empresa cadastrada com sucesso!");
      }
      
      // Fecha o modal após salvar
      setModalAberto(false);
    } catch (err) {
      console.error('Erro ao salvar empresa:', err);
      showErrorToast(
        empresaEmEdicao 
          ? "Não foi possível atualizar a empresa" 
          : "Não foi possível cadastrar a empresa"
      );
    } finally {
      setLoading(false);
    }
  };

  /**
   * Fecha o modal de edição/cadastro
   */
  const handleFecharModal = () => {
    setModalAberto(false);
    setEmpresaEmEdicao(null);
  };

  return (
    <div className="empresas-page">
      <div className="page-header">
        <h1 className="page-title">Empresas</h1>
        <div className="page-actions">
          <button 
            className="btn-primary"
            onClick={handleNovaEmpresa}
          >
            Nova Empresa
          </button>
        </div>
      </div>
      
      <DataStateHandler
        loading={loading}
        error={error}
        dataLength={empresas.length}
        onRetry={fetchEmpresas}
        emptyMessage="Nenhuma empresa encontrada."
      >
        <Table
          columns={colunas}
          data={empresas}
          emptyMessage="Nenhuma empresa encontrada."
        />
      </DataStateHandler>
      
      {/* Modal de cadastro/edição de empresa */}
      <Modal
        isOpen={modalAberto}
        onClose={handleFecharModal}
        title={empresaEmEdicao ? "Editar Empresa" : "Nova Empresa"}
      >
        <EmpresaForm
          empresa={empresaEmEdicao}
          onSave={handleSalvar}
          onCancel={handleFecharModal}
          isLoading={loading}
        />
      </Modal>
      
      {/* Diálogo de confirmação de exclusão */}
      {dialog.isOpen && (
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
      )}
    </div>
  );
} 