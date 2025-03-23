import api from "./api";
import { Conexao, Permissao, Parametro } from "../types";
import { 
  listarParametrosMock, 
  buscarParametrosMock, 
  atualizarParametrosMock,
  listarConexoesMock,
  buscarConexaoMock,
  cadastrarConexaoMock,
  atualizarConexaoMock,
  removerConexaoMock,
  testarConexaoExternaMock,
  listarPermissoesMock,
  atualizarPermissaoMock
} from "./configuracoesServiceMock";
import { useMock } from "../utils/mock";

export async function listarParametros(): Promise<Parametro[]> {
  // Verificar se deve usar mock
  if (useMock()) {
    console.log("Usando dados mock para parâmetros do sistema");
    return listarParametrosMock();
  }
  
  const response = await api.get("/configuracoes/parametros");
  return response.data;
}

export async function listarConexoes(): Promise<Conexao[]> {
  // Verificar se deve usar mock
  if (useMock()) {
    console.log("Usando dados mock para conexões externas");
    return listarConexoesMock();
  }
  
  const response = await api.get("/configuracoes/conexoes");
  return response.data;
}

export async function buscarConexao(id: string): Promise<Conexao> {
  // Verificar se deve usar mock
  if (useMock()) {
    return buscarConexaoMock(id);
  }
  
  const response = await api.get(`/configuracoes/conexoes/${id}`);
  return response.data;
}

export async function cadastrarConexao(conexao: Omit<Conexao, "id_conexao">): Promise<Conexao> {
  // Verificar se deve usar mock
  if (useMock()) {
    return cadastrarConexaoMock(conexao);
  }
  
  const response = await api.post("/configuracoes/conexoes", conexao);
  return response.data;
}

export async function atualizarConexao(id: string, conexao: Partial<Conexao>): Promise<Conexao> {
  // Verificar se deve usar mock
  if (useMock()) {
    return atualizarConexaoMock(id, conexao);
  }
  
  const response = await api.put(`/configuracoes/conexoes/${id}`, conexao);
  return response.data;
}

export async function removerConexao(id: string): Promise<void> {
  // Verificar se deve usar mock
  if (useMock()) {
    return removerConexaoMock(id);
  }
  
  await api.delete(`/configuracoes/conexoes/${id}`);
}

export async function listarPermissoes(): Promise<(Permissao & { nome: string })[]> {
  // Verificar se deve usar mock
  if (useMock()) {
    console.log("Usando dados mock para permissões");
    return listarPermissoesMock();
  }
  
  const response = await api.get("/usuarios/permissoes");
  return response.data;
}

export async function atualizarPermissao(id: string, permissao: Partial<Permissao>): Promise<Permissao> {
  // Verificar se deve usar mock
  if (useMock()) {
    return atualizarPermissaoMock(id, permissao);
  }
  
  const response = await api.put(`/configuracoes/permissoes/${id}`, permissao);
  return response.data;
}

export async function buscarParametros() {
  // Verificar se deve usar mock
  if (useMock()) {
    return buscarParametrosMock();
  }
  
  const response = await api.get("/configuracoes/parametros");
  return response.data;
}

export async function atualizarParametros(parametros: Record<string, any>) {
  // Verificar se deve usar mock
  if (useMock()) {
    return atualizarParametrosMock(parametros);
  }
  
  const response = await api.put("/configuracoes/parametros", parametros);
  return response.data;
}

export async function testarConexaoExterna(id: string): Promise<{ status: string; mensagem: string }> {
  // Verificar se deve usar mock
  if (useMock()) {
    return testarConexaoExternaMock(id);
  }
  
  const response = await api.post(`/configuracoes/conexoes/${id}/testar`);
  return response.data;
} 