import { useEffect, useState } from "react";
import api from "../services/api";
import { Conexao } from "../types";

export default function ConexoesExternas() {
  const [conexoes, setConexoes] = useState<Conexao[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    async function fetchConexoes() {
      try {
        const response = await api.get("/configuracoes/conexoes");
        setConexoes(response.data);
      } catch (err) {
        setError("Erro ao carregar conexões.");
      } finally {
        setLoading(false);
      }
    }
    fetchConexoes();
  }, []);

  if (loading) return <p className="placeholder-text">Carregando...</p>;
  if (error) return <p className="placeholder-text">{error}</p>;

  if (conexoes.length === 0) return <p className="placeholder-text">Nenhuma conexão encontrada.</p>;

  return (
    <div>
      <h1 className="page-title">Conexões Externas</h1>
      <table>
        <thead>
          <tr>
            <th>Nome</th>
            <th>Tipo</th>
            <th>URL</th>
          </tr>
        </thead>
        <tbody>
          {conexoes.map((c) => (
            <tr key={c.id_conexao}>
              <td>{c.nome}</td>
              <td>{c.tipo}</td>
              <td>{c.url}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
} 