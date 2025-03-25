import { getEmpresaId } from "./auth";

/**
 * Obtém o ID da empresa atual para ser usado em requisições à API.
 * Lança um erro se não houver ID no token.
 * 
 * @returns ID da empresa atual
 * @throws Error quando o ID da empresa não está disponível
 */
export function getEmpresa(): string {
  // Tenta obter do token
  const empresaId = getEmpresaId();
  
  // Se encontrou no token, usa o valor real
  if (empresaId) {
    return empresaId;
  }
  
  // Lançar erro em vez de usar ID fixo
  console.error('ID da empresa não disponível no token');
  throw new Error('ID da empresa não disponível. É necessário estar autenticado.');
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