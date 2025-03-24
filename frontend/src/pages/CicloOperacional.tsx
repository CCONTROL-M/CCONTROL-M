import React, { useMemo } from "react";
import { Ciclo } from "../types";
import { buscarCicloOperacional } from "../services/relatorioService";
import { buscarCicloOperacionalMock } from "../services/relatorioServiceMock";
import { formatarData } from "../utils/formatters";
import DataStateHandler from "../components/DataStateHandler";
import Table, { TableColumn } from "../components/Table";
import { useToast } from "../hooks/useToast";
import useDataFetching from "../hooks/useDataFetching";
import { safeArray, safeReduce } from "../utils/dataUtils";
import { useMock } from "../utils/mock";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Label
} from 'recharts';

/**
 * Página de Ciclo Operacional
 * Exibe informações sobre o ciclo financeiro da empresa,
 * incluindo prazos médios de pedido, faturamento e recebimento.
 */
export default function CicloOperacional() {
  // Hook de toast para notificações ao usuário
  const { showToast } = useToast();

  // Buscar dados do ciclo operacional
  const { 
    data: ciclos, 
    error, 
    loading, 
    fetchData: buscarDados,
    apiOffline
  } = useDataFetching<Ciclo[]>({
    fetchFunction: buscarCicloOperacional,
    mockFunction: buscarCicloOperacionalMock,
    loadingId: 'ciclo-operacional',
    errorMessage: 'Não foi possível carregar os dados do ciclo operacional',
    showErrorToast: true,
    useGlobalLoading: false
  });

  // Definição das colunas da tabela
  const colunas: TableColumn[] = [
    {
      header: "Cliente",
      accessor: "cliente"
    },
    {
      header: "Data do Pedido",
      accessor: "data_pedido",
      render: (item: Ciclo) => formatarData(item.data_pedido)
    },
    {
      header: "Data do Faturamento",
      accessor: "data_faturamento",
      render: (item: Ciclo) => formatarData(item.data_faturamento)
    },
    {
      header: "Data do Recebimento",
      accessor: "data_recebimento",
      render: (item: Ciclo) => formatarData(item.data_recebimento)
    },
    {
      header: "Dias de Ciclo Total",
      accessor: "dias_entre"
    }
  ];

  // Cálculos para o resumo do ciclo operacional
  const resumoCiclo = useMemo(() => {
    const ciclosValidos = safeArray<Ciclo>(ciclos || []);
    if (!Array.isArray(ciclosValidos) || ciclosValidos.length === 0) return null;
    
    // Cálculo do ciclo operacional total médio
    const cicloTotalMedio = Math.round(
      safeReduce(ciclosValidos, (sum, item: Ciclo) => sum + (item.dias_entre || 0), 0) / ciclosValidos.length
    );
    
    // Cálculo dos prazos médios entre etapas
    let prazoPedidoAteFaturamento = 0;
    let prazoFaturamentoAteRecebimento = 0;
    let ciclosComDatasCompletas = 0;
    
    ciclosValidos.forEach((ciclo: Ciclo) => {
      if (!ciclo || !ciclo.data_pedido || !ciclo.data_faturamento || !ciclo.data_recebimento) return;
      
      const dataPedido = new Date(ciclo.data_pedido);
      const dataFaturamento = new Date(ciclo.data_faturamento);
      const dataRecebimento = new Date(ciclo.data_recebimento);
      
      // Dias entre pedido e faturamento (tempo de produção/estocagem)
      const diasPedidoAteFaturamento = Math.round(
        (dataFaturamento.getTime() - dataPedido.getTime()) / (1000 * 60 * 60 * 24)
      );
      
      // Dias entre faturamento e recebimento (prazo de pagamento)
      const diasFaturamentoAteRecebimento = Math.round(
        (dataRecebimento.getTime() - dataFaturamento.getTime()) / (1000 * 60 * 60 * 24)
      );
      
      if (diasPedidoAteFaturamento >= 0 && diasFaturamentoAteRecebimento >= 0) {
        prazoPedidoAteFaturamento += diasPedidoAteFaturamento;
        prazoFaturamentoAteRecebimento += diasFaturamentoAteRecebimento;
        ciclosComDatasCompletas++;
      }
    });
    
    // Calcular as médias, certificando-se de que temos dados válidos
    prazoPedidoAteFaturamento = ciclosComDatasCompletas > 0 
      ? Math.round(prazoPedidoAteFaturamento / ciclosComDatasCompletas) 
      : 0;
      
    prazoFaturamentoAteRecebimento = ciclosComDatasCompletas > 0 
      ? Math.round(prazoFaturamentoAteRecebimento / ciclosComDatasCompletas) 
      : 0;
    
    return {
      cicloTotalMedio,
      prazoPedidoAteFaturamento,
      prazoFaturamentoAteRecebimento,
      ciclosComDatasCompletas,
      totalCiclos: ciclosValidos.length
    };
  }, [ciclos]);

  // Preparar dados para o gráfico de ciclo operacional
  const dadosGraficoCiclo = useMemo(() => {
    if (!resumoCiclo) return [];
    
    return [
      {
        name: "Pedido → Faturamento",
        dias: resumoCiclo.prazoPedidoAteFaturamento,
        fill: "#4F46E5"
      },
      {
        name: "Faturamento → Recebimento",
        dias: resumoCiclo.prazoFaturamentoAteRecebimento,
        fill: "#10B981"
      },
      {
        name: "Ciclo Completo",
        dias: resumoCiclo.cicloTotalMedio,
        fill: "#8B5CF6"
      }
    ];
  }, [resumoCiclo]);
  
  // Renderizar gráfico de ciclo operacional
  const renderizarGraficoCiclo = () => {
    if (!resumoCiclo || dadosGraficoCiclo.length === 0) return null;
    
    return (
      <div className="mt-6 pt-4 border-t border-gray-200">
        <h3 className="font-semibold mb-3">Visualização Gráfica do Ciclo</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={dadosGraficoCiclo}
              margin={{ top: 20, right: 30, left: 20, bottom: 10 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis>
                <Label value="Dias" angle={-90} position="insideLeft" style={{ textAnchor: 'middle' }} />
              </YAxis>
              <Tooltip 
                formatter={(value) => [`${value} dias`, "Duração"]}
                labelFormatter={(label) => `Etapa: ${label}`}
              />
              <Legend />
              <Bar dataKey="dias" name="Duração (dias)" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    );
  };

  return (
    <div className="page-content">
      <h1 className="page-title">Ciclo Operacional</h1>
      
      <div className="mb-6">
        <p className="text-gray-600">
          O ciclo operacional representa o tempo médio entre o pedido de materiais, 
          faturamento e recebimento das vendas, permitindo identificar oportunidades 
          de melhoria no fluxo de caixa da empresa.
        </p>
        
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
        error={error?.message}
        dataLength={Array.isArray(ciclos) ? ciclos.length : 0}
        onRetry={buscarDados}
        emptyMessage="Nenhum dado disponível para o ciclo operacional."
        useGlobalLoading={false}
        operationId="ciclo-operacional-view"
      >
        {/* Resumo do Ciclo Operacional */}
        {resumoCiclo && (
          <div className="card mb-6">
            <div className="card-body">
              <h2 className="card-title">Resumo do Ciclo Operacional</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                <div className="p-4 bg-blue-50 rounded-md border border-blue-100">
                  <h3 className="text-lg font-semibold text-blue-700 mb-2">Prazo Médio de Produção</h3>
                  <p className="text-3xl font-bold text-blue-800">{resumoCiclo.prazoPedidoAteFaturamento} dias</p>
                  <p className="text-sm text-blue-600 mt-1">Do pedido até o faturamento</p>
                </div>
                
                <div className="p-4 bg-green-50 rounded-md border border-green-100">
                  <h3 className="text-lg font-semibold text-green-700 mb-2">Prazo Médio de Recebimento</h3>
                  <p className="text-3xl font-bold text-green-800">{resumoCiclo.prazoFaturamentoAteRecebimento} dias</p>
                  <p className="text-sm text-green-600 mt-1">Do faturamento até o recebimento</p>
                </div>
                
                <div className="p-4 bg-purple-50 rounded-md border border-purple-100">
                  <h3 className="text-lg font-semibold text-purple-700 mb-2">Ciclo Operacional Total</h3>
                  <p className="text-3xl font-bold text-purple-800">{resumoCiclo.cicloTotalMedio} dias</p>
                  <p className="text-sm text-purple-600 mt-1">Do pedido até o recebimento</p>
                </div>
              </div>
              
              <div className="mt-4 pt-4 border-t border-gray-200">
                <h3 className="font-semibold mb-2">Análise e Impacto</h3>
                <p className="text-gray-700">
                  Um ciclo operacional de <span className="font-medium">{resumoCiclo.cicloTotalMedio} dias</span> significa 
                  que a empresa leva, em média, este período desde a compra de materiais até receber o pagamento. 
                  Reduzir este ciclo pode melhorar o fluxo de caixa e a liquidez da empresa.
                </p>
                
                <div className="mt-3 text-sm text-gray-600">
                  <p>Recomendações:</p>
                  <ul className="list-disc ml-5 mt-1">
                    <li>Considerar otimização no processo de produção/estocagem ({resumoCiclo.prazoPedidoAteFaturamento} dias)</li>
                    <li>Avaliar política de prazos para recebimento ({resumoCiclo.prazoFaturamentoAteRecebimento} dias)</li>
                    <li>Analisar tendências por cliente para identificar padrões</li>
                  </ul>
                </div>
              </div>
              
              {/* Gráfico do Ciclo Operacional */}
              {renderizarGraficoCiclo()}
            </div>
          </div>
        )}
        
        {/* Tabela com Detalhamento por Cliente */}
        <div className="card">
          <div className="card-body">
            <h2 className="card-title">Detalhamento por Cliente</h2>
            <p className="mb-4 text-sm text-gray-600">
              Detalhe dos ciclos operacionais por cliente, permitindo identificar padrões específicos.
            </p>
            
            <Table
              columns={colunas}
              data={Array.isArray(ciclos) ? ciclos : []}
              emptyMessage="Nenhum dado disponível para o ciclo operacional."
            />
          </div>
        </div>
      </DataStateHandler>
    </div>
  );
} 