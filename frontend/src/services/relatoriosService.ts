import api from "./api";
import { Inadimplente, FluxoItem, DREData, Ciclo } from "../types";
import { useMock } from "../utils/mock";
import { safeArray, safeObject } from "../utils/dataUtils";
import { 
  obterRelatorioInadimplenciaMock, 
  obterRelatorioFluxoCaixaMock, 
  obterRelatorioDREMock, 
  obterRelatorioCicloOperacionalMock 
} from "./relatoriosServiceMock";

// Valores padrão
const dreVazio: DREData = {
  receitas: [],
  despesas: [],
  lucro_prejuizo: 0
};

// Relatório de Inadimplência
export async function obterRelatorioInadimplencia(): Promise<Inadimplente[]> {
  // Verificar se deve usar mock
  if (useMock()) {
    console.log("Usando dados mock para relatório de inadimplência");
    return obterRelatorioInadimplenciaMock();
  }
  
  try {
    const response = await api.get("/api/v1/relatorios/inadimplencia");
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
    const response = await api.get("/api/v1/relatorios/fluxo-caixa");
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
    const response = await api.get("/api/v1/relatorios/dre");
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
    const response = await api.get("/api/v1/relatorios/ciclo-operacional");
    return safeArray<Ciclo>(response.data);
  } catch (error) {
    console.error("Erro ao obter relatório de ciclo operacional:", error);
    return [];
  }
} 