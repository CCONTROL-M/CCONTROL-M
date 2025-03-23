import { useEffect, useState } from "react";
import { Venda, Cliente, Categoria, NovaVenda } from "../types";
import { formatarData, formatarMoeda } from "../utils/formatters";
import { listarVendas, cadastrarVenda } from "../services/vendaService";
import { listarClientes } from "../services/clienteService";
import { listarCategorias } from "../services/categoriaService";

export default function VendasParcelas() {
  // Estados para a listagem de vendas
  const [vendas, setVendas] = useState<Venda[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");
  
  // Estados para o formulário
  const [formData, setFormData] = useState<NovaVenda>({
    id_cliente: "",
    valor_total: 0,
    numero_parcelas: 1,
    data_inicio: new Date().toISOString().split('T')[0],
    descricao: "",
    categoria: "venda"
  });
  
  // Estados auxiliares
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [showForm, setShowForm] = useState<boolean>(false);
  const [formSuccess, setFormSuccess] = useState<string>("");
  const [formError, setFormError] = useState<string>("");

  // Carregar vendas
  useEffect(() => {
    fetchVendas();
  }, []);
  
  // Carregar clientes e categorias para o formulário
  useEffect(() => {
    if (showForm) {
      fetchClientes();
      fetchCategorias();
    }
  }, [showForm]);

  // Buscar vendas da API
  async function fetchVendas() {
    setLoading(true);
    try {
      const data = await listarVendas();
      setVendas(data);
    } catch (err) {
      setError("Erro ao carregar as vendas.");
    } finally {
      setLoading(false);
    }
  }
  
  // Buscar clientes da API
  async function fetchClientes() {
    try {
      const data = await listarClientes();
      setClientes(data);
      // Selecionar o primeiro cliente como padrão se não houver um selecionado
      if (data.length > 0 && !formData.id_cliente) {
        setFormData(prev => ({ ...prev, id_cliente: data[0].id_cliente }));
      }
    } catch (err) {
      setFormError("Erro ao carregar a lista de clientes.");
    }
  }
  
  // Buscar categorias da API
  async function fetchCategorias() {
    try {
      const data = await listarCategorias();
      setCategorias(data);
      // Selecionar a primeira categoria como padrão se não houver uma selecionada
      if (data.length > 0 && formData.categoria === "venda") {
        setFormData(prev => ({ ...prev, categoria: data[0].id_categoria }));
      }
    } catch (err) {
      setFormError("Erro ao carregar a lista de categorias.");
    }
  }

  // Atualizar os campos do formulário
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    
    // Converter para número quando aplicável
    if (name === "valor_total") {
      setFormData({ ...formData, [name]: parseFloat(value) || 0 });
    } else if (name === "numero_parcelas") {
      setFormData({ ...formData, [name]: parseInt(value) || 1 });
    } else {
      setFormData({ ...formData, [name]: value });
    }
  };

  // Enviar formulário para a API
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setFormSuccess("");
    setFormError("");

    try {
      // Validação básica
      if (!formData.id_cliente) {
        throw new Error("Selecione um cliente.");
      }
      
      if (formData.valor_total <= 0) {
        throw new Error("O valor total deve ser maior que zero.");
      }
      
      if (formData.numero_parcelas < 1) {
        throw new Error("O número de parcelas deve ser pelo menos 1.");
      }
      
      if (!formData.data_inicio) {
        throw new Error("Selecione uma data de início.");
      }
      
      // Enviar para a API
      await cadastrarVenda(formData);
      
      // Sucesso
      setFormSuccess("Venda cadastrada com sucesso! As parcelas foram geradas automaticamente.");
      
      // Resetar formulário
      setFormData({
        id_cliente: "",
        valor_total: 0,
        numero_parcelas: 1,
        data_inicio: new Date().toISOString().split('T')[0],
        descricao: "",
        categoria: "venda"
      });
      
      // Recarregar a lista de vendas
      fetchVendas();
      
      // Fechar formulário após alguns segundos
      setTimeout(() => {
        setShowForm(false);
        setFormSuccess("");
      }, 3000);
      
    } catch (err) {
      if (err instanceof Error) {
        setFormError(err.message);
      } else {
        setFormError("Erro ao cadastrar a venda. Tente novamente.");
      }
    } finally {
      setIsSaving(false);
    }
  };

  // Mostrar mensagem de carregamento
  if (loading && !showForm) return <p className="placeholder-text">Carregando...</p>;
  if (error && !showForm) return <p className="placeholder-text">{error}</p>;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Vendas & Parcelas</h1>
        <button 
          className="btn-primary" 
          onClick={() => setShowForm(!showForm)}
        >
          {showForm ? "Cancelar" : "Nova Venda"}
        </button>
      </div>
      
      {showForm && (
        <div className="form-container">
          <h2>Cadastrar Nova Venda</h2>
          
          {formSuccess && <div className="alert-success">{formSuccess}</div>}
          {formError && <div className="alert-error">{formError}</div>}
          
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="id_cliente">Cliente:</label>
              <select 
                id="id_cliente"
                name="id_cliente"
                value={formData.id_cliente}
                onChange={handleInputChange}
                disabled={isSaving}
                required
              >
                <option value="">Selecione um cliente</option>
                {clientes.map(cliente => (
                  <option key={cliente.id_cliente} value={cliente.id_cliente}>
                    {cliente.nome}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="form-group">
              <label htmlFor="valor_total">Valor Total (R$):</label>
              <input 
                type="number"
                id="valor_total"
                name="valor_total"
                min="0.01"
                step="0.01"
                value={formData.valor_total}
                onChange={handleInputChange}
                disabled={isSaving}
                required
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="numero_parcelas">Número de Parcelas:</label>
              <input 
                type="number"
                id="numero_parcelas"
                name="numero_parcelas"
                min="1"
                max="36"
                value={formData.numero_parcelas}
                onChange={handleInputChange}
                disabled={isSaving}
                required
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="data_inicio">Data de Início:</label>
              <input 
                type="date"
                id="data_inicio"
                name="data_inicio"
                value={formData.data_inicio}
                onChange={handleInputChange}
                disabled={isSaving}
                required
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="categoria">Categoria:</label>
              <select
                id="categoria"
                name="categoria"
                value={formData.categoria}
                onChange={handleInputChange}
                disabled={isSaving}
                required
              >
                <option value="venda">Venda</option>
                {categorias.map(cat => (
                  <option key={cat.id_categoria} value={cat.id_categoria}>
                    {cat.nome}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="form-group">
              <label htmlFor="descricao">Descrição:</label>
              <textarea
                id="descricao"
                name="descricao"
                value={formData.descricao}
                onChange={handleInputChange}
                disabled={isSaving}
                required
              />
            </div>
            
            <div className="form-actions">
              <button 
                type="button" 
                className="btn-secondary"
                onClick={() => setShowForm(false)}
                disabled={isSaving}
              >
                Cancelar
              </button>
              <button 
                type="submit" 
                className="btn-primary"
                disabled={isSaving}
              >
                {isSaving ? "Salvando..." : "Cadastrar Venda"}
              </button>
            </div>
          </form>
        </div>
      )}
      
      {vendas.length === 0 && !showForm ? (
        <p className="placeholder-text">Nenhuma venda encontrada.</p>
      ) : (
        !showForm && (
          <table>
            <thead>
              <tr>
                <th>Descrição</th>
                <th>Valor Total</th>
                <th>Parcelas</th>
                <th>Data Início</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {vendas.map((v) => (
                <tr key={v.id_venda}>
                  <td>{v.descricao}</td>
                  <td>{formatarMoeda(v.valor_total)}</td>
                  <td>{v.numero_parcelas}</td>
                  <td>{formatarData(v.data_inicio)}</td>
                  <td>{v.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )
      )}
    </div>
  );
} 