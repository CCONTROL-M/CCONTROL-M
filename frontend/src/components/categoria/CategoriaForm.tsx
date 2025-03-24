import React, { useEffect } from 'react';
import FormField from '../FormField';
import { Categoria } from '../../types';
import useFormHandler from '../../hooks/useFormHandler';

// Interface para o formulário de Categoria
export interface CategoriaFormData {
  nome: string;
  tipo: string;
}

// Interface para as props do componente
export interface CategoriaFormProps {
  categoria?: Categoria | null;
  onSave: (data: CategoriaFormData) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

// Valor inicial do formulário
const categoriaVazia: CategoriaFormData = {
  nome: '',
  tipo: 'despesa'
};

/**
 * Componente de formulário para criar/editar categorias
 */
const CategoriaForm: React.FC<CategoriaFormProps> = ({
  categoria,
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
  } = useFormHandler<CategoriaFormData>(categoriaVazia);

  // Regras de validação
  const validationRules: Record<keyof CategoriaFormData, any> = {
    nome: { 
      required: true,
      minLength: 3
    },
    tipo: { 
      required: true 
    }
  };

  // Atualizar o formulário quando a categoria for carregada ou alterada
  useEffect(() => {
    if (categoria) {
      // Extrai apenas os campos relevantes para o formulário
      setFormData({
        nome: categoria.nome,
        tipo: categoria.tipo
      });
    } else {
      setFormData(categoriaVazia);
    }
  }, [categoria, setFormData]);

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
      <div className="form-group">
        <label htmlFor="nome">Nome</label>
        <input
          type="text"
          id="nome"
          name="nome"
          value={formData.nome}
          onChange={handleInputChange}
          placeholder="Digite o nome da categoria"
          className={formErrors.nome ? 'input-error' : ''}
          required
        />
        {formErrors.nome && (
          <div className="form-field-error">{formErrors.nome}</div>
        )}
      </div>
      
      <div className="form-group">
        <label htmlFor="tipo">Tipo</label>
        <select
          id="tipo"
          name="tipo"
          value={formData.tipo}
          onChange={handleInputChange}
          className={formErrors.tipo ? 'input-error' : ''}
          required
        >
          <option value="despesa">Despesa</option>
          <option value="receita">Receita</option>
        </select>
        {formErrors.tipo && (
          <div className="form-field-error">{formErrors.tipo}</div>
        )}
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

export default CategoriaForm; 