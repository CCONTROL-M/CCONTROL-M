import api from "./api";
import { Venda, NovaVenda } from "../types";
import { getEmpresaId } from "../utils/auth";
import { listarVendasMock } from "./vendaServiceMock";
import { useMock } from "../utils/mock";

// ID de empresa de teste para ambiente de desenvolvimento
const EMPRESA_TESTE_ID = "11111111-1111-1111-1111-111111111111";

// Função para obter ID da empresa ou usar valor padrão para desenvolvimento
function getEmpresa(): string {
  // Tenta obter do token
  const empresaId = getEmpresaId();
  
  // Se encontrou no token, usa o valor real
  if (empresaId) {
    return empresaId;
  }
  
  // Verifica se estamos em ambiente de desenvolvimento
  if (import.meta.env.DEV) {
    console.warn('ID da empresa não disponível no token. Usando ID de teste para ambiente de desenvolvimento.');
    return EMPRESA_TESTE_ID;
  }
  
  // Em produção, lança erro
  throw new Error("ID da empresa não disponível. Faça login novamente.");
}

export async function listarVendas(): Promise<Venda[]> {
  // Verificar se devemos usar dados mock
  if (useMock()) {
    console.log("Usando dados mock para vendas");
    return await listarVendasMock();
  }
  
  try {
    // Obter o ID da empresa usando função helper
    const id_empresa = getEmpresa();
    
    console.log("Buscando vendas para empresa:", id_empresa);
    
    // URL corrigida para incluir o prefixo /api/v1
    const response = await api.get("/api/v1/vendas", {
      params: { id_empresa }
    });
    
    console.log("Resposta da API:", response.data);
    
    // Verificação do formato da resposta
    if (response.data && response.data.items) {
      return response.data.items;
    } else if (Array.isArray(response.data)) {
      return response.data;
    } else {
      console.warn("Formato inesperado de resposta:", response.data);
      return [];
    }
  } catch (error) {
    console.error("Erro ao listar vendas:", error);
    console.warn("Usando dados mock após falha na API");
    return await listarVendasMock();
  }
}

export async function buscarVenda(id: string): Promise<Venda> {
  // Usar mock se configurado
  if (useMock()) {
    const vendasMock = await listarVendasMock();
    const venda = vendasMock.find(v => v.id_venda === id);
    if (venda) return venda;
    throw new Error("Venda não encontrada");
  }
  
  try {
    const id_empresa = getEmpresa();
    
    const response = await api.get(`/api/v1/vendas/${id}`, {
      params: { id_empresa }
    });
    
    return response.data;
  } catch (error) {
    console.error("Erro ao buscar venda:", error);
    // Tentar fallback para mock
    const vendasMock = await listarVendasMock();
    const venda = vendasMock.find(v => v.id_venda === id);
    if (venda) return venda;
    throw error;
  }
}

export async function cadastrarVenda(venda: NovaVenda): Promise<Venda> {
  // Logs para debug
  if (import.meta.env.DEV) {
    console.log("Cadastrando venda:", venda);
  }
  
  // Usar mock se configurado
  if (useMock()) {
    console.log("Usando mock para cadastrar venda");
    // Simular criação com dados mockados
    return {
      id_venda: `mock-${Date.now()}`,
      id_empresa: getEmpresa(),
      ...venda,
      data_venda: new Date().toISOString().split('T')[0],
      status: "confirmada"
    } as Venda;
  }
  
  try {
    const id_empresa = getEmpresa();
    
    // Adicionar id_empresa aos dados da venda
    const vendaData = {
      ...venda,
      id_empresa
    };
    
    const response = await api.post("/api/v1/vendas", vendaData);
    return response.data;
  } catch (error) {
    console.error("Erro ao cadastrar venda:", error);
    // Falhar silenciosamente em desenvolvimento com mock
    if (import.meta.env.DEV) {
      console.warn("Usando mock após falha na API");
      return {
        id_venda: `mock-${Date.now()}`,
        id_empresa: getEmpresa(),
        ...venda,
        data_venda: new Date().toISOString().split('T')[0],
        status: "confirmada"
      } as Venda;
    }
    throw error;
  }
}

export async function atualizarVenda(id: string, venda: Partial<Venda>): Promise<Venda> {
  const id_empresa = getEmpresa();
  
  const response = await api.put(`/api/v1/vendas/${id}`, venda, {
    params: { id_empresa }
  });
  
  return response.data;
}

export async function removerVenda(id: string): Promise<void> {
  const id_empresa = getEmpresa();
  
  await api.delete(`/api/v1/vendas/${id}`, {
    params: { id_empresa }
  });
}

export async function listarParcelasPorVenda(id: string) {
  const id_empresa = getEmpresa();
  
  const response = await api.get(`/api/v1/vendas/${id}/parcelas`, {
    params: { id_empresa }
  });
  
  return response.data;
} 