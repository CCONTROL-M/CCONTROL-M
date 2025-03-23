import { useEffect, useState } from "react";
import { Permissao } from "../types";
import { listarPermissoes } from "../services/configuracoesService";
import Table, { TableColumn } from "../components/Table";
import DataStateHandler from "../components/DataStateHandler";
import { setUseMock } from "../utils/mock";

// Usando o tipo retornado pelo serviço
type PermissaoComNome = Permissao & { nome: string };

export default function Permissoes() {
  const [permissoes, setPermissoes] = useState<PermissaoComNome[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  // Ativa o modo mock assim que o componente for renderizado
  useEffect(() => {
    // Ativar o modo mock para garantir que a aplicação funcione sem backend
    setUseMock(true);
    console.log("🔧 Modo mock foi ativado forcadamente na página de Permissões");
  }, []);

  // Definição das colunas da tabela
  const colunas: TableColumn[] = [
    {
      header: "Usuário",
      accessor: "nome"
    },
    {
      header: "Telas Permitidas",
      accessor: "telas_permitidas",
      render: (item: PermissaoComNome) => item.telas_permitidas.join(", ")
    }
  ];

  useEffect(() => {
    fetchPermissoes();
  }, []);

  async function fetchPermissoes() {
    try {
      setLoading(true);
      const data = await listarPermissoes();
      setPermissoes(data);
      setError("");
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Erro ao carregar permissões.";
      setError(errorMessage);
      console.error("Erro ao carregar permissões:", err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-content">
      <h1 className="page-title">Permissões de Usuários</h1>
      
      <DataStateHandler
        loading={loading}
        error={error}
        dataLength={permissoes.length}
        onRetry={fetchPermissoes}
        emptyMessage="Nenhuma permissão registrada."
      >
        <Table
          columns={colunas}
          data={permissoes}
          emptyMessage="Nenhuma permissão registrada."
        />
      </DataStateHandler>
    </div>
  );
} 