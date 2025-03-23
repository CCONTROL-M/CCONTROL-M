import { useEffect, useState } from "react";
import api from "../services/api";
import { FluxoItem, FluxoGrupo } from "../types";
import { formatarData, formatarMoeda } from "../utils/formatters";

export default function FluxoCaixa() {
  const [fluxoItens, setFluxoItens] = useState<FluxoItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    async function fetchFluxoCaixa() {
      try {
        const response = await api.get("/relatorios/fluxo-caixa");
        setFluxoItens(response.data);
      } catch (err) {
        setError("Erro ao carregar o fluxo de caixa.");
      } finally {
        setLoading(false);
      }
    }
    fetchFluxoCaixa();
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

  if (loading) return <p className="placeholder-text">Carregando...</p>;
  if (error) return <p className="placeholder-text">{error}</p>;
  if (fluxoItens.length === 0) return <p className="placeholder-text">Nenhum lançamento encontrado.</p>;

  const gruposFluxo = agruparPorData(fluxoItens);

  return (
    <div>
      <h1 className="page-title">Fluxo de Caixa</h1>
      
      {gruposFluxo.map((grupo) => (
        <div key={grupo.data} className="fluxo-grupo">
          <h2 className="fluxo-data">{formatarData(grupo.data)}</h2>
          <table>
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
    </div>
  );
} 