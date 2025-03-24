/**
 * Utilitário para diagnosticar problemas de roteamento e conexão com API
 */
import { getStatusAPI, verificarStatusAPI } from '../services/api';
import { useMock } from './mock';

/**
 * Verifica e retorna informações sobre o estado do sistema
 */
export async function runDiagnostics() {
  // Verificar ambiente
  const environment = {
    nodeEnv: import.meta.env.MODE,
    mockEnabled: useMock(),
    baseUrl: window.location.origin,
    currentPath: window.location.pathname,
  };

  // Verificar API
  let apiStatus;
  try {
    apiStatus = await verificarStatusAPI();
  } catch (error) {
    apiStatus = {
      online: false,
      error: error instanceof Error ? error.message : String(error)
    };
  }

  // Verificar rotas
  const routes = {
    routerLibrary: 'react-router-dom v6',
    currentRoute: window.location.pathname,
    hash: window.location.hash,
    queryParams: new URLSearchParams(window.location.search).toString(),
  };

  // Registrar informações no localStorage para debug
  localStorage.setItem('diagnostics', JSON.stringify({
    timestamp: new Date().toISOString(),
    environment,
    apiStatus,
    routes,
    userAgent: navigator.userAgent,
  }));

  return {
    environment,
    apiStatus,
    routes,
  };
}

/**
 * Verifica o status da página atual
 */
export function checkCurrentRoute() {
  const path = window.location.pathname;
  console.log(`Diagnóstico de rota para: ${path}`);
  
  // Verificar se a rota existe no App.tsx
  const registeredRoutes = [
    "/",
    "/lancamentos",
    "/vendas-parcelas",
    "/parcelas",
    "/transferencias-contas",
    "/dre",
    "/fluxo-caixa",
    "/inadimplencia",
    "/ciclo-operacional",
    "/clientes",
    "/fornecedores",
    "/contas-bancarias",
    "/categorias",
    "/centro-custos",
    "/formas-pagamento",
    "/meus-dados",
    "/gestao-usuarios",
    "/permissoes",
    "/conexoes-externas",
    "/parametros-sistema",
    "/logs-auditoria",
    "/empresas",
    "/teste-cors"
  ];

  const routeExists = registeredRoutes.includes(path);
  
  return {
    routeStatus: routeExists ? 'registered' : 'not_found',
    path,
    mockEnabled: useMock(),
    apiStatus: getStatusAPI().online ? 'online' : 'offline',
  };
}

/**
 * Redireciona para a página inicial com parâmetros de diagnóstico
 */
export function redirectWithDiagnostics() {
  const diagnostics = {
    source: window.location.pathname,
    time: new Date().getTime(),
    mock: useMock(),
    api: getStatusAPI().online
  };
  
  const params = new URLSearchParams(diagnostics as any).toString();
  window.location.href = `/?${params}`;
}

export default {
  runDiagnostics,
  checkCurrentRoute,
  redirectWithDiagnostics
}; 