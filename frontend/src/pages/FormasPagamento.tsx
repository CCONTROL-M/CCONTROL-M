import { useEffect, useState } from "react";
import api from "../services/api";
import { FormaPagamento } from "../types";

export default function FormasPagamento() {
  const [formas, setFormas] = useState<FormaPagamento[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    async function fetchFormas() {
      try {
        const response = await api.get("/formas-pagamento");
        setFormas(response.data);
      } catch (err) {
        setError("Erro ao carregar as formas de pagamento.");
      } finally {
        setLoading(false);
      }
    }
    fetchFormas();
  }, []);

  if (loading) return <p className="placeholder-text">Carregando...</p>;
  if (error) return <p className="placeholder-text">{error}</p>;

  return (
    <div>
      <h1 className="page-title">Formas de Pagamento</h1>
      
      {formas.length === 0 ? (
        <p className="placeholder-text">Nenhuma forma de pagamento encontrada.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Tipo</th>
              <th>Taxas (%)</th>
              <th>Prazo</th>
            </tr>
          </thead>
          <tbody>
            {formas.map((f) => (
              <tr key={f.id_forma}>
                <td>{f.tipo}</td>
                <td>{f.taxas}%</td>
                <td>{f.prazo}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
} 