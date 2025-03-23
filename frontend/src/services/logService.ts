import api from "./api";
import { Log } from "../types";

export async function listarLogs(): Promise<Log[]> {
  const response = await api.get("/logs");
  return response.data;
}

export async function buscarLog(id: string): Promise<Log> {
  const response = await api.get(`/logs/${id}`);
  return response.data;
}

export async function filtrarLogs(filtros: { 
  dataInicio?: string; 
  dataFim?: string;
  usuario?: string;
  acao?: string;
}): Promise<Log[]> {
  const response = await api.get("/logs", { params: filtros });
  return response.data;
} 