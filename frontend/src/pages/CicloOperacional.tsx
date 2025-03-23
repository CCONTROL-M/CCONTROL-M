import { useEffect, useState } from "react";
import { Ciclo } from "../types";
import { obterRelatorioCicloOperacional } from "../services/relatoriosService";
import { formatarData } from "../utils/formatters";
import DataStateHandler from "../components/DataStateHandler";
import Table, { TableColumn } from "../components/Table";
import { setUseMock } from "../utils/mock";

export default function CicloOperacional() {
  const [ciclos, setCiclos] = useState<Ciclo[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Ativa o modo mock assim que o componente for renderizado
  useEffect(() => {
    // Ativar o modo mock para garantir que a aplicação funcione sem backend
    setUseMock(true);
    console.log("🔧 Modo mock foi ativado forcadamente na página de Ciclo Operacional");
  }, []);

  // Definição das colunas da tabela
  const colunas: TableColumn[] = [
    {
      header: "Cliente",
      accessor: "cliente"
    },
    {
      header: "Data do Pedido",
      accessor: "data_pedido",
      render: (item: Ciclo) => formatarData(item.data_pedido)
    },
    {
      header: "Data do Faturamento",
      accessor: "data_faturamento",
      render: (item: Ciclo) => formatarData(item.data_faturamento)
    },
    {
      header: "Data do Recebimento",
      accessor: "data_recebimento",
      render: (item: Ciclo) => formatarData(item.data_recebimento)
    },
    {
      header: "Dias de Ciclo",
      accessor: "dias_entre"
    }
  ];

  // Efeito para carregar dados
  useEffect(() => {
    fetchData();
  }, []);

  // Buscar dados do ciclo operacional
  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await obterRelatorioCicloOperacional();
      setCiclos(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar dados do ciclo operacional';
      setError(errorMessage);
      console.error("Erro ao carregar ciclo operacional:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-content">
      <h1 className="page-title">Ciclo Operacional</h1>
      
      <DataStateHandler
        loading={loading}
        error={error}
        dataLength={ciclos.length}
        onRetry={fetchData}
        emptyMessage="Nenhum dado disponível para o ciclo operacional."
      >
        <Table
          columns={colunas}
          data={ciclos}
          emptyMessage="Nenhum dado disponível para o ciclo operacional."
        />
        
        {ciclos.length > 0 && (
          <div className="resumo-ciclo">
            <h3>Resumo</h3>
            <p>Ciclo médio: {Math.round(ciclos.reduce((sum, item) => sum + item.dias_entre, 0) / ciclos.length)} dias</p>
          </div>
        )}
      </DataStateHandler>
    </div>
  );
} 