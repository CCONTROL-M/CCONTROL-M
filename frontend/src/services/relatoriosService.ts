import api from "./api";
import { Inadimplente, FluxoItem, DREData, Ciclo } from "../types";
import { useMock } from "../utils/mock";
import { 
  obterRelatorioInadimplenciaMock, 
  obterRelatorioFluxoCaixaMock, 
  obterRelatorioDREMock, 
  obterRelatorioCicloOperacionalMock 
} from "./relatoriosServiceMock";

// Relatório de Inadimplência
export async function obterRelatorioInadimplencia(): Promise<Inadimplente[]> {
  // Verificar se deve usar mock
  if (useMock()) {
    console.log("Usando dados mock para relatório de inadimplência");
    return obterRelatorioInadimplenciaMock();
  }
  
  const response = await api.get("/relatorios/inadimplencia");
  return response.data;
}

// Relatório de Fluxo de Caixa
export async function obterRelatorioFluxoCaixa(): Promise<FluxoItem[]> {
  // Verificar se deve usar mock
  if (useMock()) {
    console.log("Usando dados mock para relatório de fluxo de caixa");
    return obterRelatorioFluxoCaixaMock();
  }
  
  const response = await api.get("/relatorios/fluxo-caixa");
  return response.data;
}

// Relatório de DRE
export async function obterRelatorioDRE(): Promise<DREData> {
  // Verificar se deve usar mock
  if (useMock()) {
    console.log("Usando dados mock para relatório de DRE");
    return obterRelatorioDREMock();
  }
  
  const response = await api.get("/relatorios/dre");
  return response.data;
}

// Relatório de Ciclo Operacional
export async function obterRelatorioCicloOperacional(): Promise<Ciclo[]> {
  // Verificar se deve usar mock
  if (useMock()) {
    console.log("Usando dados mock para relatório de ciclo operacional");
    return obterRelatorioCicloOperacionalMock();
  }
  
  const response = await api.get("/relatorios/ciclo-operacional");
  return response.data;
} 