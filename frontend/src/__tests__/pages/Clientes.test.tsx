import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, fireEvent, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Clientes from '../../pages/Clientes';
import { renderWithProviders } from '../utils/test-utils';
import * as clienteService from '../../services/clienteService';
import * as clienteServiceMock from '../../services/clienteServiceMock';
import * as mockUtils from '../../utils/mock';

// Mock dos serviços e utilitários
vi.mock('../../services/clienteService');
vi.mock('../../services/clienteServiceMock');
vi.mock('../../utils/mock');
vi.mock('../../hooks/useConfirmDialog', () => {
  return {
    default: () => ({
      dialog: {
        isOpen: false,
        title: '',
        description: '',
        onConfirm: vi.fn(),
        confirmText: '',
        cancelText: '',
        type: 'danger',
      },
      confirm: vi.fn((options) => {
        // Simula o comportamento do confirm chamando onConfirm
        setTimeout(() => options.onConfirm(), 0);
        return Promise.resolve();
      }),
      closeDialog: vi.fn(),
    }),
  };
});

// Mock do useToast
vi.mock('../../hooks/useToast', () => {
  const showSuccessToast = vi.fn();
  const showErrorToast = vi.fn();
  return {
    useToastUtils: () => ({
      showSuccessToast,
      showErrorToast,
    }),
    ToastProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  };
});

// Dados de teste
const clientesMock = [
  {
    id_cliente: "1",
    nome: "João Silva",
    cpf_cnpj: "123.456.789-00",
    contato: "(11) 98765-4321",
    created_at: "2023-01-15"
  },
  {
    id_cliente: "2",
    nome: "Maria Souza",
    cpf_cnpj: "987.654.321-00",
    contato: "(11) 91234-5678",
    created_at: "2023-02-20"
  }
];

describe('Clientes', () => {
  beforeEach(() => {
    // Reset dos mocks
    vi.resetAllMocks();
    
    // Mock do useMock para retornar false por padrão (não usar mock)
    vi.mocked(mockUtils.useMock).mockReturnValue(false);
    vi.mocked(mockUtils.toggleMock).mockImplementation(() => {});
    vi.mocked(mockUtils.adicionarIndicadorMock).mockImplementation(() => {});
    
    // Mock das funções do serviço de cliente
    vi.mocked(clienteService.listarClientes).mockResolvedValue(clientesMock);
    vi.mocked(clienteService.removerCliente).mockResolvedValue();
    vi.mocked(clienteService.cadastrarCliente).mockImplementation(async (cliente) => {
      return {
        ...cliente,
        id_cliente: "novo-cliente-id",
        created_at: new Date().toISOString()
      };
    });
    vi.mocked(clienteService.atualizarCliente).mockImplementation(async (id, cliente) => {
      return {
        ...cliente,
        id_cliente: id,
        created_at: "2023-01-15"
      } as any;
    });
    
    // Mock das funções do serviço mock
    vi.mocked(clienteServiceMock.listarClientesMock).mockResolvedValue(clientesMock);
    vi.mocked(clienteServiceMock.removerClienteMock).mockResolvedValue();
    vi.mocked(clienteServiceMock.cadastrarClienteMock).mockImplementation(async (cliente) => {
      return {
        ...cliente,
        id_cliente: "novo-cliente-id",
        created_at: new Date().toISOString()
      };
    });
    vi.mocked(clienteServiceMock.atualizarClienteMock).mockImplementation(async (id, cliente) => {
      return {
        ...cliente,
        id_cliente: id,
        created_at: "2023-01-15"
      } as any;
    });
  });
  
  afterEach(() => {
    vi.restoreAllMocks();
  });
  
  // Teste 1: Renderização da tabela de clientes com mock de dados
  it('deve renderizar a tabela de clientes com dados', async () => {
    // Renderizar o componente
    renderWithProviders(<Clientes />);
    
    // Verificar se a tabela está carregando
    expect(screen.getByText(/carregando/i)).toBeInTheDocument();
    
    // Aguardar o carregamento dos dados
    await waitFor(() => {
      expect(screen.queryByText(/carregando/i)).not.toBeInTheDocument();
    });
    
    // Verificar se os dados dos clientes foram renderizados
    expect(screen.getByText("João Silva")).toBeInTheDocument();
    expect(screen.getByText("Maria Souza")).toBeInTheDocument();
    expect(screen.getByText("123.456.789-00")).toBeInTheDocument();
    expect(screen.getByText("987.654.321-00")).toBeInTheDocument();
    
    // Verificar se as colunas da tabela foram renderizadas
    expect(screen.getByText("Nome")).toBeInTheDocument();
    expect(screen.getByText("CPF/CNPJ")).toBeInTheDocument();
    expect(screen.getByText("Contato")).toBeInTheDocument();
    expect(screen.getByText("Ações")).toBeInTheDocument();
    
    // Verificar se o serviço foi chamado
    expect(clienteService.listarClientes).toHaveBeenCalledTimes(1);
  });
  
  // Teste 2: Abertura do modal de criação
  it('deve abrir o modal de criação ao clicar no botão "Novo Cliente"', async () => {
    // Renderizar o componente
    renderWithProviders(<Clientes />);
    
    // Aguardar o carregamento dos dados
    await waitFor(() => {
      expect(screen.queryByText(/carregando/i)).not.toBeInTheDocument();
    });
    
    // Verificar se o botão de novo cliente está presente
    const botaoNovoCliente = screen.getByText("+ Novo Cliente");
    expect(botaoNovoCliente).toBeInTheDocument();
    
    // Clicar no botão para abrir o modal
    await userEvent.click(botaoNovoCliente);
    
    // Verificar se o modal foi aberto
    expect(screen.getByText("Novo Cliente")).toBeInTheDocument();
    
    // Verificar se o formulário está presente
    expect(screen.getByLabelText("Nome")).toBeInTheDocument();
    expect(screen.getByLabelText("CPF/CNPJ")).toBeInTheDocument();
    expect(screen.getByLabelText("Contato")).toBeInTheDocument();
    
    // Verificar se os botões do formulário estão presentes
    expect(screen.getByText("Cancelar")).toBeInTheDocument();
    expect(screen.getByText("Salvar")).toBeInTheDocument();
  });
  
  // Teste 3: Validação de campos obrigatórios no formulário
  it('deve validar campos obrigatórios ao tentar salvar um cliente sem preencher campos', async () => {
    // Renderizar o componente
    renderWithProviders(<Clientes />);
    
    // Aguardar o carregamento dos dados
    await waitFor(() => {
      expect(screen.queryByText(/carregando/i)).not.toBeInTheDocument();
    });
    
    // Abrir o modal de novo cliente
    await userEvent.click(screen.getByText("+ Novo Cliente"));
    
    // Clicar no botão salvar sem preencher os campos
    await userEvent.click(screen.getByText("Salvar"));
    
    // Verificar se as mensagens de erro aparecem
    await waitFor(() => {
      expect(screen.getByText("Este campo é obrigatório")).toBeInTheDocument();
    });
    
    // Verificar se o serviço não foi chamado
    expect(clienteService.cadastrarCliente).not.toHaveBeenCalled();
  });
  
  // Teste 4: Submissão válida com simulação de requisição ao clienteService
  it('deve cadastrar um cliente com sucesso ao preencher todos os campos corretamente', async () => {
    // Mock da função showSuccessToast
    const { useToastUtils } = await import('../../hooks/useToast');
    const { showSuccessToast } = useToastUtils();
    
    // Renderizar o componente
    renderWithProviders(<Clientes />);
    
    // Aguardar o carregamento dos dados
    await waitFor(() => {
      expect(screen.queryByText(/carregando/i)).not.toBeInTheDocument();
    });
    
    // Abrir o modal de novo cliente
    await userEvent.click(screen.getByText("+ Novo Cliente"));
    
    // Preencher os campos do formulário
    await userEvent.type(screen.getByLabelText("Nome"), "Carlos Oliveira");
    await userEvent.type(screen.getByLabelText("CPF/CNPJ"), "111.222.333-44");
    await userEvent.type(screen.getByLabelText("Contato"), "(21) 98765-4321");
    
    // Clicar no botão salvar
    await userEvent.click(screen.getByText("Salvar"));
    
    // Verificar se o serviço foi chamado com os dados corretos
    await waitFor(() => {
      expect(clienteService.cadastrarCliente).toHaveBeenCalledWith(
        expect.objectContaining({
          nome: "Carlos Oliveira",
          cpf_cnpj: "111.222.333-44",
          contato: "(21) 98765-4321"
        })
      );
    });
    
    // Verificar se o toast de sucesso foi exibido
    expect(showSuccessToast).toHaveBeenCalledWith(expect.stringContaining("sucesso"));
    
    // Verificar se o modal foi fechado
    await waitFor(() => {
      expect(screen.queryByText("Novo Cliente")).not.toBeInTheDocument();
    });
  });
  
  // Teste 5: Exclusão com uso de ConfirmDialog
  it('deve excluir um cliente ao clicar no botão de exclusão e confirmar', async () => {
    // Mock da função showSuccessToast
    const { useToastUtils } = await import('../../hooks/useToast');
    const { showSuccessToast } = useToastUtils();
    
    // Renderizar o componente
    renderWithProviders(<Clientes />);
    
    // Aguardar o carregamento dos dados
    await waitFor(() => {
      expect(screen.queryByText(/carregando/i)).not.toBeInTheDocument();
    });
    
    // Localizar o botão de exclusão do primeiro cliente
    const botoesExcluir = screen.getAllByLabelText("Excluir cliente");
    expect(botoesExcluir.length).toBeGreaterThan(0);
    
    // Clicar no botão de exclusão
    await userEvent.click(botoesExcluir[0]);
    
    // Verificar se o serviço de remoção foi chamado
    await waitFor(() => {
      expect(clienteService.removerCliente).toHaveBeenCalledWith("1");
    });
    
    // Verificar se o toast de sucesso foi exibido
    expect(showSuccessToast).toHaveBeenCalledWith(expect.stringContaining("sucesso"));
  });
  
  // Teste 6: Exibição de toast de sucesso e erro
  it('deve exibir toast de erro quando o serviço falhar', async () => {
    // Forçar o serviço a falhar
    vi.mocked(clienteService.listarClientes).mockRejectedValue(new Error("Erro ao carregar clientes"));
    
    // Mock das funções de toast
    const { useToastUtils } = await import('../../hooks/useToast');
    const { showErrorToast } = useToastUtils();
    
    // Renderizar o componente
    renderWithProviders(<Clientes />);
    
    // Aguardar o erro
    await waitFor(() => {
      expect(showErrorToast).toHaveBeenCalledWith(expect.stringContaining("Erro ao carregar clientes"));
    });
    
    // Verificar se a mensagem de erro é exibida na UI
    expect(screen.getByText("Erro ao carregar clientes")).toBeInTheDocument();
    
    // Verificar se existe um botão para tentar novamente
    expect(screen.getByText("Tentar novamente")).toBeInTheDocument();
  });
}); 