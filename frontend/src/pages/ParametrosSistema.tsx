import { useEffect, useState } from "react";
import { Parametro, Empresa } from "../types";
import { 
  listarParametros, 
  atualizarParametros,
  buscarParametros 
} from "../services/configuracoesService";
import { 
  listarEmpresas, 
  buscarEmpresaAtual,
  EmpresaCompleta
} from "../services/empresaService";
import Table, { TableColumn } from "../components/Table";
import DataStateHandler from "../components/DataStateHandler";
import FormField from "../components/FormField";
import { useToastUtils } from "../hooks/useToast";
import useFormHandler from "../hooks/useFormHandler";

type ParametroEditavel = {
  id_parametro: string;
  chave: string;
  valor: string;
  descricao: string;
  editando: boolean;
  valorOriginal: string;
};

export default function ParametrosSistema() {
  // Estados
  const [parametros, setParametros] = useState<ParametroEditavel[]>([]);
  const [empresas, setEmpresas] = useState<EmpresaCompleta[]>([]);
  const [empresaAtual, setEmpresaAtual] = useState<EmpresaCompleta | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [saving, setSaving] = useState<boolean>(false);
  const [error, setError] = useState<string>("");
  const [modoEdicaoGlobal, setModoEdicaoGlobal] = useState<boolean>(false);
  const [filtroBusca, setFiltroBusca] = useState<string>("");
  
  // Hooks
  const { showSuccessToast, showErrorToast, showInfoToast } = useToastUtils();
  
  // Formulário para novo parâmetro
  const { 
    formData: novoParametro, 
    handleInputChange: handleNovoParametroChange,
    formErrors,
    validate,
    resetForm
  } = useFormHandler<Omit<Parametro, 'id_parametro'>>({
    chave: "",
    valor: "",
    descricao: ""
  });
  
  // Regras de validação para novo parâmetro
  const validationRules = {
    chave: { 
      required: true, 
      minLength: 3,
      pattern: /^[a-z0-9_]+$/,
      custom: (value: string) => {
        if (parametros.some(p => p.chave === value)) {
          return "Esta chave já existe";
        }
        return undefined;
      }
    },
    valor: { 
      required: true 
    },
    descricao: { 
      required: true 
    }
  };

  // Definição das colunas da tabela
  const colunas: TableColumn[] = [
    {
      header: "Chave",
      accessor: "chave"
    },
    {
      header: "Valor",
      accessor: "valor",
      render: (item: ParametroEditavel) => (
        modoEdicaoGlobal || item.editando ? (
          <input
            type="text"
            value={item.valor}
            onChange={(e) => handleParametroChange(item.id_parametro, e.target.value)}
            className="form-input-small"
          />
        ) : (
          <span>{item.valor}</span>
        )
      )
    },
    {
      header: "Descrição",
      accessor: "descricao"
    },
    {
      header: "Ações",
      accessor: "id_parametro",
      render: (item: ParametroEditavel) => (
        <div className="flex space-x-2">
          {!modoEdicaoGlobal && (
            <>
              {!item.editando ? (
                <button 
                  className="btn-icon-small"
                  onClick={() => handleEditarClick(item.id_parametro)}
                  aria-label="Editar parâmetro"
                >
                  ✏️
                </button>
              ) : (
                <>
                  <button 
                    className="btn-icon-small"
                    onClick={() => handleSalvarClick(item.id_parametro)}
                    aria-label="Salvar parâmetro"
                  >
                    ✅
                  </button>
                  <button 
                    className="btn-icon-small"
                    onClick={() => handleCancelarClick(item.id_parametro)}
                    aria-label="Cancelar edição"
                  >
                    ❌
                  </button>
                </>
              )}
            </>
          )}
        </div>
      )
    }
  ];

  // Carregar dados iniciais
  useEffect(() => {
    fetchDados();
  }, []);
  
  // Carregar parâmetros e empresas
  async function fetchDados() {
    try {
      setLoading(true);
      
      // Carregar parâmetros e empresas em paralelo
      const [parametrosData, empresasData, empresaAtualData] = await Promise.all([
        buscarParametros(),
        listarEmpresas(),
        buscarEmpresaAtual()
      ]);
      
      // Converter para formato editável
      const parametrosEditaveis = parametrosData.map(p => ({
        ...p,
        editando: false,
        valorOriginal: p.valor
      }));
      
      setParametros(parametrosEditaveis);
      setEmpresas(empresasData);
      setEmpresaAtual(empresaAtualData);
      setError("");
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Erro ao carregar dados.";
      setError(errorMessage);
      console.error("Erro ao carregar dados:", err);
    } finally {
      setLoading(false);
    }
  }
  
  // Filtrar parâmetros com base na busca
  const parametrosFiltrados = parametros.filter(p => 
    filtroBusca === "" || 
    p.chave.toLowerCase().includes(filtroBusca.toLowerCase()) || 
    p.descricao.toLowerCase().includes(filtroBusca.toLowerCase())
  );
  
  // Manipular mudanças nos valores dos parâmetros
  const handleParametroChange = (id: string, novoValor: string) => {
    setParametros(prev => 
      prev.map(p => 
        p.id_parametro === id ? { ...p, valor: novoValor } : p
      )
    );
  };
  
  // Iniciar edição de um parâmetro individual
  const handleEditarClick = (id: string) => {
    setParametros(prev => 
      prev.map(p => 
        p.id_parametro === id 
          ? { ...p, editando: true, valorOriginal: p.valor } 
          : p
      )
    );
  };
  
  // Salvar um parâmetro individual
  const handleSalvarClick = async (id: string) => {
    const parametro = parametros.find(p => p.id_parametro === id);
    if (!parametro) return;
    
    try {
      setSaving(true);
      
      // Preparar dados para a API
      const parametrosAtualizados = {
        [parametro.chave]: parametro.valor
      };
      
      // Chamar API para atualizar
      await atualizarParametros(parametrosAtualizados);
      
      // Atualizar estado local
      setParametros(prev => 
        prev.map(p => 
          p.id_parametro === id ? { ...p, editando: false, valorOriginal: p.valor } : p
        )
      );
      
      showSuccessToast(`Parâmetro "${parametro.chave}" atualizado com sucesso!`);
    } catch (err) {
      // Em caso de erro, reverter para o valor original
      setParametros(prev => 
        prev.map(p => 
          p.id_parametro === id ? { ...p, valor: p.valorOriginal } : p
        )
      );
      
      const errorMessage = err instanceof Error ? err.message : "Erro ao salvar parâmetro.";
      showErrorToast(errorMessage);
    } finally {
      setSaving(false);
    }
  };
  
  // Cancelar edição de um parâmetro individual
  const handleCancelarClick = (id: string) => {
    setParametros(prev => 
      prev.map(p => 
        p.id_parametro === id 
          ? { ...p, editando: false, valor: p.valorOriginal } 
          : p
      )
    );
  };
  
  // Ativar/desativar modo de edição global
  const toggleModoEdicaoGlobal = () => {
    if (modoEdicaoGlobal) {
      // Se estamos saindo do modo de edição global, resetar quaisquer alterações não salvas
      setParametros(prev => 
        prev.map(p => ({ ...p, valor: p.valorOriginal, editando: false }))
      );
    }
    
    setModoEdicaoGlobal(!modoEdicaoGlobal);
  };
  
  // Salvar todas as alterações (no modo de edição global)
  const salvarTodasAlteracoes = async () => {
    try {
      setSaving(true);
      
      // Preparar dados para a API (todos os parâmetros)
      const parametrosAtualizados = parametros.reduce((acc, p: ParametroEditavel) => {
        acc[p.chave] = p.valor;
        return acc;
      }, {} as Record<string, string>);
      
      // Chamar API para atualizar
      await atualizarParametros(parametrosAtualizados);
      
      // Atualizar estado local
      setParametros(prev => 
        prev.map(p => ({ ...p, valorOriginal: p.valor, editando: false }))
      );
      
      setModoEdicaoGlobal(false);
      showSuccessToast("Todos os parâmetros foram atualizados com sucesso!");
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Erro ao salvar parâmetros.";
      showErrorToast(errorMessage);
    } finally {
      setSaving(false);
    }
  };
  
  // Adicionar novo parâmetro
  const adicionarNovoParametro = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validar formulário
    if (!validate(validationRules)) {
      return;
    }
    
    try {
      setSaving(true);
      
      // No mock atual, precisamos primeiro obter o próximo ID
      const proximoId = `${parametros.length + 1}`;
      
      // Criar novo parâmetro localmente
      const novoParametroCompleto: ParametroEditavel = {
        id_parametro: proximoId,
        chave: novoParametro.chave,
        valor: novoParametro.valor,
        descricao: novoParametro.descricao,
        editando: false,
        valorOriginal: novoParametro.valor
      };
      
      // Preparar dados para a API
      const parametrosAtualizados = {
        [novoParametro.chave]: novoParametro.valor
      };
      
      // Chamar API para atualizar
      await atualizarParametros(parametrosAtualizados);
      
      // Atualizar estado local
      setParametros(prev => [...prev, novoParametroCompleto]);
      
      showSuccessToast(`Parâmetro "${novoParametro.chave}" adicionado com sucesso!`);
      resetForm();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Erro ao adicionar parâmetro.";
      showErrorToast(errorMessage);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="page-content">
      <div className="page-header">
        <h1 className="page-title">Parâmetros do Sistema</h1>
        <div className="page-info">
          {empresaAtual && (
            <div className="empresa-atual-info">
              <span>Empresa atual: </span>
              <strong>{empresaAtual.nome}</strong>
            </div>
          )}
        </div>
      </div>
      
      <div className="card mb-4">
        <div className="card-header">
          <h2 className="card-title">Adicionar Novo Parâmetro</h2>
        </div>
        <div className="card-body">
          <form onSubmit={adicionarNovoParametro} className="form-container">
            <div className="form-row">
              <FormField
                label="Chave"
                name="chave"
                value={novoParametro.chave}
                onChange={handleNovoParametroChange}
                error={formErrors.chave}
                required={true}
                placeholder="Ex: taxa_juros_padrao"
              />
              <FormField
                label="Valor"
                name="valor"
                value={novoParametro.valor}
                onChange={handleNovoParametroChange}
                error={formErrors.valor}
                required={true}
                placeholder="Ex: 1.5"
              />
            </div>
            <div className="form-row">
              <FormField
                label="Descrição"
                name="descricao"
                value={novoParametro.descricao}
                onChange={handleNovoParametroChange}
                error={formErrors.descricao}
                required={true}
                placeholder="Ex: Taxa de juros padrão para cálculos"
              />
            </div>
            <div className="form-actions">
              <button
                type="submit"
                className="btn-primary"
                disabled={saving}
              >
                {saving ? 'Salvando...' : 'Adicionar Parâmetro'}
              </button>
            </div>
          </form>
        </div>
      </div>
      
      <div className="card">
        <div className="card-header flex justify-between items-center">
          <h2 className="card-title">Parâmetros do Sistema</h2>
          <div className="flex space-x-4">
            <div className="relative">
              <input
                type="text"
                placeholder="Buscar parâmetros..."
                value={filtroBusca}
                onChange={(e) => setFiltroBusca(e.target.value)}
                className="form-input-search"
              />
              {filtroBusca && (
                <button
                  className="clear-search-button"
                  onClick={() => setFiltroBusca("")}
                  aria-label="Limpar busca"
                >
                  &times;
                </button>
              )}
            </div>
            
            <button
              className={`btn ${modoEdicaoGlobal ? 'btn-secondary' : 'btn-primary'}`}
              onClick={toggleModoEdicaoGlobal}
              disabled={saving}
            >
              {modoEdicaoGlobal ? 'Cancelar Edição' : 'Editar Todos'}
            </button>
            
            {modoEdicaoGlobal && (
              <button
                className="btn-success"
                onClick={salvarTodasAlteracoes}
                disabled={saving}
              >
                {saving ? 'Salvando...' : 'Salvar Todos'}
              </button>
            )}
          </div>
        </div>
        
        <DataStateHandler
          loading={loading}
          error={error}
          dataLength={parametros.length}
          onRetry={fetchDados}
          emptyMessage="Nenhum parâmetro encontrado."
        >
          <Table
            columns={colunas}
            data={parametrosFiltrados}
            emptyMessage="Nenhum parâmetro encontrado."
          />
        </DataStateHandler>
      </div>
    </div>
  );
} 