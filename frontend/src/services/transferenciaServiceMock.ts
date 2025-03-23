import { Transferencia } from "../types";

// Dados de exemplo para transferências
const transferenciasMock: Transferencia[] = [
  {
    id_transferencia: "1",
    data: "2023-11-05",
    conta_origem: "Banco do Brasil",
    conta_destino: "Caixa Econômica",
    valor: 2000.00,
    status: "Concluída"
  },
  {
    id_transferencia: "2",
    data: "2023-11-08",
    conta_origem: "Nubank",
    conta_destino: "Banco do Brasil",
    valor: 1500.00,
    status: "Concluída"
  },
  {
    id_transferencia: "3",
    data: "2023-11-12",
    conta_origem: "Caixa Econômica",
    conta_destino: "Itaú",
    valor: 3000.00,
    status: "Pendente"
  },
  {
    id_transferencia: "4",
    data: "2023-11-15",
    conta_origem: "Itaú",
    conta_destino: "Santander",
    valor: 5000.00,
    status: "Concluída"
  },
  {
    id_transferencia: "5",
    data: "2023-11-20",
    conta_origem: "Santander",
    conta_destino: "Nubank",
    valor: 1200.00,
    status: "Agendada"
  }
];

// Função para listar todas as transferências
export async function listarTransferenciasMock(): Promise<Transferencia[]> {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([...transferenciasMock]);
    }, 500);
  });
}

// Função para buscar uma transferência pelo ID
export async function buscarTransferenciaMock(id: string): Promise<Transferencia> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const transferencia = transferenciasMock.find(t => t.id_transferencia === id);
      if (transferencia) {
        resolve({...transferencia});
      } else {
        reject(new Error(`Transferência com ID ${id} não encontrada`));
      }
    }, 500);
  });
}

// Função para cadastrar uma nova transferência
export async function cadastrarTransferenciaMock(transferencia: Omit<Transferencia, "id_transferencia">): Promise<Transferencia> {
  return new Promise((resolve) => {
    setTimeout(() => {
      const novaTransferencia: Transferencia = {
        ...transferencia,
        id_transferencia: String(transferenciasMock.length + 1)
      };
      transferenciasMock.push(novaTransferencia);
      resolve({...novaTransferencia});
    }, 500);
  });
}

// Função para atualizar uma transferência existente
export async function atualizarTransferenciaMock(id: string, transferencia: Partial<Transferencia>): Promise<Transferencia> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const index = transferenciasMock.findIndex(t => t.id_transferencia === id);
      if (index !== -1) {
        transferenciasMock[index] = { ...transferenciasMock[index], ...transferencia };
        resolve({...transferenciasMock[index]});
      } else {
        reject(new Error(`Transferência com ID ${id} não encontrada`));
      }
    }, 500);
  });
}

// Função para remover uma transferência
export async function removerTransferenciaMock(id: string): Promise<void> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const index = transferenciasMock.findIndex(t => t.id_transferencia === id);
      if (index !== -1) {
        transferenciasMock.splice(index, 1);
        resolve();
      } else {
        reject(new Error(`Transferência com ID ${id} não encontrada`));
      }
    }, 500);
  });
}

// Função para filtrar transferências
export async function filtrarTransferenciasMock(filtros: { 
  dataInicio?: string; 
  dataFim?: string;
  contaOrigem?: string;
  contaDestino?: string;
  status?: string;
}): Promise<Transferencia[]> {
  return new Promise((resolve) => {
    setTimeout(() => {
      let resultado = [...transferenciasMock];
      
      // Filtrar por data de início
      if (filtros.dataInicio) {
        resultado = resultado.filter(t => t.data >= filtros.dataInicio!);
      }
      
      // Filtrar por data de fim
      if (filtros.dataFim) {
        resultado = resultado.filter(t => t.data <= filtros.dataFim!);
      }
      
      // Filtrar por conta de origem
      if (filtros.contaOrigem) {
        resultado = resultado.filter(t => t.conta_origem.includes(filtros.contaOrigem!));
      }
      
      // Filtrar por conta de destino
      if (filtros.contaDestino) {
        resultado = resultado.filter(t => t.conta_destino.includes(filtros.contaDestino!));
      }
      
      // Filtrar por status
      if (filtros.status) {
        resultado = resultado.filter(t => t.status === filtros.status);
      }
      
      resolve(resultado);
    }, 500);
  });
} 