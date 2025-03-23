import React, { useEffect } from 'react';
import { Cliente } from '../../types';
import useFormHandler from '../../hooks/useFormHandler';
import FormField from '../FormField';

// Tipo para o formulário de cliente (sem id e created_at, gerenciados pelo sistema)
type ClienteFormData = {
  nome: string;
  cpf_cnpj: string;
  contato: string;
};

const clienteVazio: ClienteFormData = {
  nome: '',
  cpf_cnpj: '',
  contato: ''
};

interface ClienteFormProps {
  cliente?: Cliente;
  onSave: (cliente: ClienteFormData) => void;
  onCancel: () => void;
}

const ClienteForm: React.FC<ClienteFormProps> = ({
  cliente,
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
  } = useFormHandler<ClienteFormData>(clienteVazio);

  // Validação específica para CPF/CNPJ
  const validarCpfCnpj = (value: string) => {
    const apenasNumeros = value.replace(/\D/g, '');
    
    if (apenasNumeros.length === 0) {
      return 'CPF/CNPJ é obrigatório';
    }
    
    // CPF tem 11 dígitos, CNPJ tem 14
    if (apenasNumeros.length !== 11 && apenasNumeros.length !== 14) {
      return 'CPF deve ter 11 dígitos ou CNPJ deve ter 14 dígitos';
    }
    
    return undefined;
  };

  // Regras de validação
  const validationRules: Record<keyof ClienteFormData, any> = {
    nome: {
      required: true,
      minLength: 3
    },
    cpf_cnpj: {
      required: true,
      custom: validarCpfCnpj
    },
    contato: {
      required: true
    }
  };

  // Atualizar o formulário quando o cliente for carregado ou alterado
  useEffect(() => {
    if (cliente) {
      // Extrai apenas os campos relevantes para o formulário
      setFormData({
        nome: cliente.nome,
        cpf_cnpj: cliente.cpf_cnpj,
        contato: cliente.contato
      });
    } else {
      setFormData(clienteVazio);
    }
  }, [cliente, setFormData]);

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
    <form onSubmit={handleSubmit} className="cliente-form">
      <FormField
        label="Nome"
        name="nome"
        value={formData.nome}
        onChange={handleInputChange}
        error={formErrors.nome}
        required
      />
      
      <FormField
        label="CPF/CNPJ"
        name="cpf_cnpj"
        value={formData.cpf_cnpj}
        onChange={handleInputChange}
        error={formErrors.cpf_cnpj}
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

export default ClienteForm; 