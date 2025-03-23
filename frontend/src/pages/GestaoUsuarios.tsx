import { useEffect, useState } from "react";
import { Usuario } from "../types";
import { listarUsuarios } from "../services/usuarioService";
import { formatarData } from "../utils/formatters";
import Table, { TableColumn } from "../components/Table";
import DataStateHandler from "../components/DataStateHandler";

export default function GestaoUsuarios() {
  const [usuarios, setUsuarios] = useState<Usuario[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  // Definição das colunas da tabela
  const colunas: TableColumn[] = [
    {
      header: "Nome",
      accessor: "nome"
    },
    {
      header: "Email",
      accessor: "email"
    },
    {
      header: "Tipo",
      accessor: "tipo_usuario"
    },
    {
      header: "Criado em",
      accessor: "created_at",
      render: (usuario: Usuario) => formatarData(usuario.created_at)
    }
  ];

  useEffect(() => {
    fetchUsuarios();
  }, []);

  async function fetchUsuarios() {
    try {
      setLoading(true);
      const data = await listarUsuarios();
      setUsuarios(data);
      setError("");
    } catch (err) {
      setError("Erro ao carregar os usuários.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h1 className="page-title">Gestão de Usuários</h1>
      
      <DataStateHandler
        loading={loading}
        error={error}
        dataLength={usuarios.length}
        onRetry={fetchUsuarios}
        emptyMessage="Nenhum usuário encontrado."
      >
        <Table
          columns={colunas}
          data={usuarios}
          emptyMessage="Nenhum usuário encontrado."
        />
      </DataStateHandler>
    </div>
  );
} 