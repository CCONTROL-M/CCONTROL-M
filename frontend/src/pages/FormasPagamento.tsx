import React, { useEffect, useState } from 'react';
import { FormaPagamento } from '../types';
import { 
  listarFormasPagamento,
  cadastrarFormaPagamento,
  atualizarFormaPagamento,
  removerFormaPagamento
} from '../services/formaPagamentoService';
import { useToastUtils } from '../hooks/useToast';
import useConfirmDialog from '../hooks/useConfirmDialog';
import Table, { TableColumn } from '../components/Table';
import DataStateHandler from '../components/DataStateHandler';
import Modal from '../components/Modal';
import ConfirmDialog from '../components/ConfirmDialog';
import FormaPagamentoForm, { FormaPagamentoFormData } from '../components/formaPagamento/FormaPagamentoForm';

/**
 * Componente para gerenciamento de formas de pagamento
 */
export default function FormasPagamento() {
  // Estados
  const [formasPagamento, setFormasPagamento] = useState<FormaPagamento[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalAberto, setModalAberto] = useState(false);
  const [formaPagamentoEmEdicao, setFormaPagamentoEmEdicao] = useState<FormaPagamento | null>(null);
  
  // Hooks
  const { showSuccessToast, showErrorToast } = useToastUtils();
  const { dialog, confirm, closeDialog } = useConfirmDialog();

  // Definição das colunas da tabela
  const colunas: TableColumn[] = [
    {
      header: "Tipo",
      accessor: "tipo"
    },
    {
      header: "Taxas",
      accessor: "taxas"
    },
    {
      header: "Prazo",
      accessor: "prazo"
    },
    {
      header: "Ações",
      accessor: "id_forma",
      render: (formaPagamento: FormaPagamento) => (
        <div className="flex space-x-2">
          <button 
            className="btn-icon-small"
            onClick={() => handleEditarClick(formaPagamento)}
            aria-label="Editar forma de pagamento"
          >
            ✏️
          </button>
          <button 
            className="btn-icon-small text-red-500"
            onClick={() => handleExcluirClick(formaPagamento)}
            aria-label="Excluir forma de pagamento"
          >
            🗑️
          </button>
        </div>
      )
    }
  ];

  useEffect(() => {
    fetchFormasPagamento();
  }, []);

  /**
   * Busca a lista de formas de pagamento
   */
  const fetchFormasPagamento = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await listarFormasPagamento();
      setFormasPagamento(data);
    } catch (err) {
      console.error('Erro ao carregar formas de pagamento:', err);
      setError('Não foi possível carregar as formas de pagamento. Tente novamente mais tarde.');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Abre o modal para adicionar uma nova forma de pagamento
   */
  const handleNovaFormaPagamento = () => {
    setFormaPagamentoEmEdicao(null);
    setModalAberto(true);
  };

  /**
   * Abre o modal para editar uma forma de pagamento existente
   */
  const handleEditarClick = (formaPagamento: FormaPagamento) => {
    setFormaPagamentoEmEdicao(formaPagamento);
    setModalAberto(true);
  };

  /**
   * Solicita confirmação para excluir uma forma de pagamento
   */
  const handleExcluirClick = (formaPagamento: FormaPagamento) => {
    confirm({
      title: "Excluir Forma de Pagamento",
      description: `Tem certeza que deseja excluir a forma de pagamento "${formaPagamento.tipo}"?`,
      confirmText: "Excluir",
      cancelText: "Cancelar",
      type: "danger",
      onConfirm: () => excluirFormaPagamento(formaPagamento.id_forma)
    });
  };

  /**
   * Exclui uma forma de pagamento
   */
  const excluirFormaPagamento = async (id: string) => {
    try {
      setLoading(true);
      
      await removerFormaPagamento(id);
      
      setFormasPagamento(prevFormasPagamento => 
        prevFormasPagamento.filter(f => f.id_forma !== id)
      );
      
      showSuccessToast("Forma de pagamento excluída com sucesso!");
    } catch (err) {
      console.error('Erro ao excluir forma de pagamento:', err);
      showErrorToast("Não foi possível excluir a forma de pagamento. Tente novamente.");
    } finally {
      setLoading(false);
    }
  };

  /**
   * Salva a forma de pagamento (nova ou editada)
   */
  const handleSalvar = async (formData: FormaPagamentoFormData) => {
    try {
      setLoading(true);
      
      if (formaPagamentoEmEdicao) {
        // Editando forma de pagamento existente
        const formaPagamentoAtualizada = {
          tipo: formData.tipo,
          taxas: formData.taxas,
          prazo: formData.prazo
        };
        
        await atualizarFormaPagamento(formaPagamentoEmEdicao.id_forma, formaPagamentoAtualizada);
        
        // Atualiza a lista local
        setFormasPagamento(prevFormasPagamento => 
          prevFormasPagamento.map(f => 
            f.id_forma === formaPagamentoEmEdicao.id_forma 
              ? { ...f, ...formaPagamentoAtualizada } 
              : f
          )
        );
        
        showSuccessToast("Forma de pagamento atualizada com sucesso!");
      } else {
        // Cadastrando nova forma de pagamento
        const novaFormaPagamento = {
          tipo: formData.tipo,
          taxas: formData.taxas,
          prazo: formData.prazo
        };
        
        const formaPagamentoCriada = await cadastrarFormaPagamento(novaFormaPagamento);
        
        // Adiciona à lista local
        setFormasPagamento(prevFormasPagamento => [...prevFormasPagamento, formaPagamentoCriada]);
        
        showSuccessToast("Forma de pagamento cadastrada com sucesso!");
      }
      
      // Fecha o modal após salvar
      setModalAberto(false);
    } catch (err) {
      console.error('Erro ao salvar forma de pagamento:', err);
      showErrorToast(
        formaPagamentoEmEdicao 
          ? "Não foi possível atualizar a forma de pagamento" 
          : "Não foi possível cadastrar a forma de pagamento"
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
    setFormaPagamentoEmEdicao(null);
  };

  return (
    <div className="formas-pagamento-page">
      <div className="page-header">
        <h1 className="page-title">Formas de Pagamento</h1>
        <div className="page-actions">
          <button 
            className="btn-primary"
            onClick={handleNovaFormaPagamento}
          >
            Nova Forma de Pagamento
          </button>
        </div>
      </div>
      
      <DataStateHandler
        loading={loading}
        error={error}
        dataLength={formasPagamento.length}
        onRetry={fetchFormasPagamento}
        emptyMessage="Nenhuma forma de pagamento encontrada."
      >
        <Table
          columns={colunas}
          data={formasPagamento}
          emptyMessage="Nenhuma forma de pagamento encontrada."
        />
      </DataStateHandler>
      
      {/* Modal de cadastro/edição de forma de pagamento */}
      <Modal
        isOpen={modalAberto}
        onClose={handleFecharModal}
        title={formaPagamentoEmEdicao ? "Editar Forma de Pagamento" : "Nova Forma de Pagamento"}
      >
        <FormaPagamentoForm
          formaPagamento={formaPagamentoEmEdicao}
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