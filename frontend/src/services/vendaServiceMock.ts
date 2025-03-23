import { Venda, NovaVenda } from "../types";

// Dados de exemplo para vendas
const vendasMock: Venda[] = [
  {
    id_venda: "1",
    id_empresa: "11111111-1111-1111-1111-111111111111",
    id_cliente: "cliente-1",
    cliente: {
      id_cliente: "cliente-1",
      nome: "Cliente Exemplo 1",
      documento: "123.456.789-00",
      tipo: "PF"
    },
    valor_total: 1500.00,
    data_venda: "2023-08-15",
    status: "confirmada",
    descricao: "Venda à vista",
    numero_parcelas: 1,
    id_forma_pagamento: "forma-1",
    forma_pagamento: {
      id_forma_pagamento: "forma-1",
      nome: "Cartão de Crédito",
      tipo: "cartao_credito"
    }
  },
  {
    id_venda: "2",
    id_empresa: "11111111-1111-1111-1111-111111111111",
    id_cliente: "cliente-2",
    cliente: {
      id_cliente: "cliente-2",
      nome: "Cliente Exemplo 2",
      documento: "98.765.432-1",
      tipo: "PF"
    },
    valor_total: 2500.00,
    data_venda: "2023-08-20",
    status: "confirmada",
    descricao: "Venda parcelada",
    numero_parcelas: 3,
    id_forma_pagamento: "forma-2",
    forma_pagamento: {
      id_forma_pagamento: "forma-2",
      nome: "Boleto",
      tipo: "boleto"
    }
  }
];

/**
 * Simula a listagem de vendas
 */
export async function listarVendasMock(): Promise<Venda[]> {
  // Simula um atraso de rede
  await new Promise(resolve => setTimeout(resolve, 500));
  
  // Retorna os dados mocados
  return vendasMock;
}

/**
 * Simula a busca de uma venda pelo ID
 */
export async function buscarVendaMock(id: string): Promise<Venda> {
  // Simula um atraso de rede
  await new Promise(resolve => setTimeout(resolve, 300));
  
  // Busca a venda pelo ID
  const venda = vendasMock.find(v => v.id_venda === id);
  
  // Se não encontrar, simula um erro
  if (!venda) {
    throw new Error("Venda não encontrada");
  }
  
  return venda;
}

/**
 * Simula o cadastro de uma nova venda
 */
export async function cadastrarVendaMock(venda: NovaVenda): Promise<Venda> {
  // Simula um atraso de rede
  await new Promise(resolve => setTimeout(resolve, 800));
  
  // Cria uma nova venda com ID gerado
  const novaVenda: Venda = {
    id_venda: `venda-${Date.now()}`,
    id_empresa: "11111111-1111-1111-1111-111111111111",
    id_cliente: venda.id_cliente,
    valor_total: venda.valor_total,
    numero_parcelas: venda.numero_parcelas,
    data_venda: new Date().toISOString().split('T')[0],
    data_inicio: venda.data_inicio,
    descricao: venda.descricao,
    status: "confirmada",
    cliente: {
      id_cliente: venda.id_cliente,
      nome: "Cliente Exemplo",
      documento: "000.000.000-00",
      tipo: "PF"
    },
    forma_pagamento: {
      id_forma_pagamento: "forma-1",
      nome: "Forma de Pagamento",
      tipo: "cartao_credito"
    }
  };
  
  // Adiciona à lista de vendas mock
  vendasMock.push(novaVenda);
  
  return novaVenda;
}

export default {
  listarVendas: listarVendasMock,
  buscarVenda: buscarVendaMock,
  cadastrarVenda: cadastrarVendaMock
}; 