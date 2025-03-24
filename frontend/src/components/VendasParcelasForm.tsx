import React, { useState, useEffect } from "react";
import { Cliente, NovaVenda } from "../types";
import { formatarData, formatarMoeda } from "../utils/formatters";
import FormField from "./FormField";

interface VendasParcelasFormProps {
  clientes: Cliente[];
  onSubmit: (venda: NovaVenda) => Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
}

/**
 * Componente de formulário para cadastro de vendas com parcelas
 */
const VendasParcelasForm: React.FC<VendasParcelasFormProps> = ({
  clientes,
  onSubmit,
  onCancel,
  isLoading = false
}) => {
  // Estados para o formulário
  const [formData, setFormData] = useState<NovaVenda>({
    id_cliente: "",
    valor_total: 0,
    numero_parcelas: 1,
    data_inicio: new Date().toISOString().split('T')[0],
    descricao: "",
    categoria: "venda"
  });
  
  // Estado para erros do formulário
  const [formErrors, setFormErrors] = useState<{
    id_cliente?: string;
    valor_total?: string;
    numero_parcelas?: string;
    data_inicio?: string;
    descricao?: string;
  }>({});
  
  const [visualizacaoParcelas, setVisualizacaoParcelas] = useState<boolean>(false);
  
  // Reset de formulário
  const resetarFormulario = () => {
    setFormData({
      id_cliente: "",
      valor_total: 0,
      numero_parcelas: 1,
      data_inicio: new Date().toISOString().split('T')[0],
      descricao: "",
      categoria: "venda"
    });
    setFormErrors({});
    setVisualizacaoParcelas(false);
  };
  
  // Handle de mudança nos inputs
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    
    // Atualizando valores de acordo com o tipo de campo
    if (name === "valor_total") {
      setFormData(prev => ({
        ...prev,
        [name]: parseFloat(value) || 0
      }));
    } else if (name === "numero_parcelas") {
      setFormData(prev => ({
        ...prev,
        [name]: Math.max(1, parseInt(value) || 1) // número de parcelas mínimo é 1
      }));
    } else {
      // Strings e outros valores como estão
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
    
    // Limpa o erro do campo quando ele é alterado
    if (formErrors[name as keyof typeof formErrors]) {
      setFormErrors(prev => ({
        ...prev,
        [name]: undefined
      }));
    }
  };
  
  // Validação de formulário
  const validarFormulario = (): boolean => {
    const errors: {
      id_cliente?: string;
      valor_total?: string;
      numero_parcelas?: string;
      data_inicio?: string;
      descricao?: string;
    } = {};
    
    if (!formData.id_cliente) {
      errors.id_cliente = "Selecione um cliente";
    }
    
    if (!formData.valor_total || formData.valor_total <= 0) {
      errors.valor_total = "Informe um valor válido";
    }
    
    if (!formData.numero_parcelas || formData.numero_parcelas < 1) {
      errors.numero_parcelas = "Informe pelo menos 1 parcela";
    } else if (formData.numero_parcelas > 24) { // Limite máximo de parcelas
      errors.numero_parcelas = "Máximo de 24 parcelas permitido";
    }
    
    if (!formData.data_inicio) {
      errors.data_inicio = "Informe a data inicial";
    }
    
    if (!formData.descricao || formData.descricao.trim().length < 3) {
      errors.descricao = "Descrição deve ter pelo menos 3 caracteres";
    }
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };
  
  // Cálculo de parcelas para visualização
  const calcularParcelas = (): { valor: number, data: string }[] => {
    if (!formData.valor_total || !formData.numero_parcelas || !formData.data_inicio) {
      return [];
    }
    
    const valorParcela = formData.valor_total / formData.numero_parcelas;
    const parcelas = [];
    const dataInicio = new Date(formData.data_inicio);
    
    for (let i = 0; i < formData.numero_parcelas; i++) {
      const dataParcela = new Date(dataInicio);
      dataParcela.setMonth(dataInicio.getMonth() + i);
      
      parcelas.push({
        valor: valorParcela,
        data: dataParcela.toISOString().split('T')[0]
      });
    }
    
    return parcelas;
  };
  
  // Handle de submit do formulário
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validarFormulario()) {
      return;
    }
    
    try {
      await onSubmit(formData);
      resetarFormulario();
    } catch (error) {
      console.error("Erro ao processar formulário:", error);
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <div className="form-grid">
        <div className="form-group">
          <label htmlFor="id_cliente">Cliente:</label>
          <select 
            id="id_cliente"
            name="id_cliente"
            value={formData.id_cliente}
            onChange={handleInputChange}
            className={formErrors.id_cliente ? 'input-error' : ''}
            disabled={isLoading}
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
          disabled={isLoading}
          required
        />
        
        <FormField
          label="Número de Parcelas"
          name="numero_parcelas"
          type="number"
          value={formData.numero_parcelas}
          onChange={handleInputChange}
          error={formErrors.numero_parcelas}
          disabled={isLoading}
          min={1}
          required
        />
        
        <FormField
          label="Data Inicial"
          name="data_inicio"
          type="date"
          value={formData.data_inicio}
          onChange={handleInputChange}
          error={formErrors.data_inicio}
          disabled={isLoading}
          required
        />
        
        <div className="form-group col-span-2">
          <label htmlFor="descricao">Descrição:</label>
          <textarea
            id="descricao"
            name="descricao"
            value={formData.descricao}
            onChange={handleInputChange}
            className={formErrors.descricao ? 'input-error' : ''}
            disabled={isLoading}
            rows={3}
            required
          />
          {formErrors.descricao && (
            <div className="form-field-error">{formErrors.descricao}</div>
          )}
        </div>
      </div>

      <div className="mb-4 mt-4">
        <button
          type="button"
          className="text-blue-600 hover:text-blue-800 text-sm flex items-center"
          onClick={() => setVisualizacaoParcelas(!visualizacaoParcelas)}
          disabled={isLoading}
        >
          {visualizacaoParcelas ? '❌ Ocultar Simulação' : '📊 Visualizar Simulação de Parcelas'}
        </button>
      </div>
      
      {visualizacaoParcelas && (
        <div className="bg-gray-50 p-4 rounded-lg mb-6">
          <h3 className="text-md font-semibold mb-3">Simulação de Parcelas</h3>
          <div className="overflow-auto max-h-40">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-100">
                  <th className="p-2 text-left">#</th>
                  <th className="p-2 text-left">Valor</th>
                  <th className="p-2 text-left">Vencimento</th>
                </tr>
              </thead>
              <tbody>
                {calcularParcelas().map((parcela, index) => (
                  <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className="p-2">{index + 1}</td>
                    <td className="p-2">{formatarMoeda(parcela.valor)}</td>
                    <td className="p-2">{formatarData(parcela.data)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
      
      <div className="form-actions">
        <button 
          type="button" 
          onClick={onCancel}
          className="btn-outline"
          disabled={isLoading}
        >
          Cancelar
        </button>
        <button 
          type="submit" 
          className="btn-primary"
          disabled={isLoading}
        >
          {isLoading ? 'Processando...' : 'Cadastrar Venda'}
        </button>
      </div>
    </form>
  );
};

export default VendasParcelasForm; 