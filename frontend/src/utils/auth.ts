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
  window.location.href = '/login';
} 