import { useEffect, useState } from "react";
import api from "../services/api";
import { ContaBancaria } from "../types";
import { formatarMoeda } from "../utils/formatters";

export default function ContasBancarias() {
  const [contas, setContas] = useState<ContaBancaria[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    async function fetchContas() {
      try {
        const response = await api.get("/contas-bancarias");
        setContas(response.data);
      } catch (err) {
        setError("Erro ao carregar as contas bancárias.");
      } finally {
        setLoading(false);
      }
    }
    fetchContas();
  }, []);

  if (loading) return <p className="placeholder-text">Carregando...</p>;
  if (error) return <p className="placeholder-text">{error}</p>;

  return (
    <div>
      <h1 className="page-title">Contas Bancárias</h1>
      
      {contas.length === 0 ? (
        <p className="placeholder-text">Nenhuma conta bancária encontrada.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Banco</th>
              <th>Tipo</th>
              <th>Número</th>
              <th>Agência</th>
              <th>Saldo Inicial</th>
            </tr>
          </thead>
          <tbody>
            {contas.map((c) => (
              <tr key={c.id_conta}>
                <td>{c.banco}</td>
                <td>{c.tipo}</td>
                <td>{c.numero}</td>
                <td>{c.agencia}</td>
                <td>{formatarMoeda(c.saldo_inicial)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
} 