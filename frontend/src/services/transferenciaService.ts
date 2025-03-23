import api from './api';
import { Transferencia } from '../types';
import { useMock } from '../utils/mock';
import {
  listarTransferenciasMock,
  buscarTransferenciaMock,
  cadastrarTransferenciaMock,
  atualizarTransferenciaMock,
  removerTransferenciaMock,
  filtrarTransferenciasMock
} from './transferenciaServiceMock';

// Função para listar todas as transferências
export async function listarTransferencias(): Promise<Transferencia[]> {
  if (useMock()) {
    return listarTransferenciasMock();
  }
  
  const response = await api.get('/transferencias');
  return response.data;
}

// Função para buscar uma transferência pelo ID
export async function buscarTransferencia(id: string): Promise<Transferencia> {
  if (useMock()) {
    return buscarTransferenciaMock(id);
  }
  
  const response = await api.get(`/transferencias/${id}`);
  return response.data;
}

// Função para cadastrar uma nova transferência
export async function cadastrarTransferencia(transferencia: Omit<Transferencia, 'id_transferencia'>): Promise<Transferencia> {
  if (useMock()) {
    return cadastrarTransferenciaMock(transferencia);
  }
  
  const response = await api.post('/transferencias', transferencia);
  return response.data;
}

// Função para atualizar uma transferência existente
export async function atualizarTransferencia(id: string, transferencia: Partial<Transferencia>): Promise<Transferencia> {
  if (useMock()) {
    return atualizarTransferenciaMock(id, transferencia);
  }
  
  const response = await api.put(`/transferencias/${id}`, transferencia);
  return response.data;
}

// Função para remover uma transferência
export async function removerTransferencia(id: string): Promise<void> {
  if (useMock()) {
    return removerTransferenciaMock(id);
  }
  
  await api.delete(`/transferencias/${id}`);
}

// Função para filtrar transferências
export async function filtrarTransferencias(filtros: {
  dataInicio?: string;
  dataFim?: string;
  contaOrigem?: string;
  contaDestino?: string;
  status?: string;
}): Promise<Transferencia[]> {
  if (useMock()) {
    return filtrarTransferenciasMock(filtros);
  }
  
  const response = await api.get('/transferencias/filtrar', { params: filtros });
  return response.data;
} 