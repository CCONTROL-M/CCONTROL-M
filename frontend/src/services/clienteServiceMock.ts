import { Cliente } from "../types";

// Dados de exemplo para clientes
const clientesMock: Cliente[] = [
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

/**
 * Simula a listagem de clientes
 */
export async function listarClientesMock(): Promise<Cliente[]> {
  // Simula um atraso de rede
  await new Promise(resolve => setTimeout(resolve, 500));
  
  // Retorna os dados mocados
  return clientesMock;
}

/**
 * Simula a busca de um cliente pelo ID
 */
export async function buscarClienteMock(id: string): Promise<Cliente> {
  // Simula um atraso de rede
  await new Promise(resolve => setTimeout(resolve, 300));
  
  // Busca o cliente pelo ID
  const cliente = clientesMock.find(c => c.id_cliente === id);
  
  // Se não encontrar, simula um erro
  if (!cliente) {
    throw new Error("Cliente não encontrado");
  }
  
  return cliente;
}

/**
 * Simula o cadastro de um novo cliente
 */
export async function cadastrarClienteMock(cliente: Omit<Cliente, 'id_cliente' | 'created_at'>): Promise<Cliente> {
  // Simula um atraso de rede
  await new Promise(resolve => setTimeout(resolve, 800));
  
  // Cria um novo cliente com ID gerado
  const novoCliente: Cliente = {
    id_cliente: `cliente-${Date.now()}`,
    nome: cliente.nome,
    cpf_cnpj: cliente.cpf_cnpj,
    contato: cliente.contato,
    created_at: new Date().toISOString().split('T')[0]
  };
  
  // Adiciona à lista de clientes mock
  clientesMock.push(novoCliente);
  
  return novoCliente;
}

/**
 * Simula a atualização de um cliente
 */
export async function atualizarClienteMock(id: string, cliente: Partial<Cliente>): Promise<Cliente> {
  // Simula um atraso de rede
  await new Promise(resolve => setTimeout(resolve, 600));
  
  // Busca o cliente pelo ID
  const index = clientesMock.findIndex(c => c.id_cliente === id);
  
  // Se não encontrar, simula um erro
  if (index === -1) {
    throw new Error("Cliente não encontrado");
  }
  
  // Atualiza os dados do cliente
  clientesMock[index] = {
    ...clientesMock[index],
    ...cliente
  };
  
  return clientesMock[index];
}

/**
 * Simula a remoção de um cliente
 */
export async function removerClienteMock(id: string): Promise<void> {
  // Simula um atraso de rede
  await new Promise(resolve => setTimeout(resolve, 400));
  
  // Busca o cliente pelo ID
  const index = clientesMock.findIndex(c => c.id_cliente === id);
  
  // Se não encontrar, simula um erro
  if (index === -1) {
    throw new Error("Cliente não encontrado");
  }
  
  // Remove o cliente da lista
  clientesMock.splice(index, 1);
}

export default {
  listarClientes: listarClientesMock,
  buscarCliente: buscarClienteMock,
  cadastrarCliente: cadastrarClienteMock,
  atualizarCliente: atualizarClienteMock,
  removerCliente: removerClienteMock
}; 