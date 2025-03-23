import { useEffect, useState } from "react";
import api from "../services/api";
import { Parametro } from "../types";

export default function ParametrosSistema() {
  const [parametros, setParametros] = useState<Parametro[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    async function fetchParametros() {
      try {
        const response = await api.get("/configuracoes/parametros");
        setParametros(response.data);
      } catch (err) {
        setError("Erro ao carregar parâmetros.");
      } finally {
        setLoading(false);
      }
    }
    fetchParametros();
  }, []);

  if (loading) return <p className="placeholder-text">Carregando...</p>;
  if (error) return <p className="placeholder-text">{error}</p>;

  if (parametros.length === 0) return <p className="placeholder-text">Nenhum parâmetro encontrado.</p>;

  return (
    <div>
      <h1 className="page-title">Parâmetros do Sistema</h1>
      <table>
        <thead>
          <tr>
            <th>Chave</th>
            <th>Valor</th>
            <th>Descrição</th>
          </tr>
        </thead>
        <tbody>
          {parametros.map((p) => (
            <tr key={p.id_parametro}>
              <td>{p.chave}</td>
              <td>{p.valor}</td>
              <td>{p.descricao}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
} 