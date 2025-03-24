import React, { useEffect, useState, useMemo } from "react";
import { FluxoItem, FluxoGrupo, ContaBancaria } from "../types";
import { buscarFluxoCaixaFiltrado } from "../services/relatorioService";
import { listarContasBancarias } from "../services/contaBancariaService";
import { formatarData, formatarMoeda } from "../utils/formatters";
import DataStateHandler from "../components/DataStateHandler";
import { useToast } from "../hooks/useToast";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';

// Componente FilterPanel
const FilterPanel: React.FC<{
  title: string;
  className?: string;
  children: React.ReactNode;
}> = ({ title, className = "", children }) => {
  return (
    <div className={`bg-white rounded-lg shadow-sm p-4 ${className}`}>
      <h3 className="text-lg font-medium mb-4">{title}</h3>
      {children}
    </div>
  );
};

// Tipos para os filtros
interface FluxoCaixaFiltros {
  dataInicio: string;
  dataFim: string;
  id_conta?: string;
  tipo?: string;
  status?: string;
}

// Tipos de visualização
type TipoVisualizacao = "diaria" | "mensal" | "acumulada";

export default function FluxoCaixa() {
  // Estados
  const [fluxoItens, setFluxoItens] = useState<FluxoItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [contasBancarias, setContasBancarias] = useState<ContaBancaria[]>([]);
  const [tipoVisualizacao, setTipoVisualizacao] = useState<TipoVisualizacao>("diaria");
  
  // Estado para filtros
  const [filtros, setFiltros] = useState<FluxoCaixaFiltros>({
    dataInicio: new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0], // Primeiro dia do mês atual
    dataFim: new Date().toISOString().split('T')[0], // Hoje
    tipo: undefined,
    id_conta: undefined,
    status: undefined
  });

  const { showToast } = useToast();

  // Carregar contas bancárias
  useEffect(() => {
    const carregarContasBancarias = async () => {
      try {
        const contas = await listarContasBancarias();
        setContasBancarias(contas);
      } catch (err) {
        console.error("Erro ao carregar contas bancárias:", err);
      }
    };
    
    carregarContasBancarias();
  }, []);

  // Efeito para carregar dados
  useEffect(() => {
    fetchData();
  }, [filtros]);

  // Função para agrupar itens por dia
  const agruparPorDia = (itens: FluxoItem[]): FluxoGrupo[] => {
    if (!itens || itens.length === 0) return [];
    
    const grupos: { [key: string]: FluxoItem[] } = {};

    // Ordenar itens por data
    const ordenados = [...itens].sort((a, b) => 
      new Date(a.data).getTime() - new Date(b.data).getTime()
    );

    // Agrupar por data
    ordenados.forEach(item => {
      if (!grupos[item.data]) {
        grupos[item.data] = [];
      }
      grupos[item.data].push(item);
    });

    // Converter para array
    return Object.keys(grupos).map(data => ({
      data,
      itens: grupos[data]
    }));
  };

  // Função para agrupar itens por mês
  const agruparPorMes = (itens: FluxoItem[]): FluxoGrupo[] => {
    if (!itens || itens.length === 0) return [];
    
    const grupos: { [key: string]: FluxoItem[] } = {};

    // Ordenar itens por data
    const ordenados = [...itens].sort((a, b) => 
      new Date(a.data).getTime() - new Date(b.data).getTime()
    );

    // Agrupar por mês
    ordenados.forEach(item => {
      const data = new Date(item.data);
      const mesAno = `${data.getFullYear()}-${String(data.getMonth() + 1).padStart(2, '0')}`;
      
      if (!grupos[mesAno]) {
        grupos[mesAno] = [];
      }
      grupos[mesAno].push(item);
    });

    // Converter para array e formatar títulos
    return Object.keys(grupos).map(mesAno => {
      const [ano, mes] = mesAno.split('-');
      const nomesMeses = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
      ];
      
      return {
        data: `${nomesMeses[parseInt(mes) - 1]} de ${ano}`,
        itens: grupos[mesAno]
      };
    });
  };

  // Função para criar visualização acumulada
  const criarVisualizacaoAcumulada = (itens: FluxoItem[]): FluxoGrupo[] => {
    if (!itens || itens.length === 0) return [];
    
    // Ordenar itens por data
    const ordenados = [...itens].sort((a, b) => 
      new Date(a.data).getTime() - new Date(b.data).getTime()
    );
    
    // Inicializar com saldo inicial (assumindo 0)
    let saldoAcumulado = 0;
    
    // Criar itens acumulados
    const itensAcumulados = ordenados.map(item => {
      saldoAcumulado += item.valor;
      return {
        ...item,
        valor_acumulado: saldoAcumulado,
        data_formatada: formatarData(item.data)
      };
    });
    
    // Configuração do período para exibição
    const dataInicial = new Date(ordenados[0].data);
    const dataFinal = new Date(ordenados[ordenados.length - 1].data);
    
    const textoData = `${formatarData(dataInicial.toISOString())} a ${formatarData(dataFinal.toISOString())}`;
    
    return [{
      data: textoData,
      itens: itensAcumulados
    }];
  };

  // Agrupar dados de acordo com a visualização selecionada
  const dadosAgrupados = useMemo(() => {
    if (!fluxoItens || !Array.isArray(fluxoItens) || fluxoItens.length === 0) return [];
    
    switch (tipoVisualizacao) {
      case "mensal":
        return agruparPorMes(fluxoItens);
      case "acumulada":
        return criarVisualizacaoAcumulada(fluxoItens);
      case "diaria":
      default:
        return agruparPorDia(fluxoItens);
    }
  }, [fluxoItens, tipoVisualizacao]);

  // Buscar dados de fluxo de caixa
  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Cria uma cópia dos filtros sem os valores undefined
      const filtrosValidos: Record<string, string> = {
        dataInicio: filtros.dataInicio,
        dataFim: filtros.dataFim
      };
      
      // Adiciona apenas os filtros com valores definidos
      if (filtros.id_conta) filtrosValidos.id_conta = filtros.id_conta;
      if (filtros.tipo) filtrosValidos.tipo = filtros.tipo;
      if (filtros.status) filtrosValidos.status = filtros.status;
      
      const data = await buscarFluxoCaixaFiltrado(filtrosValidos);
      setFluxoItens(data);
      showToast("Dados de fluxo de caixa carregados com sucesso", "sucesso");
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar fluxo de caixa';
      setError(errorMessage);
      showToast(errorMessage, "erro");
      console.error("Erro ao carregar fluxo de caixa:", err);
    } finally {
      setLoading(false);
    }
  };

  // Handles para atualização de filtros
  const handleFiltroChange = (campo: keyof FluxoCaixaFiltros, valor: string) => {
    setFiltros(prev => ({
      ...prev,
      [campo]: valor === "" ? undefined : valor
    }));
  };

  const handleLimparFiltros = () => {
    setFiltros({
      dataInicio: new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0],
      dataFim: new Date().toISOString().split('T')[0],
      tipo: undefined,
      id_conta: undefined,
      status: undefined
    });
  };

  // Renderizar gráfico para visualização acumulada
  const renderizarGraficoAcumulado = () => {
    if (!Array.isArray(fluxoItens) || fluxoItens.length === 0 || !Array.isArray(dadosAgrupados) || dadosAgrupados.length === 0) {
      return null;
    }
    
    // Obter dados necessários para a visualização
    const grupo = dadosAgrupados[0];
    const itensAcumulados = grupo.itens;
    
    // Encontrar o valor máximo para calcular proporções
    const valorMaximo = Math.max(
      ...itensAcumulados.map(item => Math.abs((item as any).valor_acumulado || 0))
    );
    
    // Considerar apenas alguns pontos para não sobrecarregar o gráfico
    // Se tiver muitos itens, selecionar pontos representativos
    const pontosMostrados = itensAcumulados.length > 12 
      ? itensAcumulados.filter((_, index) => index % Math.floor(itensAcumulados.length / 12) === 0)
      : itensAcumulados;
      
    return (
      <div className="bg-white rounded-lg shadow-sm p-4 my-4">
        <h3 className="text-lg font-semibold mb-3">Evolução do Fluxo de Caixa</h3>
        
        {/* Visualização nativa do gráfico */}
        <div className="h-80 relative">
          {/* Eixo Y (valores) */}
          <div className="absolute top-0 left-0 h-full w-12 border-r border-gray-200 flex flex-col justify-between py-2">
            <span className="text-xs text-gray-500">{formatarMoeda(valorMaximo)}</span>
            <span className="text-xs text-gray-500">{formatarMoeda(valorMaximo/2)}</span>
            <span className="text-xs text-gray-500">{formatarMoeda(0)}</span>
            <span className="text-xs text-gray-500">{formatarMoeda(-valorMaximo/2)}</span>
            <span className="text-xs text-gray-500">{formatarMoeda(-valorMaximo)}</span>
          </div>
          
          {/* Área do gráfico */}
          <div className="ml-12 h-full flex flex-col">
            {/* Linhas de grade */}
            <div className="h-full relative">
              <div className="absolute w-full border-b border-gray-200" style={{ top: '0%' }}></div>
              <div className="absolute w-full border-b border-gray-200" style={{ top: '25%' }}></div>
              <div className="absolute w-full border-b border-gray-200" style={{ top: '50%' }}></div>
              <div className="absolute w-full border-b border-gray-200" style={{ top: '75%' }}></div>
              <div className="absolute w-full border-b border-gray-200" style={{ top: '100%' }}></div>
              
              {/* Linha do zero */}
              <div className="absolute w-full border-b-2 border-gray-400" style={{ top: '50%' }}></div>
              
              {/* Pontos do gráfico */}
              <div className="flex h-full items-center">
                {pontosMostrados.map((item, index) => {
                  const valor = (item as any).valor_acumulado || 0;
                  // Calcular posição vertical (de 0% a 100%)
                  // 50% é zero, acima é positivo, abaixo é negativo
                  const posicaoY = 50 - (valor / valorMaximo) * 50;
                  const cor = valor >= 0 ? 'bg-blue-500' : 'bg-red-500';
                  
                  return (
                    <div 
                      key={index} 
                      className="flex-1 h-full flex flex-col items-center justify-end relative"
                      title={`${formatarData(item.data)}: ${formatarMoeda(valor)}`}
                    >
                      {/* Barra/Ponto */}
                      <div 
                        className={`w-2 h-2 rounded-full ${cor}`} 
                        style={{ position: 'absolute', top: `${posicaoY}%` }}
                      ></div>
                      
                      {/* Linha conectora (se não for o primeiro item) */}
                      {index > 0 && (
                        <div 
                          className={`absolute h-0.5 ${valor >= 0 ? 'bg-blue-400' : 'bg-red-400'}`} 
                          style={{ 
                            width: `100%`, 
                            top: `${posicaoY}%`,
                            right: '50%',
                            transform: 'translateY(-50%)'
                          }}
                        ></div>
                      )}
                      
                      {/* Rótulo da data (apenas alguns para não sobrecarregar) */}
                      {index % 3 === 0 && (
                        <div className="absolute bottom-0 text-xs text-gray-500 transform -rotate-45 origin-top-left">
                          {formatarData(item.data)}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
        
        {/* Legenda */}
        <div className="flex justify-center mt-8 pt-2 border-t border-gray-200">
          <div className="flex items-center mx-2">
            <div className="w-3 h-3 rounded-full bg-blue-500 mr-1"></div>
            <span className="text-xs text-gray-600">Saldo Acumulado</span>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="page-content">
      <h1 className="page-title">Fluxo de Caixa</h1>
      
      {/* Controles de visualização */}
      <div className="flex gap-4 mb-4">
        <div className="flex border rounded-md overflow-hidden">
          <button 
            className={`px-4 py-2 ${tipoVisualizacao === "diaria" ? "bg-blue-600 text-white" : "bg-gray-100"}`}
            onClick={() => setTipoVisualizacao("diaria")}
          >
            Diária
          </button>
          <button 
            className={`px-4 py-2 ${tipoVisualizacao === "mensal" ? "bg-blue-600 text-white" : "bg-gray-100"}`}
            onClick={() => setTipoVisualizacao("mensal")}
          >
            Mensal
          </button>
          <button 
            className={`px-4 py-2 ${tipoVisualizacao === "acumulada" ? "bg-blue-600 text-white" : "bg-gray-100"}`}
            onClick={() => setTipoVisualizacao("acumulada")}
          >
            Acumulada
          </button>
        </div>
      </div>
      
      {/* Painel de filtros */}
      <FilterPanel title="Filtros" className="mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label htmlFor="dataInicio" className="block text-sm font-medium text-gray-700 mb-1">
              Data Início
            </label>
            <input
              type="date"
              id="dataInicio"
              className="input-padrao"
              value={filtros.dataInicio}
              onChange={(e) => handleFiltroChange("dataInicio", e.target.value)}
            />
          </div>
          
          <div>
            <label htmlFor="dataFim" className="block text-sm font-medium text-gray-700 mb-1">
              Data Fim
            </label>
            <input
              type="date"
              id="dataFim"
              className="input-padrao"
              value={filtros.dataFim}
              onChange={(e) => handleFiltroChange("dataFim", e.target.value)}
            />
          </div>
          
          <div>
            <label htmlFor="id_conta" className="block text-sm font-medium text-gray-700 mb-1">
              Conta Bancária
            </label>
            <select
              id="id_conta"
              className="input-padrao"
              value={filtros.id_conta || ""}
              onChange={(e) => handleFiltroChange("id_conta", e.target.value)}
            >
              <option value="">Todas as contas</option>
              {contasBancarias.map(conta => (
                <option key={conta.id_conta} value={conta.id_conta}>
                  {conta.nome} - {conta.banco}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label htmlFor="tipo" className="block text-sm font-medium text-gray-700 mb-1">
              Tipo
            </label>
            <select
              id="tipo"
              className="input-padrao"
              value={filtros.tipo || ""}
              onChange={(e) => handleFiltroChange("tipo", e.target.value)}
            >
              <option value="">Todos</option>
              <option value="receita">Receitas</option>
              <option value="despesa">Despesas</option>
            </select>
          </div>
          
          <div>
            <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              id="status"
              className="input-padrao"
              value={filtros.status || ""}
              onChange={(e) => handleFiltroChange("status", e.target.value)}
            >
              <option value="">Todos</option>
              <option value="pago">Pagos</option>
              <option value="pendente">Pendentes</option>
            </select>
          </div>
        </div>
        
        <div className="flex justify-end mt-4">
          <button 
            className="btn-outline mr-2"
            onClick={handleLimparFiltros}
          >
            Limpar Filtros
          </button>
          <button 
            className="btn-primary"
            onClick={fetchData}
          >
            Aplicar Filtros
          </button>
        </div>
      </FilterPanel>
      
      {/* Conteúdo principal */}
      <DataStateHandler
        loading={loading}
        error={error}
        dataLength={Array.isArray(fluxoItens) ? fluxoItens.length : 0}
        onRetry={fetchData}
        emptyMessage="Nenhum lançamento encontrado para o período selecionado."
      >
        {Array.isArray(fluxoItens) && fluxoItens.length > 0 && Array.isArray(dadosAgrupados) && dadosAgrupados.length > 0 && (
          <div className="space-y-6">
            {dadosAgrupados.map((grupo, groupIndex) => (
              <div key={groupIndex} className="bg-white rounded-lg shadow-sm p-4">
                <h2 className="text-xl font-semibold mb-4 text-gray-800">{grupo.data}</h2>
                
                <div className="overflow-x-auto">
                  <table className="min-w-full border-collapse">
                    <thead>
                      <tr className="bg-gray-50">
                        {tipoVisualizacao !== "acumulada" && <th className="py-2 px-4 text-left">Data</th>}
                        <th className="py-2 px-4 text-left">Tipo</th>
                        <th className="py-2 px-4 text-left">Descrição</th>
                        <th className="py-2 px-4 text-right">Valor</th>
                        {tipoVisualizacao === "acumulada" && <th className="py-2 px-4 text-right">Acumulado</th>}
                      </tr>
                    </thead>
                    <tbody>
                      {Array.isArray(grupo.itens) && grupo.itens.map((item, index) => (
                        <tr key={index} className="border-t border-gray-100">
                          {tipoVisualizacao !== "acumulada" && <td className="py-2 px-4">{formatarData(item.data)}</td>}
                          <td className="py-2 px-4">
                            <span className={`inline-block px-2 py-1 rounded-full text-xs ${
                              item && item.tipo === "receita" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
                            }`}>
                              {item && item.tipo === "receita" ? "Receita" : "Despesa"}
                            </span>
                          </td>
                          <td className="py-2 px-4">{item ? item.descricao : ''}</td>
                          <td className={`py-2 px-4 text-right font-medium ${
                            item && item.tipo === "receita" ? "text-green-600" : "text-red-600"
                          }`}>
                            {formatarMoeda(item ? Math.abs(item.valor || 0) : 0)}
                          </td>
                          {tipoVisualizacao === "acumulada" && (
                            <td className={`py-2 px-4 text-right font-medium ${
                              item && (item as any).valor_acumulado >= 0 ? "text-green-600" : "text-red-600"
                            }`}>
                              {formatarMoeda(item ? Math.abs((item as any).valor_acumulado || 0) : 0)}
                            </td>
                          )}
                        </tr>
                      ))}
                      <tr className="bg-gray-50 font-semibold border-t border-gray-200">
                        <td colSpan={tipoVisualizacao !== "acumulada" ? 3 : 2} className="py-2 px-4 text-right">
                          Total:
                        </td>
                        <td className={`py-2 px-4 text-right ${
                          Array.isArray(grupo.itens) && grupo.itens.length > 0 
                            ? (grupo.itens.reduce((acc, item) => acc + (item?.valor || 0), 0) >= 0 
                              ? "text-green-600" 
                              : "text-red-600")
                            : "text-gray-600"
                        }`}>
                          {formatarMoeda(
                            Array.isArray(grupo.itens) && grupo.itens.length > 0
                              ? grupo.itens.reduce((acc, item) => acc + (item?.valor || 0), 0)
                              : 0
                          )}
                        </td>
                        {tipoVisualizacao === "acumulada" && <td></td>}
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            ))}
            
            {/* Resumo geral apenas para visualizações diária e mensal */}
            {tipoVisualizacao !== "acumulada" && (
              <div className="bg-white rounded-lg shadow-sm p-4 my-4">
                <h3 className="text-lg font-semibold mb-3">Resumo do Período</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-green-50 p-3 rounded-md">
                    <p className="text-sm text-green-700">Total de Receitas</p>
                    <p className="text-xl font-semibold text-green-600">
                      {formatarMoeda(
                        Array.isArray(fluxoItens) && fluxoItens.length > 0
                          ? fluxoItens
                              .filter(item => item && item.tipo === "receita")
                              .reduce((acc, item) => acc + (item?.valor || 0), 0)
                          : 0
                      )}
                    </p>
                  </div>
                  <div className="bg-red-50 p-3 rounded-md">
                    <p className="text-sm text-red-700">Total de Despesas</p>
                    <p className="text-xl font-semibold text-red-600">
                      {formatarMoeda(Math.abs(
                        Array.isArray(fluxoItens) && fluxoItens.length > 0
                          ? fluxoItens
                              .filter(item => item && item.tipo === "despesa")
                              .reduce((acc, item) => acc + (item?.valor || 0), 0)
                          : 0
                      ))}
                    </p>
                  </div>
                  <div className={`p-3 rounded-md ${
                    Array.isArray(fluxoItens) && fluxoItens.length > 0 && fluxoItens.reduce((acc, item) => acc + (item?.valor || 0), 0) >= 0 
                      ? "bg-blue-50" 
                      : "bg-yellow-50"
                  }`}>
                    <p className={`text-sm ${
                      Array.isArray(fluxoItens) && fluxoItens.length > 0 && fluxoItens.reduce((acc, item) => acc + (item?.valor || 0), 0) >= 0 
                        ? "text-blue-700" 
                        : "text-yellow-700"
                    }`}>
                      Resultado
                    </p>
                    <p className={`text-xl font-semibold ${
                      Array.isArray(fluxoItens) && fluxoItens.length > 0 && fluxoItens.reduce((acc, item) => acc + (item?.valor || 0), 0) >= 0 
                        ? "text-blue-600" 
                        : "text-yellow-600"
                    }`}>
                      {formatarMoeda(
                        Array.isArray(fluxoItens) && fluxoItens.length > 0
                          ? fluxoItens.reduce((acc, item) => acc + (item?.valor || 0), 0)
                          : 0
                      )}
                    </p>
                  </div>
                </div>
              </div>
            )}
            
            {/* Adicionar gráfico para visualização acumulada */}
            {tipoVisualizacao === "acumulada" && renderizarGraficoAcumulado()}
          </div>
        )}
      </DataStateHandler>
    </div>
  );
} 