import api from "./api";
import { Cliente } from "../types";

export async function listarClientes(): Promise<Cliente[]> {
  const response = await api.get("/clientes");
  return response.data;
}

export async function buscarCliente(id: string): Promise<Cliente> {
  const response = await api.get(`/clientes/${id}`);
  return response.data;
}

export async function cadastrarCliente(cliente: Omit<Cliente, "id_cliente">): Promise<Cliente> {
  const response = await api.post("/clientes", cliente);
  return response.data;
}

export async function atualizarCliente(id: string, cliente: Partial<Cliente>): Promise<Cliente> {
  const response = await api.put(`/clientes/${id}`, cliente);
  return response.data;
}

export async function removerCliente(id: string): Promise<void> {
  await api.delete(`/clientes/${id}`);
} 