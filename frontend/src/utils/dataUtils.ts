/**
 * Funções utilitárias para manipulação segura de dados
 */

/**
 * Verifica e retorna com segurança um array.
 * Se o valor não for um array ou for vazio, retorna um array vazio.
 * 
 * @param input Valor a ser verificado
 * @returns Array tipado ou vazio se o input for inválido
 */
export function safeArray<T>(input: any): T[] {
  if (Array.isArray(input)) {
    return input;
  }
  return [];
}

/**
 * Verifica e retorna com segurança um objeto.
 * Se o valor não for um objeto, retorna o valor padrão fornecido.
 * 
 * @param input Valor a ser verificado
 * @param defaultValue Valor padrão a ser retornado se input não for um objeto válido
 * @returns Objeto tipado ou valor padrão
 */
export function safeObject<T>(input: any, defaultValue: T): T {
  if (input && typeof input === 'object' && !Array.isArray(input)) {
    return input as T;
  }
  return defaultValue;
}

/**
 * Verifica e retorna com segurança um número.
 * Se o valor não for um número, retorna o valor padrão fornecido.
 * 
 * @param input Valor a ser verificado
 * @param defaultValue Valor padrão a ser retornado se input não for um número
 * @returns Número ou valor padrão
 */
export function safeNumber(input: any, defaultValue: number = 0): number {
  if (typeof input === 'number' && !isNaN(input)) {
    return input;
  }
  
  // Tenta converter para número caso seja uma string
  if (typeof input === 'string') {
    const num = parseFloat(input);
    if (!isNaN(num)) {
      return num;
    }
  }
  
  return defaultValue;
}

/**
 * Verifica e retorna com segurança uma string.
 * Se o valor não for uma string, retorna o valor padrão fornecido.
 * 
 * @param input Valor a ser verificado
 * @param defaultValue Valor padrão a ser retornado se input não for uma string
 * @returns String ou valor padrão
 */
export function safeString(input: any, defaultValue: string = ''): string {
  if (typeof input === 'string') {
    return input;
  }
  
  // Tenta converter para string se possível
  if (input !== null && input !== undefined) {
    return String(input);
  }
  
  return defaultValue;
}

/**
 * Executa a função reduce em um array, garantindo segurança contra valores nulos.
 * 
 * @param array Array a ser reduzido
 * @param callback Função de redução
 * @param initialValue Valor inicial para a redução
 * @returns Resultado da redução ou o valor inicial se o array for inválido
 */
export function safeReduce<T, U>(
  array: any,
  callback: (accumulator: U, currentValue: T, index: number, array: T[]) => U,
  initialValue: U
): U {
  if (Array.isArray(array) && array.length > 0) {
    return array.reduce(callback, initialValue);
  }
  return initialValue;
}

/**
 * Executa a função map em um array, garantindo segurança contra valores nulos.
 * 
 * @param array Array a ser mapeado
 * @param callback Função de mapeamento
 * @returns Novo array com os resultados do mapeamento ou array vazio se o array for inválido
 */
export function safeMap<T, U>(
  array: any,
  callback: (value: T, index: number, array: T[]) => U
): U[] {
  if (Array.isArray(array) && array.length > 0) {
    return array.map(callback);
  }
  return [];
}

/**
 * Executa a função filter em um array, garantindo segurança contra valores nulos.
 * 
 * @param array Array a ser filtrado
 * @param callback Função de filtragem
 * @returns Novo array com os resultados da filtragem ou array vazio se o array for inválido
 */
export function safeFilter<T>(
  array: any,
  callback: (value: T, index: number, array: T[]) => boolean
): T[] {
  if (Array.isArray(array) && array.length > 0) {
    return array.filter(callback);
  }
  return [];
}

/**
 * Acessa com segurança uma propriedade aninhada de um objeto.
 * 
 * @param obj Objeto a ser acessado
 * @param path Caminho da propriedade, usando pontos para separação (ex: "user.address.street")
 * @param defaultValue Valor padrão caso a propriedade não exista
 * @returns Valor da propriedade ou valor padrão
 */
export function getNestedValue<T>(obj: any, path: string, defaultValue: T): T {
  if (!obj || typeof obj !== 'object') {
    return defaultValue;
  }
  
  const keys = path.split('.');
  let current = obj;
  
  for (const key of keys) {
    if (current === null || current === undefined || typeof current !== 'object') {
      return defaultValue;
    }
    current = current[key];
  }
  
  return (current !== undefined && current !== null) ? current as T : defaultValue;
}

export default {
  safeArray,
  safeObject,
  safeNumber,
  safeString,
  safeReduce,
  safeMap,
  safeFilter,
  getNestedValue
}; 