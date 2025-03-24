import React, { useEffect, useState } from 'react';
import { 
  listarLancamentos, 
  cadastrarLancamento, 
  atualizarLancamento, 
  removerLancamento,
  filtrarLancamentos
} from '../services/lancamentoService';
import { listarCategorias } from '../services/categoriaService';
import { listarContasBancarias } from '../services/contaBancariaService';
import { Lancamento, Categoria, ContaBancaria } from '../types';
import { formatarData, formatarMoeda } from '../utils/formatters';
import Table, { TableColumn } from '../components/Table';
import DataStateHandler from '../components/DataStateHandler';
import Modal from '../components/Modal';
import ConfirmDialog from '../components/ConfirmDialog';
import LancamentoForm, { LancamentoFormData } from '../components/lancamento/LancamentoForm';
import LancamentoFiltro, { LancamentoFiltroForm } from '../components/lancamento/LancamentoFiltro';
import { useToastUtils } from '../hooks/useToast';
import useConfirmDialog from '../hooks/useConfirmDialog';

// Estendendo a interface para adicionar campo descricao e tipo para exibição
interface LancamentoExibicao extends Lancamento {
  descricao: string;
  tipo: string;
  nomeCategoriaFormatado: string;
  nomeContaBancaria: string;
}

/**
 * Componente da página de lançamentos financeiros
 */
export default function Lancamentos() {
  // Estados
  const [lancamentos, setLancamentos] = useState<LancamentoExibicao[]>([]);
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [contasBancarias, setContasBancarias] = useState<ContaBancaria[]>([]);
  const [filtrosAtivos, setFiltrosAtivos] = useState<LancamentoFiltroForm | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [modalAberto, setModalAberto] = useState<boolean>(false);
  const [lancamentoEmEdicao, setLancamentoEmEdicao] = useState<Lancamento | null>(null);
  
  // Hooks
  const { showSuccessToast, showErrorToast } = useToastUtils();
  const { dialog, confirm, closeDialog } = useConfirmDialog();

  // Definição das colunas da tabela
  const colunas: TableColumn[] = [
    {
      header: "Data",
      accessor: "data",
      render: (item: LancamentoExibicao) => formatarData(item.data)
    },
    {
      header: "Categoria/Descrição",
      accessor: "descricao",
      render: (item: LancamentoExibicao) => (
        <div>
          <div className="font-medium">{item.nomeCategoriaFormatado}</div>
          <div className="text-sm text-gray-600">{item.descricao}</div>
        </div>
      )
    },
    {
      header: "Conta",
      accessor: "nomeContaBancaria",
      render: (item: LancamentoExibicao) => item.nomeContaBancaria || '-'
    },
    {
      header: "Tipo/Valor",
      accessor: "valor",
      render: (item: LancamentoExibicao) => (
        <div className={`flex flex-col ${item.tipo === 'Receita' ? 'text-green-700' : 'text-red-700'}`}>
          <span className="font-medium">{item.tipo}</span>
          <span>{formatarMoeda(item.valor)}</span>
        </div>
      )
    },
    {
      header: "Status",
      accessor: "status",
      render: (item: LancamentoExibicao) => {
        let statusClass = '';
        
        switch (item.status) {
          case 'Pago':
          case 'Recebido':
            statusClass = 'bg-green-100 text-green-800';
            break;
          case 'Pendente':
            statusClass = 'bg-yellow-100 text-yellow-800';
            break;
          case 'Agendado':
            statusClass = 'bg-blue-100 text-blue-800';
            break;
          case 'Cancelado':
            statusClass = 'bg-red-100 text-red-800';
            break;
          default:
            statusClass = 'bg-gray-100 text-gray-800';
        }
        
        return (
          <span className={`px-2 py-1 rounded-full text-xs ${statusClass}`}>
            {item.status}
          </span>
        );
      }
    },
    {
      header: "Ações",
      accessor: "id_lancamento",
      render: (item: LancamentoExibicao) => (
        <div className="flex space-x-2">
          <button 
            className="btn-icon-small"
            onClick={() => handleEditarClick(item)}
            aria-label="Editar lançamento"
          >
            ✏️
          </button>
          <button 
            className="btn-icon-small text-red-500"
            onClick={() => handleExcluirClick(item)}
            aria-label="Excluir lançamento"
          >
            🗑️
          </button>
        </div>
      )
    }
  ];

  // Efeito para carregar os dados iniciais
  useEffect(() => {
    Promise.all([
      fetchCategorias(),
      fetchContasBancarias(),
      fetchLancamentos()
    ]);
  }, []);

  /**
   * Busca a lista de categorias
   */
  const fetchCategorias = async () => {
    try {
      const data = await listarCategorias();
      setCategorias(data);
    } catch (err) {
      console.error('Erro ao carregar categorias:', err);
      showErrorToast('Erro ao carregar categorias. Tente novamente.');
    }
  };

  /**
   * Busca a lista de contas bancárias
   */
  const fetchContasBancarias = async () => {
    try {
      const data = await listarContasBancarias();
      setContasBancarias(data);
    } catch (err) {
      console.error('Erro ao carregar contas bancárias:', err);
      showErrorToast('Erro ao carregar contas bancárias. Tente novamente.');
    }
  };

  /**
   * Busca a lista de lançamentos
   */
  const fetchLancamentos = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await listarLancamentos();
      processarLancamentos(response);
    } catch (err) {
      console.error("Erro ao carregar lançamentos:", err);
      setError("Erro ao carregar os lançamentos. Tente novamente mais tarde.");
    } finally {
      setLoading(false);
    }
  };

  /**
   * Processar os lançamentos para adicionar informações de exibição
   */
  const processarLancamentos = (dados: Lancamento[]) => {
    const lancamentosProcessados = dados.map(lancamento => {
      const categoria = categorias.find(c => c.id_categoria === lancamento.id_categoria);
      const contaBancaria = contasBancarias.find(c => c.id_conta === lancamento.id_conta_bancaria);
      
      return {
        ...lancamento,
        descricao: lancamento.observacao || `Lançamento #${lancamento.id_lancamento}`,
        tipo: categoria ? (categoria.tipo === 'receita' ? 'Receita' : 'Despesa') : 'Outro',
        nomeCategoriaFormatado: categoria ? categoria.nome : 'Sem categoria',
        nomeContaBancaria: contaBancaria ? `${contaBancaria.nome} - ${contaBancaria.banco}` : ''
      } as LancamentoExibicao;
    });
    
    setLancamentos(lancamentosProcessados);
  };

  /**
   * Filtrar lançamentos
   */
  const handleFiltrar = async (filtros: LancamentoFiltroForm) => {
    setLoading(true);
    setError(null);
    
    try {
      // Criar o objeto de filtros para a API
      const filtrosParaAPI = {
        dataInicio: filtros.dataInicio,
        dataFim: filtros.dataFim,
        tipo: filtros.tipo || undefined,
        status: filtros.status || undefined
      };
      
      const response = await filtrarLancamentos(filtrosParaAPI);
      
      // Se houver filtro de conta bancária, filtrar no front (pois a API não suporta esse filtro)
      let lancamentosFiltrados = response;
      if (filtros.id_conta_bancaria) {
        lancamentosFiltrados = response.filter(
          lancamento => lancamento.id_conta_bancaria === filtros.id_conta_bancaria
        );
      }
      
      processarLancamentos(lancamentosFiltrados);
      
      // Guardar os filtros ativos
      setFiltrosAtivos(filtros);
    } catch (err) {
      console.error("Erro ao filtrar lançamentos:", err);
      setError("Erro ao filtrar os lançamentos. Tente novamente mais tarde.");
      showErrorToast("Erro ao aplicar filtros. Tente novamente.");
    } finally {
      setLoading(false);
    }
  };

  /**
   * Abre o modal para adicionar um novo lançamento
   */
  const handleNovoLancamento = () => {
    setLancamentoEmEdicao(null);
    setModalAberto(true);
  };

  /**
   * Abre o modal para editar um lançamento existente
   */
  const handleEditarClick = (lancamento: Lancamento) => {
    setLancamentoEmEdicao(lancamento);
    setModalAberto(true);
  };

  /**
   * Solicita confirmação para excluir um lançamento
   */
  const handleExcluirClick = (lancamento: Lancamento) => {
    confirm({
      title: "Excluir Lançamento",
      description: `Tem certeza que deseja excluir este lançamento? Esta ação não pode ser desfeita.`,
      confirmText: "Excluir",
      cancelText: "Cancelar",
      type: "danger",
      onConfirm: () => excluirLancamento(lancamento.id_lancamento)
    });
  };

  /**
   * Exclui um lançamento
   */
  const excluirLancamento = async (id: string) => {
    try {
      setLoading(true);
      
      await removerLancamento(id);
      
      setLancamentos(prevLancamentos => 
        prevLancamentos.filter(l => l.id_lancamento !== id)
      );
      
      showSuccessToast("Lançamento excluído com sucesso!");
    } catch (err) {
      console.error('Erro ao excluir lançamento:', err);
      showErrorToast("Não foi possível excluir o lançamento. Tente novamente.");
    } finally {
      setLoading(false);
    }
  };

  /**
   * Salva o lançamento (novo ou editado)
   */
  const handleSalvar = async (formData: LancamentoFormData) => {
    try {
      setLoading(true);
      
      if (lancamentoEmEdicao) {
        // Editando lançamento existente
        const lancamentoAtualizado = await atualizarLancamento(
          lancamentoEmEdicao.id_lancamento, 
          formData
        );
        
        // Atualiza a lista local
        setLancamentos(prevLancamentos => {
          const novaLista = prevLancamentos.map(l => 
            l.id_lancamento === lancamentoEmEdicao.id_lancamento 
              ? { 
                  ...l, 
                  ...lancamentoAtualizado,
                  descricao: formData.observacao || `Lançamento #${lancamentoEmEdicao.id_lancamento}`,
                  tipo: getCategoriaById(formData.id_categoria)?.tipo === 'receita' ? 'Receita' : 'Despesa',
                  nomeCategoriaFormatado: getCategoriaById(formData.id_categoria)?.nome || 'Sem categoria',
                  nomeContaBancaria: getContaBancariaById(formData.id_conta_bancaria)?.nome || ''
                } 
              : l
          );
          return novaLista;
        });
        
        showSuccessToast("Lançamento atualizado com sucesso!");
      } else {
        // Cadastrando novo lançamento
        const novoLancamento = await cadastrarLancamento(formData);
        
        // Adiciona à lista local
        const lancamentoFormatado: LancamentoExibicao = {
          ...novoLancamento,
          descricao: formData.observacao || `Lançamento #${novoLancamento.id_lancamento}`,
          tipo: getCategoriaById(formData.id_categoria)?.tipo === 'receita' ? 'Receita' : 'Despesa',
          nomeCategoriaFormatado: getCategoriaById(formData.id_categoria)?.nome || 'Sem categoria',
          nomeContaBancaria: getContaBancariaById(formData.id_conta_bancaria)?.nome || ''
        };
        
        setLancamentos(prevLancamentos => [...prevLancamentos, lancamentoFormatado]);
        
        showSuccessToast("Lançamento cadastrado com sucesso!");
      }
      
      // Fecha o modal após salvar
      setModalAberto(false);
    } catch (err) {
      console.error('Erro ao salvar lançamento:', err);
      showErrorToast(
        lancamentoEmEdicao 
          ? "Não foi possível atualizar o lançamento" 
          : "Não foi possível cadastrar o lançamento"
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
    setLancamentoEmEdicao(null);
  };

  /**
   * Auxiliar para obter uma categoria pelo ID
   */
  const getCategoriaById = (id?: string) => {
    if (!id) return null;
    return categorias.find(c => c.id_categoria === id) || null;
  };

  /**
   * Auxiliar para obter uma conta bancária pelo ID
   */
  const getContaBancariaById = (id?: string) => {
    if (!id) return null;
    return contasBancarias.find(c => c.id_conta === id) || null;
  };

  return (
    <div className="lancamentos-page">
      <div className="page-header">
        <h1 className="page-title">Lançamentos Financeiros</h1>
        <div className="page-actions">
          <button 
            className="btn-primary"
            onClick={handleNovoLancamento}
          >
            Novo Lançamento
          </button>
        </div>
      </div>
      
      {/* Componente de filtro */}
      <LancamentoFiltro 
        contasBancarias={contasBancarias}
        onFiltrar={handleFiltrar}
      />
      
      <DataStateHandler
        loading={loading}
        error={error}
        dataLength={lancamentos.length}
        onRetry={fetchLancamentos}
        emptyMessage="Nenhum lançamento encontrado"
      >
        <Table 
          columns={colunas}
          data={lancamentos}
          emptyMessage="Nenhum lançamento encontrado"
        />
      </DataStateHandler>
      
      {/* Modal de cadastro/edição de lançamento */}
      <Modal
        isOpen={modalAberto}
        onClose={handleFecharModal}
        title={lancamentoEmEdicao ? "Editar Lançamento" : "Novo Lançamento"}
      >
        <LancamentoForm
          lancamento={lancamentoEmEdicao}
          categorias={categorias}
          contasBancarias={contasBancarias}
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