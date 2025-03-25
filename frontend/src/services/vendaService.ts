import api from "./api";
import { Venda, NovaVenda } from "../types";
import { getEmpresaId } from "../utils/auth";
import { listarVendasMock } from "./vendaServiceMock";
import { useMock } from "../utils/mock";

// Função para obter ID da empresa ou lançar erro
function getEmpresa(): string {
  // Tenta obter do token
  const empresaId = getEmpresaId();
  
  // Se encontrou no token, usa o valor real
  if (empresaId) {
    return empresaId;
  }
  
  // Verifica se estamos em ambiente de desenvolvimento
  if (import.meta.env.DEV) {
    console.error('ID da empresa não disponível no token. Use a página de empresas para selecionar uma empresa.');
  }
  
  // Lançar erro
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
    
    // URL corrigida, sem o prefixo /api/v1 duplicado
    const response = await api.get("/vendas", {
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
    // Desativar fallback para mock - retornar lista vazia em caso de erro
    return [];
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
    
    const response = await api.get(`/vendas/${id}`, {
      params: { id_empresa }
    });
    
    return response.data;
  } catch (error) {
    console.error("Erro ao buscar venda:", error);
    // Não usar fallback para mock - repassar o erro original
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
    
    const response = await api.post("/vendas", vendaData);
    return response.data;
  } catch (error) {
    console.error("Erro ao cadastrar venda:", error);
    // Remover fallback para mock - sempre lançar o erro original
    throw error;
  }
}

export async function atualizarVenda(id: string, venda: Partial<Venda>): Promise<Venda> {
  const id_empresa = getEmpresa();
  
  const response = await api.put(`/vendas/${id}`, venda, {
    params: { id_empresa }
  });
  
  return response.data;
}

export async function removerVenda(id: string): Promise<void> {
  const id_empresa = getEmpresa();
  
  await api.delete(`/vendas/${id}`, {
    params: { id_empresa }
  });
}

export async function listarParcelasPorVenda(id: string) {
  const id_empresa = getEmpresa();
  
  const response = await api.get(`/vendas/${id}/parcelas`, {
    params: { id_empresa }
  });
  
  return response.data;
} 