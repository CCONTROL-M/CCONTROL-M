/**
 * Serviço de relatórios mock para desenvolvimento
 */

import { ResumoDashboard, DREData, FluxoItem, FluxoGrupo, Inadimplente, Ciclo, CategoriaValor } from '../types';

/**
 * Mock de dados para o dashboard
 */
export async function buscarResumoDashboardMock(): Promise<ResumoDashboard> {
  // Simula um delay de rede
  await new Promise(resolve => setTimeout(resolve, 800));
  
  return {
    caixa_atual: 23574.85,
    total_receber: 45678.23,
    total_pagar: 12987.67,
    recebimentos_hoje: 2350.00,
    pagamentos_hoje: 1875.45
  };
}

/**
 * Mock de dados para DRE
 */
export async function buscarDREMock(): Promise<DREData> {
  console.log("Buscando dados de DRE mockados...");
  
  // Simular um tempo de resposta (reduzido para 300ms)
  await new Promise(resolve => setTimeout(resolve, 300));
  
  return {
    receitas: [
      { categoria: 'Vendas', valor: 35000 },
      { categoria: 'Serviços', valor: 15000 }
    ],
    despesas: [
      { categoria: 'Operacionais', valor: 12000 },
      { categoria: 'Administrativas', valor: 8000 },
      { categoria: 'Financeiras', valor: 3000 }
    ],
    lucro_prejuizo: 27000
  };
}

/**
 * Mock de dados para Fluxo de Caixa
 */
export async function buscarFluxoCaixaMock(): Promise<FluxoGrupo[]> {
  // Simula um delay de rede
  await new Promise(resolve => setTimeout(resolve, 600));
  
  return [
    { 
      data: '2023-04-01', 
      itens: [
        { descricao: 'Vendas à vista', valor: 25000, data: '2023-04-15', tipo: 'receita' },
        { descricao: 'Recebimento de clientes', valor: 20000, data: '2023-04-18', tipo: 'receita' }
      ]
    },
    { 
      data: '2023-04-02',
      itens: [
        { descricao: 'Folha de pagamento', valor: 15000, data: '2023-04-05', tipo: 'despesa' },
        { descricao: 'Fornecedores', valor: 10000, data: '2023-04-10', tipo: 'despesa' },
        { descricao: 'Aluguel', valor: 5000, data: '2023-04-01', tipo: 'despesa' }
      ]
    }
  ];
}

/**
 * Mock de dados para Inadimplência
 */
export async function buscarInadimplenciaMock(): Promise<Inadimplente[]> {
  // Simula um delay de rede
  await new Promise(resolve => setTimeout(resolve, 700));
  
  return [
    { 
      id_parcela: '101',
      cliente: 'Cliente A',
      valor: 2500,
      vencimento: '2023-03-15',
      dias_em_atraso: 30
    },
    {
      id_parcela: '102',
      cliente: 'Cliente A',
      valor: 2500,
      vencimento: '2023-04-15',
      dias_em_atraso: 5
    },
    { 
      id_parcela: '201',
      cliente: 'Cliente B',
      valor: 3800,
      vencimento: '2023-04-10',
      dias_em_atraso: 10
    }
  ];
}

/**
 * Mock de dados para Ciclo Operacional
 */
export async function buscarCicloOperacionalMock(): Promise<Ciclo[]> {
  console.log("Buscando dados de Ciclo Operacional mockados...");
  
  // Simular um tempo de resposta (reduzido para 300ms)
  await new Promise(resolve => setTimeout(resolve, 300));
  
  console.log('Gerando dados mock para ciclo operacional');
  
  return [
    { 
      cliente: 'Cliente A',
      data_pedido: '2023-03-10',
      data_faturamento: '2023-03-13',
      data_recebimento: '2023-03-28',
      dias_entre: 18
    },
    { 
      cliente: 'Cliente B',
      data_pedido: '2023-03-15',
      data_faturamento: '2023-03-17',
      data_recebimento: '2023-04-16',
      dias_entre: 32
    },
    { 
      cliente: 'Cliente C',
      data_pedido: '2023-03-20',
      data_faturamento: '2023-03-25',
      data_recebimento: '2023-04-14',
      dias_entre: 25
    },
    {
      cliente: 'Cliente D',
      data_pedido: '2023-04-05',
      data_faturamento: '2023-04-08',
      data_recebimento: '2023-04-23',
      dias_entre: 18
    },
    {
      cliente: 'Cliente E',
      data_pedido: '2023-04-12',
      data_faturamento: '2023-04-15',
      data_recebimento: '2023-05-05',
      dias_entre: 23
    },
    {
      cliente: 'Cliente F',
      data_pedido: '2023-04-18',
      data_faturamento: '2023-04-20',
      data_recebimento: '2023-05-15',
      dias_entre: 27
    },
    {
      cliente: 'Cliente G',
      data_pedido: '2023-04-22',
      data_faturamento: '2023-04-25',
      data_recebimento: '2023-05-10',
      dias_entre: 18
    },
    {
      cliente: 'Cliente H',
      data_pedido: '2023-04-28',
      data_faturamento: '2023-05-02',
      data_recebimento: '2023-05-22',
      dias_entre: 24
    },
    {
      cliente: 'Cliente I',
      data_pedido: '2023-05-05',
      data_faturamento: '2023-05-08',
      data_recebimento: '2023-05-28',
      dias_entre: 23
    },
    {
      cliente: 'Cliente J',
      data_pedido: '2023-05-12',
      data_faturamento: '2023-05-15',
      data_recebimento: '2023-06-05',
      dias_entre: 24
    },
    {
      cliente: 'Cliente K',
      data_pedido: '2023-05-18',
      data_faturamento: '2023-05-20',
      data_recebimento: '2023-06-10',
      dias_entre: 23
    },
    {
      cliente: 'Cliente L',
      data_pedido: '2023-05-22',
      data_faturamento: '2023-05-25',
      data_recebimento: '2023-06-15',
      dias_entre: 24
    }
  ];
}

/**
 * Mock de dados para Fluxo de Caixa com filtros (retorna os mesmos dados do mock padrão)
 */
export async function buscarFluxoCaixaFiltradoMock(): Promise<FluxoGrupo[]> {
  return buscarFluxoCaixaMock();
}

/**
 * Mock de dados para DRE com filtros de período
 */
export async function buscarDREPeriodoMock(periodo?: { 
  dataInicio: string; 
  dataFim: string;
}): Promise<DREData> {
  console.log(`Buscando DRE mockado para período: ${periodo?.dataInicio} a ${periodo?.dataFim}`);
  
  // Simular um tempo de resposta (reduzido para 300ms)
  await new Promise(resolve => setTimeout(resolve, 300));
  
  console.log('Gerando dados mock para DRE com período:', periodo);
  
  // Versão mais completa do DRE com mais categorias
  return {
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
    lucro_prejuizo: 66500 - 49900 // Receitas - Despesas = 16600
  };
} 