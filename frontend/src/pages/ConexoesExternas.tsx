import { useEffect, useState } from "react";
import { Conexao } from "../types";
import { listarConexoes } from "../services/configuracoesService";
import Table, { TableColumn } from "../components/Table";
import DataStateHandler from "../components/DataStateHandler";
import { setUseMock } from "../utils/mock";

export default function ConexoesExternas() {
  const [conexoes, setConexoes] = useState<Conexao[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  // Ativa o modo mock assim que o componente for renderizado
  useEffect(() => {
    // Ativar o modo mock para garantir que a aplicação funcione sem backend
    setUseMock(true);
    console.log("🔧 Modo mock foi ativado forcadamente na página de Conexões Externas");
  }, []);

  // Definição das colunas da tabela
  const colunas: TableColumn[] = [
    {
      header: "Nome",
      accessor: "nome"
    },
    {
      header: "Tipo",
      accessor: "tipo"
    },
    {
      header: "URL",
      accessor: "url"
    }
  ];

  useEffect(() => {
    fetchConexoes();
  }, []);

  async function fetchConexoes() {
    try {
      setLoading(true);
      const data = await listarConexoes();
      setConexoes(data);
      setError("");
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Erro ao carregar conexões.";
      setError(errorMessage);
      console.error("Erro ao carregar conexões:", err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-content">
      <h1 className="page-title">Conexões Externas</h1>
      
      <DataStateHandler
        loading={loading}
        error={error}
        dataLength={conexoes.length}
        onRetry={fetchConexoes}
        emptyMessage="Nenhuma conexão encontrada."
      >
        <Table
          columns={colunas}
          data={conexoes}
          emptyMessage="Nenhuma conexão encontrada."
        />
      </DataStateHandler>
    </div>
  );
} 