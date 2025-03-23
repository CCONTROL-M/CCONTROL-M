import { useEffect, useState } from "react";
import { FluxoItem, FluxoGrupo } from "../types";
import { obterRelatorioFluxoCaixa } from "../services/relatoriosService";
import { formatarData, formatarMoeda } from "../utils/formatters";
import DataStateHandler from "../components/DataStateHandler";
import { setUseMock } from "../utils/mock";

export default function FluxoCaixa() {
  const [fluxoItens, setFluxoItens] = useState<FluxoItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Ativa o modo mock assim que o componente for renderizado
  useEffect(() => {
    // Ativar o modo mock para garantir que a aplicação funcione sem backend
    setUseMock(true);
    console.log("🔧 Modo mock foi ativado forcadamente na página de Fluxo de Caixa");
  }, []);

  // Efeito para carregar dados
  useEffect(() => {
    fetchData();
  }, []);

  // Função para agrupar itens por data
  const agruparPorData = (itens: FluxoItem[]): FluxoGrupo[] => {
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

  // Buscar dados de fluxo de caixa
  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await obterRelatorioFluxoCaixa();
      setFluxoItens(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar fluxo de caixa';
      setError(errorMessage);
      console.error("Erro ao carregar fluxo de caixa:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-content">
      <h1 className="page-title">Fluxo de Caixa</h1>
      
      <DataStateHandler
        loading={loading}
        error={error}
        dataLength={fluxoItens.length}
        onRetry={fetchData}
        emptyMessage="Nenhum lançamento encontrado."
      >
        {fluxoItens.length > 0 && (
          <>
            {agruparPorData(fluxoItens).map((grupo) => (
              <div key={grupo.data} className="fluxo-grupo">
                <h2 className="fluxo-data">{formatarData(grupo.data)}</h2>
                <table className="fluxo-tabela">
                  <thead>
                    <tr>
                      <th>Tipo</th>
                      <th>Descrição</th>
                      <th>Valor</th>
                    </tr>
                  </thead>
                  <tbody>
                    {grupo.itens.map((item, index) => (
                      <tr key={index}>
                        <td>{item.tipo === "receita" ? "Receita" : "Despesa"}</td>
                        <td>{item.descricao}</td>
                        <td className={item.tipo === "receita" ? "valor-positivo" : "valor-negativo"}>
                          {formatarMoeda(Math.abs(item.valor))}
                        </td>
                      </tr>
                    ))}
                    <tr className="total-row">
                      <td colSpan={2}>Total do dia:</td>
                      <td>
                        {formatarMoeda(grupo.itens.reduce((acc, item) => acc + item.valor, 0))}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            ))}
            
            <div className="fluxo-resumo">
              <h3>Resumo Geral</h3>
              <p>Total Geral: {formatarMoeda(fluxoItens.reduce((acc, item) => acc + item.valor, 0))}</p>
            </div>
          </>
        )}
      </DataStateHandler>
    </div>
  );
} 