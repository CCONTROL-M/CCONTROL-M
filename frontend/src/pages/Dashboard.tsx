import React, { useState } from "react";
import { formatarMoeda } from "../utils/formatters";
import { useAuth } from '../contexts/AuthContext';
import DataStateHandler from "../components/DataStateHandler";
import { useDashboardData } from "../hooks/useDashboardData";
import { listarEmpresas, EmpresaCompleta } from "../services/empresaService";

export default function Dashboard() {
  const [selectedEmpresa, setSelectedEmpresa] = useState<string | undefined>(undefined);
  const [empresas, setEmpresas] = useState<EmpresaCompleta[]>([]);
  const [carregandoEmpresas, setCarregandoEmpresas] = useState<boolean>(false);
  const { user } = useAuth();
  
  // Usar o hook personalizado para dashboard
  const { resumo, loading, error, fetchData, empresaId } = useDashboardData(selectedEmpresa);
  
  // Função para buscar empresas para o seletor
  const buscarEmpresas = async () => {
    if (carregandoEmpresas) return;
    
    try {
      setCarregandoEmpresas(true);
      const data = await listarEmpresas();
      setEmpresas(data);
    } catch (err) {
      console.error("Erro ao buscar empresas:", err);
    } finally {
      setCarregandoEmpresas(false);
    }
  };
  
  // Alternar empresa selecionada
  const handleChangeEmpresa = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const novaEmpresa = event.target.value;
    setSelectedEmpresa(novaEmpresa === "default" ? undefined : novaEmpresa);
  };
  
  // Calcular valores derivados com segurança
  const saldoLiquido = (resumo?.caixa_atual || 0) + (resumo?.total_receber || 0) - (resumo?.total_pagar || 0);
  const fluxoDiario = (resumo?.recebimentos_hoje || 0) - (resumo?.pagamentos_hoje || 0);

  return (
    <div>
      <div className="page-header-container">
        <div className="flex flex-row items-center justify-between">
          <div>
            <h1 className="page-title">Dashboard Financeiro</h1>
            <p className="text-gray-600">Bem-vindo, {user?.nome || 'Usuário'}</p>
          </div>
          
          <div className="flex items-center">
            <button
              onClick={buscarEmpresas}
              className="btn-secondary mr-2"
              disabled={carregandoEmpresas}
            >
              {carregandoEmpresas ? 'Carregando...' : 'Carregar Empresas'}
            </button>
            
            <select
              className="form-select min-w-[220px]"
              onChange={handleChangeEmpresa}
              value={selectedEmpresa || "default"}
              disabled={carregandoEmpresas || empresas.length === 0}
            >
              <option value="default">Selecione uma empresa</option>
              {empresas.map(empresa => (
                <option key={empresa.id_empresa} value={empresa.id_empresa}>
                  {empresa.nome || empresa.razao_social}
                </option>
              ))}
            </select>
          </div>
        </div>
        
        {empresaId && (
          <div className="mt-2 text-sm text-gray-500">
            Exibindo dados da empresa ID: {empresaId}
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