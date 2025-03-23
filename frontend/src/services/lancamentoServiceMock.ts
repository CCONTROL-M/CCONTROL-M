import { Lancamento } from "../types";

// Dados de exemplo para lançamentos
const lancamentosMock: Lancamento[] = [
  {
    id_lancamento: "1",
    data: "2023-11-10",
    valor: 1500.00,
    status: "Pago",
    id_categoria: "1",
    id_centro: "1",
    id_conta_bancaria: "1",
    observacao: "Pagamento de fornecedor"
  },
  {
    id_lancamento: "2",
    data: "2023-11-15",
    valor: 3000.00,
    status: "Pendente",
    id_categoria: "2",
    id_cliente: "1",
    observacao: "Venda de produto"
  },
  {
    id_lancamento: "3",
    data: "2023-11-20",
    valor: 750.50,
    status: "Pago",
    id_categoria: "3",
    id_fornecedor: "2",
    id_conta_bancaria: "1",
    observacao: "Compra de material de escritório"
  },
  {
    id_lancamento: "4",
    data: "2023-11-25",
    valor: 5000.00,
    status: "Agendado",
    id_categoria: "4",
    id_cliente: "3",
    id_conta_bancaria: "2",
    observacao: "Prestação de serviço"
  },
  {
    id_lancamento: "5",
    data: "2023-11-30",
    valor: 1200.00,
    status: "Pago",
    id_categoria: "5",
    id_centro: "2",
    id_conta_bancaria: "1",
    observacao: "Pagamento de aluguel"
  }
];

// Função para listar todos os lançamentos
export async function listarLancamentosMock(): Promise<Lancamento[]> {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([...lancamentosMock]);
    }, 500); // Simular um pequeno atraso de rede
  });
}

// Função para buscar um lançamento pelo ID
export async function buscarLancamentoMock(id: string): Promise<Lancamento> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const lancamento = lancamentosMock.find(l => l.id_lancamento === id);
      if (lancamento) {
        resolve({...lancamento});
      } else {
        reject(new Error(`Lançamento com ID ${id} não encontrado`));
      }
    }, 500);
  });
}

// Função para cadastrar um novo lançamento
export async function cadastrarLancamentoMock(lancamento: Omit<Lancamento, "id_lancamento">): Promise<Lancamento> {
  return new Promise((resolve) => {
    setTimeout(() => {
      const novoLancamento: Lancamento = {
        ...lancamento,
        id_lancamento: String(lancamentosMock.length + 1)
      };
      lancamentosMock.push(novoLancamento);
      resolve({...novoLancamento});
    }, 500);
  });
}

// Função para atualizar um lançamento existente
export async function atualizarLancamentoMock(id: string, lancamento: Partial<Lancamento>): Promise<Lancamento> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const index = lancamentosMock.findIndex(l => l.id_lancamento === id);
      if (index !== -1) {
        lancamentosMock[index] = { ...lancamentosMock[index], ...lancamento };
        resolve({...lancamentosMock[index]});
      } else {
        reject(new Error(`Lançamento com ID ${id} não encontrado`));
      }
    }, 500);
  });
}

// Função para remover um lançamento
export async function removerLancamentoMock(id: string): Promise<void> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const index = lancamentosMock.findIndex(l => l.id_lancamento === id);
      if (index !== -1) {
        lancamentosMock.splice(index, 1);
        resolve();
      } else {
        reject(new Error(`Lançamento com ID ${id} não encontrado`));
      }
    }, 500);
  });
}

// Função para filtrar lançamentos
export async function filtrarLancamentosMock(filtros: { 
  dataInicio?: string; 
  dataFim?: string;
  tipo?: string;
  status?: string;
}): Promise<Lancamento[]> {
  return new Promise((resolve) => {
    setTimeout(() => {
      let resultado = [...lancamentosMock];
      
      // Filtrar por data de início
      if (filtros.dataInicio) {
        resultado = resultado.filter(l => l.data >= filtros.dataInicio!);
      }
      
      // Filtrar por data de fim
      if (filtros.dataFim) {
        resultado = resultado.filter(l => l.data <= filtros.dataFim!);
      }
      
      // Filtrar por status
      if (filtros.status) {
        resultado = resultado.filter(l => l.status === filtros.status);
      }
      
      resolve(resultado);
    }, 500);
  });
} 