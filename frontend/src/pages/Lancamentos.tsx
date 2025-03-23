import { useEffect, useState } from "react";
import { listarLancamentos } from "../services/lancamentoService";
import { Lancamento } from "../types";
import { formatarData, formatarMoeda } from "../utils/formatters";
import Table, { TableColumn } from "../components/Table";
import DataStateHandler from "../components/DataStateHandler";

// Estendendo a interface para adicionar campo descricao e tipo
interface LancamentoExibicao extends Lancamento {
  descricao: string;
  tipo: string;
}

// Mapeamento de categorias para tipos (simulado)
const categoriaParaTipo: Record<string, string> = {
  "1": "Despesa",
  "2": "Receita",
  "3": "Despesa",
  "4": "Receita",
  "5": "Despesa",
  // Adicione mais conforme necessário
};

export default function Lancamentos() {
  const [lancamentos, setLancamentos] = useState<LancamentoExibicao[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Definição das colunas da tabela
  const columns: TableColumn[] = [
    {
      header: "Data",
      accessor: "data",
      render: (item: LancamentoExibicao) => formatarData(item.data),
    },
    {
      header: "Descrição",
      accessor: "descricao",
    },
    {
      header: "Tipo",
      accessor: "tipo",
    },
    {
      header: "Valor",
      accessor: "valor",
      render: (item: LancamentoExibicao) => formatarMoeda(item.valor),
    },
    {
      header: "Status",
      accessor: "status",
    },
  ];

  useEffect(() => {
    fetchLancamentos();
  }, []);

  async function fetchLancamentos() {
    setLoading(true);
    setError(null);
    try {
      // Usar o serviço que já tem a lógica de mock implementada
      const response = await listarLancamentos();
      
      // Mapear os dados para incluir descrição e tipo com base na categoria
      const lancamentosComDescricao = response.map(lancamento => {
        return {
          ...lancamento,
          descricao: lancamento.observacao || `Lançamento #${lancamento.id_lancamento}`,
          tipo: categoriaParaTipo[lancamento.id_categoria || ""] || "Outro"
        } as LancamentoExibicao;
      });
      
      setLancamentos(lancamentosComDescricao);
    } catch (err) {
      console.error("Erro ao carregar lançamentos:", err);
      setError("Erro ao carregar os lançamentos. Tente novamente mais tarde.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-content">
      <h1 className="page-title">Lançamentos Financeiros</h1>
      
      <DataStateHandler
        loading={loading}
        error={error}
        dataLength={lancamentos.length}
        onRetry={fetchLancamentos}
        emptyMessage="Nenhum lançamento encontrado"
      >
        <Table 
          data={lancamentos} 
          columns={columns}
        />
      </DataStateHandler>
    </div>
  );
} 