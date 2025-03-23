import api from "./api";
import { FormaPagamento } from "../types";
import { useMock } from '../utils/mock';
import {
  listarFormasPagamentoMock,
  buscarFormaPagamentoMock,
  cadastrarFormaPagamentoMock,
  atualizarFormaPagamentoMock,
  removerFormaPagamentoMock
} from './formaPagamentoServiceMock';

export async function listarFormasPagamento(): Promise<FormaPagamento[]> {
  if (useMock()) {
    return listarFormasPagamentoMock();
  }
  
  const response = await api.get("/formas-pagamento");
  return response.data;
}

export async function buscarFormaPagamento(id: string): Promise<FormaPagamento> {
  if (useMock()) {
    return buscarFormaPagamentoMock(id);
  }
  
  const response = await api.get(`/formas-pagamento/${id}`);
  return response.data;
}

export async function cadastrarFormaPagamento(formaPagamento: Omit<FormaPagamento, "id_forma">): Promise<FormaPagamento> {
  if (useMock()) {
    return cadastrarFormaPagamentoMock(formaPagamento);
  }
  
  const response = await api.post("/formas-pagamento", formaPagamento);
  return response.data;
}

export async function atualizarFormaPagamento(id: string, formaPagamento: Partial<FormaPagamento>): Promise<FormaPagamento> {
  if (useMock()) {
    return atualizarFormaPagamentoMock(id, formaPagamento);
  }
  
  const response = await api.put(`/formas-pagamento/${id}`, formaPagamento);
  return response.data;
}

export async function removerFormaPagamento(id: string): Promise<void> {
  if (useMock()) {
    return removerFormaPagamentoMock(id);
  }
  
  await api.delete(`/formas-pagamento/${id}`);
} 