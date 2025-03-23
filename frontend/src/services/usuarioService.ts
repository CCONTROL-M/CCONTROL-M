import api from "./api";
import { Usuario } from "../types";
import { getEmpresa, formatarResposta } from "../utils/empresa";

export async function listarUsuarios(): Promise<Usuario[]> {
  try {
    const response = await api.get("/usuarios", {
      params: { id_empresa: getEmpresa() }
    });
    
    return formatarResposta<Usuario>(response.data);
  } catch (error) {
    console.error("Erro ao listar usuários:", error);
    throw error;
  }
}

export async function buscarUsuario(id: string): Promise<Usuario> {
  const response = await api.get(`/usuarios/${id}`, {
    params: { id_empresa: getEmpresa() }
  });
  
  return response.data;
}

export async function buscarUsuarioAtual(): Promise<Usuario> {
  const response = await api.get("/usuarios/me");
  return response.data;
}

export async function cadastrarUsuario(usuario: Omit<Usuario, "id_usuario" | "created_at">): Promise<Usuario> {
  const userData = {
    ...usuario,
    id_empresa: getEmpresa()
  };
  
  const response = await api.post("/usuarios", userData);
  return response.data;
}

export async function atualizarUsuario(id: string, usuario: Partial<Usuario>): Promise<Usuario> {
  const response = await api.put(`/usuarios/${id}`, usuario, {
    params: { id_empresa: getEmpresa() }
  });
  
  return response.data;
}

export async function removerUsuario(id: string): Promise<void> {
  await api.delete(`/usuarios/${id}`, {
    params: { id_empresa: getEmpresa() }
  });
}

export async function login(email: string, senha: string): Promise<{ token: string; usuario: Usuario }> {
  const response = await api.post("/auth/login", { email, senha });
  return response.data;
}

export async function logout(): Promise<void> {
  localStorage.removeItem("token");
}

export async function alterarSenha(senhaAtual: string, novaSenha: string): Promise<void> {
  await api.post("/usuarios/alterar-senha", { 
    senhaAtual, 
    novaSenha,
    id_empresa: getEmpresa()
  });
} 