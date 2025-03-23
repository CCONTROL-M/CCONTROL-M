import { Categoria } from "../types";

// Dados de exemplo para categorias
const categoriasMock: Categoria[] = [
  {
    id_categoria: "1",
    nome: "Vendas",
    tipo: "receita"
  },
  {
    id_categoria: "2",
    nome: "Serviços",
    tipo: "receita"
  },
  {
    id_categoria: "3",
    nome: "Água e Luz",
    tipo: "despesa"
  },
  {
    id_categoria: "4",
    nome: "Aluguel",
    tipo: "despesa"
  },
  {
    id_categoria: "5",
    nome: "Salários",
    tipo: "despesa"
  }
];

/**
 * Simula a listagem de categorias
 */
export async function listarCategoriasMock(): Promise<Categoria[]> {
  // Simula um atraso de rede
  await new Promise(resolve => setTimeout(resolve, 500));
  
  // Retorna os dados mocados
  return categoriasMock;
}

/**
 * Simula a busca de uma categoria pelo ID
 */
export async function buscarCategoriaMock(id: string): Promise<Categoria> {
  // Simula um atraso de rede
  await new Promise(resolve => setTimeout(resolve, 300));
  
  // Busca a categoria pelo ID
  const categoria = categoriasMock.find(c => c.id_categoria === id);
  
  // Se não encontrar, simula um erro
  if (!categoria) {
    throw new Error("Categoria não encontrada");
  }
  
  return categoria;
}

/**
 * Simula o cadastro de uma nova categoria
 */
export async function cadastrarCategoriaMock(categoria: Omit<Categoria, 'id_categoria'>): Promise<Categoria> {
  // Simula um atraso de rede
  await new Promise(resolve => setTimeout(resolve, 800));
  
  // Cria uma nova categoria com ID gerado
  const novaCategoria: Categoria = {
    id_categoria: `categoria-${Date.now()}`,
    nome: categoria.nome,
    tipo: categoria.tipo
  };
  
  // Adiciona à lista de categorias mock
  categoriasMock.push(novaCategoria);
  
  return novaCategoria;
}

/**
 * Simula a atualização de uma categoria
 */
export async function atualizarCategoriaMock(id: string, categoria: Partial<Categoria>): Promise<Categoria> {
  // Simula um atraso de rede
  await new Promise(resolve => setTimeout(resolve, 600));
  
  // Busca a categoria pelo ID
  const index = categoriasMock.findIndex(c => c.id_categoria === id);
  
  // Se não encontrar, simula um erro
  if (index === -1) {
    throw new Error("Categoria não encontrada");
  }
  
  // Atualiza os dados da categoria
  categoriasMock[index] = {
    ...categoriasMock[index],
    ...categoria
  };
  
  return categoriasMock[index];
}

/**
 * Simula a remoção de uma categoria
 */
export async function removerCategoriaMock(id: string): Promise<void> {
  // Simula um atraso de rede
  await new Promise(resolve => setTimeout(resolve, 400));
  
  // Busca a categoria pelo ID
  const index = categoriasMock.findIndex(c => c.id_categoria === id);
  
  // Se não encontrar, simula um erro
  if (index === -1) {
    throw new Error("Categoria não encontrada");
  }
  
  // Remove a categoria da lista
  categoriasMock.splice(index, 1);
}

export default {
  listarCategorias: listarCategoriasMock,
  buscarCategoria: buscarCategoriaMock,
  cadastrarCategoria: cadastrarCategoriaMock,
  atualizarCategoria: atualizarCategoriaMock,
  removerCategoria: removerCategoriaMock
}; 