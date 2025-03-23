import api from "./api";
import { Lancamento } from "../types";
import { listarLancamentosMock, buscarLancamentoMock, cadastrarLancamentoMock, atualizarLancamentoMock, removerLancamentoMock, filtrarLancamentosMock } from "./lancamentoServiceMock";
import { useMock } from "../utils/mock";

export async function listarLancamentos(): Promise<Lancamento[]> {
  // Verificar se deve usar mock
  if (useMock()) {
    console.log("Usando dados mock para lançamentos");
    return listarLancamentosMock();
  }
  
  const response = await api.get("/lancamentos");
  return response.data;
}

export async function buscarLancamento(id: string): Promise<Lancamento> {
  // Verificar se deve usar mock
  if (useMock()) {
    return buscarLancamentoMock(id);
  }
  
  const response = await api.get(`/lancamentos/${id}`);
  return response.data;
}

export async function cadastrarLancamento(lancamento: Omit<Lancamento, "id_lancamento">): Promise<Lancamento> {
  // Verificar se deve usar mock
  if (useMock()) {
    return cadastrarLancamentoMock(lancamento);
  }
  
  const response = await api.post("/lancamentos", lancamento);
  return response.data;
}

export async function atualizarLancamento(id: string, lancamento: Partial<Lancamento>): Promise<Lancamento> {
  // Verificar se deve usar mock
  if (useMock()) {
    return atualizarLancamentoMock(id, lancamento);
  }
  
  const response = await api.put(`/lancamentos/${id}`, lancamento);
  return response.data;
}

export async function removerLancamento(id: string): Promise<void> {
  // Verificar se deve usar mock
  if (useMock()) {
    return removerLancamentoMock(id);
  }
  
  await api.delete(`/lancamentos/${id}`);
}

export async function filtrarLancamentos(filtros: { 
  dataInicio?: string; 
  dataFim?: string;
  tipo?: string;
  status?: string;
}): Promise<Lancamento[]> {
  // Verificar se deve usar mock
  if (useMock()) {
    return filtrarLancamentosMock(filtros);
  }
  
  const response = await api.get("/lancamentos", { params: filtros });
  return response.data;
} 