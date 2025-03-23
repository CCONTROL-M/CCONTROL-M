import { useEffect, useState } from "react";
import { Parametro } from "../types";
import { listarParametros } from "../services/configuracoesService";
import Table, { TableColumn } from "../components/Table";
import DataStateHandler from "../components/DataStateHandler";
import { setUseMock } from "../utils/mock";

export default function ParametrosSistema() {
  const [parametros, setParametros] = useState<Parametro[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  // Ativa o modo mock assim que o componente for renderizado
  useEffect(() => {
    // Ativar o modo mock para garantir que a aplicação funcione sem backend
    setUseMock(true);
    console.log("🔧 Modo mock foi ativado forcadamente na página de Parâmetros do Sistema");
  }, []);

  // Definição das colunas da tabela
  const colunas: TableColumn[] = [
    {
      header: "Chave",
      accessor: "chave"
    },
    {
      header: "Valor",
      accessor: "valor"
    },
    {
      header: "Descrição",
      accessor: "descricao"
    }
  ];

  useEffect(() => {
    fetchParametros();
  }, []);

  async function fetchParametros() {
    try {
      setLoading(true);
      const data = await listarParametros();
      setParametros(data);
      setError("");
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Erro ao carregar parâmetros.";
      setError(errorMessage);
      console.error("Erro ao carregar parâmetros:", err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-content">
      <h1 className="page-title">Parâmetros do Sistema</h1>
      
      <DataStateHandler
        loading={loading}
        error={error}
        dataLength={parametros.length}
        onRetry={fetchParametros}
        emptyMessage="Nenhum parâmetro encontrado."
      >
        <Table
          columns={colunas}
          data={parametros}
          emptyMessage="Nenhum parâmetro encontrado."
        />
      </DataStateHandler>
    </div>
  );
} 