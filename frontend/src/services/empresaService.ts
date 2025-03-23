import api from "./api";
import { Empresa } from "../types";
import { useMock } from "../utils/mock";

// Estendendo a interface Empresa para incluir campos adicionais
export interface EmpresaCompleta extends Empresa {
  razao_social: string;
  nome_fantasia?: string;
  ativo: boolean;
  cidade?: string;
  estado?: string;
}

// Dados mock para empresas
const empresasMock: EmpresaCompleta[] = [
  {
    id_empresa: "1",
    nome: "Empresa Principal",
    razao_social: "Empresa Principal LTDA",
    nome_fantasia: "Principal",
    cnpj: "12.345.678/0001-90",
    contato: "contato@empresaprincipal.com",
    ativo: true,
    cidade: "São Paulo",
    estado: "SP",
    created_at: "2023-01-01"
  },
  {
    id_empresa: "2",
    nome: "Empresa Secundária",
    razao_social: "Empresa Secundária LTDA",
    nome_fantasia: "Secundária",
    cnpj: "98.765.432/0001-10",
    contato: "contato@empresasecundaria.com",
    ativo: true,
    cidade: "Rio de Janeiro",
    estado: "RJ",
    created_at: "2023-02-01"
  }
];

// Funções mock
async function listarEmpresasMock(): Promise<EmpresaCompleta[]> {
  await new Promise(resolve => setTimeout(resolve, 500));
  return [...empresasMock];
}

async function buscarEmpresaMock(id: string): Promise<EmpresaCompleta> {
  await new Promise(resolve => setTimeout(resolve, 300));
  const empresa = empresasMock.find(e => e.id_empresa === id);
  if (!empresa) throw new Error("Empresa não encontrada");
  return {...empresa};
}

export async function listarEmpresas(): Promise<EmpresaCompleta[]> {
  // Verificar se deve usar mock
  if (useMock()) {
    console.log("Usando dados mock para empresas");
    return listarEmpresasMock();
  }
  
  const response = await api.get("/api/v1/empresas");
  return response.data.items || response.data;
}

export async function buscarEmpresa(id: string): Promise<EmpresaCompleta> {
  // Verificar se deve usar mock
  if (useMock()) {
    return buscarEmpresaMock(id);
  }
  
  const response = await api.get(`/api/v1/empresas/${id}`);
  return response.data;
}

export async function cadastrarEmpresa(empresa: Omit<EmpresaCompleta, "id_empresa">): Promise<EmpresaCompleta> {
  // Verificar se deve usar mock
  if (useMock()) {
    const novaEmpresa = {
      ...empresa,
      id_empresa: `${Date.now()}`,
      created_at: new Date().toISOString().split('T')[0]
    } as EmpresaCompleta;
    empresasMock.push(novaEmpresa);
    return {...novaEmpresa};
  }
  
  const response = await api.post("/api/v1/empresas", empresa);
  return response.data;
}

export async function atualizarEmpresa(id: string, empresa: Partial<EmpresaCompleta>): Promise<EmpresaCompleta> {
  // Verificar se deve usar mock
  if (useMock()) {
    const index = empresasMock.findIndex(e => e.id_empresa === id);
    if (index === -1) throw new Error("Empresa não encontrada");
    empresasMock[index] = { ...empresasMock[index], ...empresa };
    return {...empresasMock[index]};
  }
  
  const response = await api.put(`/api/v1/empresas/${id}`, empresa);
  return response.data;
}

export async function removerEmpresa(id: string): Promise<void> {
  // Verificar se deve usar mock
  if (useMock()) {
    const index = empresasMock.findIndex(e => e.id_empresa === id);
    if (index === -1) throw new Error("Empresa não encontrada");
    empresasMock.splice(index, 1);
    return;
  }
  
  await api.delete(`/api/v1/empresas/${id}`);
}

export async function buscarEmpresaAtual(): Promise<EmpresaCompleta> {
  // Verificar se deve usar mock
  if (useMock()) {
    // Retornar a primeira empresa como atual
    return {...empresasMock[0]};
  }
  
  const response = await api.get("/api/v1/empresas/atual");
  return response.data;
}

export async function definirEmpresaAtual(id: string): Promise<EmpresaCompleta> {
  // Verificar se deve usar mock
  if (useMock()) {
    const empresa = empresasMock.find(e => e.id_empresa === id);
    if (!empresa) throw new Error("Empresa não encontrada");
    return {...empresa};
  }
  
  const response = await api.post(`/api/v1/empresas/${id}/definir-atual`);
  return response.data;
} 