import { useEffect, useState } from "react";
import { Permissao, Usuario } from "../types";
import { 
  listarPermissoes, 
  atualizarPermissao 
} from "../services/configuracoesService";
import { listarUsuarios } from "../services/usuarioService";
import Table, { TableColumn } from "../components/Table";
import DataStateHandler from "../components/DataStateHandler";
import { useToastUtils } from "../hooks/useToast";
import useConfirmDialog from "../hooks/useConfirmDialog";
import Modal from "../components/Modal";
import FormField from "../components/FormField";
import ConfirmDialog from "../components/ConfirmDialog";
import useFormHandler from "../hooks/useFormHandler";

// Tipo estendido que inclui nome do usuário para exibição
type PermissaoComNome = Permissao & { nome: string };

// Interface para o formulário de edição de permissão
interface PermissaoForm {
  id_usuario: string;
  telas_permitidas: string[];
}

// Lista de todas as telas/rotas disponíveis no sistema
const telasDisponiveis = [
  { id: "dashboard", nome: "Dashboard", grupo: "Visão Geral" },
  { id: "lancamentos", nome: "Lançamentos", grupo: "Fluxo Financeiro" },
  { id: "vendas-parcelas", nome: "Vendas & Parcelas", grupo: "Fluxo Financeiro" },
  { id: "parcelas", nome: "Parcelas", grupo: "Fluxo Financeiro" },
  { id: "transferencias-contas", nome: "Transferências", grupo: "Fluxo Financeiro" },
  { id: "dre", nome: "DRE", grupo: "Relatórios & Indicadores" },
  { id: "fluxo-caixa", nome: "Fluxo de Caixa", grupo: "Relatórios & Indicadores" },
  { id: "inadimplencia", nome: "Inadimplência", grupo: "Relatórios & Indicadores" },
  { id: "ciclo-operacional", nome: "Ciclo Operacional", grupo: "Relatórios & Indicadores" },
  { id: "empresas", nome: "Empresas", grupo: "Cadastros Base" },
  { id: "clientes", nome: "Clientes", grupo: "Cadastros Base" },
  { id: "fornecedores", nome: "Fornecedores", grupo: "Cadastros Base" },
  { id: "contas-bancarias", nome: "Contas Bancárias", grupo: "Cadastros Base" },
  { id: "categorias", nome: "Categorias", grupo: "Cadastros Base" },
  { id: "centro-custos", nome: "Centro de Custos", grupo: "Cadastros Base" },
  { id: "formas-pagamento", nome: "Formas de Pagamento", grupo: "Cadastros Base" },
  { id: "meus-dados", nome: "Meus Dados", grupo: "Perfil do Usuário" },
  { id: "gestao-usuarios", nome: "Gestão de Usuários", grupo: "Administração" },
  { id: "permissoes", nome: "Permissões", grupo: "Administração" },
  { id: "logs-auditoria", nome: "Logs de Auditoria", grupo: "Administração" },
  { id: "conexoes-externas", nome: "Conexões Externas", grupo: "Configurações" },
  { id: "parametros-sistema", nome: "Parâmetros do Sistema", grupo: "Configurações" }
];

// Função auxiliar para agrupar telas por categoria
function agruparTelasPorGrupo() {
  const grupos: {[key: string]: {id: string, nome: string}[]} = {};
  
  telasDisponiveis.forEach(tela => {
    if (!grupos[tela.grupo]) {
      grupos[tela.grupo] = [];
    }
    grupos[tela.grupo].push({id: tela.id, nome: tela.nome});
  });
  
  return grupos;
}

export default function Permissoes() {
  // Estados
  const [permissoes, setPermissoes] = useState<PermissaoComNome[]>([]);
  const [usuarios, setUsuarios] = useState<Usuario[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");
  const [modalAberto, setModalAberto] = useState<boolean>(false);
  const [permissaoEmEdicao, setPermissaoEmEdicao] = useState<PermissaoComNome | null>(null);
  const telasPorGrupo = agruparTelasPorGrupo();
  
  // Hooks
  const { showSuccessToast, showErrorToast } = useToastUtils();
  const { dialog, confirm, closeDialog } = useConfirmDialog();
  const { formData, setFormData, resetForm } = useFormHandler<PermissaoForm>({
    id_usuario: "",
    telas_permitidas: []
  });

  // Definição das colunas da tabela
  const colunas: TableColumn[] = [
    {
      header: "Usuário",
      accessor: "nome"
    },
    {
      header: "Telas Permitidas",
      accessor: "telas_permitidas",
      render: (item: PermissaoComNome) => {
        const nomesTelas = item.telas_permitidas.map(id => {
          const tela = telasDisponiveis.find(t => t.id === id);
          return tela ? tela.nome : id;
        });
        return nomesTelas.join(", ");
      }
    },
    {
      header: "Ações",
      accessor: "id_usuario",
      render: (item: PermissaoComNome) => (
        <div className="flex space-x-2">
          <button 
            className="btn-icon-small"
            onClick={() => handleEditarClick(item)}
            aria-label="Editar permissões"
          >
            ✏️
          </button>
        </div>
      )
    }
  ];

  // Carregar dados iniciais
  useEffect(() => {
    fetchData();
  }, []);

  // Buscar dados de permissões e usuários
  async function fetchData() {
    try {
      setLoading(true);
      const [permissoesData, usuariosData] = await Promise.all([
        listarPermissoes(),
        listarUsuarios()
      ]);
      
      setPermissoes(permissoesData);
      setUsuarios(usuariosData);
      setError("");
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Erro ao carregar dados.";
      setError(errorMessage);
      console.error("Erro ao carregar dados:", err);
    } finally {
      setLoading(false);
    }
  }

  // Lidar com clique no botão de editar
  const handleEditarClick = (permissao: PermissaoComNome) => {
    setPermissaoEmEdicao(permissao);
    setFormData({
      id_usuario: permissao.id_usuario,
      telas_permitidas: [...permissao.telas_permitidas]
    });
    setModalAberto(true);
  };

  // Abrir modal para adicionar novas permissões
  const handleNovaPermissao = () => {
    setPermissaoEmEdicao(null);
    resetForm();
    setModalAberto(true);
  };

  // Fechar o modal
  const handleFecharModal = () => {
    setModalAberto(false);
    setPermissaoEmEdicao(null);
    resetForm();
  };

  // Alternar seleção de tela nas permissões
  const toggleTela = (telaId: string) => {
    setFormData(prev => {
      const telasSelecionadas = [...prev.telas_permitidas];
      
      if (telasSelecionadas.includes(telaId)) {
        return {
          ...prev,
          telas_permitidas: telasSelecionadas.filter(id => id !== telaId)
        };
      } else {
        return {
          ...prev,
          telas_permitidas: [...telasSelecionadas, telaId]
        };
      }
    });
  };

  // Marcar ou desmarcar todas as telas de um grupo
  const toggleGrupo = (grupo: string, marcar: boolean) => {
    const telasDoGrupo = telasDisponiveis
      .filter(tela => tela.grupo === grupo)
      .map(tela => tela.id);
    
    setFormData(prev => {
      let novasTelas = [...prev.telas_permitidas];
      
      if (marcar) {
        // Adicionar todas as telas do grupo que não estão selecionadas
        telasDoGrupo.forEach(telaId => {
          if (!novasTelas.includes(telaId)) {
            novasTelas.push(telaId);
          }
        });
      } else {
        // Remover todas as telas do grupo
        novasTelas = novasTelas.filter(telaId => !telasDoGrupo.includes(telaId));
      }
      
      return {
        ...prev,
        telas_permitidas: novasTelas
      };
    });
  };

  // Verificar se todas as telas de um grupo estão selecionadas
  const isGrupoCompleto = (grupo: string) => {
    const telasDoGrupo = telasDisponiveis
      .filter(tela => tela.grupo === grupo)
      .map(tela => tela.id);
    
    return telasDoGrupo.every(telaId => formData.telas_permitidas.includes(telaId));
  };

  // Verificar se alguma tela de um grupo está selecionada
  const isGrupoParcial = (grupo: string) => {
    const telasDoGrupo = telasDisponiveis
      .filter(tela => tela.grupo === grupo)
      .map(tela => tela.id);
    
    return telasDoGrupo.some(telaId => formData.telas_permitidas.includes(telaId)) 
      && !isGrupoCompleto(grupo);
  };

  // Salvar permissões
  const handleSalvar = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.id_usuario && !permissaoEmEdicao) {
      showErrorToast("Selecione um usuário");
      return;
    }
    
    try {
      setLoading(true);
      
      const id_usuario = permissaoEmEdicao?.id_usuario || formData.id_usuario;
      
      const permissaoAtualizada = await atualizarPermissao(
        id_usuario, 
        { telas_permitidas: formData.telas_permitidas }
      );
      
      // Encontrar o nome do usuário para adicionar ao objeto de permissão atualizado
      const usuario = usuarios.find(u => u.id_usuario === id_usuario);
      const permissaoComNome = {
        ...permissaoAtualizada,
        nome: usuario?.nome || "Usuário"
      };
      
      // Atualizar a lista local de permissões
      if (permissaoEmEdicao) {
        setPermissoes(prevPermissoes => 
          prevPermissoes.map(p => 
            p.id_usuario === permissaoEmEdicao.id_usuario ? permissaoComNome : p
          )
        );
      } else {
        setPermissoes(prevPermissoes => [...prevPermissoes, permissaoComNome]);
      }
      
      showSuccessToast(permissaoEmEdicao 
        ? "Permissões atualizadas com sucesso!" 
        : "Permissões adicionadas com sucesso!"
      );
      
      setModalAberto(false);
      resetForm();
    } catch (err) {
      console.error("Erro ao salvar permissões:", err);
      showErrorToast("Não foi possível salvar as permissões.");
    } finally {
      setLoading(false);
    }
  };

  // Quando um usuário é selecionado no dropdown
  const handleUsuarioChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const idUsuario = e.target.value;
    
    if (idUsuario) {
      const permissaoExistente = permissoes.find(p => p.id_usuario === idUsuario);
      
      if (permissaoExistente) {
        // Se já existir permissões para este usuário, carregá-las
        setFormData({
          id_usuario: idUsuario,
          telas_permitidas: [...permissaoExistente.telas_permitidas]
        });
      } else {
        // Caso contrário, iniciar com nenhuma tela selecionada
        setFormData({
          id_usuario: idUsuario,
          telas_permitidas: []
        });
      }
    }
  };

  return (
    <div className="page-content">
      <div className="page-header">
        <h1 className="page-title">Permissões de Usuários</h1>
        <div className="page-actions">
          <button 
            className="btn-primary"
            onClick={handleNovaPermissao}
          >
            Gerenciar Permissões
          </button>
        </div>
      </div>
      
      <DataStateHandler
        loading={loading}
        error={error}
        dataLength={permissoes.length}
        onRetry={fetchData}
        emptyMessage="Nenhuma permissão registrada."
      >
        <Table
          columns={colunas}
          data={permissoes}
          emptyMessage="Nenhuma permissão registrada."
        />
      </DataStateHandler>
    </div>
  );
} 