import React, { useState, useEffect } from 'react';
import { listarTransferencias } from '../services/transferenciaService';
import { Transferencia } from '../types';
import { formatarMoeda, formatarData } from '../utils/formatters';
import Table from '../components/Table';
import DataStateHandler from '../components/DataStateHandler';

interface TransferenciaExibicao extends Transferencia {
  numero: number;
}

export default function TransferenciasContas() {
  const [transferencias, setTransferencias] = useState<TransferenciaExibicao[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const columns = [
    {
      header: 'Nº',
      accessor: 'numero',
      render: (item: TransferenciaExibicao) => item.numero,
    },
    {
      header: 'Data',
      accessor: 'data',
      render: (item: TransferenciaExibicao) => formatarData(item.data),
    },
    {
      header: 'Conta Origem',
      accessor: 'conta_origem',
      render: (item: TransferenciaExibicao) => item.conta_origem,
    },
    {
      header: 'Conta Destino',
      accessor: 'conta_destino',
      render: (item: TransferenciaExibicao) => item.conta_destino,
    },
    {
      header: 'Valor',
      accessor: 'valor',
      render: (item: TransferenciaExibicao) => formatarMoeda(item.valor),
    },
    {
      header: 'Status',
      accessor: 'status',
      render: (item: TransferenciaExibicao) => (
        <span 
          className={`inline-block px-2 py-1 text-xs font-semibold rounded-full ${
            item.status === 'Concluída' 
              ? 'bg-green-100 text-green-800' 
              : item.status === 'Pendente' 
                ? 'bg-yellow-100 text-yellow-800' 
                : 'bg-blue-100 text-blue-800'
          }`}
        >
          {item.status}
        </span>
      ),
    },
  ];

  const fetchTransferencias = async () => {
    setLoading(true);
    try {
      const data = await listarTransferencias();
      // Adicionar número sequencial para exibição
      const transferenciasComNumero = data.map((item, index) => ({
        ...item,
        numero: index + 1
      }));
      setTransferencias(transferenciasComNumero);
      setError(null);
    } catch (err) {
      console.error('Erro ao carregar transferências:', err);
      setError('Erro ao carregar transferências');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTransferencias();
  }, []);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Transferências entre Contas</h1>
        <button
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
          onClick={() => fetchTransferencias()}
        >
          Atualizar
        </button>
      </div>

      <DataStateHandler
        loading={loading}
        error={error}
        dataLength={transferencias.length}
        emptyMessage="Nenhuma transferência encontrada."
        onRetry={fetchTransferencias}
      >
        <Table
          columns={columns}
          data={transferencias}
        />
      </DataStateHandler>
    </div>
  );
} 