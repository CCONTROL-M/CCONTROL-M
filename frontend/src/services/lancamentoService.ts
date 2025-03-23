import api from "./api";
import { Lancamento } from "../types";

export async function listarLancamentos(): Promise<Lancamento[]> {
  const response = await api.get("/lancamentos");
  return response.data;
}

export async function buscarLancamento(id: string): Promise<Lancamento> {
  const response = await api.get(`/lancamentos/${id}`);
  return response.data;
}

export async function cadastrarLancamento(lancamento: Omit<Lancamento, "id_lancamento">): Promise<Lancamento> {
  const response = await api.post("/lancamentos", lancamento);
  return response.data;
}

export async function atualizarLancamento(id: string, lancamento: Partial<Lancamento>): Promise<Lancamento> {
  const response = await api.put(`/lancamentos/${id}`, lancamento);
  return response.data;
}

export async function removerLancamento(id: string): Promise<void> {
  await api.delete(`/lancamentos/${id}`);
}

export async function filtrarLancamentos(filtros: { 
  dataInicio?: string; 
  dataFim?: string;
  tipo?: string;
  status?: string;
}): Promise<Lancamento[]> {
  const response = await api.get("/lancamentos", { params: filtros });
  return response.data;
} 