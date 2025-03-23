import { useEffect, useState } from "react";
import api from "../services/api";
import { Parcela } from "../types";
import { formatarData, formatarMoeda } from "../utils/formatters";

// Estendendo a interface para adicionar campo numero
interface ParcelaExibicao extends Parcela {
  numero: number;
}

export default function Parcelas() {
  const [parcelas, setParcelas] = useState<ParcelaExibicao[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    async function fetchParcelas() {
      try {
        const response = await api.get("/parcelas");
        setParcelas(response.data);
      } catch (err) {
        setError("Erro ao carregar as parcelas.");
      } finally {
        setLoading(false);
      }
    }
    fetchParcelas();
  }, []);

  if (loading) return <p className="placeholder-text">Carregando...</p>;
  if (error) return <p className="placeholder-text">{error}</p>;
  if (parcelas.length === 0) return <p className="placeholder-text">Nenhuma parcela encontrada.</p>;

  return (
    <div>
      <h1 className="page-title">Parcelas de Vendas</h1>
      <table>
        <thead>
          <tr>
            <th>Venda</th>
            <th>Nº Parcela</th>
            <th>Valor</th>
            <th>Vencimento</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {parcelas.map((p) => (
            <tr key={p.id_parcela}>
              <td>{p.id_venda.slice(0, 8)}...</td>
              <td>{p.numero}</td>
              <td>{formatarMoeda(p.valor)}</td>
              <td>{formatarData(p.data_vencimento)}</td>
              <td>{p.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
} 