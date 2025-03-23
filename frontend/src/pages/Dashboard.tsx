import { useEffect, useState } from "react";
import { ResumoDashboard } from "../types";
import { formatarMoeda } from "../utils/formatters";
import { buscarResumoDashboard } from "../services/relatorioService";

export default function Dashboard() {
  const [resumo, setResumo] = useState<ResumoDashboard | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    async function fetchData() {
      try {
        const data = await buscarResumoDashboard();
        setResumo(data);
      } catch (err) {
        setError("Erro ao carregar os indicadores financeiros.");
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) return <p className="placeholder-text">Carregando...</p>;
  if (error) return <p className="placeholder-text">{error}</p>;
  if (!resumo) return <p className="placeholder-text">Nenhum dado disponível.</p>;

  return (
    <div>
      <h1 className="page-title">Dashboard</h1>
      
      <div className="dashboard-cards">
        <div className="dashboard-card">
          <h2 className="dashboard-card-title">Caixa Atual</h2>
          <p className="dashboard-card-value">{formatarMoeda(resumo.caixa_atual)}</p>
        </div>
        
        <div className="dashboard-card">
          <h2 className="dashboard-card-title">Total a Receber</h2>
          <p className="dashboard-card-value">{formatarMoeda(resumo.total_receber)}</p>
        </div>
        
        <div className="dashboard-card">
          <h2 className="dashboard-card-title">Total a Pagar</h2>
          <p className="dashboard-card-value">{formatarMoeda(resumo.total_pagar)}</p>
        </div>
        
        <div className="dashboard-card">
          <h2 className="dashboard-card-title">Recebimentos Hoje</h2>
          <p className="dashboard-card-value">{formatarMoeda(resumo.recebimentos_hoje)}</p>
        </div>
        
        <div className="dashboard-card">
          <h2 className="dashboard-card-title">Pagamentos Hoje</h2>
          <p className="dashboard-card-value">{formatarMoeda(resumo.pagamentos_hoje)}</p>
        </div>
      </div>
    </div>
  );
} 