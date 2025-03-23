import { useEffect, useState } from "react";
import { Log } from "../types";
import { formatarDataHora } from "../utils/formatters";
import { listarLogs } from "../services/logService";

export default function LogsAuditoria() {
  const [logs, setLogs] = useState<Log[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    async function fetchData() {
      try {
        const data = await listarLogs();
        setLogs(data);
      } catch (err) {
        setError("Erro ao carregar os logs de auditoria.");
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) return <p className="placeholder-text">Carregando...</p>;
  if (error) return <p className="placeholder-text">{error}</p>;

  return (
    <div>
      <h1 className="page-title">Logs de Auditoria</h1>
      
      {logs.length === 0 ? (
        <p className="placeholder-text">Nenhum log encontrado.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Data</th>
              <th>Usuário</th>
              <th>Ação</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id_log}>
                <td>{formatarDataHora(log.data)}</td>
                <td>{log.usuario}</td>
                <td>{log.acao}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
} 