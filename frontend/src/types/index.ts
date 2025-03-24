export interface Cliente {
  id_cliente: string;
  nome: string;
  cpf_cnpj: string;
  contato: string;
  created_at: string;
}

export interface Fornecedor {
  id_fornecedor: string;
  nome: string;
  cnpj: string;
  contato: string;
  avaliacao: string;
  created_at: string;
}

export interface ContaBancaria {
  id_conta: string;
  nome: string;
  banco: string;
  agencia: string;
  conta: string;
  tipo: string;
  saldo_inicial: number;
  saldo_atual: number;
  ativa: boolean;
  mostrar_dashboard?: boolean;
  created_at: string;
}

export interface Venda {
  id_venda: string;
  id_empresa?: string;
  id_cliente?: string;
  cliente?: {
    id_cliente: string;
    nome: string;
    documento?: string;
    tipo?: string;
  };
  nome_cliente?: string;
  valor_total: number;
  valor_pago?: number;
  numero_parcelas: number;
  data_venda?: string;
  data_inicio?: string;
  descricao: string;
  status: string;
  created_at?: string;
  id_forma_pagamento?: string;
  forma_pagamento?: {
    id_forma_pagamento: string;
    nome: string;
    tipo: string;
  };
}

export interface Parcela {
  id_parcela: string;
  id_venda: string;
  numero?: number;
  valor: number;
  data_vencimento: string;
  data_pagamento?: string;
  status: string;
}

export interface Lancamento {
  id_lancamento: string;
  id_venda?: string;
  id_cliente?: string;
  id_conta_bancaria?: string;
  id_categoria?: string;
  id_centro?: string;
  id_fornecedor?: string;
  data: string;
  valor: number;
  status: string;
  comprovante_url?: string;
  observacao?: string;
}

export interface Categoria {
  id_categoria: string;
  nome: string;
  tipo: string;
}

export interface CentroCusto {
  id_centro: string;
  nome: string;
}

export interface FormaPagamento {
  id_forma: string;
  tipo: string;
  taxas: string;
  prazo: string;
}

export interface Usuario {
  id_usuario: string;
  nome: string;
  email: string;
  tipo_usuario: string;
  created_at: string;
}

export interface Permissao {
  id_usuario: string;
  telas_permitidas: string[];
}

export interface Conexao {
  id_conexao: string;
  nome: string;
  tipo: string;
  url: string;
  usuario?: string;
  senha?: string;
  api_key?: string;
  parametros_adicionais?: string;
}

export interface Parametro {
  id_parametro: string;
  chave: string;
  valor: string;
  descricao: string;
}

export interface Empresa {
  id_empresa: string;
  nome: string;
  cnpj: string;
  contato: string;
  created_at: string;
}

// Interfaces adicionais para dados específicos de páginas

export interface ResumoDashboard {
  caixa_atual: number;
  total_receber: number;
  total_pagar: number;
  recebimentos_hoje: number;
  pagamentos_hoje: number;
}

export interface CategoriaValor {
  categoria: string;
  valor: number;
}

export interface DREData {
  receitas: CategoriaValor[];
  despesas: CategoriaValor[];
  lucro_prejuizo: number;
}

export interface NovaVenda {
  id_cliente: string;
  valor_total: number;
  numero_parcelas: number;
  data_inicio: string;
  descricao: string;
  categoria: string;
}

export interface APIResponse {
  status: number;
  data: any;
  error?: string;
}

export interface Transferencia {
  id_transferencia: string;
  data: string;
  conta_origem: string;
  conta_destino: string;
  valor: number;
  status: string;
}

export interface FluxoItem {
  data: string;
  tipo: string;
  descricao: string;
  valor: number;
}

export interface FluxoGrupo {
  data: string;
  itens: FluxoItem[];
}

export interface Inadimplente {
  id_parcela: string;
  cliente: string;
  valor: number;
  vencimento: string;
  dias_em_atraso: number;
}

export interface Ciclo {
  cliente: string;
  data_pedido: string;
  data_faturamento: string;
  data_recebimento: string;
  dias_entre: number;
}

export interface Log {
  id_log: string;
  acao: string;
  data: string;
  usuario: string;
  detalhes: string;
} 