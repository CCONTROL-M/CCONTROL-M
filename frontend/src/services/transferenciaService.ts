import api from "./api";
import { Transferencia } from "../types";

export async function listarTransferencias(): Promise<Transferencia[]> {
  const response = await api.get("/transferencias");
  return response.data;
}

export async function buscarTransferencia(id: string): Promise<Transferencia> {
  const response = await api.get(`/transferencias/${id}`);
  return response.data;
}

export async function cadastrarTransferencia(transferencia: Omit<Transferencia, "id_transferencia">): Promise<Transferencia> {
  const response = await api.post("/transferencias", transferencia);
  return response.data;
}

export async function atualizarTransferencia(id: string, transferencia: Partial<Transferencia>): Promise<Transferencia> {
  const response = await api.put(`/transferencias/${id}`, transferencia);
  return response.data;
}

export async function filtrarTransferencias(filtros: { 
  dataInicio?: string; 
  dataFim?: string;
  contaOrigem?: string;
  contaDestino?: string;
  status?: string;
}): Promise<Transferencia[]> {
  const response = await api.get("/transferencias", { params: filtros });
  return response.data;
} 