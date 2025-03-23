import { useEffect, useState } from "react";
import api from "../services/api";
import { Transferencia } from "../types";
import { formatarData, formatarMoeda } from "../utils/formatters";

export default function TransferenciasContas() {
  const [transferencias, setTransferencias] = useState<Transferencia[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    async function fetchTransferencias() {
      try {
        const response = await api.get("/transferencias");
        setTransferencias(response.data);
      } catch (err) {
        setError("Erro ao carregar as transferências.");
      } finally {
        setLoading(false);
      }
    }
    fetchTransferencias();
  }, []);

  if (loading) return <p className="placeholder-text">Carregando...</p>;
  if (error) return <p className="placeholder-text">{error}</p>;
  if (transferencias.length === 0) return <p className="placeholder-text">Nenhuma transferência encontrada.</p>;

  return (
    <div>
      <h1 className="page-title">Transferências entre Contas</h1>
      <table>
        <thead>
          <tr>
            <th>Data</th>
            <th>Conta de Origem</th>
            <th>Conta de Destino</th>
            <th>Valor</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {transferencias.map((t) => (
            <tr key={t.id_transferencia}>
              <td>{formatarData(t.data)}</td>
              <td>{t.conta_origem}</td>
              <td>{t.conta_destino}</td>
              <td>{formatarMoeda(t.valor)}</td>
              <td>{t.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
} 