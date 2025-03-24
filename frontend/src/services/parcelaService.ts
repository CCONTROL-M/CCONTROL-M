import api from "./api";
import { Parcela } from "../types";
import { useMock } from "../utils/mock";
import { 
    listarParcelasMock, 
    buscarParcelaMock, 
    cadastrarParcelaMock, 
    atualizarParcelaMock, 
    removerParcelaMock, 
    filtrarParcelasPorVendaMock 
} from "./parcelaServiceMock";

export async function listarParcelas(): Promise<Parcela[]> {
  // Verificar se deve usar mock
  if (useMock()) {
    console.log("Usando dados mock para parcelas");
    return listarParcelasMock();
  }
  
  const response = await api.get("/parcelas");
  return response.data;
}

export async function buscarParcela(id: string): Promise<Parcela> {
  // Verificar se deve usar mock
  if (useMock()) {
    return buscarParcelaMock(id);
  }
  
  const response = await api.get(`/parcelas/${id}`);
  return response.data;
}

export async function cadastrarParcela(parcela: Omit<Parcela, "id_parcela">): Promise<Parcela> {
  // Verificar se deve usar mock
  if (useMock()) {
    return cadastrarParcelaMock(parcela);
  }
  
  const response = await api.post("/parcelas", parcela);
  return response.data;
}

export async function atualizarParcela(id: string, parcela: Partial<Parcela>): Promise<Parcela> {
  // Verificar se deve usar mock
  if (useMock()) {
    return atualizarParcelaMock(id, parcela);
  }
  
  const response = await api.put(`/parcelas/${id}`, parcela);
  return response.data;
}

export async function removerParcela(id: string): Promise<void> {
  // Verificar se deve usar mock
  if (useMock()) {
    return removerParcelaMock(id);
  }
  
  await api.delete(`/parcelas/${id}`);
}

export async function filtrarParcelasPorVenda(idVenda: string): Promise<Parcela[]> {
  // Verificar se deve usar mock
  if (useMock()) {
    return filtrarParcelasPorVendaMock(idVenda);
  }
  
  const response = await api.get(`/parcelas/venda/${idVenda}`);
  return response.data;
}

export async function marcarComoPaga(id: string, dataPagamento: string): Promise<Parcela> {
  const response = await api.post(`/parcelas/${id}/pagar`, { data_pagamento: dataPagamento });
  return response.data;
}

export async function filtrarParcelas(filtros: { 
  dataInicio?: string; 
  dataFim?: string;
  status?: string;
  idVenda?: string;
}): Promise<Parcela[]> {
  const response = await api.get("/parcelas", { params: filtros });
  return response.data;
}

/**
 * Interface para os dados da ação de inadimplência
 */
interface AcaoInadimplenciaData {
  id_parcela: string;
  tipo_acao: 'cobranca' | 'renegociacao';
  observacao: string;
  dataNovoVencimento?: string;
  valorNovo?: number;
  dataContato: string;
  meioComunicacao: string;
  responsavel: string;
}

/**
 * Registra uma ação de cobrança ou renegociação para uma parcela inadimplente
 */
export async function registrarAcaoInadimplencia(dados: AcaoInadimplenciaData): Promise<Parcela> {
  // Verificar se deve usar mock
  if (useMock()) {
    // Como não há implementação mock para esta função, simulamos um atraso
    // e retornamos uma parcela atualizada simulando o resultado da operação
    return new Promise((resolve) => {
      setTimeout(() => {
        // Buscar a parcela pelo ID
        buscarParcelaMock(dados.id_parcela).then(parcela => {
          // Se for renegociação, atualizamos a parcela
          if (dados.tipo_acao === 'renegociacao' && dados.dataNovoVencimento && dados.valorNovo) {
            const parcelaAtualizada: Parcela = {
              ...parcela,
              data_vencimento: dados.dataNovoVencimento,
              valor: dados.valorNovo,
              // Podemos adicionar campos adicionais se necessário
            };
            resolve(parcelaAtualizada);
          } else {
            // Se for cobrança, apenas retornamos a parcela original
            resolve(parcela);
          }
        });
      }, 1000);
    });
  }
  
  // Implementação real usando a API
  const response = await api.post(`/parcelas/${dados.id_parcela}/acao`, {
    tipo_acao: dados.tipo_acao,
    observacao: dados.observacao,
    data_novo_vencimento: dados.dataNovoVencimento,
    valor_novo: dados.valorNovo,
    data_contato: dados.dataContato,
    meio_comunicacao: dados.meioComunicacao,
    responsavel: dados.responsavel
  });
  
  return response.data;
} 