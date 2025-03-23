import api from "./api";
import { Fornecedor } from "../types";
import { getEmpresa, formatarResposta } from "../utils/empresa";
import { listarFornecedoresMock, buscarFornecedorMock, cadastrarFornecedorMock, atualizarFornecedorMock, removerFornecedorMock } from "./fornecedorServiceMock";
import { useMock } from "../utils/mock";

export async function listarFornecedores(): Promise<Fornecedor[]> {
  // Verificar se deve usar mock
  if (useMock()) {
    console.log("Usando dados mock para fornecedores");
    return listarFornecedoresMock();
  }
  
  try {
    const response = await api.get("/fornecedores", {
      params: { id_empresa: getEmpresa() }
    });
    
    return formatarResposta<Fornecedor>(response.data);
  } catch (error) {
    console.error("Erro ao listar fornecedores:", error);
    throw error;
  }
}

export async function buscarFornecedor(id: string): Promise<Fornecedor> {
  // Verificar se deve usar mock
  if (useMock()) {
    return buscarFornecedorMock(id);
  }
  
  const response = await api.get(`/fornecedores/${id}`, {
    params: { id_empresa: getEmpresa() }
  });
  
  return response.data;
}

export async function cadastrarFornecedor(fornecedor: Omit<Fornecedor, "id_fornecedor">): Promise<Fornecedor> {
  // Verificar se deve usar mock
  if (useMock()) {
    return cadastrarFornecedorMock(fornecedor);
  }
  
  // Adicionar id_empresa aos dados
  const fornecedorData = {
    ...fornecedor,
    id_empresa: getEmpresa()
  };
  
  const response = await api.post("/fornecedores", fornecedorData);
  return response.data;
}

export async function atualizarFornecedor(id: string, fornecedor: Partial<Fornecedor>): Promise<Fornecedor> {
  // Verificar se deve usar mock
  if (useMock()) {
    return atualizarFornecedorMock(id, fornecedor);
  }
  
  const response = await api.put(`/fornecedores/${id}`, fornecedor, {
    params: { id_empresa: getEmpresa() }
  });
  
  return response.data;
}

export async function removerFornecedor(id: string): Promise<void> {
  // Verificar se deve usar mock
  if (useMock()) {
    return removerFornecedorMock(id);
  }
  
  await api.delete(`/fornecedores/${id}`, {
    params: { id_empresa: getEmpresa() }
  });
} 