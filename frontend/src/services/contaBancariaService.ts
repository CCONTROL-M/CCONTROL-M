import api from "./api";
import { ContaBancaria } from "../types";
import { listarContasBancariasMock, buscarContaBancariaMock, cadastrarContaBancariaMock, atualizarContaBancariaMock, removerContaBancariaMock } from "./contaBancariaServiceMock";
import { useMock } from "../utils/mock";

export async function listarContasBancarias(): Promise<ContaBancaria[]> {
  // Verificar se deve usar mock
  if (useMock()) {
    console.log("Usando dados mock para contas bancárias");
    return listarContasBancariasMock();
  }
  
  const response = await api.get("/contas-bancarias");
  return response.data;
}

export async function buscarContaBancaria(id: string): Promise<ContaBancaria> {
  // Verificar se deve usar mock
  if (useMock()) {
    return buscarContaBancariaMock(id);
  }
  
  const response = await api.get(`/contas-bancarias/${id}`);
  return response.data;
}

export async function cadastrarContaBancaria(conta: Omit<ContaBancaria, "id_conta">): Promise<ContaBancaria> {
  // Verificar se deve usar mock
  if (useMock()) {
    return cadastrarContaBancariaMock(conta);
  }
  
  const response = await api.post("/contas-bancarias", conta);
  return response.data;
}

export async function atualizarContaBancaria(id: string, conta: Partial<ContaBancaria>): Promise<ContaBancaria> {
  // Verificar se deve usar mock
  if (useMock()) {
    return atualizarContaBancariaMock(id, conta);
  }
  
  const response = await api.put(`/contas-bancarias/${id}`, conta);
  return response.data;
}

export async function removerContaBancaria(id: string): Promise<void> {
  // Verificar se deve usar mock
  if (useMock()) {
    return removerContaBancariaMock(id);
  }
  
  await api.delete(`/contas-bancarias/${id}`);
} 