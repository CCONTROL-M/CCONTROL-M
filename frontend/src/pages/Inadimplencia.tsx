import { useEffect, useState } from "react";
import { Inadimplente } from "../types";
import { obterRelatorioInadimplencia } from "../services/relatoriosService";
import { formatarData, formatarMoeda } from "../utils/formatters";
import DataStateHandler from "../components/DataStateHandler";
import Table, { TableColumn } from "../components/Table";
import { setUseMock } from "../utils/mock";

export default function Inadimplencia() {
  const [inadimplentes, setInadimplentes] = useState<Inadimplente[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  // Ativa o modo mock assim que o componente for renderizado
  useEffect(() => {
    // Ativar o modo mock para garantir que a aplicação funcione sem backend
    setUseMock(true);
    console.log("🔧 Modo mock foi ativado forcadamente na página de Inadimplência");
  }, []);

  // Definição das colunas da tabela
  const colunas: TableColumn[] = [
    {
      header: "Cliente",
      accessor: "cliente"
    },
    {
      header: "Valor",
      accessor: "valor",
      render: (item: Inadimplente) => formatarMoeda(item.valor)
    },
    {
      header: "Vencimento",
      accessor: "vencimento",
      render: (item: Inadimplente) => formatarData(item.vencimento)
    },
    {
      header: "Dias em Atraso",
      accessor: "dias_em_atraso"
    }
  ];

  useEffect(() => {
    fetchInadimplencia();
  }, []);

  async function fetchInadimplencia() {
    try {
      setLoading(true);
      const data = await obterRelatorioInadimplencia();
      setInadimplentes(data);
      setError("");
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Erro ao carregar dados de inadimplência.";
      setError(errorMessage);
      console.error("Erro ao carregar inadimplência:", err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-content">
      <h1 className="page-title">Relatório de Inadimplência</h1>
      
      <DataStateHandler
        loading={loading}
        error={error}
        dataLength={inadimplentes.length}
        onRetry={fetchInadimplencia}
        emptyMessage="Nenhum cliente inadimplente encontrado."
      >
        <Table
          columns={colunas}
          data={inadimplentes}
          emptyMessage="Nenhum cliente inadimplente encontrado."
        />
      </DataStateHandler>
    </div>
  );
} 