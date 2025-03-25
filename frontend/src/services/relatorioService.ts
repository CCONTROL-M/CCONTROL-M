import api from "./api";
import { DREData, FluxoItem, FluxoGrupo, Inadimplente, Ciclo, ResumoDashboard } from "../types";
import { safeArray, safeObject } from "../utils/dataUtils";
import { getEmpresa } from "../utils/auth";
import { getToken } from "../utils/auth";

// Estruturas vazias para retorno em caso de erro
const dreVazio: DREData = {
  receitas: [],
  despesas: [],
  lucro_prejuizo: 0
};

const fluxoVazio: FluxoGrupo[] = [];
const inadimplentesVazio: Inadimplente[] = [];
const ciclosVazio: Ciclo[] = [];

// Função auxiliar para verificar erros HTTP específicos
function verificarErroHTTP(error: any): void {
  if (error.response) {
    const { status } = error.response;
    
    if (status === 404 || status === 500) {
      throw new Error('Ocorreu um erro ao buscar os indicadores financeiros.');
    }
  }
  
  // Se não for um erro HTTP específico, propaga o erro original
  throw error;
}

export async function buscarResumoDashboard(id_empresa?: string): Promise<ResumoDashboard> {
  const servico = 'dashboard';
  
  try {
    console.log(`[${servico}] Buscando dados da API...`);
    
    // Usar o ID da empresa fornecido ou obter a empresa do token
    const empresaId = id_empresa || getEmpresa();
    
    // Obter o token JWT para autenticação
    const token = getToken();
    
    if (!token) {
      throw new Error('Token de autenticação não encontrado');
    }
    
    // URL correta conforme especificação
    const response = await api.get("/dashboard/resumo", {
      params: { id_empresa: empresaId },
      headers: {
        Authorization: `Bearer ${token}`
      },
      timeout: 8000 // Timeout específico para esta rota
    });
    
    console.log(`[${servico}] Dados obtidos com sucesso:`, response.data);
    return safeObject(response.data, {
      caixa_atual: 0,
      total_receber: 0,
      total_pagar: 0,
      recebimentos_hoje: 0,
      pagamentos_hoje: 0
    });
  } catch (error) {
    console.error(`[${servico}] Erro ao buscar dados:`, error);
    verificarErroHTTP(error);
    throw error;
  }
}

export async function buscarDRE(): Promise<DREData> {
  const servico = 'dre';
  
  try {
    console.log(`[${servico}] Buscando dados da API...`);
    const id_empresa = getEmpresa();
    
    const response = await api.get("/relatorios/dre", {
      params: { id_empresa },
      timeout: 5000 // Timeout específico para esta rota
    });
    
    console.log(`[${servico}] Dados obtidos com sucesso`);
    return safeObject(response.data, dreVazio);
  } catch (error) {
    console.error(`[${servico}] Erro ao buscar dados:`, error);
    throw error;
  }
}

export async function buscarFluxoCaixa(): Promise<FluxoGrupo[]> {
  const servico = 'fluxo-caixa';
  
  try {
    console.log(`[${servico}] Buscando dados da API...`);
    const id_empresa = getEmpresa();
    
    const response = await api.get("/relatorios/fluxo-caixa", {
      params: { id_empresa },
      timeout: 5000 // Timeout específico para esta rota
    });
    
    console.log(`[${servico}] Dados obtidos com sucesso`);
    return safeArray<FluxoGrupo>(response.data);
  } catch (error) {
    console.error(`[${servico}] Erro ao buscar dados:`, error);
    return [];
  }
}

export async function buscarInadimplencia(): Promise<Inadimplente[]> {
  const servico = 'inadimplencia';
  
  try {
    console.log(`[${servico}] Buscando dados da API...`);
    const id_empresa = getEmpresa();
    
    const response = await api.get("/relatorios/inadimplencia", {
      params: { id_empresa },
      timeout: 5000 // Timeout específico para esta rota
    });
    
    console.log(`[${servico}] Dados obtidos com sucesso`);
    return safeArray<Inadimplente>(response.data);
  } catch (error) {
    console.error(`[${servico}] Erro ao buscar dados:`, error);
    return [];
  }
}

export async function buscarCicloOperacional(): Promise<Ciclo[]> {
  const servico = 'ciclo-operacional';
  
  try {
    console.log(`[${servico}] Buscando dados da API...`);
    const id_empresa = getEmpresa();
    
    const response = await api.get("/relatorios/ciclo-operacional", {
      params: { id_empresa },
      timeout: 5000 // Timeout específico para esta rota
    });
    
    console.log(`[${servico}] Dados obtidos com sucesso`);
    return safeArray<Ciclo>(response.data);
  } catch (error) {
    console.error(`[${servico}] Erro ao buscar dados:`, error);
    return [];
  }
}

export async function buscarFluxoCaixaFiltrado(filtros: { 
  dataInicio?: string; 
  dataFim?: string;
  tipo?: string;
  id_conta?: string;
  status?: string;
}): Promise<FluxoGrupo[]> {
  const servico = 'fluxo-caixa-filtrado';
  
  try {
    console.log(`[${servico}] Buscando dados da API com filtros:`, filtros);
    const id_empresa = getEmpresa();
    
    const response = await api.get("/relatorios/fluxo-caixa", {
      params: { 
        id_empresa,
        ...filtros
      }
    });
    
    console.log(`[${servico}] Dados obtidos com sucesso`);
    return safeArray<FluxoGrupo>(response.data);
  } catch (error) {
    console.error(`[${servico}] Erro ao buscar dados:`, error);
    return [];
  }
}

export async function buscarDREPeriodo(periodo: { 
  dataInicio: string; 
  dataFim: string;
}): Promise<DREData> {
  const servico = 'dre-periodo';
  
  try {
    console.log(`[${servico}] Buscando dados da API com período:`, periodo);
    const id_empresa = getEmpresa();
    
    const response = await api.get("/relatorios/dre", {
      params: {
        id_empresa,
        ...periodo
      }
    });
    
    console.log(`[${servico}] Dados obtidos com sucesso`);
    return safeObject(response.data, dreVazio);
  } catch (error) {
    console.error(`[${servico}] Erro ao buscar dados:`, error);
    throw error;
  }
} 