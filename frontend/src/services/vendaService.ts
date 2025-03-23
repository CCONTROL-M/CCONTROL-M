import api from "./api";
import { Venda, NovaVenda } from "../types";

export async function listarVendas(): Promise<Venda[]> {
  const response = await api.get("/vendas");
  return response.data;
}

export async function buscarVenda(id: string): Promise<Venda> {
  const response = await api.get(`/vendas/${id}`);
  return response.data;
}

export async function cadastrarVenda(venda: NovaVenda): Promise<Venda> {
  const response = await api.post("/vendas", venda);
  return response.data;
}

export async function atualizarVenda(id: string, venda: Partial<Venda>): Promise<Venda> {
  const response = await api.put(`/vendas/${id}`, venda);
  return response.data;
}

export async function removerVenda(id: string): Promise<void> {
  await api.delete(`/vendas/${id}`);
}

export async function listarParcelasPorVenda(id: string) {
  const response = await api.get(`/vendas/${id}/parcelas`);
  return response.data;
} 