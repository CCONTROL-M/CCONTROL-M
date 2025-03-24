import React, { useEffect, useMemo } from 'react';
import FormField from '../FormField';
import { Cliente, NovaVenda } from '../../types';
import useFormHandler from '../../hooks/useFormHandler';

// Interface para o formulário de Venda
export interface VendaFormData {
  id_cliente: string;
  valor_total: number;
  numero_parcelas: number;
  data_inicio: string;
  descricao: string;
  categoria: string;
}

// Interface para as props do componente
export interface VendaFormProps {
  clientes: Cliente[];
  onSave: (data: VendaFormData) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

// Valor inicial do formulário
const vendaVazia: VendaFormData = {
  id_cliente: '',
  valor_total: 0,
  numero_parcelas: 1,
  data_inicio: new Date().toISOString().split('T')[0],
  descricao: '',
  categoria: 'venda'
};

/**
 * Componente de formulário para criar/editar vendas com parcelas
 */
const VendaForm: React.FC<VendaFormProps> = ({
  clientes,
  onSave,
  onCancel,
  isLoading = false
}) => {
  // Usar o hook de gerenciamento de formulário
  const { 
    formData, 
    formErrors, 
    setFormData, 
    handleInputChange, 
    validate
  } = useFormHandler<VendaFormData>(vendaVazia);

  // Regras de validação
  const validationRules: Record<keyof VendaFormData, any> = {
    id_cliente: {
      required: true
    },
    valor_total: {
      required: true,
      custom: (value: number) => {
        if (value <= 0) {
          return 'O valor total deve ser maior que zero';
        }
        return undefined;
      }
    },
    numero_parcelas: {
      required: true,
      custom: (value: number) => {
        if (value < 1) {
          return 'O número de parcelas deve ser pelo menos 1';
        }
        return undefined;
      }
    },
    data_inicio: {
      required: true
    },
    descricao: {
      required: true
    },
    categoria: {}
  };

  // Calcular parcelas para preview
  const parcelasPreview = useMemo(() => {
    if (formData.valor_total <= 0 || formData.numero_parcelas <= 0) {
      return [];
    }
    
    const valorParcela = formData.valor_total / formData.numero_parcelas;
    const parcelas = [];
    
    // Data base de início
    let dataBase = new Date(formData.data_inicio);
    
    for (let i = 0; i < formData.numero_parcelas; i++) {
      // Clonar a data para não modificar a original
      const dataVencimento = new Date(dataBase);
      
      // Adicionar 1 mês para cada parcela após a primeira
      if (i > 0) {
        dataVencimento.setMonth(dataVencimento.getMonth() + i);
      }
      
      parcelas.push({
        valor: valorParcela,
        data: dataVencimento.toISOString().split('T')[0]
      });
    }
    
    return parcelas;
  }, [formData.valor_total, formData.numero_parcelas, formData.data_inicio]);

  // Formatador de moeda
  const formatarMoeda = (valor: number) => {
    return valor.toLocaleString('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    });
  };

  // Formatador de data
  const formatarData = (data: string) => {
    const dataObj = new Date(data);
    return dataObj.toLocaleDateString('pt-BR');
  };

  // Manipulador de envio do formulário
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validar todos os campos
    const isValid = validate(validationRules);
    
    if (isValid) {
      onSave(formData);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="form-container py-0">
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
          label="Data de Início"
          name="data_inicio"
          type="date"
          value={formData.data_inicio}
          onChange={handleInputChange}
          error={formErrors.data_inicio}
          disabled={isLoading}
          required
        />
        
        <FormField
          label="Descrição"
          name="descricao"
          value={formData.descricao}
          onChange={handleInputChange}
          error={formErrors.descricao}
          disabled={isLoading}
          required
        />
      </div>
      
      {/* Preview das parcelas */}
      {parcelasPreview.length > 0 && (
        <div className="parcelas-preview mt-4">
          <h3 className="text-lg font-semibold mb-2">Previsão de Parcelas</h3>
          <div className="overflow-auto max-h-40">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-100">
                  <th className="p-2 text-left">Parcela</th>
                  <th className="p-2 text-left">Valor</th>
                  <th className="p-2 text-left">Vencimento</th>
                </tr>
              </thead>
              <tbody>
                {parcelasPreview.map((parcela, index) => (
                  <tr key={index} className="border-b border-gray-200">
                    <td className="p-2">{index + 1}/{parcelasPreview.length}</td>
                    <td className="p-2">{formatarMoeda(parcela.valor)}</td>
                    <td className="p-2">{formatarData(parcela.data)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
      
      <div className="form-actions mt-4">
        <button
          type="button"
          className="btn-secondary"
          onClick={onCancel}
        >
          Cancelar
        </button>
        <button
          type="submit"
          className="btn-primary"
          disabled={isLoading}
        >
          {isLoading ? 'Salvando...' : 'Salvar'}
        </button>
      </div>
    </form>
  );
};

export default VendaForm; 