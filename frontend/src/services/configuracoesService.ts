import api from "./api";
import { Conexao, Permissao } from "../types";

export async function listarConexoes(): Promise<Conexao[]> {
  const response = await api.get("/configuracoes/conexoes");
  return response.data;
}

export async function buscarConexao(id: string): Promise<Conexao> {
  const response = await api.get(`/configuracoes/conexoes/${id}`);
  return response.data;
}

export async function cadastrarConexao(conexao: Omit<Conexao, "id_conexao">): Promise<Conexao> {
  const response = await api.post("/configuracoes/conexoes", conexao);
  return response.data;
}

export async function atualizarConexao(id: string, conexao: Partial<Conexao>): Promise<Conexao> {
  const response = await api.put(`/configuracoes/conexoes/${id}`, conexao);
  return response.data;
}

export async function removerConexao(id: string): Promise<void> {
  await api.delete(`/configuracoes/conexoes/${id}`);
}

export async function listarPermissoes(): Promise<Permissao[]> {
  const response = await api.get("/configuracoes/permissoes");
  return response.data;
}

export async function atualizarPermissao(id: string, permissao: Partial<Permissao>): Promise<Permissao> {
  const response = await api.put(`/configuracoes/permissoes/${id}`, permissao);
  return response.data;
}

export async function buscarParametros() {
  const response = await api.get("/configuracoes/parametros");
  return response.data;
}

export async function atualizarParametros(parametros: Record<string, any>) {
  const response = await api.put("/configuracoes/parametros", parametros);
  return response.data;
}

export async function testarConexaoExterna(id: string): Promise<{ status: string; mensagem: string }> {
  const response = await api.post(`/configuracoes/conexoes/${id}/testar`);
  return response.data;
} 