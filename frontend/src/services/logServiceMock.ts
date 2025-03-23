import { Log } from "../types";

// Dados de exemplo para logs
const logsMock: Log[] = [
  {
    id_log: "1",
    data: "2023-11-01T08:30:00",
    usuario: "admin",
    acao: "Login",
    detalhes: "Login bem-sucedido"
  },
  {
    id_log: "2",
    data: "2023-11-01T09:15:00",
    usuario: "admin",
    acao: "Cadastro",
    detalhes: "Cadastro de novo cliente: Empresa ABC"
  },
  {
    id_log: "3",
    data: "2023-11-01T10:20:00",
    usuario: "maria",
    acao: "Atualização",
    detalhes: "Atualização de dados do fornecedor ID: 12"
  },
  {
    id_log: "4",
    data: "2023-11-01T11:05:00",
    usuario: "joao",
    acao: "Exclusão",
    detalhes: "Exclusão de lançamento ID: 45"
  },
  {
    id_log: "5",
    data: "2023-11-01T14:30:00",
    usuario: "admin",
    acao: "Configuração",
    detalhes: "Alteração nos parâmetros do sistema"
  },
  {
    id_log: "6",
    data: "2023-11-01T15:45:00",
    usuario: "maria",
    acao: "Venda",
    detalhes: "Registro de nova venda ID: 78"
  },
  {
    id_log: "7",
    data: "2023-11-01T16:20:00",
    usuario: "joao",
    acao: "Transferência",
    detalhes: "Transferência entre contas ID: 23"
  },
  {
    id_log: "8",
    data: "2023-11-01T17:00:00",
    usuario: "admin",
    acao: "Logout",
    detalhes: "Logout do sistema"
  }
];

// Função para listar todos os logs
export async function listarLogsMock(): Promise<Log[]> {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([...logsMock]);
    }, 500);
  });
}

// Função para buscar um log pelo ID
export async function buscarLogMock(id: string): Promise<Log> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const log = logsMock.find(l => l.id_log === id);
      if (log) {
        resolve({...log});
      } else {
        reject(new Error(`Log com ID ${id} não encontrado`));
      }
    }, 500);
  });
}

// Função para filtrar logs
export async function filtrarLogsMock(filtros: {
  dataInicio?: string;
  dataFim?: string;
  usuario?: string;
  acao?: string;
}): Promise<Log[]> {
  return new Promise((resolve) => {
    setTimeout(() => {
      let resultado = [...logsMock];
      
      // Filtrar por data de início
      if (filtros.dataInicio) {
        resultado = resultado.filter(l => l.data >= filtros.dataInicio!);
      }
      
      // Filtrar por data de fim
      if (filtros.dataFim) {
        resultado = resultado.filter(l => l.data <= filtros.dataFim!);
      }
      
      // Filtrar por usuário
      if (filtros.usuario) {
        resultado = resultado.filter(l => l.usuario.includes(filtros.usuario!));
      }
      
      // Filtrar por ação
      if (filtros.acao) {
        resultado = resultado.filter(l => l.acao === filtros.acao);
      }
      
      resolve(resultado);
    }, 500);
  });
} 