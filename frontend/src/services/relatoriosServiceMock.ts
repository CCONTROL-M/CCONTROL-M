import { 
  Inadimplente, 
  FluxoItem, 
  DREData, 
  CategoriaValor, 
  Ciclo 
} from "../types";

// Mock para relatório de Inadimplência
export async function obterRelatorioInadimplenciaMock(): Promise<Inadimplente[]> {
  await new Promise(resolve => setTimeout(resolve, 800));
  
  return [
    {
      id_parcela: "1",
      cliente: "Empresa ABC Ltda",
      valor: 1580.00,
      vencimento: "2023-03-10",
      dias_em_atraso: 23
    },
    {
      id_parcela: "2",
      cliente: "João Silva MEI",
      valor: 450.00,
      vencimento: "2023-03-15",
      dias_em_atraso: 18
    },
    {
      id_parcela: "3",
      cliente: "Distribuidora XYZ",
      valor: 2300.00,
      vencimento: "2023-03-20",
      dias_em_atraso: 13
    },
    {
      id_parcela: "4",
      cliente: "Supermercado BemBom",
      valor: 3450.00,
      vencimento: "2023-03-25",
      dias_em_atraso: 8
    },
    {
      id_parcela: "5",
      cliente: "Maria Confecções ME",
      valor: 980.00,
      vencimento: "2023-03-30",
      dias_em_atraso: 3
    }
  ];
}

// Mock para relatório de Fluxo de Caixa
export async function obterRelatorioFluxoCaixaMock(): Promise<FluxoItem[]> {
  await new Promise(resolve => setTimeout(resolve, 700));
  
  return [
    {
      data: "2023-03-01",
      tipo: "receita",
      descricao: "Recebimento Cliente A",
      valor: 2500.00
    },
    {
      data: "2023-03-01",
      tipo: "despesa",
      descricao: "Pagamento Fornecedor X",
      valor: -1200.00
    },
    {
      data: "2023-03-02",
      tipo: "receita",
      descricao: "Recebimento Cliente B",
      valor: 1800.00
    },
    {
      data: "2023-03-03",
      tipo: "despesa",
      descricao: "Aluguel",
      valor: -2000.00
    },
    {
      data: "2023-03-03",
      tipo: "despesa",
      descricao: "Conta de Luz",
      valor: -450.00
    },
    {
      data: "2023-03-05",
      tipo: "receita",
      descricao: "Venda à Vista",
      valor: 1250.00
    },
    {
      data: "2023-03-05",
      tipo: "despesa",
      descricao: "Materiais de Escritório",
      valor: -180.00
    },
    {
      data: "2023-03-08",
      tipo: "receita",
      descricao: "Recebimento Cliente C",
      valor: 3200.00
    }
  ];
}

// Mock para relatório de DRE
export async function obterRelatorioDREMock(): Promise<DREData> {
  await new Promise(resolve => setTimeout(resolve, 900));
  
  const receitas: CategoriaValor[] = [
    { categoria: "Vendas de Produtos", valor: 45000.00 },
    { categoria: "Prestação de Serviços", valor: 28000.00 },
    { categoria: "Comissões", valor: 7500.00 },
    { categoria: "Outras Receitas", valor: 3200.00 }
  ];
  
  const despesas: CategoriaValor[] = [
    { categoria: "Custos dos Produtos", valor: 20000.00 },
    { categoria: "Folha de Pagamento", valor: 18000.00 },
    { categoria: "Aluguel", valor: 5000.00 },
    { categoria: "Energia/Internet", valor: 2800.00 },
    { categoria: "Marketing", valor: 4500.00 },
    { categoria: "Impostos", valor: 12000.00 },
    { categoria: "Outras Despesas", valor: 3600.00 }
  ];
  
  const totalReceitas = receitas.reduce((sum, item) => sum + item.valor, 0);
  const totalDespesas = despesas.reduce((sum, item) => sum + item.valor, 0);
  const lucroPrejuizo = totalReceitas - totalDespesas;
  
  return {
    receitas,
    despesas,
    lucro_prejuizo: lucroPrejuizo
  };
}

// Mock para relatório de Ciclo Operacional
export async function obterRelatorioCicloOperacionalMock(): Promise<Ciclo[]> {
  await new Promise(resolve => setTimeout(resolve, 600));
  
  return [
    {
      cliente: "Empresa ABC Ltda",
      data_pedido: "2023-02-05",
      data_faturamento: "2023-02-10",
      data_recebimento: "2023-03-10",
      dias_entre: 33
    },
    {
      cliente: "Distribuidora XYZ",
      data_pedido: "2023-02-08",
      data_faturamento: "2023-02-12",
      data_recebimento: "2023-03-15",
      dias_entre: 35
    },
    {
      cliente: "Supermercado BemBom",
      data_pedido: "2023-02-10",
      data_faturamento: "2023-02-15",
      data_recebimento: "2023-03-05",
      dias_entre: 23
    },
    {
      cliente: "Maria Confecções ME",
      data_pedido: "2023-02-15",
      data_faturamento: "2023-02-20",
      data_recebimento: "2023-03-20",
      dias_entre: 33
    },
    {
      cliente: "Tech Solutions SA",
      data_pedido: "2023-02-18",
      data_faturamento: "2023-02-22",
      data_recebimento: "2023-03-22",
      dias_entre: 32
    }
  ];
} 