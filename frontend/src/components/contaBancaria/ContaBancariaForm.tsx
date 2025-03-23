import React, { useEffect } from 'react';
import { ContaBancaria } from '../../types';
import useFormHandler from '../../hooks/useFormHandler';
import FormField from '../FormField';

// Tipo para o formulário de conta bancária (sem id e created_at, gerenciados pelo sistema)
type ContaBancariaFormData = {
  nome: string;
  banco: string;
  agencia: string;
  numero: string;
  tipo: string;
  saldo_inicial: number;
};

const contaBancariaVazia: ContaBancariaFormData = {
  nome: '',
  banco: '',
  agencia: '',
  numero: '',
  tipo: 'Conta Corrente',
  saldo_inicial: 0,
};

interface ContaBancariaFormProps {
  contaBancaria?: ContaBancaria;
  onSave: (contaBancaria: ContaBancariaFormData) => void;
  onCancel: () => void;
}

const ContaBancariaForm: React.FC<ContaBancariaFormProps> = ({
  contaBancaria,
  onSave,
  onCancel
}) => {
  // Usar o hook de gerenciamento de formulário
  const { 
    formData, 
    formErrors, 
    setFormData, 
    handleInputChange, 
    validate
  } = useFormHandler<ContaBancariaFormData>(contaBancariaVazia);

  // Regras de validação
  const validationRules: Record<keyof ContaBancariaFormData, any> = {
    nome: {
      required: true,
      minLength: 3
    },
    banco: {
      required: true
    },
    agencia: {
      required: true
    },
    numero: {
      required: true
    },
    tipo: {
      required: true
    },
    saldo_inicial: {
      required: true
    }
  };

  // Atualizar o formulário quando a conta bancária for carregada ou alterada
  useEffect(() => {
    if (contaBancaria) {
      // Extrai apenas os campos relevantes para o formulário
      setFormData({
        nome: contaBancaria.nome,
        banco: contaBancaria.banco,
        agencia: contaBancaria.agencia,
        numero: contaBancaria.numero,
        tipo: contaBancaria.tipo,
        saldo_inicial: contaBancaria.saldo_inicial
      });
    } else {
      setFormData(contaBancariaVazia);
    }
  }, [contaBancaria, setFormData]);

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
    <form onSubmit={handleSubmit} className="conta-bancaria-form">
      <FormField
        label="Nome da Conta"
        name="nome"
        value={formData.nome}
        onChange={handleInputChange}
        error={formErrors.nome}
        required
      />
      
      <FormField
        label="Banco"
        name="banco"
        value={formData.banco}
        onChange={handleInputChange}
        error={formErrors.banco}
        required
      />
      
      <FormField
        label="Agência"
        name="agencia"
        value={formData.agencia}
        onChange={handleInputChange}
        error={formErrors.agencia}
        required
      />
      
      <FormField
        label="Número da Conta"
        name="numero"
        value={formData.numero}
        onChange={handleInputChange}
        error={formErrors.numero}
        required
      />
      
      <div className="form-field">
        <label htmlFor="tipo">Tipo da Conta<span className="required">*</span></label>
        <select
          id="tipo"
          name="tipo"
          value={formData.tipo}
          onChange={handleInputChange}
          className={formErrors.tipo ? 'input-error' : ''}
        >
          <option value="Conta Corrente">Conta Corrente</option>
          <option value="Conta Poupança">Conta Poupança</option>
          <option value="Conta Salário">Conta Salário</option>
          <option value="Conta Digital">Conta Digital</option>
          <option value="Carteira Digital">Carteira Digital</option>
          <option value="Outro">Outro</option>
        </select>
        {formErrors.tipo && <div className="form-field-error">{formErrors.tipo}</div>}
      </div>
      
      <FormField
        label="Saldo Inicial (R$)"
        name="saldo_inicial"
        type="number"
        value={formData.saldo_inicial}
        onChange={handleInputChange}
        error={formErrors.saldo_inicial}
        required
      />
      
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
        >
          Salvar
        </button>
      </div>
    </form>
  );
};

export default ContaBancariaForm; 