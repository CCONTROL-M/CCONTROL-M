import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import DRE from '../../pages/DRE';
import { renderWithProviders } from '../utils/test-utils';
import * as relatorioService from '../../services/relatorioService';
import * as relatorioServiceMock from '../../services/relatorioServiceMock';
import * as mockUtils from '../../utils/mock';
import * as apiService from '../../services/api';

// Mock dos hooks e serviços
vi.mock('../../services/relatorioService');
vi.mock('../../services/relatorioServiceMock');
vi.mock('../../utils/mock');
vi.mock('../../services/api');

// Mock dos hooks
vi.mock('../../hooks/useToast', () => {
  const showToast = vi.fn();
  const showSuccessToast = vi.fn();
  const showErrorToast = vi.fn();

  return {
    useToast: () => ({ 
      showToast 
    }),
    useToastUtils: () => ({
      showSuccessToast,
      showErrorToast,
    }),
    ToastProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  };
});

// Dados de teste para o DRE
const dreMockData = {
  receitas: [
    { categoria: 'Vendas de Produtos', valor: 42500 },
    { categoria: 'Prestação de Serviços', valor: 18700 },
    { categoria: 'Comissões', valor: 3200 },
    { categoria: 'Outras Receitas', valor: 2100 }
  ],
  despesas: [
    { categoria: 'Custos dos Produtos', valor: 15800 },
    { categoria: 'Folha de Pagamento', valor: 12450 },
    { categoria: 'Aluguel', valor: 4800 },
    { categoria: 'Energia/Internet', valor: 2350 },
    { categoria: 'Materiais de Escritório', valor: 950 },
    { categoria: 'Marketing', valor: 3500 },
    { categoria: 'Comissões Pagas', valor: 2100 },
    { categoria: 'Impostos', valor: 6300 },
    { categoria: 'Outras Despesas', valor: 1650 }
  ],
  lucro_prejuizo: 16600 // Receitas - Despesas
};

describe('DRE', () => {
  beforeEach(() => {
    // Resetar todos os mocks
    vi.resetAllMocks();
    
    // Mock useMock para retornar false por padrão (não usar mock)
    vi.mocked(mockUtils.useMock).mockReturnValue(false);
    
    // Mock da verificação de API para retornar que está online
    vi.mocked(apiService.verificarStatusAPI).mockResolvedValue({ online: true, error: null });
    
    // Mock das funções dos serviços de relatório
    vi.mocked(relatorioService.buscarDREPeriodo).mockResolvedValue(dreMockData);
    vi.mocked(relatorioServiceMock.buscarDREPeriodoMock).mockResolvedValue(dreMockData);
  });
  
  afterEach(() => {
    vi.restoreAllMocks();
  });
  
  // Teste 1: Renderização da página com filtro de período
  it('deve renderizar a página com filtro de período', async () => {
    // Renderizar o componente
    renderWithProviders(<DRE />);
    
    // Verificar o título da página
    expect(screen.getByText('DRE')).toBeInTheDocument();
    expect(screen.getByText('Demonstrativo de Resultados (DRE)')).toBeInTheDocument();
    
    // Verificar se os filtros estão presentes (inicialmente ocultos)
    expect(screen.getByText('Exibir Filtros')).toBeInTheDocument();
    
    // Clicar no botão para exibir filtros
    await userEvent.click(screen.getByText('Exibir Filtros'));
    
    // Verificar se os filtros foram exibidos
    expect(screen.getByText('Filtros')).toBeInTheDocument();
    expect(screen.getByLabelText('Data Início')).toBeInTheDocument();
    expect(screen.getByLabelText('Data Fim')).toBeInTheDocument();
    
    // Verificar se os botões de ação estão presentes
    expect(screen.getByText('Limpar')).toBeInTheDocument();
    expect(screen.getByText('Atualizar')).toBeInTheDocument();
  });
  
  // Teste 2: Chamada ao relatorioService com os parâmetros corretos
  it('deve chamar relatorioService com os parâmetros corretos', async () => {
    // Data atual para verificação
    const hoje = new Date();
    const inicioMes = new Date(hoje.getFullYear(), hoje.getMonth(), 1);
    
    const dataInicio = inicioMes.toISOString().split('T')[0];
    const dataFim = hoje.toISOString().split('T')[0];
    
    // Renderizar o componente
    renderWithProviders(<DRE />);
    
    // Aguardar a chamada do serviço
    await waitFor(() => {
      expect(relatorioService.buscarDREPeriodo).toHaveBeenCalledWith({
        dataInicio,
        dataFim
      });
    });
    
    // Abrir filtros e mudar os valores
    await userEvent.click(screen.getByText('Exibir Filtros'));
    
    // Definir novas datas nos inputs
    const novaDataInicio = '2023-01-01';
    const novaDataFim = '2023-01-31';
    
    // Limpar e inserir novas datas
    const inputDataInicio = screen.getByLabelText('Data Início');
    await userEvent.clear(inputDataInicio);
    await userEvent.type(inputDataInicio, novaDataInicio);
    
    const inputDataFim = screen.getByLabelText('Data Fim');
    await userEvent.clear(inputDataFim);
    await userEvent.type(inputDataFim, novaDataFim);
    
    // Clicar em atualizar
    await userEvent.click(screen.getByText('Atualizar'));
    
    // Verificar se o serviço foi chamado com os novos parâmetros
    await waitFor(() => {
      expect(relatorioService.buscarDREPeriodo).toHaveBeenCalledWith({
        dataInicio: novaDataInicio,
        dataFim: novaDataFim
      });
    });
  });
  
  // Teste 3: Teste da exibição do resultado líquido
  it('deve exibir o resultado líquido corretamente', async () => {
    // Renderizar o componente
    renderWithProviders(<DRE />);
    
    // Aguardar o carregamento dos dados
    await waitFor(() => {
      expect(relatorioService.buscarDREPeriodo).toHaveBeenCalled();
    });
    
    // Verificar se o resultado líquido é exibido corretamente
    await waitFor(() => {
      expect(screen.getByText('Resultado Líquido')).toBeInTheDocument();
      expect(screen.getByText('Lucro do período')).toBeInTheDocument();
      // O valor formatado como moeda deve conter R$ e o valor do lucro_prejuizo
      expect(screen.getByText(/R\$ 16.600,00/)).toBeInTheDocument();
    });
  });
  
  // Teste 4: Teste de loading enquanto carrega
  it('deve mostrar indicador de loading enquanto carrega', async () => {
    // Simular uma resposta lenta
    vi.mocked(relatorioService.buscarDREPeriodo).mockImplementation(async () => {
      await new Promise(resolve => setTimeout(resolve, 100));
      return dreMockData;
    });
    
    // Renderizar o componente
    renderWithProviders(<DRE />);
    
    // Verificar se o loading é exibido
    expect(screen.getByText(/Carregando/i)).toBeInTheDocument();
    
    // Aguardar o carregamento dos dados
    await waitFor(() => {
      expect(screen.queryByText(/Carregando/i)).not.toBeInTheDocument();
      expect(relatorioService.buscarDREPeriodo).toHaveBeenCalled();
    });
  });
  
  // Teste 5: Teste de mensagem de erro caso a API falhe
  it('deve exibir mensagem de erro caso a API falhe', async () => {
    // Forçar erro na API
    vi.mocked(relatorioService.buscarDREPeriodo).mockRejectedValue(
      new Error('Erro ao buscar dados do DRE')
    );
    
    // Renderizar o componente
    renderWithProviders(<DRE />);
    
    // Aguardar a chamada da API e verificar o erro
    await waitFor(() => {
      expect(screen.getByText('Erro ao buscar dados do DRE')).toBeInTheDocument();
      expect(screen.getByText('Tentar novamente')).toBeInTheDocument();
    });
    
    // Clicar em tentar novamente
    await userEvent.click(screen.getByText('Tentar novamente'));
    
    // Verificar se a API foi chamada novamente
    expect(relatorioService.buscarDREPeriodo).toHaveBeenCalledTimes(2);
  });
  
  // Teste 6: Teste da renderização dos grupos de categorias
  it('deve renderizar os grupos de categorias corretamente', async () => {
    // Renderizar o componente
    renderWithProviders(<DRE />);
    
    // Aguardar o carregamento dos dados
    await waitFor(() => {
      expect(relatorioService.buscarDREPeriodo).toHaveBeenCalled();
    });
    
    // Verificar se os títulos das seções estão presentes
    await waitFor(() => {
      // Verificar seções de receitas
      expect(screen.getByText('Receitas')).toBeInTheDocument();
      expect(screen.getByText('Receitas Operacionais')).toBeInTheDocument();
      expect(screen.getByText('Outras Receitas')).toBeInTheDocument();
      
      // Verificar seções de despesas
      expect(screen.getByText('Despesas')).toBeInTheDocument();
      expect(screen.getByText('Custos Operacionais')).toBeInTheDocument();
      expect(screen.getByText('Despesas Administrativas')).toBeInTheDocument();
      expect(screen.getByText('Despesas Comerciais')).toBeInTheDocument();
      expect(screen.getByText('Impostos e Taxas')).toBeInTheDocument();
      expect(screen.getByText('Outras Despesas')).toBeInTheDocument();
      
      // Verificar uma categoria específica de receita
      expect(screen.getByText('Vendas de Produtos')).toBeInTheDocument();
      expect(screen.getByText('Prestação de Serviços')).toBeInTheDocument();
      
      // Verificar uma categoria específica de despesa
      expect(screen.getByText('Custos dos Produtos')).toBeInTheDocument();
      expect(screen.getByText('Folha de Pagamento')).toBeInTheDocument();
    });
  });
  
  // Teste adicional: Verificar mudança para dados mock quando a API está offline
  it('deve usar dados mock quando a API está offline', async () => {
    // Simular API offline
    vi.mocked(apiService.verificarStatusAPI).mockResolvedValue({ online: false, error: null });
    vi.mocked(mockUtils.useMock).mockReturnValue(true);
    
    // Renderizar o componente
    renderWithProviders(<DRE />);
    
    // Aguardar o carregamento dos dados
    await waitFor(() => {
      // Verificar se a mensagem de modo demonstração é exibida
      expect(screen.getByText(/Modo de demonstração/i)).toBeInTheDocument();
      // Verificar se o serviço mock foi chamado
      expect(relatorioServiceMock.buscarDREPeriodoMock).toHaveBeenCalled();
    });
  });
}); 