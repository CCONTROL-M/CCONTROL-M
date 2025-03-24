import React, { useState, useEffect } from 'react';
import Table, { TableColumn } from '../Table';
import { ContaBancaria } from '../../types';

// Tipo para as transações
interface Transacao {
  id_transacao: string;
  data: string;
  descricao: string;
  valor: number;
  tipo: 'entrada' | 'saida' | 'transferencia';
  categoria?: string;
}

// Mock de dados de transações (em um cenário real, seriam carregados da API)
const mockTransacoes: Transacao[] = [
  {
    id_transacao: '1',
    data: '2023-06-15T10:30:00',
    descricao: 'Pagamento de cliente',
    valor: 1500.00,
    tipo: 'entrada',
    categoria: 'Vendas'
  },
  {
    id_transacao: '2',
    data: '2023-06-12T14:45:00',
    descricao: 'Pagamento de fornecedor',
    valor: -650.75,
    tipo: 'saida',
    categoria: 'Despesas operacionais'
  },
  {
    id_transacao: '3',
    data: '2023-06-05T09:15:00',
    descricao: 'Transferência entre contas',
    valor: -1000.00,
    tipo: 'transferencia',
    categoria: 'Transferências'
  },
  {
    id_transacao: '4',
    data: '2023-05-28T16:20:00',
    descricao: 'Recebimento de venda',
    valor: 890.50,
    tipo: 'entrada',
    categoria: 'Vendas'
  },
  {
    id_transacao: '5',
    data: '2023-05-25T11:10:00',
    descricao: 'Pagamento de aluguel',
    valor: -1200.00,
    tipo: 'saida',
    categoria: 'Aluguel'
  }
];

interface TransacoesContaBancariaProps {
  conta: ContaBancaria;
}

/**
 * Componente para exibir transações relacionadas a uma conta bancária
 */
export default function TransacoesContaBancaria({ conta }: TransacoesContaBancariaProps) {
  const [transacoes, setTransacoes] = useState<Transacao[]>([]);
  const [loading, setLoading] = useState(true);

  // Buscar transações (simulado com dados mock)
  useEffect(() => {
    // Simulação de chamada à API
    const buscarTransacoes = async () => {
      setLoading(true);
      
      try {
        // Em um cenário real, aqui seria feita uma chamada à API
        // Simulando um atraso de rede
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Usando dados mock para demonstração
        setTransacoes(mockTransacoes);
      } catch (error) {
        console.error('Erro ao buscar transações:', error);
      } finally {
        setLoading(false);
      }
    };
    
    buscarTransacoes();
  }, [conta.id_conta]);

  // Função para formatar a data
  const formatarData = (dataString: string) => {
    const data = new Date(dataString);
    return data.toLocaleDateString('pt-BR');
  };

  // Função para formatar valor monetário
  const formatarMoeda = (valor: number) => {
    return valor.toLocaleString('pt-BR', { 
      style: 'currency', 
      currency: 'BRL' 
    });
  };

  // Definição das colunas da tabela
  const colunas: TableColumn[] = [
    {
      header: "Data",
      accessor: "data",
      render: (transacao: Transacao) => formatarData(transacao.data)
    },
    {
      header: "Descrição",
      accessor: "descricao"
    },
    {
      header: "Categoria",
      accessor: "categoria",
      render: (transacao: Transacao) => transacao.categoria || '-'
    },
    {
      header: "Tipo",
      accessor: "tipo",
      render: (transacao: Transacao) => {
        switch (transacao.tipo) {
          case 'entrada':
            return <span className="badge bg-green-100 text-green-800">Entrada</span>;
          case 'saida':
            return <span className="badge bg-red-100 text-red-800">Saída</span>;
          case 'transferencia':
            return <span className="badge bg-blue-100 text-blue-800">Transferência</span>;
          default:
            return transacao.tipo;
        }
      }
    },
    {
      header: "Valor",
      accessor: "valor",
      render: (transacao: Transacao) => (
        <span className={transacao.valor >= 0 ? 'text-green-600' : 'text-red-600'}>
          {formatarMoeda(transacao.valor)}
        </span>
      )
    }
  ];

  return (
    <div className="transacoes-conta-bancaria">
      <div className="mb-6 flex justify-between items-center">
        <h3 className="text-lg font-medium">Transações Recentes</h3>
        <button className="btn-secondary text-sm">Ver Todas</button>
      </div>
      
      <Table
        columns={colunas}
        data={transacoes}
        loading={loading}
        emptyMessage="Nenhuma transação encontrada para esta conta."
      />
    </div>
  );
} 