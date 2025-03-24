import { useEffect, useState } from "react";
import { Conexao } from "../types";
import {
  listarConexoes,
  buscarConexao,
  cadastrarConexao,
  atualizarConexao,
  removerConexao,
  testarConexaoExterna
} from "../services/configuracoesService";
import Table, { TableColumn } from "../components/Table";
import DataStateHandler from "../components/DataStateHandler";
import Modal from "../components/Modal";
import FormField from "../components/FormField";
import { useToastUtils } from "../hooks/useToast";
import useFormHandler from "../hooks/useFormHandler";
import useConfirmDialog from "../hooks/useConfirmDialog";
import ConfirmDialog from "../components/ConfirmDialog";

// Interface para o formulário de conexão
interface ConexaoForm {
  nome: string;
  tipo: string;
  url: string;
  usuario?: string;
  senha?: string;
  api_key?: string;
  parametros_adicionais?: string;
}

// Tipos de conexão disponíveis
const tiposConexao = [
  { id: "REST", nome: "API REST" },
  { id: "SOAP", nome: "Serviço SOAP" },
  { id: "BANCO", nome: "Banco de Dados" },
  { id: "ERP", nome: "Sistema ERP" },
  { id: "CRM", nome: "Sistema CRM" },
  { id: "EDI", nome: "EDI (Intercâmbio Eletrônico de Dados)" }
];

export default function ConexoesExternas() {
  // Estados
  const [conexoes, setConexoes] = useState<Conexao[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");
  const [modalAberto, setModalAberto] = useState<boolean>(false);
  const [conexaoEmEdicao, setConexaoEmEdicao] = useState<Conexao | null>(null);
  const [testando, setTestando] = useState<boolean>(false);
  
  // Hooks
  const { showSuccessToast, showErrorToast, showInfoToast } = useToastUtils();
  const { dialog, confirm, closeDialog } = useConfirmDialog();
  
  // Formulário e validação
  const { 
    formData, 
    setFormData, 
    formErrors, 
    setFormErrors, 
    handleInputChange, 
    validate, 
    resetForm 
  } = useFormHandler<ConexaoForm>({
    nome: "",
    tipo: "",
    url: "",
    usuario: "",
    senha: "",
    api_key: "",
    parametros_adicionais: ""
  });

  // Regras de validação
  const validationRules = {
    nome: { 
      required: true, 
      minLength: 3, 
      maxLength: 100 
    },
    tipo: { 
      required: true 
    },
    url: { 
      required: true, 
      minLength: 5,
      pattern: /^(https?:\/\/|ftp:\/\/|jdbc:|[a-z]+:\/\/)/i,
      custom: (value: string) => {
        if (!value) return undefined;
        if (value.includes(" ")) return "URL não pode conter espaços";
        return undefined;
      }
    },
    usuario: { 
      required: formData.tipo === "BANCO"
    },
    senha: { 
      required: formData.tipo === "BANCO"
    },
    api_key: {}, // Validação opcional
    parametros_adicionais: {} // Validação opcional
  };

  // Definição das colunas da tabela
  const colunas: TableColumn[] = [
    {
      header: "Nome",
      accessor: "nome"
    },
    {
      header: "Tipo",
      accessor: "tipo",
      render: (item: Conexao) => {
        const tipo = tiposConexao.find(t => t.id === item.tipo);
        return tipo ? tipo.nome : item.tipo;
      }
    },
    {
      header: "URL",
      accessor: "url"
    },
    {
      header: "Ações",
      accessor: "id_conexao",
      render: (item: Conexao) => (
        <div className="flex space-x-2">
          <button 
            className="btn-icon-small"
            onClick={() => handleEditarClick(item.id_conexao)}
            aria-label="Editar conexão"
          >
            ✏️
          </button>
          <button 
            className="btn-icon-small"
            onClick={() => handleTestarClick(item.id_conexao)}
            aria-label="Testar conexão"
            disabled={testando}
          >
            🔄
          </button>
          <button 
            className="btn-icon-small"
            onClick={() => handleExcluirClick(item.id_conexao)}
            aria-label="Excluir conexão"
          >
            🗑️
          </button>
        </div>
      )
    }
  ];

  // Carregar dados iniciais
  useEffect(() => {
    fetchConexoes();
  }, []);

  // Buscar conexões
  async function fetchConexoes() {
    try {
      setLoading(true);
      const data = await listarConexoes();
      setConexoes(data);
      setError("");
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Erro ao carregar conexões.";
      setError(errorMessage);
      console.error("Erro ao carregar conexões:", err);
    } finally {
      setLoading(false);
    }
  }

  // Lidar com clique no botão de editar
  const handleEditarClick = async (id: string) => {
    try {
      setLoading(true);
      const conexao = await buscarConexao(id);
      setConexaoEmEdicao(conexao);
      
      setFormData({
        nome: conexao.nome,
        tipo: conexao.tipo,
        url: conexao.url,
        usuario: conexao.usuario || "",
        senha: conexao.senha || "",
        api_key: conexao.api_key || "",
        parametros_adicionais: conexao.parametros_adicionais || ""
      });
      
      setModalAberto(true);
    } catch (err) {
      showErrorToast("Erro ao carregar dados da conexão.");
      console.error("Erro ao buscar conexão:", err);
    } finally {
      setLoading(false);
    }
  };

  // Abrir modal para nova conexão
  const handleNovaConexao = () => {
    setConexaoEmEdicao(null);
    resetForm();
    setModalAberto(true);
  };

  // Fechar o modal
  const handleFecharModal = () => {
    setModalAberto(false);
    setFormErrors({});
  };

  // Testar conexão
  const handleTestarClick = async (id: string) => {
    try {
      setTestando(true);
      showInfoToast("Testando conexão...");
      
      const resultado = await testarConexaoExterna(id);
      
      if (resultado.status === "sucesso") {
        showSuccessToast(resultado.mensagem);
      } else {
        showErrorToast(resultado.mensagem);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Erro ao testar conexão.";
      showErrorToast(errorMessage);
    } finally {
      setTestando(false);
    }
  };

  // Confirmar exclusão de conexão
  const handleExcluirClick = (id: string) => {
    const conexao = conexoes.find(c => c.id_conexao === id);
    if (!conexao) return;
    
    confirm({
      title: "Excluir Conexão",
      description: `Tem certeza que deseja excluir a conexão "${conexao.nome}"? Esta ação não pode ser desfeita.`,
      confirmText: "Excluir",
      cancelText: "Cancelar",
      type: "danger",
      onConfirm: () => excluirConexao(id)
    });
  };

  // Excluir conexão
  const excluirConexao = async (id: string) => {
    try {
      setLoading(true);
      await removerConexao(id);
      
      // Atualizar a lista local
      setConexoes(prevConexoes => 
        prevConexoes.filter(c => c.id_conexao !== id)
      );
      
      showSuccessToast("Conexão excluída com sucesso.");
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Erro ao excluir conexão.";
      showErrorToast(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Salvar conexão (criar ou atualizar)
  const handleSalvar = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validar formulário
    if (!validate(validationRules)) {
      return;
    }
    
    try {
      setLoading(true);
      
      // Preparar dados
      const dadosConexao = {
        nome: formData.nome,
        tipo: formData.tipo,
        url: formData.url,
        usuario: formData.usuario || undefined,
        senha: formData.senha || undefined,
        api_key: formData.api_key || undefined,
        parametros_adicionais: formData.parametros_adicionais || undefined
      };
      
      let conexaoSalva: Conexao;
      
      if (conexaoEmEdicao) {
        // Atualizar conexão existente
        conexaoSalva = await atualizarConexao(conexaoEmEdicao.id_conexao, dadosConexao);
        
        // Atualizar a lista local
        setConexoes(prevConexoes => 
          prevConexoes.map(c => 
            c.id_conexao === conexaoEmEdicao.id_conexao ? conexaoSalva : c
          )
        );
        
        showSuccessToast("Conexão atualizada com sucesso!");
      } else {
        // Criar nova conexão
        conexaoSalva = await cadastrarConexao(dadosConexao);
        
        // Adicionar à lista local
        setConexoes(prevConexoes => [...prevConexoes, conexaoSalva]);
        
        showSuccessToast("Conexão cadastrada com sucesso!");
      }
      
      // Fechar modal e resetar formulário
      setModalAberto(false);
      resetForm();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Erro ao salvar conexão.";
      showErrorToast(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Exibir ou ocultar campos baseados no tipo de conexão
  const renderCamposEspecificos = () => {
    switch (formData.tipo) {
      case "BANCO":
        return (
          <>
            <div className="form-row">
              <FormField
                label="Usuário"
                name="usuario"
                value={formData.usuario || ""}
                onChange={handleInputChange}
                error={formErrors.usuario}
                required={true}
              />
              <FormField
                label="Senha"
                name="senha"
                type="password"
                value={formData.senha || ""}
                onChange={handleInputChange}
                error={formErrors.senha}
                required={true}
              />
            </div>
          </>
        );
      case "REST":
      case "SOAP":
        return (
          <div className="form-row">
            <FormField
              label="API Key"
              name="api_key"
              value={formData.api_key || ""}
              onChange={handleInputChange}
              error={formErrors.api_key}
            />
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="page-content">
      <div className="page-header">
        <h1 className="page-title">Conexões Externas</h1>
        <div className="page-actions">
          <button 
            className="btn-primary"
            onClick={handleNovaConexao}
          >
            Nova Conexão
          </button>
        </div>
      </div>
      
      <DataStateHandler
        loading={loading}
        error={error}
        dataLength={conexoes.length}
        onRetry={fetchConexoes}
        emptyMessage="Nenhuma conexão encontrada."
      >
        <Table
          columns={colunas}
          data={conexoes}
          emptyMessage="Nenhuma conexão encontrada."
        />
      </DataStateHandler>
      
      {/* Modal para criar/editar conexão */}
      <Modal
        isOpen={modalAberto}
        onClose={handleFecharModal}
        title={conexaoEmEdicao ? "Editar Conexão" : "Nova Conexão"}
        size="medium"
      >
        <form onSubmit={handleSalvar} className="form-container py-0">
          <div className="form-row">
            <FormField
              label="Nome"
              name="nome"
              value={formData.nome}
              onChange={handleInputChange}
              error={formErrors.nome}
              required={true}
              placeholder="Ex: API Banco Central"
            />
          </div>
          
          <div className="form-row">
            <div className="form-field">
              <label htmlFor="tipo">Tipo <span className="text-red-500">*</span></label>
              <select
                id="tipo"
                name="tipo"
                value={formData.tipo}
                onChange={handleInputChange}
                className={`form-select ${formErrors.tipo ? 'error-input' : ''}`}
                required
              >
                <option value="">Selecione um tipo</option>
                {tiposConexao.map(tipo => (
                  <option key={tipo.id} value={tipo.id}>
                    {tipo.nome}
                  </option>
                ))}
              </select>
              {formErrors.tipo && <div className="error">{formErrors.tipo}</div>}
            </div>
          </div>
          
          <div className="form-row">
            <FormField
              label="URL"
              name="url"
              value={formData.url}
              onChange={handleInputChange}
              error={formErrors.url}
              required={true}
              placeholder="Ex: https://api.exemplo.com/v1"
            />
          </div>
          
          {/* Campos específicos baseados no tipo de conexão */}
          {renderCamposEspecificos()}
          
          <div className="form-row">
            <div className="form-field">
              <label htmlFor="parametros_adicionais">Parâmetros Adicionais</label>
              <textarea
                id="parametros_adicionais"
                name="parametros_adicionais"
                value={formData.parametros_adicionais || ""}
                onChange={handleInputChange}
                className="form-textarea"
                placeholder="Adicione parâmetros em formato JSON ou chave=valor (um por linha)"
                rows={4}
              />
            </div>
          </div>
          
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
      
      {/* Diálogo de confirmação */}
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