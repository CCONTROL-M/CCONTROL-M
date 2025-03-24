import { useEffect, useState } from "react";
import { Usuario } from "../types";
import { buscarUsuarioAtual, atualizarUsuario, alterarSenha } from "../services/usuarioService";
import { formatarData } from "../utils/formatters";
import DataStateHandler from "../components/DataStateHandler";
import FormField from "../components/FormField";
import useFormHandler from "../hooks/useFormHandler";
import { useToastUtils } from "../hooks/useToast";

// Interface para os dados do formulário de perfil
interface PerfilFormData {
  nome: string;
  email: string;
}

// Interface para os dados do formulário de senha
interface SenhaFormData {
  senhaAtual: string;
  novaSenha: string;
  confirmarSenha: string;
}

export default function MeusDados() {
  // Estados
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [saving, setSaving] = useState<boolean>(false);
  const [error, setError] = useState<string>("");
  const [abaAtiva, setAbaAtiva] = useState<"perfil" | "senha">("perfil");
  const [editMode, setEditMode] = useState<boolean>(false);
  
  // Toast
  const { showSuccessToast, showErrorToast } = useToastUtils();
  
  // Formulário de perfil
  const {
    formData: perfilData,
    setFormData: setPerfilData,
    formErrors: perfilErrors,
    handleInputChange: handlePerfilChange,
    validate: validatePerfil,
    resetForm: resetPerfilForm
  } = useFormHandler<PerfilFormData>({
    nome: "",
    email: "",
  });
  
  // Formulário de senha
  const {
    formData: senhaData,
    formErrors: senhaErrors,
    handleInputChange: handleSenhaChange,
    validate: validateSenha,
    resetForm: resetSenhaForm
  } = useFormHandler<SenhaFormData>({
    senhaAtual: "",
    novaSenha: "",
    confirmarSenha: ""
  });

  // Carregar dados do usuário
  useEffect(() => {
    fetchUsuario();
  }, []);
  
  // Atualizar o formulário quando os dados do usuário forem carregados
  useEffect(() => {
    if (usuario) {
      setPerfilData({
        nome: usuario.nome || "",
        email: usuario.email || "",
      });
    }
  }, [usuario, setPerfilData]);

  // Buscar dados do usuário
  async function fetchUsuario() {
    try {
      setLoading(true);
      const data = await buscarUsuarioAtual();
      setUsuario(data);
      setError("");
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Erro ao carregar os dados do usuário.";
      setError(errorMessage);
      console.error("Erro ao carregar dados do usuário:", err);
    } finally {
      setLoading(false);
    }
  }

  // Verificar se há dados do usuário para o DataStateHandler
  const temDados = usuario !== null;
  
  // Regras de validação para o perfil
  const perfilValidationRules = {
    nome: { required: true, minLength: 3 },
    email: { 
      required: true, 
      pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
      custom: (value: string) => value.includes('@') ? undefined : 'Email inválido'
    }
  };
  
  // Regras de validação para a senha
  const senhaValidationRules = {
    senhaAtual: { required: true, minLength: 6 },
    novaSenha: { 
      required: true, 
      minLength: 8,
      custom: (value: string) => {
        // Verifica se a senha tem ao menos um número e uma letra
        if (!/\d/.test(value)) {
          return 'A senha deve conter pelo menos um número';
        }
        if (!/[a-zA-Z]/.test(value)) {
          return 'A senha deve conter pelo menos uma letra';
        }
        return undefined;
      }
    },
    confirmarSenha: {
      required: true,
      custom: (value: string) => {
        if (value !== senhaData.novaSenha) {
          return 'As senhas não coincidem';
        }
        return undefined;
      }
    }
  };
  
  // Salvar alterações do perfil
  const handleSalvarPerfil = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validatePerfil(perfilValidationRules)) {
      return;
    }
    
    if (!usuario) {
      showErrorToast("Dados do usuário não encontrados");
      return;
    }
    
    try {
      setSaving(true);
      
      await atualizarUsuario(usuario.id_usuario, {
        nome: perfilData.nome,
        email: perfilData.email
      });
      
      // Atualizar os dados em memória
      setUsuario(prev => prev ? {
        ...prev,
        nome: perfilData.nome,
        email: perfilData.email
      } : null);
      
      setEditMode(false);
      showSuccessToast("Perfil atualizado com sucesso!");
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Erro ao atualizar perfil.";
      showErrorToast(errorMessage);
      console.error("Erro ao atualizar perfil:", err);
    } finally {
      setSaving(false);
    }
  };
  
  // Alterar senha
  const handleAlterarSenha = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateSenha(senhaValidationRules)) {
      return;
    }
    
    try {
      setSaving(true);
      
      await alterarSenha(senhaData.senhaAtual, senhaData.novaSenha);
      
      resetSenhaForm();
      showSuccessToast("Senha alterada com sucesso!");
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Erro ao alterar senha.";
      showErrorToast(errorMessage);
      console.error("Erro ao alterar senha:", err);
    } finally {
      setSaving(false);
    }
  };
  
  // Cancelar edição
  const handleCancelar = () => {
    if (usuario) {
      setPerfilData({
        nome: usuario.nome || "",
        email: usuario.email || "",
      });
    }
    setEditMode(false);
  };
  
  return (
    <div className="page-content">
      <div className="page-header">
        <h1 className="page-title">Meus Dados</h1>
        {!editMode && abaAtiva === "perfil" && (
          <button 
            className="btn-primary" 
            onClick={() => setEditMode(true)}
          >
            Editar Perfil
          </button>
        )}
      </div>
      
      <div className="tabs-container mb-4">
        <button
          className={`tab-button ${abaAtiva === "perfil" ? "tab-active" : ""}`}
          onClick={() => setAbaAtiva("perfil")}
        >
          Perfil
        </button>
        <button
          className={`tab-button ${abaAtiva === "senha" ? "tab-active" : ""}`}
          onClick={() => setAbaAtiva("senha")}
        >
          Alterar Senha
        </button>
      </div>
      
      <DataStateHandler
        loading={loading}
        error={error}
        dataLength={temDados ? 1 : 0}
        onRetry={fetchUsuario}
        emptyMessage="Nenhum dado encontrado."
      >
        {abaAtiva === "perfil" && (
          <div className="card">
            <div className="card-header">
              <h2 className="card-title">Informações do Perfil</h2>
            </div>
            <div className="card-body">
              {!editMode && usuario && (
                <div className="user-profile-info">
                  <div className="profile-info-section">
                    <div className="profile-avatar">
                      <div className="avatar-circle">
                        {usuario.nome ? usuario.nome.charAt(0).toUpperCase() : "U"}
                      </div>
                    </div>
                    <div className="profile-details">
                      <h3 className="profile-name">{usuario.nome}</h3>
                      <p className="profile-email">{usuario.email}</p>
                      <p className="profile-type">Tipo: <span>{usuario.tipo_usuario}</span></p>
                      <p className="profile-created">Conta criada em: <span>{formatarData(usuario.created_at)}</span></p>
                    </div>
                  </div>
                </div>
              )}
              
              {editMode && (
                <form onSubmit={handleSalvarPerfil} className="form-container">
                  <div className="form-group">
                    <FormField
                      label="Nome"
                      name="nome"
                      value={perfilData.nome}
                      onChange={handlePerfilChange}
                      error={perfilErrors.nome}
                      required
                    />
                  </div>
                  
                  <div className="form-group">
                    <FormField
                      label="Email"
                      name="email"
                      type="email"
                      value={perfilData.email}
                      onChange={handlePerfilChange}
                      error={perfilErrors.email}
                      required
                    />
                  </div>
                  
                  <div className="form-actions">
                    <button 
                      type="button" 
                      className="btn-secondary"
                      onClick={handleCancelar}
                      disabled={saving}
                    >
                      Cancelar
                    </button>
                    <button 
                      type="submit" 
                      className="btn-primary"
                      disabled={saving}
                    >
                      {saving ? "Salvando..." : "Salvar Alterações"}
                    </button>
                  </div>
                </form>
              )}
            </div>
          </div>
        )}
        
        {abaAtiva === "senha" && (
          <div className="card">
            <div className="card-header">
              <h2 className="card-title">Alterar Senha</h2>
            </div>
            <div className="card-body">
              <form onSubmit={handleAlterarSenha} className="form-container">
                <div className="form-group">
                  <FormField
                    label="Senha Atual"
                    name="senhaAtual"
                    type="password"
                    value={senhaData.senhaAtual}
                    onChange={handleSenhaChange}
                    error={senhaErrors.senhaAtual}
                    required
                  />
                </div>
                
                <div className="form-group">
                  <FormField
                    label="Nova Senha"
                    name="novaSenha"
                    type="password"
                    value={senhaData.novaSenha}
                    onChange={handleSenhaChange}
                    error={senhaErrors.novaSenha}
                    required
                    helperText="Mínimo de 8 caracteres, contendo pelo menos um número e uma letra"
                  />
                </div>
                
                <div className="form-group">
                  <FormField
                    label="Confirmar Nova Senha"
                    name="confirmarSenha"
                    type="password"
                    value={senhaData.confirmarSenha}
                    onChange={handleSenhaChange}
                    error={senhaErrors.confirmarSenha}
                    required
                  />
                </div>
                
                <div className="form-actions">
                  <button 
                    type="submit" 
                    className="btn-primary"
                    disabled={saving}
                  >
                    {saving ? "Alterando Senha..." : "Alterar Senha"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </DataStateHandler>
    </div>
  );
} 