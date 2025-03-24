import React, { useEffect } from 'react';
import { ContaBancaria } from '../../types';
import useFormHandler from '../../hooks/useFormHandler';
import FormField from '../FormField';

// Tipo para o formulário de conta bancária (sem id e created_at, gerenciados pelo sistema)
type ContaBancariaFormData = {
  nome: string;
  banco: string;
  agencia: string;
  conta: string;
  tipo: string;
  saldo_inicial: number;
  ativa: boolean;
  mostrar_dashboard: boolean;
};

const contaVazia: ContaBancariaFormData = {
  nome: '',
  banco: '',
  agencia: '',
  conta: '',
  tipo: 'corrente',
  saldo_inicial: 0,
  ativa: true,
  mostrar_dashboard: true
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
  } = useFormHandler<ContaBancariaFormData>(contaVazia);
  
  // Validação específica para valores monetários
  const validarValor = (value: number) => {
    if (isNaN(value)) {
      return 'Digite um valor numérico válido';
    }
    return undefined;
  };

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
    conta: {
      required: true
    },
    tipo: {
      required: true
    },
    saldo_inicial: {
      required: true,
      custom: validarValor
    },
    ativa: {
      required: false
    },
    mostrar_dashboard: {
      required: false
    }
  };

  // Atualizar o formulário quando a conta for carregada ou alterada
  useEffect(() => {
    if (contaBancaria) {
      // Extrai apenas os campos relevantes para o formulário
      setFormData({
        nome: contaBancaria.nome,
        banco: contaBancaria.banco,
        agencia: contaBancaria.agencia,
        conta: contaBancaria.conta,
        tipo: contaBancaria.tipo,
        saldo_inicial: contaBancaria.saldo_inicial,
        ativa: contaBancaria.ativa,
        mostrar_dashboard: contaBancaria.mostrar_dashboard || true
      });
    } else {
      setFormData(contaVazia);
    }
  }, [contaBancaria, setFormData]);

  // Função para formatar valores monetários para exibição
  const formatarMoeda = (valor: number): string => {
    return valor.toLocaleString('pt-BR', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  };

  // Função para converter valor monetário de string para número
  const parseMoeda = (valorString: string): number => {
    // Remove caracteres não numéricos (exceto ponto e vírgula)
    const valorLimpo = valorString.replace(/[^\d,-]/g, '').replace(',', '.');
    return parseFloat(valorLimpo) || 0;
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

  // Manipulador de mudança para campos numéricos
  const handleValorChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    const valorNumerico = parseMoeda(value);
    
    setFormData(prev => ({
      ...prev,
      [name]: valorNumerico
    }));
  };

  // Manipulador para campos checkbox
  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = e.target;
    
    setFormData(prev => ({
      ...prev,
      [name]: checked
    }));
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
      
      <div className="form-row">
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
          name="conta"
          value={formData.conta}
          onChange={handleInputChange}
          error={formErrors.conta}
          required
        />
      </div>
      
      <div className="form-row">
        <div className="form-field">
          <label htmlFor="tipo">Tipo de Conta</label>
          <select
            id="tipo"
            name="tipo"
            value={formData.tipo}
            onChange={handleInputChange}
            className={formErrors.tipo ? "error-input" : ""}
          >
            <option value="corrente">Conta Corrente</option>
            <option value="poupança">Conta Poupança</option>
          </select>
          {formErrors.tipo && <div className="error">{formErrors.tipo}</div>}
        </div>
        
        <FormField
          label="Saldo Inicial (R$)"
          name="saldo_inicial"
          value={formatarMoeda(formData.saldo_inicial)}
          onChange={handleValorChange}
          error={formErrors.saldo_inicial}
          type="text"
          required
        />
      </div>
      
      <div className="form-row">
        <div className="form-field checkbox-field">
          <label>
            <input
              type="checkbox"
              name="ativa"
              checked={formData.ativa}
              onChange={handleCheckboxChange}
            />
            Conta Ativa
          </label>
        </div>
        
        <div className="form-field checkbox-field">
          <label>
            <input
              type="checkbox"
              name="mostrar_dashboard"
              checked={formData.mostrar_dashboard}
              onChange={handleCheckboxChange}
            />
            Mostrar no Dashboard
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
        >
          Salvar
        </button>
      </div>
    </form>
  );
};

export default ContaBancariaForm; 