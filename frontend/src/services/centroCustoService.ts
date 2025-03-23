import api from "./api";
import { CentroCusto } from "../types";

export async function listarCentrosCusto(): Promise<CentroCusto[]> {
  const response = await api.get("/centros-custo");
  return response.data;
}

export async function buscarCentroCusto(id: string): Promise<CentroCusto> {
  const response = await api.get(`/centros-custo/${id}`);
  return response.data;
}

export async function cadastrarCentroCusto(centroCusto: Omit<CentroCusto, "id_centro_custo">): Promise<CentroCusto> {
  const response = await api.post("/centros-custo", centroCusto);
  return response.data;
}

export async function atualizarCentroCusto(id: string, centroCusto: Partial<CentroCusto>): Promise<CentroCusto> {
  const response = await api.put(`/centros-custo/${id}`, centroCusto);
  return response.data;
}

export async function removerCentroCusto(id: string): Promise<void> {
  await api.delete(`/centros-custo/${id}`);
} 