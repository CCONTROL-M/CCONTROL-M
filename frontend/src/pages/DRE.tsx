import { useEffect, useState } from "react";
import { DREData, CategoriaValor } from "../types";
import { buscarDREPeriodo } from "../services/relatorioService";
import { buscarDREPeriodoMock } from "../services/relatorioServiceMock";
import { formatarMoeda, formatarData } from "../utils/formatters";
import DataStateHandler from "../components/DataStateHandler";
import { useToast } from "../hooks/useToast";
import useDataFetching from "../hooks/useDataFetching";
import { useMock, setUseMock } from "../utils/mock";
import { verificarStatusAPI } from "../services/api";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip
} from 'recharts';

// Definição de grupo de categorias para agrupamento de DRE
interface GrupoDRE {
  titulo: string;
  categorias: string[];
  isPositivo: boolean;
}

// Definição dos filtros
interface FiltroDRE {
  dataInicio: string;
  dataFim: string;
}

export default function DRE() {
  // Toast para notificações
  const { showToast } = useToast();

  // Estados para filtros
  const hoje = new Date();
  const inicioMes = new Date(hoje.getFullYear(), hoje.getMonth(), 1);
  
  const [filtros, setFiltros] = useState<FiltroDRE>({
    dataInicio: inicioMes.toISOString().split('T')[0],
    dataFim: hoje.toISOString().split('T')[0]
  });
  
  const [mostrarFiltros, setMostrarFiltros] = useState<boolean>(false);
  const [apiOffline, setApiOffline] = useState<boolean>(false);
  
  // Definição dos grupos de categorias
  const gruposCategorias: GrupoDRE[] = [
    {
      titulo: "Receitas Operacionais",
      categorias: ["Vendas de Produtos", "Prestação de Serviços"],
      isPositivo: true
    },
    {
      titulo: "Outras Receitas",
      categorias: ["Comissões", "Outras Receitas"],
      isPositivo: true
    },
    {
      titulo: "Custos Operacionais",
      categorias: ["Custos dos Produtos", "Folha de Pagamento"],
      isPositivo: false
    },
    {
      titulo: "Despesas Administrativas",
      categorias: ["Aluguel", "Energia/Internet", "Materiais de Escritório"],
      isPositivo: false
    },
    {
      titulo: "Despesas Comerciais",
      categorias: ["Marketing", "Comissões Pagas"],
      isPositivo: false
    },
    {
      titulo: "Impostos e Taxas",
      categorias: ["Impostos"],
      isPositivo: false
    },
    {
      titulo: "Outras Despesas",
      categorias: ["Outras Despesas"],
      isPositivo: false
    }
  ];
  
  // Função para verificar API
  const verificarApi = async () => {
    const { online } = await verificarStatusAPI();
    setApiOffline(!online);
    
    // Não ativamos mais o modo mock automaticamente
    // Apenas registramos o status da API
    if (!online) {
      console.warn("API offline no relatório DRE, continuando com modo atual");
    }
  };

  // Usar o hook personalizado para buscar dados
  const { 
    data: dreData, 
    loading, 
    error, 
    fetchData 
  } = useDataFetching<DREData>({
    fetchFunction: () => buscarDREPeriodo(filtros),
    mockFunction: () => buscarDREPeriodoMock(filtros),
    dependencies: [filtros],
    loadingId: 'dre-report',
    errorMessage: 'Não foi possível carregar os dados do DRE',
    showErrorToast: true,
    useGlobalLoading: false
  });

  // Verificar API ao carregar
  useEffect(() => {
    verificarApi();
  }, []);

  // Atualizar valor de filtro
  const atualizarFiltro = (campo: keyof FiltroDRE, valor: string) => {
    setFiltros(prev => ({
      ...prev,
      [campo]: valor
    }));
  };
  
  // Aplicar filtros
  const aplicarFiltros = () => {
    setMostrarFiltros(false);
    fetchData();
  };
  
  // Limpar filtros
  const limparFiltros = () => {
    setFiltros({
      dataInicio: inicioMes.toISOString().split('T')[0],
      dataFim: hoje.toISOString().split('T')[0]
    });
  };

  // Filtrar itens por grupo de categoria
  const filtrarItensPorGrupo = (itens: CategoriaValor[] = [], categorias: string[]): CategoriaValor[] => {
    if (!Array.isArray(itens)) return [];
    return itens.filter(item => categorias.includes(item.categoria));
  };

  // Renderizar uma seção do relatório (receitas ou despesas)
  const renderizarGrupo = (grupo: GrupoDRE) => {
    if (!dreData) return null;
    
    // Determinar se o grupo é de receitas ou despesas
    const itensOrigem = grupo.isPositivo 
      ? (Array.isArray(dreData.receitas) ? dreData.receitas : []) 
      : (Array.isArray(dreData.despesas) ? dreData.despesas : []);
    
    // Filtrar apenas os itens que pertencem a este grupo
    const itensGrupo = filtrarItensPorGrupo(itensOrigem, grupo.categorias);
    
    // Se não houver itens neste grupo, não renderizar
    if (!Array.isArray(itensGrupo) || itensGrupo.length === 0) return null;
    
    // Calcular total do grupo
    const totalGrupo = itensGrupo.reduce((acc, item) => acc + (item?.valor || 0), 0);
    
    // Calcular total geral de receitas ou despesas para percentuais
    const totalGeral = itensOrigem.reduce((acc, item) => acc + (item?.valor || 0), 0);
    
    // Calcular percentuais para cada item
    const itensComPercentual = itensGrupo.map(item => ({
      ...item,
      percentual: totalGeral > 0 ? ((item?.valor || 0) / totalGeral) * 100 : 0
    }));
    
    // Calcular percentual do grupo em relação ao total
    const percentualGrupo = totalGeral > 0 ? (totalGrupo / totalGeral) * 100 : 0;
    
    return (
      <div key={grupo.titulo} className={`bg-white rounded-lg shadow-sm p-4 mb-4`}>
        <div className="flex justify-between items-center mb-3 border-b pb-2">
          <h3 className="text-lg font-semibold">{grupo.titulo}</h3>
          <div className="text-right">
            <span className={`font-semibold ${grupo.isPositivo ? 'text-green-600' : 'text-red-600'}`}>
              {formatarMoeda(totalGrupo)}
            </span>
            <span className="text-gray-600 text-sm ml-2">
              ({percentualGrupo.toFixed(1)}%)
            </span>
          </div>
        </div>
        
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="py-2 px-4 text-left text-sm font-medium text-gray-700">Categoria</th>
              <th className="py-2 px-4 text-right text-sm font-medium text-gray-700">Valor</th>
              <th className="py-2 px-4 text-right text-sm font-medium text-gray-700">%</th>
            </tr>
          </thead>
          <tbody>
            {itensComPercentual.map((item, index) => (
              <tr key={index} className="border-b border-gray-100">
                <td className="py-2 px-4">{item.categoria}</td>
                <td className={`py-2 px-4 text-right ${grupo.isPositivo ? 'text-green-600' : 'text-red-600'}`}>
                  {formatarMoeda(item.valor)}
                </td>
                <td className="py-2 px-4 text-right">{item.percentual.toFixed(1)}%</td>
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr className="bg-gray-50 font-semibold">
              <td className="py-2 px-4">Total de {grupo.titulo}</td>
              <td className={`py-2 px-4 text-right ${grupo.isPositivo ? 'text-green-600' : 'text-red-600'}`}>
                {formatarMoeda(totalGrupo)}
              </td>
              <td className="py-2 px-4 text-right">{percentualGrupo.toFixed(1)}%</td>
            </tr>
          </tfoot>
        </table>
      </div>
    );
  };
  
  // Renderizar resumo financeiro
  const renderizarResumo = () => {
    if (!dreData) return null;
    
    const totalReceitas = Array.isArray(dreData.receitas) 
      ? dreData.receitas.reduce((acc, item) => acc + (item?.valor || 0), 0) 
      : 0;
    
    const totalDespesas = Array.isArray(dreData.despesas) 
      ? dreData.despesas.reduce((acc, item) => acc + (item?.valor || 0), 0) 
      : 0;
    
    const margemLucro = totalReceitas > 0 
      ? (dreData.lucro_prejuizo / totalReceitas) * 100 
      : 0;

    // Preparar dados para os gráficos
    const dadosReceitas = Array.isArray(dreData.receitas) && dreData.receitas.length > 0
      ? dreData.receitas.map(item => ({
          name: item.categoria,
          value: item.valor
        }))
      : [];

    const dadosDespesas = Array.isArray(dreData.despesas) && dreData.despesas.length > 0
      ? dreData.despesas.map(item => ({
          name: item.categoria,
          value: Math.abs(item.valor)
        }))
      : [];

    return (
      <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
        <h2 className="text-xl font-bold mb-4">Resumo Financeiro</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-green-50 p-3 rounded-md">
            <p className="text-sm text-green-700">Total de Receitas</p>
            <p className="text-xl font-semibold text-green-600">
              {formatarMoeda(totalReceitas)}
            </p>
          </div>
          
          <div className="bg-red-50 p-3 rounded-md">
            <p className="text-sm text-red-700">Total de Despesas</p>
            <p className="text-xl font-semibold text-red-600">
              {formatarMoeda(totalDespesas)}
            </p>
          </div>
          
          <div className={`p-3 rounded-md ${dreData.lucro_prejuizo >= 0 ? 'bg-blue-50' : 'bg-yellow-50'}`}>
            <p className="text-sm text-gray-700">
              {dreData.lucro_prejuizo >= 0 ? 'Lucro Líquido' : 'Prejuízo Líquido'}
            </p>
            <p className={`text-xl font-semibold ${dreData.lucro_prejuizo >= 0 ? 'text-blue-600' : 'text-yellow-600'}`}>
              {formatarMoeda(Math.abs(dreData.lucro_prejuizo))}
            </p>
          </div>
        </div>
        
        {/* Indicadores */}
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Margem de Lucro</p>
              <p className={`text-lg font-medium ${margemLucro >= 0 ? 'text-blue-600' : 'text-yellow-600'}`}>
                {margemLucro.toFixed(2)}%
              </p>
            </div>
            
            <div>
              <p className="text-sm text-gray-600">Índice de Lucratividade</p>
              <p className="text-lg font-medium text-gray-800">
                {dreData.lucro_prejuizo >= 0 ? 
                  (totalReceitas / totalDespesas).toFixed(2) : 
                  "0.00"}
              </p>
            </div>
          </div>
        </div>

        {/* Gráficos */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Gráfico de Receitas */}
          {dadosReceitas.length > 0 && (
            <div>
              <h3 className="text-lg font-medium mb-2 text-center">Composição das Receitas</h3>
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <div className="space-y-3">
                  {dadosReceitas.map((item, index) => {
                    const percent = item.value / totalReceitas * 100;
                    return (
                      <div key={`receita-${index}`} className="flex flex-col">
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-sm">{item.name}</span>
                          <div className="flex items-center">
                            <span className="text-sm font-medium">{formatarMoeda(item.value)}</span>
                            <span className="text-xs text-gray-500 ml-2">({percent.toFixed(1)}%)</span>
                          </div>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-green-500 h-2 rounded-full" 
                            style={{ width: `${percent}%` }}
                          ></div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {/* Gráfico de Despesas */}
          {dadosDespesas.length > 0 && (
            <div>
              <h3 className="text-lg font-medium mb-2 text-center">Composição das Despesas</h3>
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <div className="space-y-3">
                  {dadosDespesas.map((item, index) => {
                    const percent = item.value / totalDespesas * 100;
                    return (
                      <div key={`despesa-${index}`} className="flex flex-col">
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-sm">{item.name}</span>
                          <div className="flex items-center">
                            <span className="text-sm font-medium">{formatarMoeda(item.value)}</span>
                            <span className="text-xs text-gray-500 ml-2">({percent.toFixed(1)}%)</span>
                          </div>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-red-500 h-2 rounded-full" 
                            style={{ width: `${percent}%` }}
                          ></div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="page-content">
      <h1 className="page-title">DRE</h1>
      
      <div className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Demonstrativo de Resultados (DRE)</h2>
          <button 
            onClick={() => setMostrarFiltros(!mostrarFiltros)}
            className="btn-secondary"
          >
            {mostrarFiltros ? 'Esconder Filtros' : 'Exibir Filtros'}
          </button>
        </div>
        
        <p className="text-gray-600 mb-2">
          Período: {formatarData(filtros.dataInicio)} a {formatarData(filtros.dataFim)}
        </p>
        
        {apiOffline && (
          <div className="mt-2 p-2 bg-yellow-100 border border-yellow-300 rounded text-sm">
            <p className="text-yellow-700">
              <span className="font-bold">Modo de demonstração:</span> Servidor não disponível, exibindo dados simulados
            </p>
          </div>
        )}
        
        {mostrarFiltros && (
          <div className="bg-white rounded-lg shadow-sm p-4 mb-4 mt-2">
            <h3 className="text-lg font-semibold mb-3">Filtros</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Data Início</label>
                <input 
                  type="date" 
                  value={filtros.dataInicio}
                  onChange={e => atualizarFiltro('dataInicio', e.target.value)}
                  className="input-field w-full"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Data Fim</label>
                <input 
                  type="date" 
                  value={filtros.dataFim}
                  onChange={e => atualizarFiltro('dataFim', e.target.value)}
                  className="input-field w-full"
                />
              </div>
            </div>
            <div className="flex justify-end mt-3">
              <button 
                onClick={limparFiltros}
                className="btn-outline mr-2"
              >
                Limpar
              </button>
              <button 
                onClick={aplicarFiltros}
                className="btn-primary"
              >
                Atualizar
              </button>
            </div>
          </div>
        )}
      </div>
      
      <DataStateHandler
        loading={loading}
        error={error ? error.message : null}
        dataLength={dreData ? 1 : 0}
        onRetry={fetchData}
        emptyMessage="Nenhum dado disponível para o período selecionado."
        useGlobalLoading={false}
        operationId="dre-view"
      >
        {dreData && (
          <div>
            {/* Resumo Geral */}
            {renderizarResumo()}
            
            {/* Seções de receitas */}
            <div className="mb-6">
              <h2 className="text-xl font-bold mb-3">Receitas</h2>
              {gruposCategorias
                .filter(grupo => grupo.isPositivo)
                .map(grupo => renderizarGrupo(grupo))}
            </div>
            
            {/* Seções de despesas */}
            <div className="mb-6">
              <h2 className="text-xl font-bold mb-3">Despesas</h2>
              {gruposCategorias
                .filter(grupo => !grupo.isPositivo)
                .map(grupo => renderizarGrupo(grupo))}
            </div>
            
            {/* Resultado final */}
            <div className="bg-white rounded-lg shadow-sm p-4 mt-6">
              <h2 className="text-xl font-bold mb-3">Resultado Líquido</h2>
              <div className="flex justify-between items-center">
                <div>
                  <p className="text-lg">
                    {dreData.lucro_prejuizo >= 0 ? 'Lucro' : 'Prejuízo'} do período
                  </p>
                  <p className="text-sm text-gray-600">
                    {formatarData(filtros.dataInicio)} a {formatarData(filtros.dataFim)}
                  </p>
                </div>
                <div className={`text-2xl font-bold ${
                  dreData.lucro_prejuizo >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {formatarMoeda(Math.abs(dreData.lucro_prejuizo))}
                </div>
              </div>
            </div>
          </div>
        )}
      </DataStateHandler>
    </div>
  );
} 