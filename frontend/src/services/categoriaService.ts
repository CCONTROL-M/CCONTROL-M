import api from "./api";
import { Categoria } from "../types";
import { listarCategoriasMock, buscarCategoriaMock, cadastrarCategoriaMock, atualizarCategoriaMock, removerCategoriaMock } from "./categoriaServiceMock";
import { useMock } from "../utils/mock";

export async function listarCategorias(): Promise<Categoria[]> {
  // Verificar se deve usar mock
  if (useMock()) {
    console.log("Usando dados mock para categorias");
    return listarCategoriasMock();
  }
  
  const response = await api.get("/categorias");
  return response.data;
}

export async function buscarCategoria(id: string): Promise<Categoria> {
  // Verificar se deve usar mock
  if (useMock()) {
    return buscarCategoriaMock(id);
  }
  
  const response = await api.get(`/categorias/${id}`);
  return response.data;
}

export async function cadastrarCategoria(categoria: Omit<Categoria, "id_categoria">): Promise<Categoria> {
  // Verificar se deve usar mock
  if (useMock()) {
    return cadastrarCategoriaMock(categoria);
  }
  
  const response = await api.post("/categorias", categoria);
  return response.data;
}

export async function atualizarCategoria(id: string, categoria: Partial<Categoria>): Promise<Categoria> {
  // Verificar se deve usar mock
  if (useMock()) {
    return atualizarCategoriaMock(id, categoria);
  }
  
  const response = await api.put(`/categorias/${id}`, categoria);
  return response.data;
}

export async function removerCategoria(id: string): Promise<void> {
  // Verificar se deve usar mock
  if (useMock()) {
    return removerCategoriaMock(id);
  }
  
  await api.delete(`/categorias/${id}`);
} 