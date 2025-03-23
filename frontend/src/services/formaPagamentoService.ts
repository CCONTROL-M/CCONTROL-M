import api from "./api";
import { FormaPagamento } from "../types";

export async function listarFormasPagamento(): Promise<FormaPagamento[]> {
  const response = await api.get("/formas-pagamento");
  return response.data;
}

export async function buscarFormaPagamento(id: string): Promise<FormaPagamento> {
  const response = await api.get(`/formas-pagamento/${id}`);
  return response.data;
}

export async function cadastrarFormaPagamento(formaPagamento: Omit<FormaPagamento, "id_forma">): Promise<FormaPagamento> {
  const response = await api.post("/formas-pagamento", formaPagamento);
  return response.data;
}

export async function atualizarFormaPagamento(id: string, formaPagamento: Partial<FormaPagamento>): Promise<FormaPagamento> {
  const response = await api.put(`/formas-pagamento/${id}`, formaPagamento);
  return response.data;
}

export async function removerFormaPagamento(id: string): Promise<void> {
  await api.delete(`/formas-pagamento/${id}`);
} 