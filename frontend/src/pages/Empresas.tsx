import { useEffect, useState } from "react";
import APIDebug from "../components/APIDebug";
import { listarEmpresas, EmpresaCompleta } from "../services/empresaService";
import Table, { TableColumn } from "../components/Table";
import DataStateHandler from "../components/DataStateHandler";

export default function Empresas() {
  const [empresas, setEmpresas] = useState<EmpresaCompleta[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");
  const [showDebug, setShowDebug] = useState<boolean>(false);

  // Definição das colunas da tabela
  const colunas: TableColumn[] = [
    {
      header: "Razão Social",
      accessor: "razao_social"
    },
    {
      header: "Nome Fantasia",
      accessor: "nome_fantasia",
      render: (item: EmpresaCompleta) => item.nome_fantasia || '-'
    },
    {
      header: "CNPJ",
      accessor: "cnpj"
    },
    {
      header: "Cidade/UF",
      accessor: "cidade",
      render: (item: EmpresaCompleta) => {
        return item.cidade && item.estado 
          ? `${item.cidade}/${item.estado}`
          : item.cidade || item.estado || '-';
      }
    },
    {
      header: "Status",
      accessor: "ativo",
      render: (item: EmpresaCompleta) => item.ativo ? "Ativa" : "Inativa"
    }
  ];

  useEffect(() => {
    fetchEmpresas();
  }, []);

  async function fetchEmpresas() {
    try {
      setLoading(true);
      const data = await listarEmpresas();
      setEmpresas(data);
      setError("");
    } catch (err) {
      console.error("Erro ao carregar empresas:", err);
      setError("Erro ao carregar empresas. Verifique a conexão com o servidor.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h1 className="page-title">Empresas</h1>
      
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
        dataLength={empresas.length}
        onRetry={fetchEmpresas}
        emptyMessage="Nenhuma empresa encontrada."
      >
        <Table
          columns={colunas}
          data={empresas}
          emptyMessage="Nenhuma empresa encontrada."
        />
      </DataStateHandler>
    </div>
  );
} 