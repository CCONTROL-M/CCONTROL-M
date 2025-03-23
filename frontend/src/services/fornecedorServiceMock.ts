import { Fornecedor } from "../types";

// Função simples para gerar ID único
const gerarId = () => {
  return `f${Date.now().toString(36)}${Math.random().toString(36).substr(2, 5)}`;
};

// Dados mock de fornecedores
const fornecedoresMock: Fornecedor[] = [
  {
    id_fornecedor: "f1",
    nome: "Fornecedor Exemplo 1",
    cnpj: "12345678000190",
    contato: "(11) 9876-5432",
    avaliacao: "Ótimo",
    created_at: "2023-08-10T10:30:00Z"
  },
  {
    id_fornecedor: "f2",
    nome: "Fornecedor Exemplo 2",
    cnpj: "98765432000121",
    contato: "(11) 1234-5678",
    avaliacao: "Bom",
    created_at: "2023-09-15T08:45:00Z"
  },
  {
    id_fornecedor: "f3",
    nome: "Fornecedor Exemplo 3",
    cnpj: "45678912000134",
    contato: "(21) 9876-4321",
    avaliacao: "Regular",
    created_at: "2023-10-20T14:20:00Z"
  }
];

/**
 * Simula a listagem de fornecedores
 */
export async function listarFornecedoresMock(): Promise<Fornecedor[]> {
  // Simula um atraso de rede
  await new Promise(resolve => setTimeout(resolve, 500));
  
  // Retorna uma cópia do array de fornecedores
  return [...fornecedoresMock];
}

/**
 * Simula a busca de um fornecedor pelo ID
 */
export async function buscarFornecedorMock(id: string): Promise<Fornecedor> {
  // Simula um atraso de rede
  await new Promise(resolve => setTimeout(resolve, 300));
  
  // Busca o fornecedor pelo ID
  const fornecedor = fornecedoresMock.find(f => f.id_fornecedor === id);
  
  // Se não encontrar, simula um erro
  if (!fornecedor) {
    throw new Error("Fornecedor não encontrado");
  }
  
  return { ...fornecedor };
}

/**
 * Simula o cadastro de um novo fornecedor
 */
export async function cadastrarFornecedorMock(fornecedor: Omit<Fornecedor, "id_fornecedor">): Promise<Fornecedor> {
  // Simula um atraso de rede
  await new Promise(resolve => setTimeout(resolve, 800));
  
  // Cria um novo fornecedor com ID gerado
  const novoFornecedor: Fornecedor = {
    ...fornecedor,
    id_fornecedor: gerarId(),
    created_at: new Date().toISOString()
  };
  
  // Adiciona à lista de fornecedores mock
  fornecedoresMock.push(novoFornecedor);
  
  return { ...novoFornecedor };
}

/**
 * Simula a atualização de um fornecedor
 */
export async function atualizarFornecedorMock(id: string, dados: Partial<Fornecedor>): Promise<Fornecedor> {
  // Simula um atraso de rede
  await new Promise(resolve => setTimeout(resolve, 600));
  
  // Busca o fornecedor pelo ID
  const index = fornecedoresMock.findIndex(f => f.id_fornecedor === id);
  
  // Se não encontrar, simula um erro
  if (index === -1) {
    throw new Error("Fornecedor não encontrado");
  }
  
  // Atualiza o fornecedor
  fornecedoresMock[index] = {
    ...fornecedoresMock[index],
    ...dados
  };
  
  return { ...fornecedoresMock[index] };
}

/**
 * Simula a remoção de um fornecedor
 */
export async function removerFornecedorMock(id: string): Promise<void> {
  // Simula um atraso de rede
  await new Promise(resolve => setTimeout(resolve, 700));
  
  // Busca o fornecedor pelo ID
  const index = fornecedoresMock.findIndex(f => f.id_fornecedor === id);
  
  // Se não encontrar, simula um erro
  if (index === -1) {
    throw new Error("Fornecedor não encontrado");
  }
  
  // Remove o fornecedor do array
  fornecedoresMock.splice(index, 1);
} 