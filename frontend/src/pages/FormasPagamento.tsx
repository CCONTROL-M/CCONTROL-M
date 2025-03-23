import React, { useEffect, useState } from 'react';
import { FormaPagamento } from "../types";
import { listarFormasPagamento } from "../services/formaPagamentoService";
import { listarFormasPagamentoMock } from "../services/formaPagamentoServiceMock";
import { useMock } from '../utils/mock';
import Table, { TableColumn } from "../components/Table";
import DataStateHandler from "../components/DataStateHandler";

export default function FormasPagamento() {
  const [formas, setFormas] = useState<FormaPagamento[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Definição das colunas da tabela
  const colunas: TableColumn[] = [
    {
      header: "Tipo",
      accessor: "tipo"
    },
    {
      header: "Taxas (%)",
      accessor: "taxas",
      render: (item: FormaPagamento) => `${item.taxas}%`
    },
    {
      header: "Prazo",
      accessor: "prazo"
    }
  ];

  useEffect(() => {
    fetchFormas();
  }, []);

  const fetchFormas = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Usa o utilitário useMock() para determinar se deve usar mock ou dados reais
      const data = useMock() 
        ? await listarFormasPagamentoMock()
        : await listarFormasPagamento();
      
      setFormas(data);
    } catch (err) {
      console.error('Erro ao carregar formas de pagamento:', err);
      setError('Não foi possível carregar as formas de pagamento. Tente novamente mais tarde.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="page-title">Formas de Pagamento</h1>
      
      <DataStateHandler
        loading={loading}
        error={error}
        dataLength={formas.length}
        onRetry={fetchFormas}
        emptyMessage="Nenhuma forma de pagamento encontrada."
      >
        <Table
          columns={colunas}
          data={formas}
          emptyMessage="Nenhuma forma de pagamento encontrada."
        />
      </DataStateHandler>
    </div>
  );
} 