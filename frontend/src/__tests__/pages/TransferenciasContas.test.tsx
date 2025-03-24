import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import TransferenciasContas from '../../pages/TransferenciasContas';
import { renderWithProviders } from '../utils/test-utils';
import * as transferenciaService from '../../services/transferenciaService';
import * as contaBancariaService from '../../services/contaBancariaService';
import * as mockUtils from '../../utils/mock';

// Mock dos hooks e serviços
vi.mock('../../services/transferenciaService');
vi.mock('../../services/contaBancariaService');
vi.mock('../../utils/mock');

// Mock de useConfirmDialog
vi.mock('../../hooks/useConfirmDialog', () => {
  let confirmCallback: () => Promise<void>;
  let confirmResolve: (value: boolean) => void;
  
  return {
    useConfirmDialog: () => {
      return {
        dialog: { isOpen: false, title: '', description: '', onConfirm: vi.fn() },
        closeDialog: vi.fn(),
        confirm: (options: any) => {
          confirmCallback = options.onConfirm;
          // Retornar uma promessa que será resolvida manualmente nos testes
          return new Promise<boolean>((resolve) => {
            confirmResolve = resolve;
          });
        },
        // Funções auxiliares para os testes
        _simulateConfirm: async () => {
          await confirmCallback();
          confirmResolve(true);
        },
        _simulateCancel: () => {
          confirmResolve(false);
        }
      };
    }
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

// Mock do useFormHandler
vi.mock('../../hooks/useFormHandler', () => {
  return {
    default: (initialData: any) => {
      const [formData, setFormData] = vi.hoisted(() => [initialData, vi.fn()]);
      const [formErrors, setFormErrors] = vi.hoisted(() => [{}, vi.fn()]);
      
      const validate = vi.fn((rules: any) => {
        // Implementação simplificada de validação para os testes
        let isValid = true;
        const errors: Record<string, string> = {};
        
        if (formData.conta_origem === formData.conta_destino && formData.conta_origem !== '') {
          errors.conta_origem = 'A conta de origem não pode ser igual à conta de destino';
          errors.conta_destino = 'A conta de destino não pode ser igual à conta de origem';
          isValid = false;
        }
        
        if (formData.valor <= 0) {
          errors.valor = 'O valor deve ser maior que zero';
          isValid = false;
        }
        
        if (!formData.data) {
          errors.data = 'A data é obrigatória';
          isValid = false;
        }
        
        setFormErrors(errors);
        return isValid;
      });
      
      const handleInputChange = vi.fn((e: any) => {
        const { name, value } = e.target;
        formData[name] = value;
        setFormData({ ...formData });
      });
      
      const resetForm = vi.fn(() => {
        setFormData(initialData);
        setFormErrors({});
      });
      
      return {
        formData,
        setFormData,
        formErrors,
        handleInputChange,
        validate,
        resetForm,
      };
    }
  };
});

// Dados de exemplo
const transferenciasMock = [
  {
    id_transferencia: "1",
    data: "2023-11-05",
    conta_origem: "Banco do Brasil",
    conta_destino: "Caixa Econômica",
    valor: 2000.00,
    status: "Concluída"
  },
  {
    id_transferencia: "2",
    data: "2023-11-08",
    conta_origem: "Nubank",
    conta_destino: "Banco do Brasil",
    valor: 1500.00,
    status: "Concluída"
  },
  {
    id_transferencia: "3",
    data: "2023-11-12",
    conta_origem: "Caixa Econômica",
    conta_destino: "Itaú",
    valor: 3000.00,
    status: "Pendente"
  }
];

const contasBancariasMock = [
  {
    id_conta: "1",
    nome: "Banco do Brasil",
    banco: "BB",
    agencia: "1234",
    conta: "56789-0",
    tipo: "Corrente",
    saldo_inicial: 10000,
    saldo_atual: 12000,
    ativa: true,
    created_at: "2023-01-01"
  },
  {
    id_conta: "2",
    nome: "Caixa Econômica",
    banco: "CEF",
    agencia: "4321",
    conta: "98765-4",
    tipo: "Corrente",
    saldo_inicial: 5000,
    saldo_atual: 7000,
    ativa: true,
    created_at: "2023-01-01"
  },
  {
    id_conta: "3",
    nome: "Nubank",
    banco: "Nubank",
    agencia: "0001",
    conta: "123456-7",
    tipo: "Corrente",
    saldo_inicial: 2000,
    saldo_atual: 3500,
    ativa: true,
    created_at: "2023-01-01"
  }
];

describe('TransferenciasContas', () => {
  beforeEach(() => {
    // Resetar todos os mocks
    vi.resetAllMocks();
    
    // Mock useMock para retornar false por padrão (não usar mock)
    vi.mocked(mockUtils.useMock).mockReturnValue(false);
    
    // Mock das funções dos serviços
    vi.mocked(transferenciaService.listarTransferencias).mockResolvedValue(transferenciasMock);
    vi.mocked(transferenciaService.filtrarTransferencias).mockResolvedValue(transferenciasMock);
    vi.mocked(transferenciaService.cadastrarTransferencia).mockImplementation(async (transferencia) => {
      return {
        ...transferencia,
        id_transferencia: "9999"
      };
    });
    
    vi.mocked(contaBancariaService.listarContasBancarias).mockResolvedValue(contasBancariasMock);
  });
  
  afterEach(() => {
    vi.restoreAllMocks();
  });
  
  // 1. Teste de renderização da lista de transferências
  it('deve renderizar a lista de transferências', async () => {
    // Renderizar o componente
    renderWithProviders(<TransferenciasContas />);
    
    // Verificar título da página
    expect(screen.getByText('Transferências entre Contas')).toBeInTheDocument();
    
    // Verificar se o serviço de listar foi chamado
    await waitFor(() => {
      expect(transferenciaService.listarTransferencias).toHaveBeenCalled();
    });
    
    // Verificar se os dados das transferências estão sendo exibidos
    await waitFor(() => {
      // Cabeçalhos da tabela
      expect(screen.getByText('Data')).toBeInTheDocument();
      expect(screen.getByText('Conta Origem')).toBeInTheDocument();
      expect(screen.getByText('Conta Destino')).toBeInTheDocument();
      expect(screen.getByText('Valor')).toBeInTheDocument();
      expect(screen.getByText('Status')).toBeInTheDocument();
      
      // Dados das transferências
      expect(screen.getByText('Banco do Brasil')).toBeInTheDocument();
      expect(screen.getByText('Caixa Econômica')).toBeInTheDocument();
      expect(screen.getByText('Nubank')).toBeInTheDocument();
      expect(screen.getByText('Pendente')).toBeInTheDocument();
      expect(screen.getAllByText('Concluída').length).toBe(2);
    });
  });
  
  // 2. Teste de filtro por data, conta de origem e destino
  it('deve filtrar transferências por data, conta de origem e destino', async () => {
    // Mock para filtro específico
    const transferenciasFiltradas = [transferenciasMock[0]]; // Apenas a primeira transferência
    vi.mocked(transferenciaService.filtrarTransferencias).mockResolvedValue(transferenciasFiltradas);
    
    // Renderizar o componente
    renderWithProviders(<TransferenciasContas />);
    
    // Aguardar carregamento inicial
    await waitFor(() => {
      expect(transferenciaService.listarTransferencias).toHaveBeenCalled();
    });
    
    // Abrir filtros
    await userEvent.click(screen.getByText('Filtros'));
    
    // Preencher filtros
    const dataInicio = screen.getByLabelText('Data Início');
    await userEvent.clear(dataInicio);
    await userEvent.type(dataInicio, '2023-11-01');
    
    const dataFim = screen.getByLabelText('Data Fim');
    await userEvent.clear(dataFim);
    await userEvent.type(dataFim, '2023-11-06');
    
    // Selecionar conta origem (primeiro deve buscar contas)
    await waitFor(() => {
      expect(contaBancariaService.listarContasBancarias).toHaveBeenCalled();
    });
    
    // Selecionar os filtros de conta
    const contaOrigemSelect = screen.getByLabelText('Conta Origem');
    await userEvent.selectOptions(contaOrigemSelect, 'Banco do Brasil');
    
    const contaDestinoSelect = screen.getByLabelText('Conta Destino');
    await userEvent.selectOptions(contaDestinoSelect, 'Caixa Econômica');
    
    // Clicar em aplicar
    await userEvent.click(screen.getByText('Aplicar'));
    
    // Verificar se a função de filtrar foi chamada com os parâmetros corretos
    await waitFor(() => {
      expect(transferenciaService.filtrarTransferencias).toHaveBeenCalledWith({
        dataInicio: '2023-11-01',
        dataFim: '2023-11-06',
        contaOrigem: 'Banco do Brasil',
        contaDestino: 'Caixa Econômica'
      });
    });
    
    // Verificar se apenas os resultados filtrados são exibidos
    const { showInfoToast } = (await import('../../hooks/useToast')).useToastUtils();
    expect(showInfoToast).toHaveBeenCalledWith(
      expect.stringMatching(/1 transferência\(s\) encontrada\(s\)/)
    );
  });
  
  // 3. Validação de formulário com regra: conta origem ≠ destino
  it('deve validar que a conta de origem não pode ser igual à de destino', async () => {
    // Renderizar o componente
    renderWithProviders(<TransferenciasContas />);
    
    // Abrir modal de nova transferência
    await userEvent.click(screen.getByText('Nova Transferência'));
    
    // Aguardar carregamento das contas
    await waitFor(() => {
      expect(contaBancariaService.listarContasBancarias).toHaveBeenCalled();
    });
    
    // Preencher o formulário com a mesma conta de origem e destino
    const contaOrigemSelect = screen.getByLabelText('Conta de Origem:');
    await userEvent.selectOptions(contaOrigemSelect, '1'); // Primeira conta
    
    const contaDestinoSelect = screen.getByLabelText('Conta de Destino:');
    await userEvent.selectOptions(contaDestinoSelect, '1'); // Mesma conta
    
    // Preencher outros campos obrigatórios
    const valorInput = screen.getByLabelText('Valor (R$)');
    await userEvent.clear(valorInput);
    await userEvent.type(valorInput, '1000');
    
    // Tentar enviar o formulário
    await userEvent.click(screen.getByText('Salvar'));
    
    // Verificar se as mensagens de erro são exibidas
    await waitFor(() => {
      expect(screen.getByText('A conta de origem não pode ser igual à conta de destino')).toBeInTheDocument();
      expect(screen.getByText('A conta de destino não pode ser igual à conta de origem')).toBeInTheDocument();
    });
    
    // Verificar que a função de cadastrar não foi chamada
    expect(transferenciaService.cadastrarTransferencia).not.toHaveBeenCalled();
  });
  
  // 4. Teste de envio com dados válidos
  it('deve enviar o formulário com dados válidos', async () => {
    // Renderizar o componente
    renderWithProviders(<TransferenciasContas />);
    
    // Abrir modal de nova transferência
    await userEvent.click(screen.getByText('Nova Transferência'));
    
    // Aguardar carregamento das contas
    await waitFor(() => {
      expect(contaBancariaService.listarContasBancarias).toHaveBeenCalled();
    });
    
    // Preencher o formulário com dados válidos
    const contaOrigemSelect = screen.getByLabelText('Conta de Origem:');
    await userEvent.selectOptions(contaOrigemSelect, '1'); // Primeira conta
    
    const contaDestinoSelect = screen.getByLabelText('Conta de Destino:');
    await userEvent.selectOptions(contaDestinoSelect, '2'); // Segunda conta
    
    const valorInput = screen.getByLabelText('Valor (R$)');
    await userEvent.clear(valorInput);
    await userEvent.type(valorInput, '1000');
    
    const dataInput = screen.getByLabelText('Data');
    await userEvent.clear(dataInput);
    await userEvent.type(dataInput, '2023-11-15');
    
    const observacaoInput = screen.getByLabelText('Observação:');
    await userEvent.type(observacaoInput, 'Transferência de teste');
    
    // Enviar o formulário
    await userEvent.click(screen.getByText('Salvar'));
    
    // Simular confirmação do diálogo
    const useConfirmDialogMock = (await import('../../hooks/useConfirmDialog')).useConfirmDialog;
    await (useConfirmDialogMock as any)()._simulateConfirm();
    
    // Verificar se a função de cadastrar foi chamada com os dados corretos
    await waitFor(() => {
      expect(transferenciaService.cadastrarTransferencia).toHaveBeenCalledWith({
        data: '2023-11-15',
        conta_origem: 'Banco do Brasil',
        conta_destino: 'Caixa Econômica',
        valor: 1000,
        status: 'Pendente',
        observacao: 'Transferência de teste'
      });
    });
  });
  
  // 5. Toast de sucesso e erro
  it('deve exibir toast de sucesso ao cadastrar com sucesso', async () => {
    // Renderizar o componente
    renderWithProviders(<TransferenciasContas />);
    
    // Abrir modal de nova transferência
    await userEvent.click(screen.getByText('Nova Transferência'));
    
    // Aguardar carregamento das contas
    await waitFor(() => {
      expect(contaBancariaService.listarContasBancarias).toHaveBeenCalled();
    });
    
    // Preencher o formulário com dados válidos
    const contaOrigemSelect = screen.getByLabelText('Conta de Origem:');
    await userEvent.selectOptions(contaOrigemSelect, '1');
    
    const contaDestinoSelect = screen.getByLabelText('Conta de Destino:');
    await userEvent.selectOptions(contaDestinoSelect, '2');
    
    const valorInput = screen.getByLabelText('Valor (R$)');
    await userEvent.clear(valorInput);
    await userEvent.type(valorInput, '1000');
    
    const dataInput = screen.getByLabelText('Data');
    await userEvent.clear(dataInput);
    await userEvent.type(dataInput, '2023-11-15');
    
    // Obter a função showSuccessToast para verificação
    const { showSuccessToast } = (await import('../../hooks/useToast')).useToastUtils();
    
    // Enviar o formulário
    await userEvent.click(screen.getByText('Salvar'));
    
    // Simular confirmação do diálogo
    const useConfirmDialogMock = (await import('../../hooks/useConfirmDialog')).useConfirmDialog;
    await (useConfirmDialogMock as any)()._simulateConfirm();
    
    // Verificar se o toast de sucesso foi exibido
    await waitFor(() => {
      expect(showSuccessToast).toHaveBeenCalledWith(
        expect.stringContaining('Transferência cadastrada com sucesso')
      );
    });
  });
  
  it('deve exibir toast de erro quando o serviço falha', async () => {
    // Configurar mock para falhar
    vi.mocked(transferenciaService.cadastrarTransferencia).mockRejectedValue(
      new Error('Erro ao cadastrar transferência')
    );
    
    // Renderizar o componente
    renderWithProviders(<TransferenciasContas />);
    
    // Abrir modal de nova transferência
    await userEvent.click(screen.getByText('Nova Transferência'));
    
    // Aguardar carregamento das contas
    await waitFor(() => {
      expect(contaBancariaService.listarContasBancarias).toHaveBeenCalled();
    });
    
    // Preencher o formulário com dados válidos
    const contaOrigemSelect = screen.getByLabelText('Conta de Origem:');
    await userEvent.selectOptions(contaOrigemSelect, '1');
    
    const contaDestinoSelect = screen.getByLabelText('Conta de Destino:');
    await userEvent.selectOptions(contaDestinoSelect, '2');
    
    const valorInput = screen.getByLabelText('Valor (R$)');
    await userEvent.clear(valorInput);
    await userEvent.type(valorInput, '1000');
    
    const dataInput = screen.getByLabelText('Data');
    await userEvent.clear(dataInput);
    await userEvent.type(dataInput, '2023-11-15');
    
    // Obter a função showErrorToast para verificação
    const { showErrorToast } = (await import('../../hooks/useToast')).useToastUtils();
    
    // Enviar o formulário
    await userEvent.click(screen.getByText('Salvar'));
    
    // Simular confirmação do diálogo
    const useConfirmDialogMock = (await import('../../hooks/useConfirmDialog')).useConfirmDialog;
    await (useConfirmDialogMock as any)()._simulateConfirm();
    
    // Verificar se o toast de erro foi exibido
    await waitFor(() => {
      expect(showErrorToast).toHaveBeenCalledWith(
        expect.stringContaining('Erro ao cadastrar transferência')
      );
    });
  });
  
  // 6. Cancelamento e exclusão com confirmação
  it('deve cancelar a ação quando o usuário cancela o diálogo de confirmação', async () => {
    // Renderizar o componente
    renderWithProviders(<TransferenciasContas />);
    
    // Abrir modal de nova transferência
    await userEvent.click(screen.getByText('Nova Transferência'));
    
    // Aguardar carregamento das contas
    await waitFor(() => {
      expect(contaBancariaService.listarContasBancarias).toHaveBeenCalled();
    });
    
    // Preencher o formulário com dados válidos
    const contaOrigemSelect = screen.getByLabelText('Conta de Origem:');
    await userEvent.selectOptions(contaOrigemSelect, '1');
    
    const contaDestinoSelect = screen.getByLabelText('Conta de Destino:');
    await userEvent.selectOptions(contaDestinoSelect, '2');
    
    const valorInput = screen.getByLabelText('Valor (R$)');
    await userEvent.clear(valorInput);
    await userEvent.type(valorInput, '1000');
    
    const dataInput = screen.getByLabelText('Data');
    await userEvent.clear(dataInput);
    await userEvent.type(dataInput, '2023-11-15');
    
    // Enviar o formulário
    await userEvent.click(screen.getByText('Salvar'));
    
    // Simular cancelamento do diálogo
    const useConfirmDialogMock = (await import('../../hooks/useConfirmDialog')).useConfirmDialog;
    (useConfirmDialogMock as any)()._simulateCancel();
    
    // Verificar que o serviço não foi chamado
    await new Promise(resolve => setTimeout(resolve, 100)); // Pequeno delay
    expect(transferenciaService.cadastrarTransferencia).not.toHaveBeenCalled();
  });
}); 