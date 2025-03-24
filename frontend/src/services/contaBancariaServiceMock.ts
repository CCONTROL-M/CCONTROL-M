import { ContaBancaria } from "../types";

// Interface para criação de conta bancária
interface ContaBancariaCreate {
  nome: string;
  banco: string;
  agencia: string;
  conta: string;
  tipo: string;
  saldo_inicial: number;
  ativa: boolean;
  mostrar_dashboard?: boolean;
  id_empresa?: string;
}

// Dados de exemplo para contas bancárias
const contasBancariasMock: ContaBancaria[] = [
  {
    id_conta: "1",
    nome: "Conta Principal BB",
    banco: "Banco do Brasil",
    tipo: "corrente",
    conta: "12345-6",
    agencia: "1234",
    saldo_inicial: 5000.00,
    saldo_atual: 4800.00,
    ativa: true,
    mostrar_dashboard: true,
    created_at: "2023-01-10"
  },
  {
    id_conta: "2",
    nome: "Conta Itaú Empresa",
    banco: "Itaú",
    tipo: "corrente",
    conta: "98765-4",
    agencia: "5678",
    saldo_inicial: 8000.00,
    saldo_atual: 8500.00,
    ativa: true,
    mostrar_dashboard: true,
    created_at: "2023-01-15"
  },
  {
    id_conta: "3",
    nome: "Poupança Caixa",
    banco: "Caixa Econômica",
    tipo: "poupança",
    conta: "11223-3",
    agencia: "4321",
    saldo_inicial: 3000.00,
    saldo_atual: 3200.00,
    ativa: true,
    mostrar_dashboard: true,
    created_at: "2023-02-01"
  },
  {
    id_conta: "4",
    nome: "Conta Bradesco",
    banco: "Bradesco",
    tipo: "corrente",
    conta: "55667-8",
    agencia: "7890",
    saldo_inicial: -500.00,
    saldo_atual: -200.00,
    ativa: false,
    mostrar_dashboard: false,
    created_at: "2023-03-15"
  },
  {
    id_conta: "5",
    nome: "Nubank PJ",
    banco: "Nubank",
    tipo: "corrente",
    conta: "12345678-9",
    agencia: "0001",
    saldo_inicial: 12000.00,
    saldo_atual: 11500.00,
    ativa: true,
    mostrar_dashboard: true,
    created_at: "2023-04-10"
  }
];

/**
 * Simula a listagem de contas bancárias
 */
export async function listarContasBancariasMock(): Promise<ContaBancaria[]> {
  // Simula um atraso de rede
  await new Promise(resolve => setTimeout(resolve, 500));
  
  // Retorna os dados mocados
  return contasBancariasMock;
}

/**
 * Simula a busca de uma conta bancária pelo ID
 */
export async function buscarContaBancariaMock(id: string): Promise<ContaBancaria> {
  // Simula um atraso de rede
  await new Promise(resolve => setTimeout(resolve, 300));
  
  // Busca a conta bancária pelo ID
  const contaBancaria = contasBancariasMock.find(cb => cb.id_conta === id);
  
  // Se não encontrar, simula um erro
  if (!contaBancaria) {
    throw new Error("Conta bancária não encontrada");
  }
  
  return contaBancaria;
}

/**
 * Simula o cadastro de uma nova conta bancária
 */
export async function cadastrarContaBancariaMock(contaBancaria: ContaBancariaCreate): Promise<ContaBancaria> {
  // Simula um atraso de rede
  await new Promise(resolve => setTimeout(resolve, 800));
  
  // Cria uma nova conta bancária com ID gerado
  const novaContaBancaria: ContaBancaria = {
    id_conta: `conta-${Date.now()}`,
    nome: contaBancaria.nome,
    banco: contaBancaria.banco,
    tipo: contaBancaria.tipo,
    conta: contaBancaria.conta,
    agencia: contaBancaria.agencia,
    saldo_inicial: contaBancaria.saldo_inicial,
    saldo_atual: contaBancaria.saldo_inicial,
    ativa: contaBancaria.ativa ?? true,
    mostrar_dashboard: contaBancaria.mostrar_dashboard ?? true,
    created_at: new Date().toISOString().split('T')[0]
  };
  
  // Adiciona à lista de contas bancárias mock
  contasBancariasMock.push(novaContaBancaria);
  
  return novaContaBancaria;
}

/**
 * Simula a atualização de uma conta bancária
 */
export async function atualizarContaBancariaMock(id: string, contaBancaria: Partial<ContaBancariaCreate>): Promise<ContaBancaria> {
  // Simula um atraso de rede
  await new Promise(resolve => setTimeout(resolve, 600));
  
  // Busca a conta bancária pelo ID
  const index = contasBancariasMock.findIndex(cb => cb.id_conta === id);
  
  // Se não encontrar, simula um erro
  if (index === -1) {
    throw new Error("Conta bancária não encontrada");
  }
  
  // Se estiver alterando saldo_inicial, atualizar saldo_atual também
  if (contaBancaria.saldo_inicial !== undefined) {
    const diferenca = contaBancaria.saldo_inicial - contasBancariasMock[index].saldo_inicial;
    contasBancariasMock[index].saldo_atual += diferenca;
  }
  
  // Atualiza os dados da conta bancária
  contasBancariasMock[index] = {
    ...contasBancariasMock[index],
    ...contaBancaria
  };
  
  return contasBancariasMock[index];
}

/**
 * Simula a remoção de uma conta bancária
 */
export async function removerContaBancariaMock(id: string): Promise<void> {
  // Simula um atraso de rede
  await new Promise(resolve => setTimeout(resolve, 400));
  
  // Busca a conta bancária pelo ID
  const index = contasBancariasMock.findIndex(cb => cb.id_conta === id);
  
  // Se não encontrar, simula um erro
  if (index === -1) {
    throw new Error("Conta bancária não encontrada");
  }
  
  // Remove a conta bancária da lista
  contasBancariasMock.splice(index, 1);
}

export default {
  listarContasBancarias: listarContasBancariasMock,
  buscarContaBancaria: buscarContaBancariaMock,
  cadastrarContaBancaria: cadastrarContaBancariaMock,
  atualizarContaBancaria: atualizarContaBancariaMock,
  removerContaBancaria: removerContaBancariaMock
}; 