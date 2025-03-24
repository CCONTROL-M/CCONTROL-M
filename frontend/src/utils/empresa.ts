import { getEmpresaId } from "./auth";

// ID de empresa de teste para ambiente de desenvolvimento
const EMPRESA_TESTE_ID = "11111111-1111-1111-1111-111111111111";

/**
 * Obtém o ID da empresa atual para ser usado em requisições à API.
 * 
 * Em ambiente de desenvolvimento, se não houver ID no token, retorna um ID de teste.
 * Em produção, se não houver ID no token, lança um erro.
 * 
 * @returns ID da empresa atual
 */
export function getEmpresa(): string {
  // Tenta obter do token
  const empresaId = getEmpresaId();
  
  // Se encontrou no token, usa o valor real
  if (empresaId) {
    return empresaId;
  }
  
  // Verifica se estamos em ambiente de desenvolvimento
  if (import.meta.env.DEV) {
    console.warn('ID da empresa não disponível no token. Usando ID de teste para ambiente de desenvolvimento.');
    return EMPRESA_TESTE_ID;
  }
  
  // Em produção, lança erro
  throw new Error("ID da empresa não disponível. Faça login novamente.");
}

/**
 * Formata e valida uma resposta da API, lidando com diferentes formatos possíveis.
 * 
 * @param response Resposta da API
 * @returns Array formatado com os itens recebidos
 */
export function formatarResposta<T>(response: any): T[] {
  if (response && response.items) {
    return response.items;
  } else if (Array.isArray(response)) {
    return response;
  } else {
    console.warn("Formato inesperado de resposta:", response);
    return [];
  }
}

/**
 * Adiciona o ID da empresa atual aos parâmetros de filtro.
 * 
 * @param filtros Filtros existentes
 * @returns Filtros com ID da empresa
 */
export function adicionarEmpresaFiltro<T extends object>(filtros?: T): T & { id_empresa: string } {
  return {
    ...(filtros || {} as T),
    id_empresa: getEmpresa()
  } as T & { id_empresa: string };
}

/**
 * Adiciona o ID da empresa atual ao objeto.
 * 
 * @param objeto Objeto base
 * @returns Objeto com ID da empresa adicionado
 */
export function adicionarIdEmpresa<T extends {}>(objeto: T): T & { id_empresa: string } {
  // Adiciona o ID da empresa atual ao objeto
  return {
    ...objeto,
    id_empresa: getEmpresa()
  } as T & { id_empresa: string };
} 