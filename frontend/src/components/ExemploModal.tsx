import React, { useState } from 'react';
import Modal from './Modal';
import FormField from './FormField';
import useFormHandler from '../hooks/useFormHandler';

// Definir a interface do formulário
interface FormularioExemplo {
  nome: string;
  email: string;
}

const ExemploModal: React.FC = () => {
  const [isOpen, setIsOpen] = useState<boolean>(false);
  
  // Valores iniciais do formulário
  const formularioVazio: FormularioExemplo = {
    nome: '',
    email: ''
  };
  
  // Usar o hook useFormHandler para gerenciar o formulário
  const { 
    formData, 
    formErrors, 
    handleInputChange, 
    validate,
    resetForm
  } = useFormHandler<FormularioExemplo>(formularioVazio);

  // Regras de validação
  const validationRules: Record<keyof FormularioExemplo, any> = {
    nome: {
      required: true,
      minLength: 3,
    },
    email: {
      required: true,
      pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
      custom: (value: string) => {
        // Validação adicional personalizada se necessário
        return undefined;
      }
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validar todos os campos
    const isValid = validate(validationRules);
    
    if (isValid) {
      // Simulação de envio bem-sucedido
      alert(`Formulário enviado com sucesso!\nNome: ${formData.nome}\nE-mail: ${formData.email}`);
      setIsOpen(false);
      resetForm(); // Resetar o formulário ao fechar
    }
  };

  // Função para abrir o modal e resetar o formulário
  const abrirModal = () => {
    resetForm();
    setIsOpen(true);
  };

  // Função para fechar o modal
  const fecharModal = () => {
    setIsOpen(false);
  };

  return (
    <div>
      <button 
        onClick={abrirModal}
        style={{ 
          padding: '8px 16px', 
          backgroundColor: '#1e293b',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer'
        }}
      >
        Abrir Modal de Exemplo
      </button>
      
      <Modal
        isOpen={isOpen}
        onClose={fecharModal}
        title="Exemplo de Formulário"
      >
        <form onSubmit={handleSubmit}>
          <FormField
            label="Nome"
            name="nome"
            value={formData.nome}
            onChange={handleInputChange}
            error={formErrors.nome}
            required
          />
          
          <FormField
            label="E-mail"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleInputChange}
            error={formErrors.email}
            placeholder="exemplo@email.com"
            required
          />
          
          <div style={{ 
            marginTop: '20px',
            display: 'flex',
            justifyContent: 'flex-end',
            gap: '10px'
          }}>
            <button
              type="button"
              onClick={fecharModal}
              style={{ 
                padding: '8px 16px', 
                backgroundColor: '#6c757d',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Cancelar
            </button>
            <button
              type="submit"
              style={{ 
                padding: '8px 16px', 
                backgroundColor: '#1e293b',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Enviar
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default ExemploModal; 