import { useEffect, useState } from "react";
import api from "../services/api";
import { Lancamento } from "../types";
import { formatarData, formatarMoeda } from "../utils/formatters";

// Estendendo a interface para adicionar campo descricao e tipo
interface LancamentoExibicao extends Lancamento {
  descricao: string;
  tipo: string;
}

export default function Lancamentos() {
  const [lancamentos, setLancamentos] = useState<LancamentoExibicao[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    async function fetchLancamentos() {
      try {
        const response = await api.get("/lancamentos");
        setLancamentos(response.data);
      } catch (err) {
        setError("Erro ao carregar os lançamentos.");
      } finally {
        setLoading(false);
      }
    }
    fetchLancamentos();
  }, []);

  if (loading) return <p className="placeholder-text">Carregando...</p>;
  if (error) return <p className="placeholder-text">{error}</p>;
  if (lancamentos.length === 0) return <p className="placeholder-text">Nenhum lançamento encontrado.</p>;

  return (
    <div>
      <h1 className="page-title">Lançamentos Financeiros</h1>
      <table>
        <thead>
          <tr>
            <th>Data</th>
            <th>Descrição</th>
            <th>Tipo</th>
            <th>Valor</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {lancamentos.map((l) => (
            <tr key={l.id_lancamento}>
              <td>{formatarData(l.data)}</td>
              <td>{l.descricao}</td>
              <td>{l.tipo}</td>
              <td>{formatarMoeda(l.valor)}</td>
              <td>{l.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
} 