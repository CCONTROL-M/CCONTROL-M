import api from "./api";
import { Log } from "../types";
import { useMock } from '../utils/mock';
import { 
  listarLogsMock, 
  buscarLogMock, 
  filtrarLogsMock 
} from './logServiceMock';

export async function listarLogs(): Promise<Log[]> {
  if (useMock()) {
    return listarLogsMock();
  }
  
  const response = await api.get("/logs");
  return response.data;
}

export async function buscarLog(id: string): Promise<Log> {
  if (useMock()) {
    return buscarLogMock(id);
  }
  
  const response = await api.get(`/logs/${id}`);
  return response.data;
}

export async function filtrarLogs(filtros: {
  dataInicio?: string;
  dataFim?: string;
  usuario?: string;
  acao?: string;
}): Promise<Log[]> {
  if (useMock()) {
    return filtrarLogsMock(filtros);
  }
  
  const response = await api.get("/logs/filtrar", { params: filtros });
  return response.data;
} 