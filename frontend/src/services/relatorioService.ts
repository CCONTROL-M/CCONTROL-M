import api from "./api";
import { DREData, FluxoItem, Inadimplente, Ciclo } from "../types";

export async function buscarResumoDashboard() {
  const response = await api.get("/dashboard/resumo");
  return response.data;
}

export async function buscarDRE(): Promise<DREData> {
  const response = await api.get("/relatorios/dre");
  return response.data;
}

export async function buscarFluxoCaixa(): Promise<FluxoItem[]> {
  const response = await api.get("/relatorios/fluxo-caixa");
  return response.data;
}

export async function buscarInadimplencia(): Promise<Inadimplente[]> {
  const response = await api.get("/relatorios/inadimplencia");
  return response.data;
}

export async function buscarCicloOperacional(): Promise<Ciclo[]> {
  const response = await api.get("/relatorios/ciclo-operacional");
  return response.data;
}

export async function buscarFluxoCaixaFiltrado(filtros: { 
  dataInicio?: string; 
  dataFim?: string;
  tipo?: string;
}): Promise<FluxoItem[]> {
  const response = await api.get("/relatorios/fluxo-caixa", { params: filtros });
  return response.data;
}

export async function buscarDREPeriodo(periodo: { 
  dataInicio: string; 
  dataFim: string;
}): Promise<DREData> {
  const response = await api.get("/relatorios/dre", { params: periodo });
  return response.data;
} 