import React, { useEffect } from 'react';
import FormField from '../FormField';
import { Lancamento, Categoria, ContaBancaria } from '../../types';
import useFormHandler from '../../hooks/useFormHandler';

// Interface para o formulário de Lançamento
export interface LancamentoFormData {
  data: string;
  valor: number;
  status: string;
  id_categoria: string;
  id_conta_bancaria: string;
  observacao: string;
}

// Interface para as props do componente
export interface LancamentoFormProps {
  lancamento?: Lancamento | null;
  categorias: Categoria[];
  contasBancarias: ContaBancaria[];
  onSave: (data: LancamentoFormData) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

// Valor inicial do formulário
const lancamentoVazio: LancamentoFormData = {
  data: new Date().toISOString().split('T')[0],
  valor: 0,
  status: 'Pendente',
  id_categoria: '',
  id_conta_bancaria: '',
  observacao: ''
};

// Função auxiliar para garantir que o valor seja sempre um número
const garantirNumero = (valor: any): number => {
  if (typeof valor === 'number') return valor;
  if (typeof valor === 'string') {
    const valorConvertido = parseFloat(valor);
    return isNaN(valorConvertido) ? 0 : valorConvertido;
  }
  return 0;
};

/**
 * Componente de formulário para criar/editar lançamentos financeiros
 */
const LancamentoForm: React.FC<LancamentoFormProps> = ({
  lancamento,
  categorias,
  contasBancarias,
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
  } = useFormHandler<LancamentoFormData>(lancamentoVazio);

  // Regras de validação
  const validationRules: Record<keyof LancamentoFormData, any> = {
    data: { 
      required: true
    },
    valor: { 
      required: true,
      custom: (value: number) => {
        if (value <= 0) {
          return 'O valor deve ser maior que zero';
        }
        return undefined;
      } 
    },
    status: { 
      required: true 
    },
    id_categoria: { 
      required: true 
    },
    id_conta_bancaria: {},
    observacao: {}
  };

  // Atualizar o formulário quando o lançamento for carregado ou alterado
  useEffect(() => {
    if (lancamento) {
      // Extrai apenas os campos relevantes para o formulário
      setFormData({
        data: lancamento.data,
        valor: garantirNumero(lancamento.valor), // Usar a função auxiliar
        status: lancamento.status,
        id_categoria: lancamento.id_categoria || '',
        id_conta_bancaria: lancamento.id_conta_bancaria || '',
        observacao: lancamento.observacao || ''
      });
    } else {
      setFormData(lancamentoVazio);
    }
  }, [lancamento, setFormData]);

  // Manipulador de envio do formulário
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validar todos os campos
    const isValid = validate(validationRules);
    
    if (isValid) {
      // Garantir que o valor é um número antes de enviar
      const dadosFormulario = {
        ...formData,
        valor: garantirNumero(formData.valor)
      };
      
      onSave(dadosFormulario);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="form-container py-0">
      <div className="form-row">
        <FormField
          label="Data"
          name="data"
          type="date"
          value={formData.data}
          onChange={handleInputChange}
          error={formErrors.data}
          required
        />
        <FormField
          label="Valor"
          name="valor"
          type="number"
          value={formData.valor}
          onChange={handleInputChange}
          error={formErrors.valor}
          step="0.01"
          min="0"
          required
        />
      </div>

      <div className="form-row">
        <div className="form-field">
          <label htmlFor="id_categoria">Categoria</label>
          <select
            id="id_categoria"
            name="id_categoria"
            value={formData.id_categoria}
            onChange={handleInputChange}
            className={formErrors.id_categoria ? 'input-error' : ''}
            required
          >
            <option value="">Selecione uma categoria</option>
            {categorias.map(categoria => (
              <option key={categoria.id_categoria} value={categoria.id_categoria}>
                {categoria.nome} ({categoria.tipo})
              </option>
            ))}
          </select>
          {formErrors.id_categoria && (
            <div className="form-field-error">{formErrors.id_categoria}</div>
          )}
        </div>

        <div className="form-field">
          <label htmlFor="id_conta_bancaria">Conta Bancária</label>
          <select
            id="id_conta_bancaria"
            name="id_conta_bancaria"
            value={formData.id_conta_bancaria}
            onChange={handleInputChange}
            className={formErrors.id_conta_bancaria ? 'input-error' : ''}
          >
            <option value="">Selecione uma conta bancária</option>
            {contasBancarias.map(conta => (
              <option key={conta.id_conta} value={conta.id_conta}>
                {conta.nome} - {conta.banco}
              </option>
            ))}
          </select>
          {formErrors.id_conta_bancaria && (
            <div className="form-field-error">{formErrors.id_conta_bancaria}</div>
          )}
        </div>
      </div>

      <div className="form-row">
        <div className="form-field">
          <label htmlFor="status">Status</label>
          <select
            id="status"
            name="status"
            value={formData.status}
            onChange={handleInputChange}
            className={formErrors.status ? 'input-error' : ''}
            required
          >
            <option value="Pendente">Pendente</option>
            <option value="Pago">Pago</option>
            <option value="Recebido">Recebido</option>
            <option value="Agendado">Agendado</option>
            <option value="Cancelado">Cancelado</option>
          </select>
          {formErrors.status && (
            <div className="form-field-error">{formErrors.status}</div>
          )}
        </div>
      </div>

      <div className="form-row">
        <FormField
          label="Observação"
          name="observacao"
          type="textarea"
          value={formData.observacao}
          onChange={handleInputChange}
          error={formErrors.observacao}
          placeholder="Adicione uma observação (opcional)"
        />
      </div>
      
      <div className="form-actions">
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

export default LancamentoForm; 