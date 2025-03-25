import React, { useEffect } from 'react';
import FormField from '../FormField';
import Form from '../Form';
import ButtonGroup from '../ButtonGroup';
import Button from '../Button';
import { FormaPagamento } from '../../types';
import useFormHandler from '../../hooks/useFormHandler';

// Interface para o formulário de Forma de Pagamento
export interface FormaPagamentoFormData {
  tipo: string;
  taxas: string;
  prazo: string;
}

// Interface para as props do componente
export interface FormaPagamentoFormProps {
  formaPagamento?: FormaPagamento | null;
  onSave: (data: FormaPagamentoFormData) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

// Valor inicial do formulário
const formaPagamentoVazia: FormaPagamentoFormData = {
  tipo: '',
  taxas: '',
  prazo: ''
};

/**
 * Componente de formulário para criar/editar formas de pagamento
 */
const FormaPagamentoForm: React.FC<FormaPagamentoFormProps> = ({
  formaPagamento,
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
  } = useFormHandler<FormaPagamentoFormData>(formaPagamentoVazia);

  // Regras de validação
  const validationRules: Record<keyof FormaPagamentoFormData, any> = {
    tipo: { 
      required: true,
      minLength: 3
    },
    taxas: { 
      required: true 
    },
    prazo: { 
      required: true 
    }
  };

  // Atualizar o formulário quando a forma de pagamento for carregada ou alterada
  useEffect(() => {
    if (formaPagamento) {
      // Extrai apenas os campos relevantes para o formulário
      setFormData({
        tipo: formaPagamento.tipo,
        taxas: formaPagamento.taxas,
        prazo: formaPagamento.prazo
      });
    } else {
      setFormData(formaPagamentoVazia);
    }
  }, [formaPagamento, setFormData]);

  // Manipulador de envio do formulário
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validar todos os campos
    const isValid = validate(validationRules);
    
    if (isValid) {
      onSave(formData);
    }
  };

  const actions = (
    <ButtonGroup orientation="responsive" alignment="end" spacing="md">
      <Button 
        variant="secondary" 
        type="button"
        onClick={onCancel}
      >
        Cancelar
      </Button>
      <Button
        variant="primary"
        type="submit"
        loading={isLoading}
      >
        {isLoading ? 'Salvando...' : 'Salvar'}
      </Button>
    </ButtonGroup>
  );

  return (
    <Form 
      onSubmit={handleSubmit} 
      layout="column" 
      gap="md" 
      actions={actions}
      actionPosition="end"
    >
      <FormField
        label="Tipo"
        name="tipo"
        value={formData.tipo}
        onChange={handleInputChange}
        error={formErrors.tipo}
        placeholder="Ex: Cartão, Boleto, Pix"
        required
        width="full"
      />
      
      <div className="form-row gap-md">
        <FormField
          label="Taxa"
          name="taxas"
          value={formData.taxas}
          onChange={handleInputChange}
          error={formErrors.taxas}
          placeholder="Ex: 2.5%, Isento"
          required
          width="half"
        />
        
        <FormField
          label="Prazo (dias)"
          name="prazo"
          value={formData.prazo}
          onChange={handleInputChange}
          error={formErrors.prazo}
          placeholder="Ex: 30 dias, À vista"
          required
          width="half"
        />
      </div>
    </Form>
  );
};

export default FormaPagamentoForm; 