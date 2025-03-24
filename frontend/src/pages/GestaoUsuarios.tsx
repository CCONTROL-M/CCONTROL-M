import { useEffect, useState, ChangeEvent } from "react";
import { Usuario } from "../types";
import { 
  listarUsuarios, 
  cadastrarUsuario, 
  atualizarUsuario, 
  removerUsuario 
} from "../services/usuarioService";
import { formatarData } from "../utils/formatters";
import Table, { TableColumn } from "../components/Table";
import DataStateHandler from "../components/DataStateHandler";
import Modal from "../components/Modal";
import FormField from "../components/FormField";
import ConfirmDialog from "../components/ConfirmDialog";
import { useToastUtils } from "../hooks/useToast";
import useFormHandler from "../hooks/useFormHandler";
import useConfirmDialog from "../hooks/useConfirmDialog";

interface UsuarioForm {
  nome: string;
  email: string;
  tipo_usuario: string;
  senha?: string;
  confirmar_senha?: string;
}

// Tipos de usuário disponíveis
const tiposUsuario = [
  { value: "admin", label: "Administrador" },
  { value: "gestor", label: "Gestor" },
  { value: "operador", label: "Operador" },
  { value: "financeiro", label: "Financeiro" },
  { value: "contador", label: "Contador" }
];

export default function GestaoUsuarios() {
  // Estados
  const [usuarios, setUsuarios] = useState<Usuario[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");
  const [modalAberto, setModalAberto] = useState<boolean>(false);
  const [usuarioEmEdicao, setUsuarioEmEdicao] = useState<Usuario | null>(null);
  const [mostrarSenha, setMostrarSenha] = useState<boolean>(false);
  
  // Hooks
  const { showSuccessToast, showErrorToast } = useToastUtils();
  const { dialog, confirm, closeDialog } = useConfirmDialog();
  const { 
    formData, 
    handleInputChange, 
    resetForm, 
    formErrors, 
    validate, 
    setFormData 
  } = useFormHandler<UsuarioForm>({
    nome: '',
    email: '',
    tipo_usuario: 'operador',
    senha: '',
    confirmar_senha: ''
  });

  // Definição das colunas da tabela
  const colunas: TableColumn[] = [
    {
      header: "Nome",
      accessor: "nome"
    },
    {
      header: "Email",
      accessor: "email"
    },
    {
      header: "Perfil",
      accessor: "tipo_usuario",
      render: (usuario: Usuario) => {
        const tipo = tiposUsuario.find(t => t.value === usuario.tipo_usuario);
        return tipo?.label || usuario.tipo_usuario;
      }
    },
    {
      header: "Criado em",
      accessor: "created_at",
      render: (usuario: Usuario) => formatarData(usuario.created_at)
    },
    {
      header: "Ações",
      accessor: "id_usuario",
      render: (usuario: Usuario) => (
        <div className="flex space-x-2">
          <button 
            className="btn-icon-small"
            onClick={() => handleEditarClick(usuario)}
            aria-label="Editar usuário"
          >
            ✏️
          </button>
          <button 
            className="btn-icon-small text-red-500"
            onClick={() => handleExcluirClick(usuario)}
            aria-label="Excluir usuário"
          >
            🗑️
          </button>
        </div>
      )
    }
  ];

  useEffect(() => {
    fetchUsuarios();
  }, []);

  /**
   * Busca a lista de usuários
   */
  async function fetchUsuarios() {
    try {
      setLoading(true);
      const data = await listarUsuarios();
      setUsuarios(data);
      setError("");
    } catch (err) {
      console.error("Erro ao carregar usuários:", err);
      setError("Erro ao carregar os usuários. Verifique a conexão com o servidor.");
    } finally {
      setLoading(false);
    }
  }

  /**
   * Abre o modal para adicionar um novo usuário
   */
  const handleNovoUsuario = () => {
    setUsuarioEmEdicao(null);
    resetForm();
    setModalAberto(true);
    setMostrarSenha(true);
  };

  /**
   * Abre o modal para editar um usuário existente
   */
  const handleEditarClick = (usuario: Usuario) => {
    setUsuarioEmEdicao(usuario);
    setFormData({
      nome: usuario.nome || '',
      email: usuario.email || '',
      tipo_usuario: usuario.tipo_usuario || 'operador',
      senha: '',
      confirmar_senha: ''
    });
    setModalAberto(true);
    setMostrarSenha(false); // Não mostra campos de senha na edição
  };

  /**
   * Solicita confirmação para excluir um usuário
   */
  const handleExcluirClick = (usuario: Usuario) => {
    confirm({
      title: "Excluir Usuário",
      description: `Tem certeza que deseja excluir o usuário "${usuario.nome}"? Esta ação não pode ser desfeita.`,
      confirmText: "Excluir",
      cancelText: "Cancelar",
      type: "danger",
      onConfirm: () => excluirUsuario(usuario.id_usuario)
    });
  };

  /**
   * Exclui um usuário
   */
  const excluirUsuario = async (id: string) => {
    try {
      setLoading(true);
      
      await removerUsuario(id);
      
      setUsuarios(prevUsuarios => 
        prevUsuarios.filter(u => u.id_usuario !== id)
      );
      
      showSuccessToast("Usuário excluído com sucesso!");
    } catch (err) {
      console.error('Erro ao excluir usuário:', err);
      showErrorToast("Não foi possível excluir o usuário. Tente novamente.");
    } finally {
      setLoading(false);
    }
  };

  /**
   * Valida as regras específicas da senha
   */
  const validarSenha = () => {
    if (!mostrarSenha) return true;
    
    // Se estiver criando um novo usuário, senha é obrigatória
    if (!usuarioEmEdicao && (!formData.senha || formData.senha.length < 6)) {
      setFormData(prev => ({
        ...prev,
        senha: prev.senha
      }));
      return false;
    }
    
    // Se senha e confirmação não batem
    if (formData.senha && formData.senha !== formData.confirmar_senha) {
      setFormData(prev => ({
        ...prev,
        confirmar_senha: prev.confirmar_senha
      }));
      return false;
    }
    
    return true;
  };

  /**
   * Salva o usuário (novo ou editado)
   */
  const handleSalvar = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validar formulário
    const isValid = validate({
      nome: { required: true },
      email: { required: true, pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/ },
      tipo_usuario: { required: true },
      senha: {}, // Validação específica feita em validarSenha()
      confirmar_senha: {}
    });
    
    if (!isValid || !validarSenha()) {
      return;
    }
    
    try {
      setLoading(true);
      
      const usuarioData = {
        nome: formData.nome,
        email: formData.email,
        tipo_usuario: formData.tipo_usuario,
        ...(formData.senha ? { senha: formData.senha } : {})
      };
      
      if (usuarioEmEdicao) {
        // Editando usuário existente
        const usuarioAtualizado = await atualizarUsuario(usuarioEmEdicao.id_usuario, usuarioData);
        
        // Atualiza a lista local
        setUsuarios(prevUsuarios => 
          prevUsuarios.map(u => 
            u.id_usuario === usuarioEmEdicao.id_usuario 
              ? usuarioAtualizado
              : u
          )
        );
        
        showSuccessToast("Usuário atualizado com sucesso!");
      } else {
        // Cadastrando novo usuário
        const novoUsuario = await cadastrarUsuario(usuarioData);
        
        // Adiciona à lista local
        setUsuarios(prevUsuarios => [...prevUsuarios, novoUsuario]);
        
        showSuccessToast("Usuário cadastrado com sucesso!");
      }
      
      // Fecha o modal após salvar
      setModalAberto(false);
      resetForm();
    } catch (err) {
      console.error('Erro ao salvar usuário:', err);
      showErrorToast(
        usuarioEmEdicao 
          ? "Não foi possível atualizar o usuário" 
          : "Não foi possível cadastrar o usuário"
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
    setUsuarioEmEdicao(null);
    resetForm();
  };

  return (
    <div className="usuarios-page">
      <div className="page-header">
        <h1 className="page-title">Gestão de Usuários</h1>
        <div className="page-actions">
          <button 
            className="btn-primary"
            onClick={handleNovoUsuario}
          >
            Novo Usuário
          </button>
        </div>
      </div>
      
      <DataStateHandler
        loading={loading}
        error={error}
        dataLength={usuarios.length}
        onRetry={fetchUsuarios}
        emptyMessage="Nenhum usuário encontrado."
      >
        <Table
          columns={colunas}
          data={usuarios}
          emptyMessage="Nenhum usuário encontrado."
        />
      </DataStateHandler>
      
      {/* Modal de cadastro/edição de usuário */}
      <Modal
        isOpen={modalAberto}
        onClose={handleFecharModal}
        title={usuarioEmEdicao ? "Editar Usuário" : "Novo Usuário"}
      >
        <form onSubmit={handleSalvar} className="form-container py-0">
          <div className="form-row">
            <FormField
              label="Nome"
              name="nome"
              value={formData.nome}
              onChange={handleInputChange}
              error={formErrors.nome}
              required
            />
          </div>
          
          <div className="form-row">
            <FormField
              label="Email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleInputChange}
              error={formErrors.email}
              required
            />
          </div>
          
          <div className="form-row">
            <div className="form-field">
              <label htmlFor="tipo_usuario">Perfil do Usuário <span className="text-red-500">*</span></label>
              <select
                id="tipo_usuario"
                name="tipo_usuario"
                value={formData.tipo_usuario}
                onChange={handleInputChange}
                className="form-select"
              >
                {tiposUsuario.map(tipo => (
                  <option key={tipo.value} value={tipo.value}>
                    {tipo.label}
                  </option>
                ))}
              </select>
              {formErrors.tipo_usuario && (
                <span className="form-error">{formErrors.tipo_usuario}</span>
              )}
            </div>
          </div>
          
          {mostrarSenha && (
            <>
              <div className="form-row">
                <FormField
                  label="Senha"
                  name="senha"
                  type="password"
                  value={formData.senha || ''}
                  onChange={handleInputChange}
                  error={formErrors.senha}
                  required={!usuarioEmEdicao}
                />
              </div>
              
              <div className="form-row">
                <FormField
                  label="Confirmar Senha"
                  name="confirmar_senha"
                  type="password"
                  value={formData.confirmar_senha || ''}
                  onChange={handleInputChange}
                  error={formErrors.confirmar_senha}
                  required={!usuarioEmEdicao}
                />
              </div>
            </>
          )}
          
          {usuarioEmEdicao && !mostrarSenha && (
            <div className="form-row">
              <button
                type="button"
                className="btn-text"
                onClick={() => setMostrarSenha(true)}
              >
                Alterar senha
              </button>
            </div>
          )}
          
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