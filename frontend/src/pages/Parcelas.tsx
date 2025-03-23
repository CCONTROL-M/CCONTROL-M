import { useEffect, useState } from "react";
import { listarParcelas } from "../services/parcelaService";
import { Parcela } from "../types";
import { formatarData, formatarMoeda } from "../utils/formatters";
import Table, { TableColumn } from "../components/Table";
import DataStateHandler from "../components/DataStateHandler";

// Estendendo a interface para adicionar campo numero
interface ParcelaExibicao extends Parcela {
  numero: number;
}

export default function Parcelas() {
  const [parcelas, setParcelas] = useState<ParcelaExibicao[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Definição das colunas da tabela
  const columns: TableColumn[] = [
    {
      header: "Venda",
      accessor: "id_venda",
      render: (item: ParcelaExibicao) => item.id_venda.length > 8 ? `${item.id_venda.slice(0, 8)}...` : item.id_venda,
    },
    {
      header: "Nº Parcela",
      accessor: "numero",
    },
    {
      header: "Valor",
      accessor: "valor",
      render: (item: ParcelaExibicao) => formatarMoeda(item.valor),
    },
    {
      header: "Vencimento",
      accessor: "data_vencimento",
      render: (item: ParcelaExibicao) => formatarData(item.data_vencimento),
    },
    {
      header: "Status",
      accessor: "status",
    },
  ];

  useEffect(() => {
    fetchParcelas();
  }, []);

  async function fetchParcelas() {
    setLoading(true);
    setError(null);
    try {
      const response = await listarParcelas();
      
      // Adicionar o número da parcela para exibição
      // Agrupamos por venda e contamos a posição de cada parcela
      const vendasMap: Record<string, ParcelaExibicao[]> = {};
      
      // Agrupar parcelas por venda
      response.forEach(parcela => {
        if (!vendasMap[parcela.id_venda]) {
          vendasMap[parcela.id_venda] = [];
        }
        vendasMap[parcela.id_venda].push({
          ...parcela,
          numero: 0 // Valor temporário
        });
      });
      
      // Ordenar por data de vencimento e atribuir números
      const parcelasProcessadas: ParcelaExibicao[] = [];
      
      Object.values(vendasMap).forEach(vendaParcelas => {
        // Ordenar parcelas por data de vencimento
        vendaParcelas.sort((a, b) => 
          new Date(a.data_vencimento).getTime() - new Date(b.data_vencimento).getTime()
        );
        
        // Atribuir número sequencial
        vendaParcelas.forEach((parcela, index) => {
          parcela.numero = index + 1;
          parcelasProcessadas.push(parcela);
        });
      });
      
      setParcelas(parcelasProcessadas);
    } catch (err) {
      console.error("Erro ao carregar parcelas:", err);
      setError("Erro ao carregar as parcelas. Tente novamente mais tarde.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-content">
      <h1 className="page-title">Parcelas de Vendas</h1>
      
      <DataStateHandler
        loading={loading}
        error={error}
        dataLength={parcelas.length}
        onRetry={fetchParcelas}
        emptyMessage="Nenhuma parcela encontrada"
      >
        <Table 
          data={parcelas} 
          columns={columns}
        />
      </DataStateHandler>
    </div>
  );
} 