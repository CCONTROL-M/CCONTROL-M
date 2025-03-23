import api from "./api";
import { Parcela } from "../types";

export async function listarParcelas(): Promise<Parcela[]> {
  const response = await api.get("/parcelas");
  return response.data;
}

export async function buscarParcela(id: string): Promise<Parcela> {
  const response = await api.get(`/parcelas/${id}`);
  return response.data;
}

export async function atualizarParcela(id: string, parcela: Partial<Parcela>): Promise<Parcela> {
  const response = await api.put(`/parcelas/${id}`, parcela);
  return response.data;
}

export async function marcarComoPaga(id: string, dataPagamento: string): Promise<Parcela> {
  const response = await api.post(`/parcelas/${id}/pagar`, { data_pagamento: dataPagamento });
  return response.data;
}

export async function filtrarParcelas(filtros: { 
  dataInicio?: string; 
  dataFim?: string;
  status?: string;
  idVenda?: string;
}): Promise<Parcela[]> {
  const response = await api.get("/parcelas", { params: filtros });
  return response.data;
} 