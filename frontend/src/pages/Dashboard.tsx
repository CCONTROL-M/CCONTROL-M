import React, { useEffect, useState } from "react";
import { ResumoDashboard } from "../types";
import { formatarMoeda } from "../utils/formatters";
import { buscarResumoDashboard } from "../services/relatorioService";
import { useMock } from '../utils/mock';
import { useAuth } from '../contexts/AuthContext';
import { verificarStatusAPI } from "../services/api";
import DataStateHandler from "../components/DataStateHandler";

// Estado inicial para o resumo
const resumoInicial: ResumoDashboard = {
  caixa_atual: 0,
  total_receber: 0,
  total_pagar: 0,
  recebimentos_hoje: 0,
  pagamentos_hoje: 0
};

export default function Dashboard() {
  const [resumo, setResumo] = useState<ResumoDashboard>(resumoInicial);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [apiOffline, setApiOffline] = useState<boolean>(false);
  const { user } = useAuth();

  useEffect(() => {
    verificarApi();
    fetchData();
  }, []);

  const verificarApi = async () => {
    const { online } = await verificarStatusAPI();
    setApiOffline(!online);
    
    // Não ativamos mais o modo mock automaticamente
    // Apenas registramos o status da API
    if (!online) {
      console.warn("API offline no dashboard, continuando com modo atual");
    }
  };

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Verificar status da API antes de tentar buscar dados
      await verificarApi();
      
      // Não ativamos mais o modo mock automaticamente
      // Se a API estiver offline, os componentes de tratamento de erro lidarão com isso
      
      const data = await buscarResumoDashboard();
      
      // Verifica se os dados recebidos são válidos
      if (data) {
        setResumo({
          caixa_atual: data.caixa_atual || 0,
          total_receber: data.total_receber || 0,
          total_pagar: data.total_pagar || 0,
          recebimentos_hoje: data.recebimentos_hoje || 0,
          pagamentos_hoje: data.pagamentos_hoje || 0
        });
      } else {
        throw new Error('Dados inválidos recebidos do servidor');
      }
    } catch (err) {
      console.error('Erro ao carregar os indicadores financeiros:', err);
      setError('Não foi possível carregar os indicadores financeiros. Tente novamente mais tarde.');
      
      // Não tentamos mais ativar o mock automaticamente em caso de erro
      // O usuário precisa ativar manualmente se quiser
    } finally {
      setLoading(false);
    }
  };

  // Calcular valores derivados com segurança
  const saldoLiquido = (resumo?.caixa_atual || 0) + (resumo?.total_receber || 0) - (resumo?.total_pagar || 0);
  const fluxoDiario = (resumo?.recebimentos_hoje || 0) - (resumo?.pagamentos_hoje || 0);

  return (
    <div>
      <div className="page-header-container">
        <h1 className="page-title">Dashboard Financeiro</h1>
        <p className="text-gray-600">Bem-vindo, {user?.nome || 'Usuário'}</p>
        
        {apiOffline && (
          <div className="mt-2 p-2 bg-yellow-100 border border-yellow-300 rounded text-sm">
            <p className="text-yellow-700">
              <span className="font-bold">Modo de demonstração:</span> Servidor não disponível, exibindo dados simulados
            </p>
          </div>
        )}
      </div>
      
      <DataStateHandler
        loading={loading}
        error={error}
        onRetry={fetchData}
        useGlobalLoading={false}
      >
        <div className="dashboard-cards">
          <div className="dashboard-card">
            <h2 className="dashboard-card-title">Caixa Atual</h2>
            <p className="dashboard-card-value">{formatarMoeda(resumo.caixa_atual)}</p>
            <p className="text-sm text-gray-500 mt-2">Saldo disponível nas contas</p>
          </div>
          
          <div className="dashboard-card">
            <h2 className="dashboard-card-title">A Receber</h2>
            <p className="dashboard-card-value dashboard-card-positive">{formatarMoeda(resumo.total_receber)}</p>
            <p className="text-sm text-gray-500 mt-2">Total de valores a receber</p>
          </div>
          
          <div className="dashboard-card">
            <h2 className="dashboard-card-title">A Pagar</h2>
            <p className="dashboard-card-value dashboard-card-negative">{formatarMoeda(resumo.total_pagar)}</p>
            <p className="text-sm text-gray-500 mt-2">Total de valores a pagar</p>
          </div>
          
          <div className="dashboard-card">
            <h2 className="dashboard-card-title">Recebimentos Hoje</h2>
            <p className="dashboard-card-value dashboard-card-positive">{formatarMoeda(resumo.recebimentos_hoje)}</p>
            <p className="text-sm text-gray-500 mt-2">Valores recebidos no dia atual</p>
          </div>
          
          <div className="dashboard-card">
            <h2 className="dashboard-card-title">Pagamentos Hoje</h2>
            <p className="dashboard-card-value dashboard-card-negative">{formatarMoeda(resumo.pagamentos_hoje)}</p>
            <p className="text-sm text-gray-500 mt-2">Valores pagos no dia atual</p>
          </div>
          
          <div className="dashboard-card">
            <h2 className="dashboard-card-title">Saldo Líquido</h2>
            <p className={`dashboard-card-value ${saldoLiquido >= 0 ? 'dashboard-card-positive' : 'dashboard-card-negative'}`}>
              {formatarMoeda(saldoLiquido)}
            </p>
            <p className="text-sm text-gray-500 mt-2">Caixa + A Receber - A Pagar</p>
          </div>
          
          <div className="dashboard-card">
            <h2 className="dashboard-card-title">Fluxo Diário</h2>
            <p className={`dashboard-card-value ${fluxoDiario >= 0 ? 'dashboard-card-positive' : 'dashboard-card-negative'}`}>
              {formatarMoeda(fluxoDiario)}
            </p>
            <p className="text-sm text-gray-500 mt-2">Recebimentos - Pagamentos (Hoje)</p>
          </div>
        </div>
      </DataStateHandler>
    </div>
  );
} 