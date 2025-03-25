import api from "./api";
import { CentroCusto } from "../types";
import { useMock } from "../utils/mock";
import { getEmpresa } from "../utils/auth";

// Como não encontramos um arquivo de mock para este serviço, vamos criar dados mock simples aqui
const centrosCustoMock: CentroCusto[] = [
  {
    id_centro: "1",
    nome: "Administrativo"
  },
  {
    id_centro: "2",
    nome: "Comercial"
  },
  {
    id_centro: "3",
    nome: "Financeiro"
  },
  {
    id_centro: "4",
    nome: "Operacional"
  }
];

// Funções mock para o serviço
async function listarCentrosCustoMock(): Promise<CentroCusto[]> {
  await new Promise(resolve => setTimeout(resolve, 500)); // Delay simulado
  return [...centrosCustoMock];
}

async function buscarCentroCustoMock(id: string): Promise<CentroCusto> {
  await new Promise(resolve => setTimeout(resolve, 300)); // Delay simulado
  const item = centrosCustoMock.find(c => c.id_centro === id);
  if (!item) throw new Error("Centro de custo não encontrado");
  return {...item};
}

export async function listarCentrosCusto(): Promise<CentroCusto[]> {
  // Verificar se deve usar mock
  if (useMock()) {
    console.log("Usando dados mock para centros de custo");
    return listarCentrosCustoMock();
  }
  
  const response = await api.get("/centros-custo");
  return response.data.items || response.data;
}

export async function buscarCentroCusto(id: string): Promise<CentroCusto> {
  // Verificar se deve usar mock
  if (useMock()) {
    return buscarCentroCustoMock(id);
  }
  
  const response = await api.get(`/centros-custo/${id}`);
  return response.data;
}

export async function cadastrarCentroCusto(centroCusto: Omit<CentroCusto, "id_centro">): Promise<CentroCusto> {
  // Se estiver em modo mock, cria um mock sem chamar a API
  if (useMock()) {
    const novoCentro = {
      ...centroCusto,
      id_centro: `${Date.now()}`
    } as CentroCusto;
    centrosCustoMock.push(novoCentro);
    return novoCentro;
  }
  
  const id_empresa = getEmpresa();
  
  const centroCustoData = {
    ...centroCusto,
    id_empresa
  };
  
  const response = await api.post("/centros-custo", centroCustoData);
  return response.data;
}

export async function atualizarCentroCusto(id: string, centroCusto: Partial<CentroCusto>): Promise<CentroCusto> {
  // Se estiver em modo mock, atualiza o mock sem chamar a API
  if (useMock()) {
    const index = centrosCustoMock.findIndex(c => c.id_centro === id);
    if (index === -1) throw new Error("Centro de custo não encontrado");
    centrosCustoMock[index] = { ...centrosCustoMock[index], ...centroCusto };
    return centrosCustoMock[index];
  }
  
  const response = await api.put(`/centros-custo/${id}`, centroCusto);
  return response.data;
}

export async function removerCentroCusto(id: string): Promise<void> {
  // Se estiver em modo mock, remove do mock sem chamar a API
  if (useMock()) {
    const index = centrosCustoMock.findIndex(c => c.id_centro === id);
    if (index === -1) throw new Error("Centro de custo não encontrado");
    centrosCustoMock.splice(index, 1);
    return;
  }
  
  await api.delete(`/centros-custo/${id}`);
} 