import { jwtDecode } from 'jwt-decode';

interface DecodedToken {
  id_usuario: string;
  id_empresa: string;
  nome: string;
  email: string;
  tipo_usuario: string;
  exp: number;
}

/**
 * Obtém o token JWT do localStorage
 */
export function getToken(): string | null {
  return localStorage.getItem('token');
}

/**
 * Verifica se o token é válido (existe e não está expirado)
 */
export function isTokenValid(): boolean {
  const token = getToken();
  
  if (!token) {
    return false;
  }
  
  try {
    const decoded = jwtDecode<DecodedToken>(token);
    const currentTime = Date.now() / 1000;
    
    return decoded.exp > currentTime;
  } catch (error) {
    return false;
  }
}

/**
 * Obtém o ID da empresa do usuário logado
 */
export function getEmpresaId(): string | null {
  const token = getToken();
  
  if (!token) {
    return null;
  }
  
  try {
    const decoded = jwtDecode<DecodedToken>(token);
    return decoded.id_empresa;
  } catch (error) {
    return null;
  }
}

/**
 * Obtém o ID da empresa para uso em requisições à API
 * Retorna o ID da empresa do token ou null se não existir
 * 
 * @returns ID da empresa do token autenticado ou null
 */
export function getEmpresa(): string {
  // Tenta obter do token
  const empresaId = getEmpresaId();
  
  // Se encontrou no token, usa o valor real
  if (empresaId) {
    return empresaId;
  }
  
  // Em vez de usar um ID fictício, lança um erro
  console.error('ID da empresa não disponível no token');
  throw new Error('ID da empresa não disponível. É necessário estar autenticado.');
}

/**
 * Obtém o ID do usuário logado
 */
export function getUserId(): string | null {
  const token = getToken();
  
  if (!token) {
    return null;
  }
  
  try {
    const decoded = jwtDecode<DecodedToken>(token);
    return decoded.id_usuario;
  } catch (error) {
    return null;
  }
}

/**
 * Obtém os dados completos do usuário logado
 */
export function getUserData(): Partial<DecodedToken> | null {
  const token = getToken();
  
  if (!token) {
    return null;
  }
  
  try {
    const decoded = jwtDecode<DecodedToken>(token);
    const { exp, ...userData } = decoded;
    return userData;
  } catch (error) {
    return null;
  }
}

/**
 * Limpa os dados de autenticação e faz logout
 */
export function logout(): void {
  localStorage.removeItem('token');
  // Não redirecionar para login, apenas limpar o token
  console.log('Logout realizado, token removido');
} 