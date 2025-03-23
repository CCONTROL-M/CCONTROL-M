import { Parcela } from "../types";

// Dados de exemplo para parcelas
const parcelasMock: Parcela[] = [
  {
    id_parcela: "1",
    id_venda: "venda-0001",
    valor: 500.00,
    data_vencimento: "2023-11-15",
    status: "Paga"
  },
  {
    id_parcela: "2",
    id_venda: "venda-0001",
    valor: 500.00,
    data_vencimento: "2023-12-15",
    status: "Pendente"
  },
  {
    id_parcela: "3",
    id_venda: "venda-0002",
    valor: 750.00,
    data_vencimento: "2023-11-10",
    status: "Paga"
  },
  {
    id_parcela: "4",
    id_venda: "venda-0002",
    valor: 750.00,
    data_vencimento: "2023-12-10",
    status: "Pendente"
  },
  {
    id_parcela: "5",
    id_venda: "venda-0003",
    valor: 1000.00,
    data_vencimento: "2023-11-20",
    status: "Paga"
  },
  {
    id_parcela: "6",
    id_venda: "venda-0003",
    valor: 1000.00,
    data_vencimento: "2023-12-20",
    status: "Pendente"
  }
];

// Função para listar todas as parcelas
export async function listarParcelasMock(): Promise<Parcela[]> {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([...parcelasMock]);
    }, 500);
  });
}

// Função para buscar uma parcela pelo ID
export async function buscarParcelaMock(id: string): Promise<Parcela> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const parcela = parcelasMock.find(p => p.id_parcela === id);
      if (parcela) {
        resolve({...parcela});
      } else {
        reject(new Error(`Parcela com ID ${id} não encontrada`));
      }
    }, 500);
  });
}

// Função para cadastrar uma nova parcela
export async function cadastrarParcelaMock(parcela: Omit<Parcela, "id_parcela">): Promise<Parcela> {
  return new Promise((resolve) => {
    setTimeout(() => {
      const novaParcela: Parcela = {
        ...parcela,
        id_parcela: String(parcelasMock.length + 1)
      };
      parcelasMock.push(novaParcela);
      resolve({...novaParcela});
    }, 500);
  });
}

// Função para atualizar uma parcela existente
export async function atualizarParcelaMock(id: string, parcela: Partial<Parcela>): Promise<Parcela> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const index = parcelasMock.findIndex(p => p.id_parcela === id);
      if (index !== -1) {
        parcelasMock[index] = { ...parcelasMock[index], ...parcela };
        resolve({...parcelasMock[index]});
      } else {
        reject(new Error(`Parcela com ID ${id} não encontrada`));
      }
    }, 500);
  });
}

// Função para remover uma parcela
export async function removerParcelaMock(id: string): Promise<void> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const index = parcelasMock.findIndex(p => p.id_parcela === id);
      if (index !== -1) {
        parcelasMock.splice(index, 1);
        resolve();
      } else {
        reject(new Error(`Parcela com ID ${id} não encontrada`));
      }
    }, 500);
  });
}

// Função para filtrar parcelas por venda
export async function filtrarParcelasPorVendaMock(idVenda: string): Promise<Parcela[]> {
  return new Promise((resolve) => {
    setTimeout(() => {
      const resultado = parcelasMock.filter(p => p.id_venda === idVenda);
      resolve(resultado);
    }, 500);
  });
} 