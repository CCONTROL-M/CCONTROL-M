import { useEffect, useState } from "react";
import { Usuario } from "../types";
import { buscarUsuarioAtual } from "../services/usuarioService";
import { formatarData } from "../utils/formatters";
import DataStateHandler from "../components/DataStateHandler";
import FormField from "../components/FormField";
import useFormHandler from "../hooks/useFormHandler";

export default function MeusDados() {
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");
  const [editMode, setEditMode] = useState<boolean>(false);
  
  // Inicializar o formulário com valores vazios
  const {
    formData,
    setFormData,
    formErrors,
    handleInputChange,
    validate,
    resetForm
  } = useFormHandler<{
    nome: string;
    email: string;
    senha: string;
    confirmarSenha: string;
  }>({
    nome: "",
    email: "",
    senha: "",
    confirmarSenha: ""
  });

  useEffect(() => {
    fetchUsuario();
  }, []);
  
  // Atualizar o formulário quando os dados do usuário forem carregados
  useEffect(() => {
    if (usuario) {
      setFormData({
        nome: usuario.nome || "",
        email: usuario.email || "",
        senha: "",
        confirmarSenha: ""
      });
    }
  }, [usuario, setFormData]);

  async function fetchUsuario() {
    try {
      setLoading(true);
      const data = await buscarUsuarioAtual();
      setUsuario(data);
      setError("");
    } catch (err) {
      setError("Erro ao carregar os dados do usuário.");
    } finally {
      setLoading(false);
    }
  }

  // Verificar se há dados do usuário para o DataStateHandler
  const temDados = usuario !== null;
  
  // Validar o formulário
  const validateForm = () => {
    return validate({
      nome: { required: true, minLength: 3 },
      email: { 
        required: true, 
        pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
        custom: (value: string) => value.includes('@') ? undefined : 'Email inválido'
      },
      senha: formData.senha ? { minLength: 6 } : {},
      confirmarSenha: {
        custom: (value: string) => {
          if (formData.senha && value !== formData.senha) {
            return 'As senhas não coincidem';
          }
          return undefined;
        }
      }
    });
  };
  
  // Enviar o formulário
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    // Aqui você implementaria a lógica de envio do formulário
    console.log("Dados a serem atualizados:", formData);
    
    // Sair do modo de edição
    setEditMode(false);
  };
  
  // Cancelar a edição
  const handleCancel = () => {
    resetForm();
    setEditMode(false);
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Meus Dados</h1>
        {!editMode && (
          <button 
            className="btn-primary" 
            onClick={() => setEditMode(true)}
          >
            Editar Perfil
          </button>
        )}
      </div>
      
      <DataStateHandler
        loading={loading}
        error={error}
        dataLength={temDados ? 1 : 0}
        onRetry={fetchUsuario}
        emptyMessage="Nenhum dado encontrado."
      >
        {!editMode && usuario && (
          <div className="form-container">
            <ul className="data-list">
              <li><strong>Nome:</strong> {usuario.nome}</li>
              <li><strong>Email:</strong> {usuario.email}</li>
              <li><strong>Tipo de Usuário:</strong> {usuario.tipo_usuario}</li>
              <li><strong>Criado em:</strong> {formatarData(usuario.created_at)}</li>
            </ul>
          </div>
        )}
        
        {editMode && (
          <div className="form-container">
            <h2>Editar Perfil</h2>
            <form onSubmit={handleSubmit}>
              <FormField
                label="Nome"
                name="nome"
                value={formData.nome}
                onChange={handleInputChange}
                error={formErrors.nome}
                required
              />
              
              <FormField
                label="Email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleInputChange}
                error={formErrors.email}
                required
              />
              
              <FormField
                label="Nova Senha"
                name="senha"
                type="password"
                value={formData.senha}
                onChange={handleInputChange}
                error={formErrors.senha}
                placeholder="Deixe em branco para manter a atual"
              />
              
              <FormField
                label="Confirmar Nova Senha"
                name="confirmarSenha"
                type="password"
                value={formData.confirmarSenha}
                onChange={handleInputChange}
                error={formErrors.confirmarSenha}
                placeholder="Confirme a nova senha"
              />
              
              <div className="form-actions">
                <button 
                  type="button" 
                  className="btn-secondary"
                  onClick={handleCancel}
                >
                  Cancelar
                </button>
                <button 
                  type="submit" 
                  className="btn-primary"
                >
                  Salvar Alterações
                </button>
              </div>
            </form>
          </div>
        )}
      </DataStateHandler>
    </div>
  );
} 