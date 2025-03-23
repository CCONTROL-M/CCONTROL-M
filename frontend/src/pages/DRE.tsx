import { useEffect, useState } from "react";
import { DREData, CategoriaValor } from "../types";
import { obterRelatorioDRE } from "../services/relatoriosService";
import { formatarMoeda } from "../utils/formatters";
import DataStateHandler from "../components/DataStateHandler";
import { setUseMock } from "../utils/mock";

export default function DRE() {
  const [dreData, setDreData] = useState<DREData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Ativa o modo mock assim que o componente for renderizado
  useEffect(() => {
    // Ativar o modo mock para garantir que a aplicação funcione sem backend
    setUseMock(true);
    console.log("🔧 Modo mock foi ativado forcadamente na página de DRE");
  }, []);

  // Efeito para carregar dados
  useEffect(() => {
    fetchData();
  }, []);

  // Buscar dados do DRE
  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await obterRelatorioDRE();
      setDreData(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar dados do DRE';
      setError(errorMessage);
      console.error("Erro ao carregar DRE:", err);
    } finally {
      setLoading(false);
    }
  };

  // Renderizar uma seção do relatório (receitas ou despesas)
  const renderizarSecao = (titulo: string, itens: CategoriaValor[], isPositivo: boolean) => (
    <div className={`dre-secao ${isPositivo ? 'dre-receitas' : 'dre-despesas'}`}>
      <h2>{titulo}</h2>
      <table>
        <thead>
          <tr>
            <th>Categoria</th>
            <th>Valor</th>
          </tr>
        </thead>
        <tbody>
          {itens.map((item, index) => (
            <tr key={index}>
              <td>{item.categoria}</td>
              <td className={isPositivo ? 'valor-positivo' : 'valor-negativo'}>
                {formatarMoeda(item.valor)}
              </td>
            </tr>
          ))}
          <tr className="total-row">
            <td>Total de {titulo}</td>
            <td>
              {formatarMoeda(itens.reduce((acc, item) => acc + item.valor, 0))}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  );

  return (
    <div className="page-content">
      <h1 className="page-title">Demonstrativo de Resultados</h1>
      
      <DataStateHandler
        loading={loading}
        error={error}
        dataLength={dreData ? 1 : 0}
        onRetry={fetchData}
        emptyMessage="Nenhum dado disponível para o DRE."
      >
        {dreData && (
          <div className="dre-container">
            {renderizarSecao("Receitas", dreData.receitas, true)}
            {renderizarSecao("Despesas", dreData.despesas, false)}
            
            <div className="dre-resultado">
              <h2>Resultado</h2>
              <p className={dreData.lucro_prejuizo >= 0 ? 'valor-positivo' : 'valor-negativo'}>
                {dreData.lucro_prejuizo >= 0 ? 'Lucro' : 'Prejuízo'}: {formatarMoeda(Math.abs(dreData.lucro_prejuizo))}
              </p>
            </div>
          </div>
        )}
      </DataStateHandler>
    </div>
  );
} 