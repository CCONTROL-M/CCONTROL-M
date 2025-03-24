import api from "./api";
import { DREData, FluxoItem, FluxoGrupo, Inadimplente, Ciclo, ResumoDashboard } from "../types";
import { safeArray, safeObject } from "../utils/dataUtils";
import { useMock } from "../utils/mock";
import {
  buscarResumoDashboardMock,
  buscarDREMock,
  buscarFluxoCaixaMock,
  buscarInadimplenciaMock,
  buscarCicloOperacionalMock,
  buscarFluxoCaixaFiltradoMock,
  buscarDREPeriodoMock
} from "./relatorioServiceMock";

// Estruturas vazias para retorno em caso de erro
const dreVazio: DREData = {
  receitas: [],
  despesas: [],
  lucro_prejuizo: 0
};

const fluxoVazio: FluxoGrupo[] = [];
const inadimplentesVazio: Inadimplente[] = [];
const ciclosVazio: Ciclo[] = [];

export async function buscarResumoDashboard(): Promise<ResumoDashboard> {
  const servico = 'dashboard';
  
  // Verificar se deve usar mock explicitamente definido pelo usuário
  if (useMock()) {
    console.log(`[${servico}] Usando dados mock conforme configuração de usuário`);
    return await buscarResumoDashboardMock();
  }

  // Se não estiver em modo mock, buscar da API real
  console.log(`[${servico}] Buscando dados da API...`);
  const response = await api.get("/api/v1/dashboard/resumo");
  console.log(`[${servico}] Dados obtidos com sucesso:`, response.data);
  return safeObject(response.data, {
    caixa_atual: 0,
    total_receber: 0,
    total_pagar: 0,
    recebimentos_hoje: 0,
    pagamentos_hoje: 0
  });
}

export async function buscarDRE(): Promise<DREData> {
  const servico = 'dre';
  
  // Verificar se deve usar mock explicitamente definido pelo usuário
  if (useMock()) {
    console.log(`[${servico}] Usando dados mock conforme configuração de usuário`);
    return await buscarDREMock();
  }

  // Se não estiver em modo mock, buscar da API real
  console.log(`[${servico}] Buscando dados da API...`);
  const response = await api.get("/api/v1/relatorios/dre");
  console.log(`[${servico}] Dados obtidos com sucesso`);
  return safeObject(response.data, dreVazio);
}

export async function buscarFluxoCaixa(): Promise<FluxoGrupo[]> {
  const servico = 'fluxo-caixa';
  
  // Verificar se deve usar mock explicitamente definido pelo usuário
  if (useMock()) {
    console.log(`[${servico}] Usando dados mock conforme configuração de usuário`);
    return await buscarFluxoCaixaMock();
  }

  // Se não estiver em modo mock, buscar da API real
  console.log(`[${servico}] Buscando dados da API...`);
  const response = await api.get("/api/v1/relatorios/fluxo-caixa");
  console.log(`[${servico}] Dados obtidos com sucesso`);
  return safeArray<FluxoGrupo>(response.data);
}

export async function buscarInadimplencia(): Promise<Inadimplente[]> {
  const servico = 'inadimplencia';
  
  // Verificar se deve usar mock explicitamente definido pelo usuário
  if (useMock()) {
    console.log(`[${servico}] Usando dados mock conforme configuração de usuário`);
    return await buscarInadimplenciaMock();
  }

  // Se não estiver em modo mock, buscar da API real
  console.log(`[${servico}] Buscando dados da API...`);
  const response = await api.get("/api/v1/relatorios/inadimplencia");
  console.log(`[${servico}] Dados obtidos com sucesso`);
  return safeArray<Inadimplente>(response.data);
}

export async function buscarCicloOperacional(): Promise<Ciclo[]> {
  const servico = 'ciclo-operacional';
  
  // Verificar se deve usar mock explicitamente definido pelo usuário
  if (useMock()) {
    console.log(`[${servico}] Usando dados mock conforme configuração de usuário`);
    return await buscarCicloOperacionalMock();
  }

  // Se não estiver em modo mock, buscar da API real
  console.log(`[${servico}] Buscando dados da API...`);
  const response = await api.get("/api/v1/relatorios/ciclo-operacional");
  console.log(`[${servico}] Dados obtidos com sucesso`);
  return safeArray<Ciclo>(response.data);
}

export async function buscarFluxoCaixaFiltrado(filtros: { 
  dataInicio?: string; 
  dataFim?: string;
  tipo?: string;
  id_conta?: string;
  status?: string;
}): Promise<FluxoGrupo[]> {
  const servico = 'fluxo-caixa-filtrado';
  
  // Verificar se deve usar mock explicitamente definido pelo usuário
  if (useMock()) {
    console.log(`[${servico}] Usando dados mock conforme configuração de usuário`);
    return await buscarFluxoCaixaFiltradoMock();
  }

  // Se não estiver em modo mock, buscar da API real
  console.log(`[${servico}] Buscando dados da API com filtros:`, filtros);
  const response = await api.get("/api/v1/relatorios/fluxo-caixa", { params: filtros });
  console.log(`[${servico}] Dados obtidos com sucesso`);
  return safeArray<FluxoGrupo>(response.data);
}

export async function buscarDREPeriodo(periodo: { 
  dataInicio: string; 
  dataFim: string;
}): Promise<DREData> {
  const servico = 'dre-periodo';
  
  // Verificar se deve usar mock explicitamente definido pelo usuário
  if (useMock()) {
    console.log(`[${servico}] Usando dados mock conforme configuração de usuário para período:`, periodo);
    return await buscarDREPeriodoMock(periodo);
  }

  // Se não estiver em modo mock, buscar da API real
  console.log(`[${servico}] Buscando dados da API para período:`, periodo);
  const response = await api.get("/api/v1/relatorios/dre", { params: periodo });
  console.log(`[${servico}] Dados obtidos com sucesso`);
  return safeObject(response.data, dreVazio);
} 