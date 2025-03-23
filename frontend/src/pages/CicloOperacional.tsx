import { useEffect, useState } from "react";
import api from "../services/api";
import { Ciclo } from "../types";
import { formatarData } from "../utils/formatters";

export default function CicloOperacional() {
  const [ciclos, setCiclos] = useState<Ciclo[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    async function fetchCiclos() {
      try {
        const response = await api.get("/relatorios/ciclo-operacional");
        setCiclos(response.data);
      } catch (err) {
        setError("Erro ao carregar os dados.");
      } finally {
        setLoading(false);
      }
    }
    fetchCiclos();
  }, []);

  if (loading) return <p className="placeholder-text">Carregando...</p>;
  if (error) return <p className="placeholder-text">{error}</p>;
  if (ciclos.length === 0) return <p className="placeholder-text">Nenhum ciclo registrado.</p>;

  return (
    <div>
      <h1 className="page-title">Ciclo Operacional</h1>
      <table>
        <thead>
          <tr>
            <th>Cliente</th>
            <th>Data do Pedido</th>
            <th>Data de Faturamento</th>
            <th>Data de Recebimento</th>
            <th>Dias entre Pedido e Recebimento</th>
          </tr>
        </thead>
        <tbody>
          {ciclos.map((ciclo, index) => (
            <tr key={index}>
              <td>{ciclo.cliente}</td>
              <td>{formatarData(ciclo.data_pedido)}</td>
              <td>{formatarData(ciclo.data_faturamento)}</td>
              <td>{formatarData(ciclo.data_recebimento)}</td>
              <td>{ciclo.dias_entre}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
} 