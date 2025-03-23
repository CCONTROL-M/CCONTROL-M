import api from "./api";
import { Categoria } from "../types";

export async function listarCategorias(): Promise<Categoria[]> {
  const response = await api.get("/categorias");
  return response.data;
}

export async function buscarCategoria(id: string): Promise<Categoria> {
  const response = await api.get(`/categorias/${id}`);
  return response.data;
}

export async function cadastrarCategoria(categoria: Omit<Categoria, "id_categoria">): Promise<Categoria> {
  const response = await api.post("/categorias", categoria);
  return response.data;
}

export async function atualizarCategoria(id: string, categoria: Partial<Categoria>): Promise<Categoria> {
  const response = await api.put(`/categorias/${id}`, categoria);
  return response.data;
}

export async function removerCategoria(id: string): Promise<void> {
  await api.delete(`/categorias/${id}`);
} 