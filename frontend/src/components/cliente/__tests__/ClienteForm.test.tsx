import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ClienteForm from '../ClienteForm';
import { Cliente } from '../../../types';

describe('ClienteForm', () => {
  // Cliente para teste de edição
  const clienteTeste: Cliente = {
    id_cliente: '123',
    nome: 'João Silva',
    cpf_cnpj: '123.456.789-00',
    contato: '(11) 98765-4321',
    created_at: '2023-01-01'
  };
  
  // Funções mock para os callbacks
  const mockOnSave = vi.fn();
  const mockOnCancel = vi.fn();
  
  beforeEach(() => {
    vi.resetAllMocks();
  });
  
  it('deve renderizar o formulário vazio para novo cliente', () => {
    // Renderizar o formulário sem passar cliente (modo criação)
    render(
      <ClienteForm 
        onSave={mockOnSave} 
        onCancel={mockOnCancel} 
      />
    );
    
    // Verificar se os campos estão presentes e vazios
    const inputNome = screen.getByLabelText('Nome') as HTMLInputElement;
    const inputCpfCnpj = screen.getByLabelText('CPF/CNPJ') as HTMLInputElement;
    const inputContato = screen.getByLabelText('Contato') as HTMLInputElement;
    
    expect(inputNome.value).toBe('');
    expect(inputCpfCnpj.value).toBe('');
    expect(inputContato.value).toBe('');
    
    // Verificar se os botões estão presentes
    expect(screen.getByText('Cancelar')).toBeInTheDocument();
    expect(screen.getByText('Salvar')).toBeInTheDocument();
  });
  
  it('deve renderizar o formulário preenchido para edição de cliente', () => {
    // Renderizar o formulário passando um cliente (modo edição)
    render(
      <ClienteForm 
        cliente={clienteTeste}
        onSave={mockOnSave} 
        onCancel={mockOnCancel} 
      />
    );
    
    // Verificar se os campos estão preenchidos com os dados do cliente
    const inputNome = screen.getByLabelText('Nome') as HTMLInputElement;
    const inputCpfCnpj = screen.getByLabelText('CPF/CNPJ') as HTMLInputElement;
    const inputContato = screen.getByLabelText('Contato') as HTMLInputElement;
    
    expect(inputNome.value).toBe(clienteTeste.nome);
    expect(inputCpfCnpj.value).toBe(clienteTeste.cpf_cnpj);
    expect(inputContato.value).toBe(clienteTeste.contato);
  });
  
  it('deve validar campos obrigatórios ao tentar salvar', async () => {
    // Renderizar o formulário vazio
    render(
      <ClienteForm 
        onSave={mockOnSave} 
        onCancel={mockOnCancel} 
      />
    );
    
    // Clicar no botão salvar sem preencher os campos
    await userEvent.click(screen.getByText('Salvar'));
    
    // Verificar se as mensagens de erro aparecem
    await waitFor(() => {
      expect(screen.getAllByText('Este campo é obrigatório').length).toBeGreaterThan(0);
    });
    
    // Verificar se o callback de salvamento não foi chamado
    expect(mockOnSave).not.toHaveBeenCalled();
  });
  
  it('deve chamar onSave quando o formulário é válido', async () => {
    // Renderizar o formulário vazio
    render(
      <ClienteForm 
        onSave={mockOnSave} 
        onCancel={mockOnCancel} 
      />
    );
    
    // Preencher os campos
    const inputNome = screen.getByLabelText('Nome');
    const inputCpfCnpj = screen.getByLabelText('CPF/CNPJ');
    const inputContato = screen.getByLabelText('Contato');
    
    await userEvent.type(inputNome, 'Novo Cliente');
    await userEvent.type(inputCpfCnpj, '987.654.321-00');
    await userEvent.type(inputContato, '(21) 98765-4321');
    
    // Clicar no botão salvar
    await userEvent.click(screen.getByText('Salvar'));
    
    // Verificar se o callback de salvamento foi chamado com os dados corretos
    await waitFor(() => {
      expect(mockOnSave).toHaveBeenCalledWith({
        nome: 'Novo Cliente',
        cpf_cnpj: '987.654.321-00',
        contato: '(21) 98765-4321'
      });
    });
  });
  
  it('deve chamar onCancel quando o botão cancelar é clicado', async () => {
    // Renderizar o formulário
    render(
      <ClienteForm 
        onSave={mockOnSave} 
        onCancel={mockOnCancel} 
      />
    );
    
    // Clicar no botão cancelar
    await userEvent.click(screen.getByText('Cancelar'));
    
    // Verificar se o callback de cancelamento foi chamado
    expect(mockOnCancel).toHaveBeenCalledTimes(1);
  });
  
  it('deve validar o formato de CPF/CNPJ', async () => {
    // Renderizar o formulário
    render(
      <ClienteForm 
        onSave={mockOnSave} 
        onCancel={mockOnCancel} 
      />
    );
    
    // Preencher os campos obrigatórios
    await userEvent.type(screen.getByLabelText('Nome'), 'Teste CPF/CNPJ');
    await userEvent.type(screen.getByLabelText('Contato'), '(11) 1234-5678');
    
    // Preencher o CPF com um formato inválido
    await userEvent.type(screen.getByLabelText('CPF/CNPJ'), '1234567');
    
    // Clicar no botão salvar
    await userEvent.click(screen.getByText('Salvar'));
    
    // Verificar se a mensagem de erro específica aparece
    await waitFor(() => {
      expect(screen.getByText('CPF deve ter 11 dígitos ou CNPJ deve ter 14 dígitos')).toBeInTheDocument();
    });
    
    // Verificar se o callback de salvamento não foi chamado
    expect(mockOnSave).not.toHaveBeenCalled();
  });
}); 