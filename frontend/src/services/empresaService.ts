import api from "./api";
import { Empresa } from "../types";

export async function listarEmpresas(): Promise<Empresa[]> {
  const response = await api.get("/empresas");
  return response.data;
}

export async function buscarEmpresa(id: string): Promise<Empresa> {
  const response = await api.get(`/empresas/${id}`);
  return response.data;
}

export async function cadastrarEmpresa(empresa: Omit<Empresa, "id_empresa">): Promise<Empresa> {
  const response = await api.post("/empresas", empresa);
  return response.data;
}

export async function atualizarEmpresa(id: string, empresa: Partial<Empresa>): Promise<Empresa> {
  const response = await api.put(`/empresas/${id}`, empresa);
  return response.data;
}

export async function removerEmpresa(id: string): Promise<void> {
  await api.delete(`/empresas/${id}`);
}

export async function buscarEmpresaAtual(): Promise<Empresa> {
  const response = await api.get("/empresas/atual");
  return response.data;
}

export async function definirEmpresaAtual(id: string): Promise<Empresa> {
  const response = await api.post("/empresas/atual", { id_empresa: id });
  return response.data;
} 