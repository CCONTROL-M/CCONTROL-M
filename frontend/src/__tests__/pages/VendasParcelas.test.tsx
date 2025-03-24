import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, fireEvent, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from '../utils/test-utils';
import VendasParcelas from '../../pages/VendasParcelas';
import * as vendaService from '../../services/vendaService';
import * as clienteService from '../../services/clienteService';
import * as mockUtils from '../../utils/mock';

// Mock dos serviços
vi.mock('../../services/vendaService');
vi.mock('../../services/clienteService');
vi.mock('../../utils/mock');

// Mock do hook de toast
const showToastMock = vi.fn();
const showSuccessToastMock = vi.fn();
const showErrorToastMock = vi.fn();

vi.mock('../../hooks/useToast', () => {
  return {
    useToast: () => ({ 
      showToast: showToastMock
    }),
    useToastUtils: () => ({
      showSuccessToast: showSuccessToastMock,
      showErrorToast: showErrorToastMock,
    }),
    ToastProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  };
});

// Mock do hook useConfirmDialog
const confirmMock = vi.fn(async () => true); // Por padrão, confirma a ação

vi.mock('../../hooks/useConfirmDialog', () => {
  return {
    useConfirmDialog: () => ({
      confirm: confirmMock,
      closeDialog: vi.fn(),
      isOpen: false
    })
  };
});

// Dados mock para vendas
const vendasMock = [
  {
    id_venda: "1",
    id_empresa: "11111111-1111-1111-1111-111111111111",
    id_cliente: "1",
    cliente: {
      id_cliente: "1",
      nome: "João Silva",
      documento: "123.456.789-00",
      tipo: "PF"
    },
    valor_total: 1500.00,
    data_venda: "2023-08-15",
    status: "confirmada",
    descricao: "Venda à vista",
    numero_parcelas: 1,
    parcelas: [
      {
        id_parcela: "1",
        id_venda: "1",
        numero: 1,
        valor: 1500.00,
        data_vencimento: "2023-08-30",
        status: "pendente"
      }
    ]
  },
  {
    id_venda: "2",
    id_empresa: "11111111-1111-1111-1111-111111111111",
    id_cliente: "2",
    cliente: {
      id_cliente: "2",
      nome: "Maria Souza",
      documento: "98.765.432-1",
      tipo: "PF"
    },
    valor_total: 2500.00,
    data_venda: "2023-08-20",
    status: "confirmada",
    descricao: "Venda parcelada",
    numero_parcelas: 3,
    parcelas: [
      {
        id_parcela: "2",
        id_venda: "2",
        numero: 1,
        valor: 833.33,
        data_vencimento: "2023-09-20",
        status: "pendente"
      },
      {
        id_parcela: "3",
        id_venda: "2",
        numero: 2,
        valor: 833.33,
        data_vencimento: "2023-10-20",
        status: "pendente"
      },
      {
        id_parcela: "4",
        id_venda: "2",
        numero: 3,
        valor: 833.34,
        data_vencimento: "2023-11-20",
        status: "pendente"
      }
    ]
  }
];

// Dados mock para clientes
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
  },
  {
    id_cliente: "3",
    nome: "Empresa ABC Ltda",
    cpf_cnpj: "12.345.678/0001-90",
    contato: "(11) 3456-7890",
    created_at: "2023-03-10"
  }
];

// Nova venda para testes
const novaVenda = {
  id_cliente: "1",
  valor_total: 1200,
  numero_parcelas: 2,
  data_inicio: "2023-10-01",
  descricao: "Venda de teste",
  categoria: "venda"
};

describe('VendasParcelas', () => {
  beforeEach(() => {
    // Resetar mocks
    vi.resetAllMocks();
    
    // Mock de serviços
    vi.mocked(mockUtils.useMock).mockReturnValue(false);
    vi.mocked(vendaService.listarVendas).mockResolvedValue(vendasMock);
    vi.mocked(clienteService.listarClientes).mockResolvedValue(clientesMock);
    vi.mocked(vendaService.cadastrarVenda).mockImplementation(async (venda) => {
      return {
        id_venda: "novo-id",
        id_empresa: "11111111-1111-1111-1111-111111111111",
        ...venda,
        status: "confirmada",
        data_venda: new Date().toISOString().split('T')[0],
        cliente: clientesMock.find(c => c.id_cliente === venda.id_cliente),
        parcelas: Array(venda.numero_parcelas).fill(null).map((_, index) => ({
          id_parcela: `novo-parcela-${index + 1}`,
          id_venda: "novo-id",
          numero: index + 1,
          valor: venda.valor_total / venda.numero_parcelas,
          data_vencimento: new Date(venda.data_inicio).toISOString().split('T')[0],
          status: "pendente"
        }))
      };
    });
    
    vi.mocked(vendaService.removerVenda).mockResolvedValue();
  });
  
  afterEach(() => {
    vi.restoreAllMocks();
  });
  
  // Teste 1: Renderizar vendas com tabela expandida de parcelas
  it('deve renderizar vendas com tabela expandida de parcelas', async () => {
    renderWithProviders(<VendasParcelas />);
    
    // Verificar se a tabela principal está sendo renderizada
    expect(screen.getByText('Vendas')).toBeInTheDocument();
    
    // Aguardar carregamento dos dados
    await waitFor(() => {
      expect(vendaService.listarVendas).toHaveBeenCalled();
    });
    
    // Verificar se as vendas foram carregadas
    expect(screen.getByText('João Silva')).toBeInTheDocument();
    expect(screen.getByText('Maria Souza')).toBeInTheDocument();
    expect(screen.getByText('Venda à vista')).toBeInTheDocument();
    expect(screen.getByText('Venda parcelada')).toBeInTheDocument();
    
    // Expandir detalhes da venda para ver as parcelas
    const botaoDetalhe = screen.getAllByText('Detalhes')[0];
    await userEvent.click(botaoDetalhe);
    
    // Verificar se os detalhes mostram as parcelas
    await waitFor(() => {
      const modal = screen.getByText('Detalhes da Venda');
      expect(modal).toBeInTheDocument();
      
      // Verificar se a tabela de parcelas está sendo mostrada
      expect(screen.getByText('Parcelas')).toBeInTheDocument();
      expect(screen.getByText('1/1')).toBeInTheDocument(); // Número da parcela
      expect(screen.getByText('R$ 1.500,00')).toBeInTheDocument(); // Valor da parcela
    });
  });
  
  // Teste 2: Abrir modal para nova venda
  it('deve abrir o modal de nova venda ao clicar no botão', async () => {
    renderWithProviders(<VendasParcelas />);
    
    // Aguardar carregamento dos dados
    await waitFor(() => {
      expect(vendaService.listarVendas).toHaveBeenCalled();
    });
    
    // Clicar no botão de nova venda
    const botaoNovaVenda = screen.getByText('Nova Venda');
    await userEvent.click(botaoNovaVenda);
    
    // Verificar se o modal de nova venda foi aberto
    await waitFor(() => {
      expect(screen.getByText('Cadastrar Nova Venda')).toBeInTheDocument();
      
      // Verificar se o formulário está presente
      expect(screen.getByText('Cliente:')).toBeInTheDocument();
      expect(screen.getByText('Valor Total (R$)')).toBeInTheDocument();
      expect(screen.getByText('Número de Parcelas')).toBeInTheDocument();
      expect(screen.getByText('Data Inicial')).toBeInTheDocument();
      expect(screen.getByText('Descrição:')).toBeInTheDocument();
    });
    
    // Verificar se os clientes foram carregados no select
    const clienteSelect = screen.getByLabelText('Cliente:');
    expect(clienteSelect).toBeInTheDocument();
    
    // Verificar se o cliente foi carregado no select
    const options = within(clienteSelect).getAllByRole('option');
    expect(options.length).toBe(clientesMock.length + 1); // +1 pois há a opção "Selecione um cliente"
    expect(options[1].textContent).toBe('João Silva');
  });
  
  // Teste 3: Validação de campos obrigatórios
  it('deve validar campos obrigatórios no formulário', async () => {
    renderWithProviders(<VendasParcelas />);
    
    // Aguardar carregamento dos dados
    await waitFor(() => {
      expect(vendaService.listarVendas).toHaveBeenCalled();
    });
    
    // Abrir o modal de nova venda
    const botaoNovaVenda = screen.getByText('Nova Venda');
    await userEvent.click(botaoNovaVenda);
    
    // Tentar cadastrar sem preencher os campos
    await waitFor(() => {
      const cadastrarButton = screen.getByText('Cadastrar Venda');
      userEvent.click(cadastrarButton);
    });
    
    // Verificar se as mensagens de erro estão sendo exibidas
    await waitFor(() => {
      expect(screen.getByText('Selecione um cliente')).toBeInTheDocument();
      expect(screen.getByText('Informe um valor válido')).toBeInTheDocument();
      expect(screen.getByText('Descrição deve ter pelo menos 3 caracteres')).toBeInTheDocument();
    });
    
    // Verificar que o serviço não foi chamado
    expect(vendaService.cadastrarVenda).not.toHaveBeenCalled();
  });
  
  // Teste 4: Geração de parcelas baseada nas condições fornecidas
  it('deve gerar parcelas baseadas nas condições fornecidas', async () => {
    renderWithProviders(<VendasParcelas />);
    
    // Aguardar carregamento dos dados
    await waitFor(() => {
      expect(vendaService.listarVendas).toHaveBeenCalled();
    });
    
    // Abrir o modal de nova venda
    const botaoNovaVenda = screen.getByText('Nova Venda');
    await userEvent.click(botaoNovaVenda);
    
    // Preencher o formulário
    await waitFor(async () => {
      // Selecionar cliente
      const clienteSelect = screen.getByLabelText('Cliente:');
      fireEvent.change(clienteSelect, { target: { value: '1' } });
      
      // Preencher valor total
      const valorInput = screen.getByLabelText('Valor Total (R$)');
      await userEvent.clear(valorInput);
      await userEvent.type(valorInput, '1200');
      
      // Preencher número de parcelas
      const parcelasInput = screen.getByLabelText('Número de Parcelas');
      await userEvent.clear(parcelasInput);
      await userEvent.type(parcelasInput, '3');
      
      // Preencher data inicial
      const dataInput = screen.getByLabelText('Data Inicial');
      await userEvent.clear(dataInput);
      await userEvent.type(dataInput, '2023-10-01');
      
      // Preencher descrição
      const descricaoInput = screen.getByLabelText('Descrição:');
      await userEvent.clear(descricaoInput);
      await userEvent.type(descricaoInput, 'Venda de teste com 3 parcelas');
    });
    
    // Clicar no botão para visualizar simulação de parcelas
    const botaoSimulacao = screen.getByText('📊 Visualizar Simulação de Parcelas');
    await userEvent.click(botaoSimulacao);
    
    // Verificar se a simulação de parcelas foi exibida corretamente
    await waitFor(() => {
      expect(screen.getByText('Simulação de Parcelas')).toBeInTheDocument();
      
      // Verificar se as 3 parcelas foram geradas
      const rows = screen.getAllByRole('row');
      expect(rows.length).toBe(4); // 1 cabeçalho + 3 parcelas
      
      // Verificar valor das parcelas (1200 / 3 = 400)
      expect(screen.getAllByText('R$ 400,00')).toHaveLength(3);
    });
  });
  
  // Teste 5: Feedback visual (toast) de sucesso e erro
  it('deve mostrar feedback visual (toast) de sucesso e erro', async () => {
    renderWithProviders(<VendasParcelas />);
    
    // Aguardar carregamento dos dados
    await waitFor(() => {
      expect(vendaService.listarVendas).toHaveBeenCalled();
    });
    
    // Abrir o modal de nova venda
    const botaoNovaVenda = screen.getByText('Nova Venda');
    await userEvent.click(botaoNovaVenda);
    
    // Preencher o formulário
    await waitFor(async () => {
      // Selecionar cliente
      const clienteSelect = screen.getByLabelText('Cliente:');
      fireEvent.change(clienteSelect, { target: { value: '1' } });
      
      // Preencher valor total
      const valorInput = screen.getByLabelText('Valor Total (R$)');
      await userEvent.clear(valorInput);
      await userEvent.type(valorInput, '1200');
      
      // Preencher número de parcelas
      const parcelasInput = screen.getByLabelText('Número de Parcelas');
      await userEvent.clear(parcelasInput);
      await userEvent.type(parcelasInput, '2');
      
      // Preencher data inicial
      const dataInput = screen.getByLabelText('Data Inicial');
      await userEvent.clear(dataInput);
      await userEvent.type(dataInput, '2023-10-01');
      
      // Preencher descrição
      const descricaoInput = screen.getByLabelText('Descrição:');
      await userEvent.clear(descricaoInput);
      await userEvent.type(descricaoInput, 'Venda de teste');
    });
    
    // Cadastrar venda com sucesso
    const cadastrarButton = screen.getByText('Cadastrar Venda');
    await userEvent.click(cadastrarButton);
    
    // Verificar se o serviço foi chamado com os parâmetros corretos
    await waitFor(() => {
      expect(vendaService.cadastrarVenda).toHaveBeenCalledWith({
        id_cliente: "1",
        valor_total: 1200,
        numero_parcelas: 2,
        data_inicio: "2023-10-01",
        descricao: "Venda de teste",
        categoria: "venda"
      });
      
      // Verificar se o toast de sucesso foi mostrado
      expect(showSuccessToastMock).toHaveBeenCalledWith(expect.stringContaining('Venda cadastrada'));
    });
    
    // Testar o cenário de erro
    vi.mocked(vendaService.cadastrarVenda).mockRejectedValueOnce(new Error('Erro ao cadastrar venda'));
    
    // Abrir o modal novamente
    await userEvent.click(botaoNovaVenda);
    
    // Preencher o formulário novamente
    await waitFor(async () => {
      // Selecionar cliente
      const clienteSelect = screen.getByLabelText('Cliente:');
      fireEvent.change(clienteSelect, { target: { value: '1' } });
      
      // Preencher valor total
      const valorInput = screen.getByLabelText('Valor Total (R$)');
      await userEvent.clear(valorInput);
      await userEvent.type(valorInput, '1200');
      
      // Preencher número de parcelas
      const parcelasInput = screen.getByLabelText('Número de Parcelas');
      await userEvent.clear(parcelasInput);
      await userEvent.type(parcelasInput, '2');
      
      // Preencher data inicial
      const dataInput = screen.getByLabelText('Data Inicial');
      await userEvent.clear(dataInput);
      await userEvent.type(dataInput, '2023-10-01');
      
      // Preencher descrição
      const descricaoInput = screen.getByLabelText('Descrição:');
      await userEvent.clear(descricaoInput);
      await userEvent.type(descricaoInput, 'Venda com erro');
    });
    
    // Tentar cadastrar venda com erro
    const cadastrarButtonErro = screen.getByText('Cadastrar Venda');
    await userEvent.click(cadastrarButtonErro);
    
    // Verificar se o toast de erro foi mostrado
    await waitFor(() => {
      expect(showErrorToastMock).toHaveBeenCalledWith('Erro ao cadastrar venda');
    });
  });
  
  // Teste 6: Confirmar antes de excluir uma venda
  it('deve pedir confirmação antes de excluir uma venda', async () => {
    renderWithProviders(<VendasParcelas />);
    
    // Aguardar carregamento dos dados
    await waitFor(() => {
      expect(vendaService.listarVendas).toHaveBeenCalled();
    });
    
    // Clicar no ícone de exclusão da primeira venda
    const botoesExcluir = screen.getAllByText('Excluir');
    await userEvent.click(botoesExcluir[0]);
    
    // Verificar se o diálogo de confirmação foi chamado
    await waitFor(() => {
      expect(confirmMock).toHaveBeenCalledWith({
        title: expect.stringContaining('Excluir Venda'),
        message: expect.stringContaining('confirmada'),
        confirmText: 'Excluir',
        cancelText: 'Cancelar',
        type: 'danger'
      });
    });
    
    // Como o mock do confirm retorna true por padrão, a venda deve ser excluída
    await waitFor(() => {
      expect(vendaService.removerVenda).toHaveBeenCalledWith('1');
    });
    
    // Verificar se o toast de sucesso foi mostrado
    expect(showSuccessToastMock).toHaveBeenCalledWith(expect.stringContaining('excluída'));
    
    // Testar cenário onde o usuário cancela a confirmação
    confirmMock.mockResolvedValueOnce(false);
    
    // Clicar em excluir novamente
    const botoesExcluirNovos = screen.getAllByText('Excluir');
    await userEvent.click(botoesExcluirNovos[0]);
    
    // Aguardar a chamada do diálogo
    await waitFor(() => {
      expect(confirmMock).toHaveBeenCalledTimes(2);
    });
    
    // Verificar que o serviço não foi chamado novamente
    expect(vendaService.removerVenda).toHaveBeenCalledTimes(1);
  });
}); 