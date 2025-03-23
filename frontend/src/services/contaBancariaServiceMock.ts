import { ContaBancaria } from "../types";

// Dados de exemplo para contas bancárias
const contasBancariasMock: ContaBancaria[] = [
  {
    id_conta: "1",
    nome: "Conta Principal BB",
    banco: "Banco do Brasil",
    tipo: "Conta Corrente",
    numero: "12345-6",
    agencia: "1234",
    saldo_inicial: 5000.00,
    created_at: "2023-01-10"
  },
  {
    id_conta: "2",
    nome: "Conta Itaú Empresa",
    banco: "Itaú",
    tipo: "Conta Corrente",
    numero: "98765-4",
    agencia: "5678",
    saldo_inicial: 8000.00,
    created_at: "2023-01-15"
  },
  {
    id_conta: "3",
    nome: "Poupança Caixa",
    banco: "Caixa Econômica",
    tipo: "Poupança",
    numero: "11223-3",
    agencia: "4321",
    saldo_inicial: 3000.00,
    created_at: "2023-02-01"
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
export async function cadastrarContaBancariaMock(contaBancaria: Omit<ContaBancaria, 'id_conta' | 'created_at'>): Promise<ContaBancaria> {
  // Simula um atraso de rede
  await new Promise(resolve => setTimeout(resolve, 800));
  
  // Cria uma nova conta bancária com ID gerado
  const novaContaBancaria: ContaBancaria = {
    id_conta: `conta-${Date.now()}`,
    nome: contaBancaria.nome,
    banco: contaBancaria.banco,
    tipo: contaBancaria.tipo,
    numero: contaBancaria.numero,
    agencia: contaBancaria.agencia,
    saldo_inicial: contaBancaria.saldo_inicial,
    created_at: new Date().toISOString().split('T')[0]
  };
  
  // Adiciona à lista de contas bancárias mock
  contasBancariasMock.push(novaContaBancaria);
  
  return novaContaBancaria;
}

/**
 * Simula a atualização de uma conta bancária
 */
export async function atualizarContaBancariaMock(id: string, contaBancaria: Partial<ContaBancaria>): Promise<ContaBancaria> {
  // Simula um atraso de rede
  await new Promise(resolve => setTimeout(resolve, 600));
  
  // Busca a conta bancária pelo ID
  const index = contasBancariasMock.findIndex(cb => cb.id_conta === id);
  
  // Se não encontrar, simula um erro
  if (index === -1) {
    throw new Error("Conta bancária não encontrada");
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