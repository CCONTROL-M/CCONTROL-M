import { Parametro, Conexao, Permissao } from "../types";

// Dados de exemplo para parâmetros do sistema
const parametrosMock: Parametro[] = [
  {
    id_parametro: "1",
    chave: "empresa_nome",
    valor: "CCONTROL-M Software Financeiro",
    descricao: "Nome da empresa exibido no sistema"
  },
  {
    id_parametro: "2",
    chave: "moeda_padrao",
    valor: "BRL",
    descricao: "Moeda padrão para exibição de valores"
  },
  {
    id_parametro: "3",
    chave: "formato_data",
    valor: "DD/MM/YYYY",
    descricao: "Formato de data padrão do sistema"
  },
  {
    id_parametro: "4",
    chave: "dias_alerta_vencimento",
    valor: "3",
    descricao: "Dias antes do vencimento para exibir alertas"
  },
  {
    id_parametro: "5",
    chave: "tema_padrao",
    valor: "claro",
    descricao: "Tema visual padrão do sistema"
  }
];

// Dados de exemplo para conexões externas
const conexoesMock: Conexao[] = [
  {
    id_conexao: "1",
    nome: "API Banco Central",
    tipo: "REST",
    url: "https://api.bancoCentral.gov.br/v1"
  },
  {
    id_conexao: "2",
    nome: "Serviço de Nota Fiscal",
    tipo: "SOAP",
    url: "https://nfe.fazenda.gov.br/soap"
  },
  {
    id_conexao: "3",
    nome: "API Cielo",
    tipo: "REST",
    url: "https://api.cielo.com.br/v3"
  },
  {
    id_conexao: "4",
    nome: "API Correios",
    tipo: "REST",
    url: "https://api.correios.com.br/v1"
  }
];

// Dados de exemplo para permissões de usuários
const permissoesMock: (Permissao & { nome: string })[] = [
  {
    id_usuario: "1",
    nome: "Administrador",
    telas_permitidas: ["dashboard", "lancamentos", "clientes", "fornecedores", "contas-bancarias", "categorias", "centro-custos", "relatorios", "configuracoes"]
  },
  {
    id_usuario: "2",
    nome: "Contador",
    telas_permitidas: ["dashboard", "lancamentos", "categorias", "relatorios"]
  },
  {
    id_usuario: "3",
    nome: "Vendedor",
    telas_permitidas: ["dashboard", "clientes", "lancamentos"]
  },
  {
    id_usuario: "4",
    nome: "Financeiro",
    telas_permitidas: ["lancamentos", "contas-bancarias", "fornecedores", "relatorios"]
  }
];

// Funções mock para parâmetros
export async function listarParametrosMock(): Promise<Parametro[]> {
  await new Promise(resolve => setTimeout(resolve, 500)); // Simulação de delay
  return [...parametrosMock];
}

export async function buscarParametrosMock(): Promise<Parametro[]> {
  await new Promise(resolve => setTimeout(resolve, 300));
  return [...parametrosMock];
}

export async function atualizarParametrosMock(parametros: Record<string, any>): Promise<Parametro[]> {
  await new Promise(resolve => setTimeout(resolve, 800));
  
  // Atualizar valores dos parâmetros existentes
  for (const chave in parametros) {
    const parametro = parametrosMock.find(p => p.chave === chave);
    if (parametro) {
      parametro.valor = parametros[chave];
    }
  }
  
  return [...parametrosMock];
}

// Funções mock para conexões
export async function listarConexoesMock(): Promise<Conexao[]> {
  await new Promise(resolve => setTimeout(resolve, 500));
  return [...conexoesMock];
}

export async function buscarConexaoMock(id: string): Promise<Conexao> {
  await new Promise(resolve => setTimeout(resolve, 300));
  const conexao = conexoesMock.find(c => c.id_conexao === id);
  if (!conexao) throw new Error("Conexão não encontrada");
  return {...conexao};
}

export async function cadastrarConexaoMock(conexao: Omit<Conexao, "id_conexao">): Promise<Conexao> {
  await new Promise(resolve => setTimeout(resolve, 700));
  
  const novaConexao = {
    ...conexao,
    id_conexao: `${Date.now()}`
  } as Conexao;
  
  conexoesMock.push(novaConexao);
  return {...novaConexao};
}

export async function atualizarConexaoMock(id: string, conexao: Partial<Conexao>): Promise<Conexao> {
  await new Promise(resolve => setTimeout(resolve, 600));
  
  const index = conexoesMock.findIndex(c => c.id_conexao === id);
  if (index === -1) throw new Error("Conexão não encontrada");
  
  conexoesMock[index] = { ...conexoesMock[index], ...conexao };
  return {...conexoesMock[index]};
}

export async function removerConexaoMock(id: string): Promise<void> {
  await new Promise(resolve => setTimeout(resolve, 500));
  
  const index = conexoesMock.findIndex(c => c.id_conexao === id);
  if (index === -1) throw new Error("Conexão não encontrada");
  
  conexoesMock.splice(index, 1);
}

export async function testarConexaoExternaMock(id: string): Promise<{ status: string; mensagem: string }> {
  await new Promise(resolve => setTimeout(resolve, 1000)); // Simulação de teste de conexão
  
  const existe = conexoesMock.some(c => c.id_conexao === id);
  if (!existe) throw new Error("Conexão não encontrada");
  
  // Simulação de sucesso/falha aleatória
  const sucesso = Math.random() > 0.3;
  
  return {
    status: sucesso ? "sucesso" : "erro",
    mensagem: sucesso ? "Conexão testada com sucesso." : "Falha ao conectar: timeout."
  };
}

// Funções mock para permissões
export async function listarPermissoesMock(): Promise<(Permissao & { nome: string })[]> {
  await new Promise(resolve => setTimeout(resolve, 500));
  return [...permissoesMock];
}

export async function atualizarPermissaoMock(id: string, permissao: Partial<Permissao>): Promise<Permissao & { nome: string }> {
  await new Promise(resolve => setTimeout(resolve, 600));
  
  const index = permissoesMock.findIndex(p => p.id_usuario === id);
  if (index === -1) throw new Error("Permissão não encontrada");
  
  permissoesMock[index] = { ...permissoesMock[index], ...permissao };
  return {...permissoesMock[index]};
} 