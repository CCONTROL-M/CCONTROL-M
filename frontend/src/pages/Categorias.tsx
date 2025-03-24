import React, { useEffect, useState } from 'react';
import { Categoria } from "../types";
import { 
  listarCategorias, 
  cadastrarCategoria,
  atualizarCategoria,
  removerCategoria 
} from "../services/categoriaService";
import { 
  listarCategoriasMock, 
  cadastrarCategoriaMock,
  atualizarCategoriaMock,
  removerCategoriaMock 
} from "../services/categoriaServiceMock";
import { useMock } from '../utils/mock';
import { useToastUtils } from '../hooks/useToast';
import useConfirmDialog from '../hooks/useConfirmDialog';
import ConfirmDialog from '../components/ConfirmDialog';
import Table, { TableColumn } from "../components/Table";
import DataStateHandler from "../components/DataStateHandler";
import Modal from "../components/Modal";
import CategoriaForm, { CategoriaFormData } from '../components/categoria/CategoriaForm';
import CadastroFiltro from '../components/CadastroFiltro';

/**
 * Página de gerenciamento de categorias
 * 
 * Funcionalidades:
 * - Listagem de categorias
 * - Cadastro de novas categorias
 * - Edição de categorias existentes
 * - Exclusão de categorias
 * - Busca por nome ou código
 * - Paginação de resultados
 */
export default function Categorias() {
  // Estados
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [categoriasFiltradas, setCategoriasFiltradas] = useState<Categoria[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalAberto, setModalAberto] = useState(false);
  const [categoriaEmEdicao, setCategoriaEmEdicao] = useState<Categoria | undefined>(undefined);
  const [termoBusca, setTermoBusca] = useState<string>("");
  
  // Estados para paginação
  const [paginaAtual, setPaginaAtual] = useState<number>(1);
  const itensPorPagina = 10;
  const [totalPaginas, setTotalPaginas] = useState<number>(1);
  const [categoriasPaginadas, setCategoriasPaginadas] = useState<Categoria[]>([]);
  
  // Hooks
  const { showSuccessToast, showErrorToast } = useToastUtils();
  const { dialog, confirm, closeDialog } = useConfirmDialog();

  // Colunas da tabela
  const colunas: TableColumn[] = [
    {
      header: "Nome",
      accessor: "nome"
    },
    {
      header: "Tipo",
      accessor: "tipo"
    },
    {
      header: "Ações",
      accessor: "id_categoria",
      render: (categoria: Categoria) => (
        <div className="table-actions">
          <button 
            className="btn-icon btn-edit"
            onClick={(e) => {
              e.stopPropagation();
              handleEditarClick(categoria);
            }}
            aria-label="Editar categoria"
          >
            ✏️
          </button>
          <button 
            className="btn-icon btn-delete"
            onClick={(e) => {
              e.stopPropagation();
              handleExcluirClick(categoria);
            }}
            aria-label="Excluir categoria"
          >
            🗑️
          </button>
        </div>
      )
    }
  ];

  // Efeito para carregar categorias
  useEffect(() => {
    fetchCategorias();
  }, []);
  
  // Efeito para filtrar as categorias quando o termo de busca mudar
  useEffect(() => {
    filtrarCategorias();
  }, [termoBusca, categorias]);
  
  // Efeito para paginar as categorias filtradas
  useEffect(() => {
    paginarCategorias();
  }, [categoriasFiltradas, paginaAtual]);

  // Buscar categorias
  const fetchCategorias = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = useMock() 
        ? await listarCategoriasMock() 
        : await listarCategorias();
      setCategorias(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar categorias';
      setError(errorMessage);
      showErrorToast(errorMessage);
    } finally {
      setLoading(false);
    }
  };
  
  // Filtrar categorias com base no termo de busca
  const filtrarCategorias = () => {
    if (!termoBusca) {
      setCategoriasFiltradas(categorias);
    } else {
      const termo = termoBusca.toLowerCase();
      const filtradas = categorias.filter(categoria => 
        categoria.nome.toLowerCase().includes(termo) || 
        categoria.id_categoria.toLowerCase().includes(termo)
      );
      setCategoriasFiltradas(filtradas);
    }
    
    // Resetar para a primeira página quando filtrar
    setPaginaAtual(1);
  };
  
  // Buscar categorias com base no termo de busca
  const buscarCategorias = (termo: string) => {
    setTermoBusca(termo);
  };
  
  // Limpar filtros
  const limparFiltros = () => {
    setTermoBusca("");
    setPaginaAtual(1);
  };
  
  // Paginar categorias filtradas
  const paginarCategorias = () => {
    // Calcular total de páginas
    const total = Math.ceil(categoriasFiltradas.length / itensPorPagina);
    setTotalPaginas(total);
    
    // Obter itens da página atual
    const inicio = (paginaAtual - 1) * itensPorPagina;
    const fim = inicio + itensPorPagina;
    const itensPaginados = categoriasFiltradas.slice(inicio, fim);
    setCategoriasPaginadas(itensPaginados);
  };
  
  // Função para mudar de página
  const mudarPagina = (pagina: number) => {
    setPaginaAtual(pagina);
  };

  // Abrir modal para criar nova categoria
  const handleNovaCategoria = () => {
    setCategoriaEmEdicao(undefined);
    setModalAberto(true);
  };

  // Abrir modal para editar categoria
  const handleEditarClick = (categoria: Categoria) => {
    setCategoriaEmEdicao(categoria);
    setModalAberto(true);
  };

  // Confirmar exclusão de categoria
  const handleExcluirClick = (categoria: Categoria) => {
    confirm({
      title: "Excluir categoria",
      description: `Tem certeza que deseja excluir a categoria "${categoria.nome}"? Essa ação não poderá ser desfeita.`,
      confirmText: "Excluir",
      cancelText: "Cancelar",
      type: "danger",
      onConfirm: () => excluirCategoria(categoria.id_categoria)
    });
  };
  
  // Excluir categoria
  const excluirCategoria = async (id: string) => {
    try {
      if (useMock()) {
        await removerCategoriaMock(id);
      } else {
        await removerCategoria(id);
      }
      
      // Atualizar lista de categorias
      setCategorias(prevState => prevState.filter(cat => cat.id_categoria !== id));
      showSuccessToast('Categoria excluída com sucesso!');
    } catch (err) {
      console.error('Erro ao excluir categoria:', err);
      const errorMessage = err instanceof Error ? err.message : 'Não foi possível excluir a categoria';
      showErrorToast(`${errorMessage}. Tente novamente mais tarde.`);
    }
  };
  
  // Salvar categoria (criar ou atualizar)
  const handleSalvar = async (formData: CategoriaFormData) => {
    try {
      if (categoriaEmEdicao) {
        // Atualizar categoria existente
        const categoriaAtualizada = useMock()
          ? await atualizarCategoriaMock(categoriaEmEdicao.id_categoria, formData)
          : await atualizarCategoria(categoriaEmEdicao.id_categoria, formData);
        
        setCategorias(prevCategorias => 
          prevCategorias.map(cat => 
            cat.id_categoria === categoriaEmEdicao.id_categoria ? categoriaAtualizada : cat
          )
        );
        
        showSuccessToast('Categoria atualizada com sucesso!');
      } else {
        // Criar nova categoria
        const novaCategoria = useMock()
          ? await cadastrarCategoriaMock(formData)
          : await cadastrarCategoria(formData);
        
        setCategorias(prevCategorias => [...prevCategorias, novaCategoria]);
        
        showSuccessToast('Categoria criada com sucesso!');
      }
      
      handleFecharModal();
    } catch (err) {
      console.error('Erro ao salvar categoria:', err);
      const operacao = categoriaEmEdicao ? 'atualizar' : 'criar';
      const errorMessage = err instanceof Error ? err.message : `Não foi possível ${operacao} a categoria`;
      showErrorToast(`${errorMessage}. Tente novamente mais tarde.`);
    }
  };
  
  // Fechar modal
  const handleFecharModal = () => {
    setModalAberto(false);
    setCategoriaEmEdicao(undefined);
  };

  return (
    <div className="categorias-page">
      <div className="page-header">
        <h1 className="page-title">Categorias</h1>
        <div className="page-actions">
          <button 
            className="btn-primary"
            onClick={handleNovaCategoria}
          >
            Nova Categoria
          </button>
        </div>
      </div>
      
      {/* Adicionar filtro de busca */}
      <CadastroFiltro
        onBuscar={buscarCategorias}
        onLimpar={limparFiltros}
        totalPaginas={totalPaginas}
        paginaAtual={paginaAtual}
        onMudarPagina={mudarPagina}
        placeholder="Buscar por nome ou código..."
        isLoading={loading}
      />
      
      <DataStateHandler
        loading={loading}
        error={error}
        dataLength={categoriasFiltradas.length}
        onRetry={fetchCategorias}
        emptyMessage="Nenhuma categoria encontrada."
      >
        <Table
          columns={colunas}
          data={categoriasPaginadas}
          emptyMessage="Nenhuma categoria encontrada."
        />
        
        {categoriasFiltradas.length > 0 && categoriasPaginadas.length === 0 && (
          <p className="text-gray-600 text-center mt-4">
            Não há categorias nesta página. Tente uma página diferente.
          </p>
        )}
      </DataStateHandler>
      
      {/* Modal de cadastro/edição de categoria */}
      <Modal
        isOpen={modalAberto}
        onClose={handleFecharModal}
        title={categoriaEmEdicao ? "Editar Categoria" : "Nova Categoria"}
      >
        <CategoriaForm
          categoria={categoriaEmEdicao}
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