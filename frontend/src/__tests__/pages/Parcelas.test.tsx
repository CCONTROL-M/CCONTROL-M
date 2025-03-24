import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Parcelas from '../../pages/Parcelas';
import { renderWithProviders } from '../utils/test-utils';
import * as parcelaService from '../../services/parcelaService';
import * as parcelaServiceMock from '../../services/parcelaServiceMock';
import * as mockUtils from '../../utils/mock';

// Mock dos hooks e serviços
vi.mock('../../services/parcelaService');
vi.mock('../../services/parcelaServiceMock');
vi.mock('../../utils/mock');

// Mock de useConfirmDialog
vi.mock('../../hooks/useConfirmDialog', () => {
  // Armazenar a última função de confirmação para podermos invocar diretamente nos testes
  let lastConfirmFn: () => Promise<boolean>;
  
  return {
    useConfirmDialog: () => {
      return {
        confirm: async (options: any) => {
          // Armazenar a função de confirmação para chamá-la nos testes
          lastConfirmFn = options.onConfirm;
          return true; // Simular que o usuário confirmou por padrão
        },
        getConfirmFn: () => lastConfirmFn,
        isOpen: false,
        dialogState: { isOpen: false, title: '', description: '', onConfirm: vi.fn() },
      };
    },
  };
});

// Mock dos hooks de toast
vi.mock('../../hooks/useToast', () => {
  const showToast = vi.fn();
  const showSuccessToast = vi.fn();
  const showErrorToast = vi.fn();
  const showInfoToast = vi.fn();

  return {
    useToast: () => ({ 
      showToast 
    }),
    useToastUtils: () => ({
      showSuccessToast,
      showErrorToast,
      showInfoToast,
    }),
    ToastProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  };
});

// Dados de exemplo para parcelas
const parcelasMock = [
  {
    id_parcela: "1",
    id_venda: "venda-0001",
    valor: 500.00,
    data_vencimento: "2023-11-15",
    status: "Paga",
    data_pagamento: "2023-11-15"
  },
  {
    id_parcela: "2",
    id_venda: "venda-0001",
    valor: 500.00,
    data_vencimento: "2023-12-15",
    status: "Pendente"
  },
  {
    id_parcela: "3",
    id_venda: "venda-0002",
    valor: 750.00,
    data_vencimento: "2023-11-10",
    status: "Paga",
    data_pagamento: "2023-11-10"
  },
  {
    id_parcela: "4",
    id_venda: "venda-0002",
    valor: 750.00,
    data_vencimento: "2023-12-10",
    status: "Pendente"
  },
  {
    id_parcela: "5",
    id_venda: "venda-0003",
    valor: 1000.00,
    data_vencimento: "2023-01-20", // Vencida (data passada)
    status: "Pendente"
  }
];

describe('Parcelas', () => {
  beforeEach(() => {
    // Resetar todos os mocks
    vi.resetAllMocks();
    
    // Mock useMock para retornar false por padrão (não usar mock)
    vi.mocked(mockUtils.useMock).mockReturnValue(false);
    
    // Mock das funções dos serviços de parcela
    vi.mocked(parcelaService.listarParcelas).mockResolvedValue(parcelasMock);
    vi.mocked(parcelaService.filtrarParcelas).mockResolvedValue(parcelasMock);
    vi.mocked(parcelaService.marcarComoPaga).mockImplementation(async (id, dataPagamento) => {
      const parcela = parcelasMock.find(p => p.id_parcela === id);
      if (!parcela) throw new Error('Parcela não encontrada');
      
      return {
        ...parcela,
        status: "Paga",
        data_pagamento: dataPagamento
      };
    });
  });
  
  afterEach(() => {
    vi.restoreAllMocks();
  });
  
  // 1. Teste de renderização da tabela com dados de parcelas
  it('deve renderizar a tabela com dados de parcelas', async () => {
    // Renderizar o componente
    renderWithProviders(<Parcelas />);
    
    // Verificar título da página
    expect(screen.getByText('Parcelas a Receber/Pagar')).toBeInTheDocument();
    
    // Verificar se a tabela foi carregada com dados
    await waitFor(() => {
      expect(parcelaService.listarParcelas).toHaveBeenCalled();
    });
    
    // Verificar se os dados das parcelas estão presentes
    await waitFor(() => {
      // Verificar cabeçalhos da tabela
      expect(screen.getByText('Venda')).toBeInTheDocument();
      expect(screen.getByText('Nº Parcela')).toBeInTheDocument();
      expect(screen.getByText('Tipo')).toBeInTheDocument();
      expect(screen.getByText('Valor')).toBeInTheDocument();
      expect(screen.getByText('Vencimento')).toBeInTheDocument();
      expect(screen.getByText('Status')).toBeInTheDocument();
      
      // Verificar dados das parcelas (pelo menos alguns)
      expect(screen.getAllByText('A Receber').length).toBeGreaterThan(0);
      expect(screen.getAllByText('Pendente').length).toBeGreaterThan(0);
      expect(screen.getAllByText('Paga').length).toBeGreaterThan(0);
    });
  });
  
  // 2. Teste de filtro por status (paga, pendente, vencida)
  it('deve filtrar parcelas por status', async () => {
    // Configurar o retorno do mock para filtrar parcelas
    const parcelasPagasMock = parcelasMock.filter(p => p.status === 'Paga');
    vi.mocked(parcelaService.filtrarParcelas).mockResolvedValue(parcelasPagasMock);
    
    // Renderizar o componente
    renderWithProviders(<Parcelas />);
    
    // Aguardar o carregamento inicial
    await waitFor(() => {
      expect(parcelaService.listarParcelas).toHaveBeenCalled();
    });
    
    // Clicar no botão de filtros
    await userEvent.click(screen.getByText('Filtros'));
    
    // Selecionar filtro de status "Pagas"
    const statusSelect = screen.getByLabelText('Status');
    await userEvent.selectOptions(statusSelect, 'Paga');
    
    // Aplicar filtro
    await userEvent.click(screen.getByText('Aplicar'));
    
    // Verificar se filtrarParcelas foi chamado com o parâmetro correto
    await waitFor(() => {
      expect(parcelaService.filtrarParcelas).toHaveBeenCalledWith(
        expect.objectContaining({ 
          status: 'Paga' 
        })
      );
    });
    
    // Verificar se apenas parcelas pagas são exibidas
    await waitFor(() => {
      const statusCells = screen.getAllByText('Paga');
      expect(statusCells.length).toBe(parcelasPagasMock.length);
      expect(screen.queryByText('Pendente')).not.toBeInTheDocument();
    });
  });
  
  // 3. Teste de ação de "Marcar como paga"
  it('deve abrir modal para marcar parcela como paga', async () => {
    // Renderizar o componente
    renderWithProviders(<Parcelas />);
    
    // Aguardar o carregamento inicial
    await waitFor(() => {
      expect(parcelaService.listarParcelas).toHaveBeenCalled();
    });
    
    // Clicar no botão "Pagar" da primeira parcela pendente
    await userEvent.click(screen.getAllByText('Pagar')[0]);
    
    // Verificar se o modal foi aberto
    expect(screen.getByText('Marcar Parcela como Paga')).toBeInTheDocument();
    
    // Verificar se os detalhes da parcela estão no modal
    expect(screen.getByText(/Venda:/)).toBeInTheDocument();
    expect(screen.getByText(/Parcela:/)).toBeInTheDocument();
    expect(screen.getByText(/Valor:/)).toBeInTheDocument();
    expect(screen.getByText(/Vencimento:/)).toBeInTheDocument();
    
    // Verificar se o campo de data está presente
    expect(screen.getByLabelText('Data de Pagamento')).toBeInTheDocument();
  });
  
  // 4. Teste de toast de sucesso após alteração de status
  it('deve exibir toast de sucesso após marcar parcela como paga', async () => {
    // Renderizar o componente
    const { container } = renderWithProviders(<Parcelas />);
    
    // Aguardar o carregamento inicial
    await waitFor(() => {
      expect(parcelaService.listarParcelas).toHaveBeenCalled();
    });
    
    // Clicar no botão "Pagar" da primeira parcela pendente
    await userEvent.click(screen.getAllByText('Pagar')[0]);
    
    // Obter a função showSuccessToast mockada
    const { showSuccessToast } = (await import('../../hooks/useToast')).useToastUtils();
    
    // Confirmar pagamento
    const dataAtual = new Date().toISOString().split('T')[0];
    const inputData = screen.getByLabelText('Data de Pagamento');
    await userEvent.clear(inputData);
    await userEvent.type(inputData, dataAtual);
    
    // Clicar no botão "Salvar"
    await userEvent.click(screen.getByText('Salvar'));
    
    // Verificar se a função marcarComoPaga foi chamada corretamente
    await waitFor(() => {
      expect(parcelaService.marcarComoPaga).toHaveBeenCalledWith(
        expect.any(String),
        dataAtual
      );
    });
    
    // Verificar se o toast de sucesso foi exibido
    await waitFor(() => {
      expect(showSuccessToast).toHaveBeenCalledWith(
        expect.stringContaining('Parcela marcada como paga'),
        expect.any(Number)
      );
    });
  });
  
  // 5. Teste de exibição de erro caso a API falhe
  it('deve exibir erro caso a API falhe ao marcar como paga', async () => {
    // Mock da API para falhar
    vi.mocked(parcelaService.marcarComoPaga).mockRejectedValue(
      new Error('Erro ao marcar parcela como paga')
    );
    
    // Renderizar o componente
    renderWithProviders(<Parcelas />);
    
    // Aguardar o carregamento inicial
    await waitFor(() => {
      expect(parcelaService.listarParcelas).toHaveBeenCalled();
    });
    
    // Clicar no botão "Pagar" da primeira parcela pendente
    await userEvent.click(screen.getAllByText('Pagar')[0]);
    
    // Obter a função showErrorToast mockada
    const { showErrorToast } = (await import('../../hooks/useToast')).useToastUtils();
    
    // Confirmar pagamento
    const dataAtual = new Date().toISOString().split('T')[0];
    const inputData = screen.getByLabelText('Data de Pagamento');
    await userEvent.clear(inputData);
    await userEvent.type(inputData, dataAtual);
    
    // Clicar no botão "Salvar"
    await userEvent.click(screen.getByText('Salvar'));
    
    // Verificar se o toast de erro foi exibido
    await waitFor(() => {
      expect(showErrorToast).toHaveBeenCalledWith(
        expect.stringContaining('Erro ao marcar parcela como paga'),
        expect.any(Number)
      );
    });
  });
  
  // 6. Teste de confirmação antes da alteração (ConfirmDialog)
  it('deve confirmar antes de marcar a parcela como paga', async () => {
    // Renderizar o componente
    renderWithProviders(<Parcelas />);
    
    // Aguardar o carregamento inicial
    await waitFor(() => {
      expect(parcelaService.listarParcelas).toHaveBeenCalled();
    });
    
    // Clicar no botão "Pagar" da primeira parcela pendente
    await userEvent.click(screen.getAllByText('Pagar')[0]);
    
    // Verificar se o modal foi aberto
    expect(screen.getByText('Marcar Parcela como Paga')).toBeInTheDocument();
    
    // Preencher data de pagamento
    const dataAtual = new Date().toISOString().split('T')[0];
    const inputData = screen.getByLabelText('Data de Pagamento');
    await userEvent.clear(inputData);
    await userEvent.type(inputData, dataAtual);
    
    // Simular que usuário cancela o diálogo de confirmação
    // Para isso, modificamos o mock da useConfirmDialog para retornar false
    const originalModule = await import('../../hooks/useConfirmDialog');
    const originalUseConfirmDialog = originalModule.useConfirmDialog;
    vi.doMock('../../hooks/useConfirmDialog', () => ({
      useConfirmDialog: () => ({
        ...originalUseConfirmDialog(),
        confirm: async () => false  // Simular cancelamento
      })
    }));
    
    // Obter a função marcarComoPaga para verificar se não foi chamada
    const mockMarcarComoPaga = vi.mocked(parcelaService.marcarComoPaga);
    
    // Clicar no botão "Salvar"
    await userEvent.click(screen.getByText('Salvar'));
    
    // Verificar que marcarComoPaga não foi chamado (porque o usuário "cancelou" no diálogo)
    await new Promise(resolve => setTimeout(resolve, 100)); // Pequeno delay para garantir
    expect(mockMarcarComoPaga).not.toHaveBeenCalled();
    
    // Restaurar o mock original
    vi.doMock('../../hooks/useConfirmDialog', () => ({
      useConfirmDialog: originalUseConfirmDialog
    }));
  });
}); 