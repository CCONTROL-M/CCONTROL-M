import React, { useState } from 'react';
import Modal from './Modal';
import FormField from './FormField';

const ExemploModal: React.FC = () => {
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [formData, setFormData] = useState({
    nome: '',
    email: '',
  });
  const [errors, setErrors] = useState<{
    nome?: string;
    email?: string;
  }>({});

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });

    // Limpar erro do campo quando o usuário digitar
    if (errors[name as keyof typeof errors]) {
      setErrors({
        ...errors,
        [name]: undefined,
      });
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validação simples
    const newErrors: {
      nome?: string;
      email?: string;
    } = {};
    
    if (!formData.nome.trim()) {
      newErrors.nome = 'Nome é obrigatório';
    }
    
    if (!formData.email.trim()) {
      newErrors.email = 'E-mail é obrigatório';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'E-mail inválido';
    }
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    
    // Simulação de envio bem-sucedido
    alert(`Formulário enviado com sucesso!\nNome: ${formData.nome}\nE-mail: ${formData.email}`);
    setIsOpen(false);
    setFormData({ nome: '', email: '' });
  };

  return (
    <div>
      <button 
        onClick={() => setIsOpen(true)}
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
        onClose={() => setIsOpen(false)}
        title="Exemplo de Formulário"
      >
        <form onSubmit={handleSubmit}>
          <FormField
            label="Nome"
            name="nome"
            value={formData.nome}
            onChange={handleChange}
            error={errors.nome}
            required
          />
          
          <FormField
            label="E-mail"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            error={errors.email}
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
              onClick={() => setIsOpen(false)}
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