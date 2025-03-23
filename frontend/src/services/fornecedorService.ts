import api from "./api";
import { Fornecedor } from "../types";

export async function listarFornecedores(): Promise<Fornecedor[]> {
  const response = await api.get("/fornecedores");
  return response.data;
}

export async function buscarFornecedor(id: string): Promise<Fornecedor> {
  const response = await api.get(`/fornecedores/${id}`);
  return response.data;
}

export async function cadastrarFornecedor(fornecedor: Omit<Fornecedor, "id_fornecedor">): Promise<Fornecedor> {
  const response = await api.post("/fornecedores", fornecedor);
  return response.data;
}

export async function atualizarFornecedor(id: string, fornecedor: Partial<Fornecedor>): Promise<Fornecedor> {
  const response = await api.put(`/fornecedores/${id}`, fornecedor);
  return response.data;
}

export async function removerFornecedor(id: string): Promise<void> {
  await api.delete(`/fornecedores/${id}`);
} 