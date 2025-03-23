import { useEffect, useState } from "react";
import { Log } from "../types";
import { formatarDataHora } from "../utils/formatters";
import { listarLogs } from "../services/logService";
import Table, { TableColumn } from "../components/Table";
import DataStateHandler from "../components/DataStateHandler";

export default function LogsAuditoria() {
  const [logs, setLogs] = useState<Log[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  // Definição das colunas da tabela
  const colunas: TableColumn[] = [
    {
      header: "Data",
      accessor: "data",
      render: (log: Log) => formatarDataHora(log.data)
    },
    {
      header: "Usuário",
      accessor: "usuario"
    },
    {
      header: "Ação",
      accessor: "acao"
    }
  ];

  useEffect(() => {
    fetchData();
  }, []);

  async function fetchData() {
    try {
      setLoading(true);
      const data = await listarLogs();
      setLogs(data);
      setError("");
    } catch (err) {
      setError("Erro ao carregar os logs de auditoria.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h1 className="page-title">Logs de Auditoria</h1>
      
      <DataStateHandler
        loading={loading}
        error={error}
        dataLength={logs.length}
        onRetry={fetchData}
        emptyMessage="Nenhum log encontrado."
      >
        <Table
          columns={colunas}
          data={logs}
          emptyMessage="Nenhum log encontrado."
        />
      </DataStateHandler>
    </div>
  );
} 