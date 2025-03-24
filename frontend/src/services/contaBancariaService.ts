import api from "./api";
import { ContaBancaria } from "../types";
import { listarContasBancariasMock, buscarContaBancariaMock, cadastrarContaBancariaMock, atualizarContaBancariaMock, removerContaBancariaMock } from "./contaBancariaServiceMock";
import { useMock, registerApiError } from "../utils/mock";

interface ContaBancariaCreate {
  nome: string;
  banco: string;
  agencia: string;
  conta: string;
  tipo: string;
  saldo_inicial: number;
  ativa: boolean;
  mostrar_dashboard?: boolean;
  id_empresa?: string;
}

export async function listarContasBancarias(id_empresa: string = '1'): Promise<ContaBancaria[]> {
  // Verificar se deve usar mock
  if (useMock()) {
    console.log("Usando dados mock para contas bancárias");
    return listarContasBancariasMock();
  }
  
  try {
    console.log(`Buscando contas bancárias para empresa ID: ${id_empresa}`);
    const response = await api.get("/contas-bancarias", {
      params: { id_empresa }
    });
    return response.data.items;
  } catch (error) {
    console.error("Erro ao listar contas bancárias:", error);
    // Registrar o erro para diagnóstico
    registerApiError("/contas-bancarias", error);
    throw error;
  }
}

export async function buscarContaBancaria(id: string, id_empresa: string = '1'): Promise<ContaBancaria> {
  // Verificar se deve usar mock
  if (useMock()) {
    return buscarContaBancariaMock(id);
  }
  
  try {
    const response = await api.get(`/contas-bancarias/${id}`, {
      params: { id_empresa }
    });
    return response.data;
  } catch (error) {
    console.error(`Erro ao buscar conta bancária ID ${id}:`, error);
    registerApiError(`/contas-bancarias/${id}`, error);
    throw error;
  }
}

export async function cadastrarContaBancaria(conta: ContaBancariaCreate): Promise<ContaBancaria> {
  // Verificar se deve usar mock
  if (useMock()) {
    return cadastrarContaBancariaMock(conta);
  }
  
  try {
    const response = await api.post("/contas-bancarias", {
      ...conta,
      id_empresa: conta.id_empresa || '1'
    });
    return response.data;
  } catch (error) {
    console.error("Erro ao cadastrar conta bancária:", error);
    registerApiError("/contas-bancarias [POST]", error);
    throw error;
  }
}

export async function atualizarContaBancaria(id: string, conta: Partial<ContaBancariaCreate>, id_empresa: string = '1'): Promise<ContaBancaria> {
  // Verificar se deve usar mock
  if (useMock()) {
    return atualizarContaBancariaMock(id, conta);
  }
  
  try {
    const response = await api.put(`/contas-bancarias/${id}`, conta, {
      params: { id_empresa }
    });
    return response.data;
  } catch (error) {
    console.error(`Erro ao atualizar conta bancária ID ${id}:`, error);
    registerApiError(`/contas-bancarias/${id} [PUT]`, error);
    throw error;
  }
}

export async function removerContaBancaria(id: string, id_empresa: string = '1'): Promise<void> {
  // Verificar se deve usar mock
  if (useMock()) {
    return removerContaBancariaMock(id);
  }
  
  try {
    await api.delete(`/contas-bancarias/${id}`, {
      params: { id_empresa }
    });
  } catch (error) {
    console.error(`Erro ao remover conta bancária ID ${id}:`, error);
    registerApiError(`/contas-bancarias/${id} [DELETE]`, error);
    throw error;
  }
} 