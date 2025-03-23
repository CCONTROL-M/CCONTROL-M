import React, { useEffect, useState } from "react";
import { ResumoDashboard } from "../types";
import { formatarMoeda } from "../utils/formatters";
import { buscarResumoDashboard } from "../services/relatorioService";
import { buscarResumoDashboardMock } from "../services/relatorioServiceMock";
import { useMock } from '../utils/mock';
import { useLoading } from '../contexts/LoadingContext';

export default function Dashboard() {
  const [resumo, setResumo] = useState<ResumoDashboard | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { setLoading } = useLoading();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Usa o utilitário useMock() para determinar se deve usar mock ou dados reais
      const data = useMock() 
        ? await buscarResumoDashboardMock()
        : await buscarResumoDashboard();
      
      setResumo(data);
    } catch (err) {
      console.error('Erro ao carregar os indicadores financeiros:', err);
      setError('Não foi possível carregar os indicadores financeiros. Tente novamente mais tarde.');
    } finally {
      setLoading(false);
    }
  };

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