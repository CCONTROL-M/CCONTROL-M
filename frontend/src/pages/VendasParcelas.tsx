import React, { useEffect, useState } from "react";
import { Venda, Cliente, NovaVenda } from "../types";
import { formatarData, formatarMoeda } from "../utils/formatters";
import { listarVendas } from "../services/vendaService";
import { listarVendasMock } from "../services/vendaServiceMock";
import { listarClientes } from "../services/clienteService";
import { listarClientesMock } from "../services/clienteServiceMock";
import Modal from "../components/Modal";
import FormField from "../components/FormField";
import { useMock } from '../utils/mock';
import Table, { TableColumn } from "../components/Table";
import DataStateHandler from "../components/DataStateHandler";

export default function VendasParcelas() {
  // Estados para a listagem de vendas
  const [vendas, setVendas] = useState<Venda[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
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
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [formErrors, setFormErrors] = useState<{
    id_cliente?: string;
    valor_total?: string;
    numero_parcelas?: string;
    data_inicio?: string;
    descricao?: string;
  }>({});

  // Definição das colunas da tabela
  const colunas: TableColumn[] = [
    {
      header: "Descrição",
      accessor: "descricao"
    },
    {
      header: "Valor Total",
      accessor: "valor_total",
      render: (venda: Venda) => formatarMoeda(venda.valor_total)
    },
    {
      header: "Parcelas",
      accessor: "numero_parcelas"
    },
    {
      header: "Data Início",
      accessor: "data_inicio",
      render: (venda: Venda) => formatarData(venda.data_inicio)
    },
    {
      header: "Status",
      accessor: "status"
    }
  ];

  // Carregar vendas
  useEffect(() => {
    fetchVendas();
  }, []);
  
  // Carregar clientes para o formulário
  useEffect(() => {
    if (isOpen) {
      fetchClientes();
    }
  }, [isOpen]);

  // Buscar vendas da API ou mock
  async function fetchVendas() {
    setLoading(true);
    setError(null);
    
    try {
      console.log("Iniciando a busca de vendas...");
      
      // Usar dados mock ou reais dependendo do utilitário useMock()
      const data = useMock() ? await listarVendasMock() : await listarVendas();
      
      console.log("Dados recebidos:", data);
      setVendas(Array.isArray(data) ? data : []);
    } catch (err: any) {
      console.error("Erro ao buscar vendas:", err);
      
      // Exibir mensagem de erro mais detalhada
      if (err.response) {
        // Resposta do servidor com erro
        const status = err.response.status;
        const message = err.response.data?.detail || err.response.statusText;
        setError(`Erro ao carregar as vendas (${status}): ${message}`);
      } else if (err.request) {
        // Sem resposta do servidor
        setError("Erro de comunicação com o servidor. Verifique sua conexão.");
      } else if (err.message) {
        // Erro específico
        setError(`Erro ao carregar as vendas: ${err.message}`);
      } else {
        // Erro genérico
        setError("Erro desconhecido ao carregar as vendas.");
      }
    } finally {
      setLoading(false);
    }
  }
  
  // Buscar clientes da API ou mock
  async function fetchClientes() {
    try {
      const data = useMock() ? await listarClientesMock() : await listarClientes();
      setClientes(data);
      // Selecionar o primeiro cliente como padrão se não houver um selecionado
      if (data.length > 0 && !formData.id_cliente) {
        setFormData(prev => ({ ...prev, id_cliente: data[0].id_cliente }));
      }
    } catch (err) {
      console.error("Erro ao carregar a lista de clientes:", err);
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

    // Limpar erro do campo quando o usuário digitar
    if (formErrors[name as keyof typeof formErrors]) {
      setFormErrors({
        ...formErrors,
        [name]: undefined,
      });
    }
  };

  // Validar o formulário
  const validateForm = (): boolean => {
    const newErrors: {
      id_cliente?: string;
      valor_total?: string;
      numero_parcelas?: string;
      data_inicio?: string;
      descricao?: string;
    } = {};
    
    if (!formData.id_cliente) {
      newErrors.id_cliente = "Selecione um cliente";
    }
    
    if (formData.valor_total <= 0) {
      newErrors.valor_total = "O valor total deve ser maior que zero";
    }
    
    if (formData.numero_parcelas < 1) {
      newErrors.numero_parcelas = "O número de parcelas deve ser pelo menos 1";
    }
    
    if (!formData.data_inicio) {
      newErrors.data_inicio = "Selecione uma data de início";
    }
    
    if (!formData.descricao.trim()) {
      newErrors.descricao = "A descrição é obrigatória";
    }
    
    setFormErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Enviar formulário
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    // Por enquanto, apenas imprime no console e fecha o modal
    console.log("Dados da nova venda:", formData);
    
    // Resetar formulário
    setFormData({
      id_cliente: "",
      valor_total: 0,
      numero_parcelas: 1,
      data_inicio: new Date().toISOString().split('T')[0],
      descricao: "",
      categoria: "venda"
    });
    
    // Fechar modal
    setIsOpen(false);
  };

  // Abrir o modal e resetar estado
  const openModal = () => {
    setFormData({
      id_cliente: "",
      valor_total: 0,
      numero_parcelas: 1,
      data_inicio: new Date().toISOString().split('T')[0],
      descricao: "",
      categoria: "venda"
    });
    setFormErrors({});
    setIsOpen(true);
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Vendas & Parcelas</h1>
        <button 
          className="btn-primary" 
          onClick={openModal}
        >
          Nova Venda
        </button>
      </div>
      
      <Modal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        title="Cadastrar Nova Venda"
      >
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="id_cliente">Cliente:</label>
            <select 
              id="id_cliente"
              name="id_cliente"
              value={formData.id_cliente}
              onChange={handleInputChange}
              className={formErrors.id_cliente ? 'input-error' : ''}
            >
              <option value="">Selecione um cliente</option>
              {clientes.map(cliente => (
                <option key={cliente.id_cliente} value={cliente.id_cliente}>
                  {cliente.nome}
                </option>
              ))}
            </select>
            {formErrors.id_cliente && (
              <div className="form-field-error">{formErrors.id_cliente}</div>
            )}
          </div>
          
          <FormField
            label="Valor Total (R$)"
            name="valor_total"
            type="number"
            value={formData.valor_total}
            onChange={handleInputChange}
            error={formErrors.valor_total}
            required
          />
          
          <FormField
            label="Número de Parcelas"
            name="numero_parcelas"
            type="number"
            value={formData.numero_parcelas}
            onChange={handleInputChange}
            error={formErrors.numero_parcelas}
            required
          />
          
          <FormField
            label="Data de Início"
            name="data_inicio"
            type="date"
            value={formData.data_inicio}
            onChange={handleInputChange}
            error={formErrors.data_inicio}
            required
          />
          
          <div className="form-group">
            <label htmlFor="descricao">Descrição:</label>
            <textarea
              id="descricao"
              name="descricao"
              value={formData.descricao}
              onChange={handleInputChange}
              className={formErrors.descricao ? 'input-error' : ''}
              required
            />
            {formErrors.descricao && (
              <div className="form-field-error">{formErrors.descricao}</div>
            )}
          </div>
          
          <div style={{ 
            marginTop: '20px',
            display: 'flex',
            justifyContent: 'flex-end',
            gap: '10px'
          }}>
            <button
              type="button"
              onClick={() => setIsOpen(false)}
              style={{ 
                padding: '8px 16px', 
                backgroundColor: '#6c757d',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Cancelar
            </button>
            <button
              type="submit"
              style={{ 
                padding: '8px 16px', 
                backgroundColor: '#1e293b',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Salvar
            </button>
          </div>
        </form>
      </Modal>
      
      <DataStateHandler
        loading={loading}
        error={error}
        dataLength={vendas.length}
        onRetry={fetchVendas}
        emptyMessage="Nenhuma venda encontrada."
      >
        <Table
          columns={colunas}
          data={vendas}
          emptyMessage="Nenhuma venda encontrada."
        />
      </DataStateHandler>
    </div>
  );
} 