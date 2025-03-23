import { useEffect, useState } from "react";
import api from "../services/api";
import { Inadimplente } from "../types";
import { formatarData, formatarMoeda } from "../utils/formatters";

export default function Inadimplencia() {
  const [inadimplentes, setInadimplentes] = useState<Inadimplente[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    async function fetchInadimplencia() {
      try {
        const response = await api.get("/relatorios/inadimplencia");
        setInadimplentes(response.data);
      } catch (err) {
        setError("Erro ao carregar os dados de inadimplência.");
      } finally {
        setLoading(false);
      }
    }
    fetchInadimplencia();
  }, []);

  if (loading) return <p className="placeholder-text">Carregando...</p>;
  if (error) return <p className="placeholder-text">{error}</p>;
  if (inadimplentes.length === 0) return <p className="placeholder-text">Nenhum inadimplente encontrado.</p>;

  return (
    <div>
      <h1 className="page-title">Relatório de Inadimplência</h1>
      <table>
        <thead>
          <tr>
            <th>Cliente</th>
            <th>Valor</th>
            <th>Vencimento</th>
            <th>Dias em Atraso</th>
          </tr>
        </thead>
        <tbody>
          {inadimplentes.map((item) => (
            <tr key={item.id_parcela}>
              <td>{item.cliente}</td>
              <td>{formatarMoeda(item.valor)}</td>
              <td>{formatarData(item.vencimento)}</td>
              <td>{item.dias_em_atraso}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
} 