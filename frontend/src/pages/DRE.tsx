import { useEffect, useState } from "react";
import api from "../services/api";
import { CategoriaValor, DREData } from "../types";
import { formatarMoeda } from "../utils/formatters";

export default function DRE() {
  const [dreData, setDreData] = useState<DREData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    async function fetchDRE() {
      try {
        const response = await api.get("/relatorios/dre");
        setDreData(response.data);
      } catch (err) {
        setError("Erro ao carregar o DRE.");
      } finally {
        setLoading(false);
      }
    }
    fetchDRE();
  }, []);

  if (loading) return <p className="placeholder-text">Carregando...</p>;
  if (error) return <p className="placeholder-text">{error}</p>;
  if (!dreData) return <p className="placeholder-text">Nenhum dado encontrado.</p>;

  // Calcular totais
  const totalReceitas = dreData.receitas.reduce((acc, item) => acc + item.valor, 0);
  const totalDespesas = dreData.despesas.reduce((acc, item) => acc + item.valor, 0);
  
  // Verificar se o resultado é lucro ou prejuízo
  const isLucro = dreData.lucro_prejuizo >= 0;

  return (
    <div>
      <h1 className="page-title">DRE – Demonstrativo de Resultados</h1>
      
      {/* Tabela de Receitas */}
      <div className="dre-section">
        <h2 className="dre-section-title dre-receitas">Receitas</h2>
        <table>
          <thead>
            <tr>
              <th>Categoria</th>
              <th>Valor</th>
            </tr>
          </thead>
          <tbody>
            {dreData.receitas.map((item, index) => (
              <tr key={index}>
                <td>{item.categoria}</td>
                <td className="valor-positivo">{formatarMoeda(item.valor)}</td>
              </tr>
            ))}
            <tr className="total-row">
              <td><strong>Total de Receitas</strong></td>
              <td className="valor-positivo"><strong>{formatarMoeda(totalReceitas)}</strong></td>
            </tr>
          </tbody>
        </table>
      </div>
      
      {/* Tabela de Despesas */}
      <div className="dre-section">
        <h2 className="dre-section-title dre-despesas">Despesas</h2>
        <table>
          <thead>
            <tr>
              <th>Categoria</th>
              <th>Valor</th>
            </tr>
          </thead>
          <tbody>
            {dreData.despesas.map((item, index) => (
              <tr key={index}>
                <td>{item.categoria}</td>
                <td className="valor-negativo">{formatarMoeda(item.valor)}</td>
              </tr>
            ))}
            <tr className="total-row">
              <td><strong>Total de Despesas</strong></td>
              <td className="valor-negativo"><strong>{formatarMoeda(totalDespesas)}</strong></td>
            </tr>
          </tbody>
        </table>
      </div>
      
      {/* Resultado Final */}
      <div className="dre-resultado">
        <h2 className="dre-resultado-titulo">Resultado Final</h2>
        <div className={`dre-valor-final ${isLucro ? 'dre-lucro' : 'dre-prejuizo'}`}>
          <p className="dre-resultado-label">
            {isLucro ? 'Lucro' : 'Prejuízo'}: <span>{formatarMoeda(Math.abs(dreData.lucro_prejuizo))}</span>
          </p>
        </div>
      </div>
    </div>
  );
} 