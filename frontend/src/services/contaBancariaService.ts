import api from "./api";
import { ContaBancaria } from "../types";

export async function listarContasBancarias(): Promise<ContaBancaria[]> {
  const response = await api.get("/contas-bancarias");
  return response.data;
}

export async function buscarContaBancaria(id: string): Promise<ContaBancaria> {
  const response = await api.get(`/contas-bancarias/${id}`);
  return response.data;
}

export async function cadastrarContaBancaria(conta: Omit<ContaBancaria, "id_conta">): Promise<ContaBancaria> {
  const response = await api.post("/contas-bancarias", conta);
  return response.data;
}

export async function atualizarContaBancaria(id: string, conta: Partial<ContaBancaria>): Promise<ContaBancaria> {
  const response = await api.put(`/contas-bancarias/${id}`, conta);
  return response.data;
}

export async function removerContaBancaria(id: string): Promise<void> {
  await api.delete(`/contas-bancarias/${id}`);
} 