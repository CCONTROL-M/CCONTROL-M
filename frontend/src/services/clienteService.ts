import api from "./api";
import { Cliente } from "../types";
import { getEmpresa, formatarResposta } from "../utils/empresa";
import { listarClientesMock, buscarClienteMock, cadastrarClienteMock, atualizarClienteMock, removerClienteMock } from "./clienteServiceMock";
import { useMock } from "../utils/mock";

export async function listarClientes(): Promise<Cliente[]> {
  // Verificar se deve usar mock
  if (useMock()) {
    console.log("Usando dados mock para clientes");
    return listarClientesMock();
  }
  
  try {
    const id_empresa = getEmpresa();
    
    const response = await api.get("/clientes", {
      params: { id_empresa }
    });
    
    return formatarResposta<Cliente>(response.data);
  } catch (error) {
    console.error("Erro ao listar clientes:", error);
    throw error;
  }
}

export async function buscarCliente(id: string): Promise<Cliente> {
  // Verificar se deve usar mock
  if (useMock()) {
    return buscarClienteMock(id);
  }
  
  const response = await api.get(`/clientes/${id}`, {
    params: { id_empresa: getEmpresa() }
  });
  
  return response.data;
}

export async function cadastrarCliente(cliente: Omit<Cliente, "id_cliente">): Promise<Cliente> {
  // Verificar se deve usar mock
  if (useMock()) {
    return cadastrarClienteMock(cliente);
  }
  
  // Adicionar id_empresa aos dados
  const clienteData = {
    ...cliente,
    id_empresa: getEmpresa()
  };
  
  const response = await api.post("/clientes", clienteData);
  return response.data;
}

export async function atualizarCliente(id: string, cliente: Partial<Cliente>): Promise<Cliente> {
  // Verificar se deve usar mock
  if (useMock()) {
    return atualizarClienteMock(id, cliente);
  }
  
  const response = await api.put(`/clientes/${id}`, cliente, {
    params: { id_empresa: getEmpresa() }
  });
  
  return response.data;
}

export async function removerCliente(id: string): Promise<void> {
  // Verificar se deve usar mock
  if (useMock()) {
    return removerClienteMock(id);
  }
  
  await api.delete(`/clientes/${id}`, {
    params: { id_empresa: getEmpresa() }
  });
} 