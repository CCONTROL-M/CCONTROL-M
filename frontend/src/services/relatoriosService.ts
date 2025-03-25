import api from "./api";
import { safeArray, safeObject } from "../utils/dataUtils";
import { Inadimplente, Ciclo, FluxoItem, DREData } from "../types";
import { useMock } from "../utils/mock";
import { 
  obterRelatorioInadimplenciaMock, 
  obterRelatorioFluxoCaixaMock, 
  obterRelatorioDREMock, 
  obterRelatorioCicloOperacionalMock 
} from "./relatoriosServiceMock";

// Estruturas vazias para retorno em caso de erro
const dreVazio: DREData = {
  receitas: [],
  despesas: [],
  lucro_prejuizo: 0
};

/**
 * Obtém dados de inadimplência
 */
export async function buscarInadimplencia() {
  try {
    const response = await api.get("/relatorios/inadimplencia");
    return safeArray<Inadimplente>(response.data);
  } catch (error) {
    console.error("Erro ao obter relatório de inadimplência:", error);
    return [];
  }
}

/**
 * Obtém dados de fluxo de caixa
 */
export async function buscarFluxoCaixa() {
  try {
    const response = await api.get("/relatorios/fluxo-caixa");
    return safeArray<FluxoItem>(response.data);
  } catch (error) {
    console.error("Erro ao obter relatório de fluxo de caixa:", error);
    return [];
  }
}

/**
 * Obtém dados de DRE
 */
export async function buscarDRE() {
  try {
    const response = await api.get("/relatorios/dre");
    return safeObject<DREData>(response.data, dreVazio);
  } catch (error) {
    console.error("Erro ao obter relatório de DRE:", error);
    return dreVazio;
  }
}

/**
 * Obtém dados de ciclo operacional
 */
export async function buscarCicloOperacional() {
  try {
    const response = await api.get("/relatorios/ciclo-operacional");
    return safeArray<Ciclo>(response.data);
  } catch (error) {
    console.error("Erro ao obter relatório de ciclo operacional:", error);
    return [];
  }
}

// Relatório de Inadimplência
export async function obterRelatorioInadimplencia(): Promise<Inadimplente[]> {
  // Verificar se deve usar mock
  if (useMock()) {
    console.log("Usando dados mock para relatório de inadimplência");
    return obterRelatorioInadimplenciaMock();
  }
  
  try {
    const response = await api.get("/relatorios/inadimplencia");
    return safeArray<Inadimplente>(response.data);
  } catch (error) {
    console.error("Erro ao obter relatório de inadimplência:", error);
    return [];
  }
}

// Relatório de Fluxo de Caixa
export async function obterRelatorioFluxoCaixa(): Promise<FluxoItem[]> {
  // Verificar se deve usar mock
  if (useMock()) {
    console.log("Usando dados mock para relatório de fluxo de caixa");
    return obterRelatorioFluxoCaixaMock();
  }
  
  try {
    const response = await api.get("/relatorios/fluxo-caixa");
    return safeArray<FluxoItem>(response.data);
  } catch (error) {
    console.error("Erro ao obter relatório de fluxo de caixa:", error);
    return [];
  }
}

// Relatório de DRE
export async function obterRelatorioDRE(): Promise<DREData> {
  // Verificar se deve usar mock
  if (useMock()) {
    console.log("Usando dados mock para relatório de DRE");
    return obterRelatorioDREMock();
  }
  
  try {
    const response = await api.get("/relatorios/dre");
    return safeObject<DREData>(response.data, dreVazio);
  } catch (error) {
    console.error("Erro ao obter relatório de DRE:", error);
    return dreVazio;
  }
}

// Relatório de Ciclo Operacional
export async function obterRelatorioCicloOperacional(): Promise<Ciclo[]> {
  // Verificar se deve usar mock
  if (useMock()) {
    console.log("Usando dados mock para relatório de ciclo operacional");
    return obterRelatorioCicloOperacionalMock();
  }
  
  try {
    const response = await api.get("/relatorios/ciclo-operacional");
    return safeArray<Ciclo>(response.data);
  } catch (error) {
    console.error("Erro ao obter relatório de ciclo operacional:", error);
    return [];
  }
} 