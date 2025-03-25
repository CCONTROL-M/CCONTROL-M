import api from "./api";
import { Lancamento } from "../types";
import { listarLancamentosMock, buscarLancamentoMock, cadastrarLancamentoMock, atualizarLancamentoMock, removerLancamentoMock, filtrarLancamentosMock } from "./lancamentoServiceMock";
import { useMock } from "../utils/mock";

/**
 * [TEMPORÁRIO]
 * Serviço configurado para comunicação com o servidor de teste em http://localhost:8002/api/v1
 * Este arquivo foi adaptado para trabalhar com as rotas e parâmetros do servidor de teste.
 * Endpoints atualizados para não incluir o prefixo "/api/v1" que agora está na baseURL.
 * Quando o backend real estiver pronto, revisar:
 * - Os caminhos das APIs (paths)
 * - O formato dos parâmetros de consulta
 * - A estrutura da resposta (especialmente a paginação)
 * - O uso do ID_EMPRESA fixo (que virá do contexto de autenticação)
 */

// ID da empresa para teste - em produção viria do contexto de autenticação
const ID_EMPRESA = "3fa85f64-5717-4562-b3fc-2c963f66afa6";

export async function listarLancamentos(): Promise<Lancamento[]> {
  // Verificar se deve usar mock
  if (useMock()) {
    console.log("Usando dados mock para lançamentos");
    return listarLancamentosMock();
  }
  
  const response = await api.get("/lancamentos", {
    params: { id_empresa: ID_EMPRESA }
  });
  return response.data.items || []; // Ajustado para pegar items da resposta paginada
}

export async function buscarLancamento(id: string): Promise<Lancamento> {
  // Verificar se deve usar mock
  if (useMock()) {
    return buscarLancamentoMock(id);
  }
  
  const response = await api.get(`/lancamentos/${id}`, {
    params: { id_empresa: ID_EMPRESA }
  });
  return response.data;
}

export async function cadastrarLancamento(lancamento: Omit<Lancamento, "id_lancamento">): Promise<Lancamento> {
  // Verificar se deve usar mock
  if (useMock()) {
    return cadastrarLancamentoMock(lancamento);
  }
  
  // Garantir que o id_empresa esteja no objeto
  const lancamentoComEmpresa = {
    ...lancamento,
    id_empresa: ID_EMPRESA
  };
  
  const response = await api.post("/lancamentos", lancamentoComEmpresa);
  return response.data;
}

export async function atualizarLancamento(id: string, lancamento: Partial<Lancamento>): Promise<Lancamento> {
  // Verificar se deve usar mock
  if (useMock()) {
    return atualizarLancamentoMock(id, lancamento);
  }
  
  // Garantir que o id_empresa esteja no objeto
  const lancamentoComEmpresa = {
    ...lancamento,
    id_empresa: ID_EMPRESA
  };
  
  const response = await api.put(`/lancamentos/${id}`, lancamentoComEmpresa, {
    params: { id_empresa: ID_EMPRESA }
  });
  return response.data;
}

export async function removerLancamento(id: string): Promise<void> {
  // Verificar se deve usar mock
  if (useMock()) {
    return removerLancamentoMock(id);
  }
  
  await api.delete(`/lancamentos/${id}`, {
    params: { id_empresa: ID_EMPRESA }
  });
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
  
  // Converter nomes dos filtros para o formato da API do servidor de teste
  const params = {
    id_empresa: ID_EMPRESA,
    data_inicio: filtros.dataInicio,
    data_fim: filtros.dataFim,
    tipo: filtros.tipo,
    status: filtros.status
  };
  
  const response = await api.get("/lancamentos", { params });
  return response.data.items || []; // Ajustado para pegar items da resposta paginada
} 