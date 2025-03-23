import { FormaPagamento } from "../types";

// Dados de exemplo para formas de pagamento
const formasPagamentoMock: FormaPagamento[] = [
  {
    id_forma: "1",
    tipo: "Dinheiro",
    taxas: "0%",
    prazo: "À vista"
  },
  {
    id_forma: "2",
    tipo: "Cartão de Crédito",
    taxas: "2.5%",
    prazo: "30 dias"
  },
  {
    id_forma: "3",
    tipo: "Cartão de Débito",
    taxas: "1.5%",
    prazo: "1 dia útil"
  },
  {
    id_forma: "4",
    tipo: "Boleto",
    taxas: "1.2%",
    prazo: "3 dias úteis"
  },
  {
    id_forma: "5",
    tipo: "Transferência Bancária",
    taxas: "0%",
    prazo: "1 dia útil"
  },
  {
    id_forma: "6",
    tipo: "Pix",
    taxas: "0%",
    prazo: "Imediato"
  }
];

/**
 * Simula a listagem de formas de pagamento
 */
export async function listarFormasPagamentoMock(): Promise<FormaPagamento[]> {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([...formasPagamentoMock]);
    }, 500);
  });
}

/**
 * Simula a busca de uma forma de pagamento pelo ID
 */
export async function buscarFormaPagamentoMock(id: string): Promise<FormaPagamento> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const formaPagamento = formasPagamentoMock.find(fp => fp.id_forma === id);
      if (formaPagamento) {
        resolve({...formaPagamento});
      } else {
        reject(new Error(`Forma de pagamento com ID ${id} não encontrada`));
      }
    }, 500);
  });
}

/**
 * Simula o cadastro de uma nova forma de pagamento
 */
export async function cadastrarFormaPagamentoMock(formaPagamento: Omit<FormaPagamento, "id_forma">): Promise<FormaPagamento> {
  return new Promise((resolve) => {
    setTimeout(() => {
      const novaFormaPagamento: FormaPagamento = {
        ...formaPagamento,
        id_forma: String(formasPagamentoMock.length + 1)
      };
      formasPagamentoMock.push(novaFormaPagamento);
      resolve({...novaFormaPagamento});
    }, 500);
  });
}

/**
 * Simula a atualização de uma forma de pagamento
 */
export async function atualizarFormaPagamentoMock(id: string, formaPagamento: Partial<FormaPagamento>): Promise<FormaPagamento> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const index = formasPagamentoMock.findIndex(fp => fp.id_forma === id);
      if (index !== -1) {
        formasPagamentoMock[index] = { ...formasPagamentoMock[index], ...formaPagamento };
        resolve({...formasPagamentoMock[index]});
      } else {
        reject(new Error(`Forma de pagamento com ID ${id} não encontrada`));
      }
    }, 500);
  });
}

/**
 * Simula a remoção de uma forma de pagamento
 */
export async function removerFormaPagamentoMock(id: string): Promise<void> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const index = formasPagamentoMock.findIndex(fp => fp.id_forma === id);
      if (index !== -1) {
        formasPagamentoMock.splice(index, 1);
        resolve();
      } else {
        reject(new Error(`Forma de pagamento com ID ${id} não encontrada`));
      }
    }, 500);
  });
}

export default {
  listarFormasPagamento: listarFormasPagamentoMock,
  buscarFormaPagamento: buscarFormaPagamentoMock,
  cadastrarFormaPagamento: cadastrarFormaPagamentoMock,
  atualizarFormaPagamento: atualizarFormaPagamentoMock,
  removerFormaPagamento: removerFormaPagamentoMock
}; 