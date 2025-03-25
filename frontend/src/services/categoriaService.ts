import api from "./api";
import { Categoria } from "../types";
import { listarCategoriasMock, buscarCategoriaMock, cadastrarCategoriaMock, atualizarCategoriaMock, removerCategoriaMock } from "./categoriaServiceMock";
import { useMock } from "../utils/mock";
import { getEmpresaId } from "../utils/auth";

export async function listarCategorias(): Promise<Categoria[]> {
  // Verificar se deve usar mock
  if (useMock()) {
    console.log("Usando dados mock para categorias");
    return listarCategoriasMock();
  }
  
  // Obter ID da empresa
  const id_empresa = getEmpresaId();
  if (!id_empresa) {
    console.error("ID da empresa não disponível");
    return [];
  }
  
  try {
    const response = await api.get("/categorias", {
      params: { id_empresa }
    });
    return response.data.items || response.data;
  } catch (error) {
    console.error("Erro ao listar categorias:", error);
    return [];
  }
}

export async function buscarCategoria(id: string): Promise<Categoria> {
  // Verificar se deve usar mock
  if (useMock()) {
    return buscarCategoriaMock(id);
  }
  
  // Obter ID da empresa
  const id_empresa = getEmpresaId();
  if (!id_empresa) {
    throw new Error("ID da empresa não disponível");
  }
  
  const response = await api.get(`/categorias/${id}`, {
    params: { id_empresa }
  });
  return response.data;
}

export async function cadastrarCategoria(categoria: Omit<Categoria, "id_categoria">): Promise<Categoria> {
  // Verificar se deve usar mock
  if (useMock()) {
    return cadastrarCategoriaMock(categoria);
  }
  
  // Obter ID da empresa
  const id_empresa = getEmpresaId();
  if (!id_empresa) {
    throw new Error("ID da empresa não disponível");
  }
  
  // Adicionar o ID da empresa aos dados da categoria
  const categoriaData = {
    ...categoria,
    id_empresa
  };
  
  const response = await api.post("/categorias", categoriaData);
  return response.data;
}

export async function atualizarCategoria(id: string, categoria: Partial<Categoria>): Promise<Categoria> {
  // Verificar se deve usar mock
  if (useMock()) {
    return atualizarCategoriaMock(id, categoria);
  }
  
  // Obter ID da empresa
  const id_empresa = getEmpresaId();
  if (!id_empresa) {
    throw new Error("ID da empresa não disponível");
  }
  
  const response = await api.put(`/categorias/${id}`, categoria, {
    params: { id_empresa }
  });
  return response.data;
}

export async function removerCategoria(id: string): Promise<void> {
  // Verificar se deve usar mock
  if (useMock()) {
    return removerCategoriaMock(id);
  }
  
  // Obter ID da empresa
  const id_empresa = getEmpresaId();
  if (!id_empresa) {
    throw new Error("ID da empresa não disponível");
  }
  
  await api.delete(`/categorias/${id}`, {
    params: { id_empresa }
  });
} 