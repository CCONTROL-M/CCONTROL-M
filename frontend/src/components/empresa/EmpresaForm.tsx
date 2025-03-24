import React, { useEffect, ChangeEvent } from 'react';
import FormField from '../FormField';
import { Empresa } from '../../types';
import { EmpresaCompleta } from '../../services/empresaService';
import useFormHandler from '../../hooks/useFormHandler';

// Interface para o formulário de Empresa
export interface EmpresaFormData {
  nome: string;
  razao_social: string;
  nome_fantasia: string;
  cnpj: string;
  contato: string;
  cidade: string;
  estado: string;
  ativo: boolean;
}

// Interface para as props do componente
export interface EmpresaFormProps {
  empresa?: EmpresaCompleta | null;
  onSave: (data: EmpresaFormData) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

// Valor inicial do formulário
const empresaVazia: EmpresaFormData = {
  nome: '',
  razao_social: '',
  nome_fantasia: '',
  cnpj: '',
  contato: '',
  cidade: '',
  estado: '',
  ativo: true
};

/**
 * Componente de formulário para criar/editar empresas
 */
const EmpresaForm: React.FC<EmpresaFormProps> = ({
  empresa,
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
  } = useFormHandler<EmpresaFormData>(empresaVazia);

  // Função para manipular checkbox manualmente já que useFormHandler não tem handleCheckboxChange
  const handleCheckboxChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: checked
    }));
  };

  // Regras de validação
  const validationRules: Record<keyof EmpresaFormData, any> = {
    nome: { required: true },
    razao_social: { required: true },
    cnpj: { required: true, pattern: /^\d{2}\.\d{3}\.\d{3}\/\d{4}\-\d{2}$/ },
    contato: { required: true },
    nome_fantasia: {},
    cidade: {},
    estado: {},
    ativo: {}
  };

  // Atualizar o formulário quando a empresa for carregada ou alterada
  useEffect(() => {
    if (empresa) {
      // Extrai apenas os campos relevantes para o formulário
      setFormData({
        nome: empresa.nome || '',
        razao_social: empresa.razao_social || '',
        nome_fantasia: empresa.nome_fantasia || '',
        cnpj: empresa.cnpj || '',
        contato: empresa.contato || '',
        cidade: empresa.cidade || '',
        estado: empresa.estado || '',
        ativo: empresa.ativo
      });
    } else {
      setFormData(empresaVazia);
    }
  }, [empresa, setFormData]);

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
      <div className="form-row">
        <FormField
          label="Razão Social"
          name="razao_social"
          value={formData.razao_social}
          onChange={handleInputChange}
          error={formErrors.razao_social}
          required
        />
        <FormField
          label="Nome Fantasia"
          name="nome_fantasia"
          value={formData.nome_fantasia}
          onChange={handleInputChange}
          error={formErrors.nome_fantasia}
        />
      </div>
      
      <div className="form-row">
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
          placeholder="00.000.000/0000-00"
          required
        />
      </div>
      
      <div className="form-row">
        <FormField
          label="Contato"
          name="contato"
          value={formData.contato}
          onChange={handleInputChange}
          error={formErrors.contato}
          placeholder="Email ou telefone"
          required
        />
      </div>
      
      <div className="form-row">
        <FormField
          label="Cidade"
          name="cidade"
          value={formData.cidade}
          onChange={handleInputChange}
          error={formErrors.cidade}
        />
        <FormField
          label="Estado"
          name="estado"
          value={formData.estado}
          onChange={handleInputChange}
          error={formErrors.estado}
        />
      </div>
      
      <div className="form-row">
        <div className="form-field">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              name="ativo"
              checked={formData.ativo}
              onChange={handleCheckboxChange}
              className="form-checkbox"
            />
            <span>Empresa Ativa</span>
          </label>
        </div>
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

export default EmpresaForm; 