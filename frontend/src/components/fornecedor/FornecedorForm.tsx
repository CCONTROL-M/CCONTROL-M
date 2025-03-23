import React, { useEffect } from 'react';
import { Fornecedor } from '../../types';
import useFormHandler from '../../hooks/useFormHandler';
import FormField from '../FormField';

// Tipo para o formulário de fornecedor (sem id e created_at, gerenciados pelo sistema)
type FornecedorFormData = {
  nome: string;
  cnpj: string;
  contato: string;
};

const fornecedorVazio: FornecedorFormData = {
  nome: '',
  cnpj: '',
  contato: ''
};

interface FornecedorFormProps {
  fornecedor?: Fornecedor;
  onSave: (fornecedor: FornecedorFormData) => void;
  onCancel: () => void;
}

const FornecedorForm: React.FC<FornecedorFormProps> = ({
  fornecedor,
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
  } = useFormHandler<FornecedorFormData>(fornecedorVazio);

  // Validação específica para CNPJ
  const validarCnpj = (value: string) => {
    const apenasNumeros = value.replace(/\D/g, '');
    
    if (apenasNumeros.length === 0) {
      return 'CNPJ é obrigatório';
    }
    
    // CNPJ tem 14 dígitos
    if (apenasNumeros.length !== 14) {
      return 'CNPJ deve ter 14 dígitos';
    }
    
    return undefined;
  };

  // Regras de validação
  const validationRules: Record<keyof FornecedorFormData, any> = {
    nome: {
      required: true,
      minLength: 3
    },
    cnpj: {
      required: true,
      custom: validarCnpj
    },
    contato: {
      required: true
    }
  };

  // Atualizar o formulário quando o fornecedor for carregado ou alterado
  useEffect(() => {
    if (fornecedor) {
      // Extrai apenas os campos relevantes para o formulário
      setFormData({
        nome: fornecedor.nome,
        cnpj: fornecedor.cnpj,
        contato: fornecedor.contato
      });
    } else {
      setFormData(fornecedorVazio);
    }
  }, [fornecedor, setFormData]);

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
    <form onSubmit={handleSubmit} className="fornecedor-form">
      <FormField
        label="Nome"
        name="nome"
        value={formData.nome}
        onChange={handleInputChange}
        error={formErrors.nome}
        required
      />
      
      <FormField
        label="CNPJ"
        name="cnpj"
        value={formData.cnpj}
        onChange={handleInputChange}
        error={formErrors.cnpj}
        required
      />
      
      <FormField
        label="Contato"
        name="contato"
        value={formData.contato}
        onChange={handleInputChange}
        error={formErrors.contato}
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

export default FornecedorForm; 