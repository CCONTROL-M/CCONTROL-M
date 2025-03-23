import { useEffect, useState } from "react";
import APIDebug from "../components/APIDebug";
import { CentroCusto } from "../types";
import { listarCentrosCusto } from "../services/centroCustoService";
import Table, { TableColumn } from "../components/Table";
import DataStateHandler from "../components/DataStateHandler";

export default function CentroCustos() {
  const [centros, setCentros] = useState<CentroCusto[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");
  const [showDebug, setShowDebug] = useState<boolean>(false);

  // Definição das colunas da tabela
  const colunas: TableColumn[] = [
    {
      header: "Nome",
      accessor: "nome"
    }
  ];

  useEffect(() => {
    fetchCentros();
  }, []);

  async function fetchCentros() {
    try {
      setLoading(true);
      const data = await listarCentrosCusto();
      setCentros(data);
      setError("");
    } catch (err) {
      console.error("Erro ao carregar centros de custo:", err);
      setError("Erro ao carregar os centros de custo.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h1 className="page-title">Centro de Custos</h1>
      
      <button 
        onClick={() => setShowDebug(!showDebug)}
        style={{ 
          padding: '5px 10px', 
          marginBottom: '10px',
          backgroundColor: '#6c757d',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer'
        }}
      >
        {showDebug ? 'Ocultar Diagnóstico' : 'Mostrar Diagnóstico'}
      </button>
      
      {showDebug && <APIDebug />}
      
      <DataStateHandler
        loading={loading}
        error={error}
        dataLength={centros.length}
        onRetry={fetchCentros}
        emptyMessage="Nenhum centro de custo encontrado."
      >
        <Table
          columns={colunas}
          data={centros}
          emptyMessage="Nenhum centro de custo encontrado."
        />
      </DataStateHandler>
    </div>
  );
} 