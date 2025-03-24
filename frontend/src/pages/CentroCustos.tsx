import React, { useEffect, useState } from 'react';
import { CentroCusto } from "../types";
import {
  listarCentrosCusto,
  cadastrarCentroCusto,
  atualizarCentroCusto,
  removerCentroCusto
} from "../services/centroCustoService";
import { useMock } from '../utils/mock';
import { useToastUtils } from '../hooks/useToast';
import useConfirmDialog from '../hooks/useConfirmDialog';
import useFormHandler from '../hooks/useFormHandler';
import ConfirmDialog from '../components/ConfirmDialog';
import Table, { TableColumn } from "../components/Table";
import DataStateHandler from "../components/DataStateHandler";
import Modal from "../components/Modal";
import FormField from "../components/FormField";

/**
 * Componente da página de gerenciamento de centros de custo
 */
export default function CentroCustos() {
  // Estados
  const [centrosCusto, setCentrosCusto] = useState<CentroCusto[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalAberto, setModalAberto] = useState(false);
  const [centroCustoEmEdicao, setCentroCustoEmEdicao] = useState<CentroCusto | null>(null);
  
  // Hooks
  const { showSuccessToast, showErrorToast } = useToastUtils();
  const { dialog, confirm, closeDialog } = useConfirmDialog();
  const { formData, handleInputChange, resetForm, formErrors, validate, setFormData } = 
    useFormHandler<{ nome: string }>({ nome: "" });

  // Definição das colunas da tabela
  const colunas: TableColumn[] = [
    {
      header: "Nome",
      accessor: "nome"
    },
    {
      header: "Ações",
      accessor: "id_centro",
      render: (centroCusto: CentroCusto) => (
        <div className="flex space-x-2">
          <button 
            className="btn-icon-small"
            onClick={() => handleEditarClick(centroCusto)}
            aria-label="Editar centro de custo"
          >
            ✏️
          </button>
          <button 
            className="btn-icon-small text-red-500"
            onClick={() => handleExcluirClick(centroCusto)}
            aria-label="Excluir centro de custo"
          >
            🗑️
          </button>
        </div>
      )
    }
  ];

  useEffect(() => {
    fetchCentrosCusto();
  }, []);

  /**
   * Busca a lista de centros de custo na API ou nos dados mock
   */
  const fetchCentrosCusto = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await listarCentrosCusto();
      setCentrosCusto(data);
    } catch (err) {
      console.error('Erro ao carregar centros de custo:', err);
      setError('Não foi possível carregar os centros de custo. Tente novamente mais tarde.');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Abre o modal para adicionar um novo centro de custo
   */
  const handleNovoCentroCusto = () => {
    setCentroCustoEmEdicao(null);
    resetForm();
    setModalAberto(true);
  };

  /**
   * Abre o modal para editar um centro de custo existente
   */
  const handleEditarClick = (centroCusto: CentroCusto) => {
    setCentroCustoEmEdicao(centroCusto);
    setFormData({ nome: centroCusto.nome });
    setModalAberto(true);
  };

  /**
   * Solicita confirmação para excluir um centro de custo
   */
  const handleExcluirClick = (centroCusto: CentroCusto) => {
    confirm({
      title: "Excluir Centro de Custo",
      description: `Tem certeza que deseja excluir o centro de custo "${centroCusto.nome}"?`,
      confirmText: "Excluir",
      cancelText: "Cancelar",
      type: "danger",
      onConfirm: () => excluirCentroCusto(centroCusto.id_centro)
    });
  };

  /**
   * Exclui um centro de custo da base de dados
   */
  const excluirCentroCusto = async (id: string) => {
    try {
      setLoading(true);
      
      await removerCentroCusto(id);
      
      setCentrosCusto(prevCentrosCusto => 
        prevCentrosCusto.filter(c => c.id_centro !== id)
      );
      
      showSuccessToast("Centro de custo excluído com sucesso!");
    } catch (err) {
      console.error('Erro ao excluir centro de custo:', err);
      showErrorToast("Não foi possível excluir o centro de custo. Tente novamente.");
    } finally {
      setLoading(false);
    }
  };

  /**
   * Salva o centro de custo (novo ou editado)
   */
  const handleSalvar = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validar formulário
    const isValid = validate({
      nome: { required: true, minLength: 3 }
    });
    
    if (!isValid) return;
    
    try {
      setLoading(true);
      
      if (centroCustoEmEdicao) {
        // Editando centro de custo existente
        const centroCustoAtualizado = {
          nome: formData.nome
        };
        
        await atualizarCentroCusto(centroCustoEmEdicao.id_centro, centroCustoAtualizado);
        
        // Atualiza a lista local
        setCentrosCusto(prevCentrosCusto => 
          prevCentrosCusto.map(c => 
            c.id_centro === centroCustoEmEdicao.id_centro 
              ? { ...c, ...centroCustoAtualizado } 
              : c
          )
        );
        
        showSuccessToast("Centro de custo atualizado com sucesso!");
      } else {
        // Cadastrando novo centro de custo
        const novoCentroCusto = {
          nome: formData.nome
        };
        
        const centroCustoCriado = await cadastrarCentroCusto(novoCentroCusto);
        
        // Adiciona à lista local
        setCentrosCusto(prevCentrosCusto => [...prevCentrosCusto, centroCustoCriado]);
        
        showSuccessToast("Centro de custo cadastrado com sucesso!");
      }
      
      // Fecha o modal após salvar
      setModalAberto(false);
      resetForm();
    } catch (err) {
      console.error('Erro ao salvar centro de custo:', err);
      showErrorToast(
        centroCustoEmEdicao 
          ? "Não foi possível atualizar o centro de custo" 
          : "Não foi possível cadastrar o centro de custo"
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
    setCentroCustoEmEdicao(null);
    resetForm();
  };

  return (
    <div className="centro-custos-page">
      <div className="page-header">
        <h1 className="page-title">Centros de Custo</h1>
        <div className="page-actions">
          <button 
            className="btn-primary"
            onClick={handleNovoCentroCusto}
          >
            Novo Centro de Custo
          </button>
        </div>
      </div>
      
      <DataStateHandler
        loading={loading}
        error={error}
        dataLength={centrosCusto.length}
        onRetry={fetchCentrosCusto}
        emptyMessage="Nenhum centro de custo encontrado."
      >
        <Table
          columns={colunas}
          data={centrosCusto}
          emptyMessage="Nenhum centro de custo encontrado."
        />
      </DataStateHandler>
      
      {/* Modal de cadastro/edição de centro de custo */}
      <Modal
        isOpen={modalAberto}
        onClose={handleFecharModal}
        title={centroCustoEmEdicao ? "Editar Centro de Custo" : "Novo Centro de Custo"}
      >
        <form onSubmit={handleSalvar} className="form-container py-0">
          <FormField
            label="Nome"
            name="nome"
            value={formData.nome}
            onChange={handleInputChange}
            error={formErrors.nome}
            placeholder="Digite o nome do centro de custo"
            required
          />
          
          <div className="form-actions">
            <button
              type="button"
              className="btn-secondary"
              onClick={handleFecharModal}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="btn-primary"
              disabled={loading}
            >
              {loading ? 'Salvando...' : 'Salvar'}
            </button>
          </div>
        </form>
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