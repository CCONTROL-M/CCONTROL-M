import React, { useEffect, useState } from 'react';
import { ContaBancaria } from "../types";
import { listarContasBancarias } from "../services/contaBancariaService";
import { listarContasBancariasMock } from "../services/contaBancariaServiceMock";
import { useMock, setUseMock } from '../utils/mock';
import { formatarMoeda } from "../utils/formatters";
import DataStateHandler from '../components/DataStateHandler';
import Table, { TableColumn } from '../components/Table';

/**
 * Página de gerenciamento de contas bancárias - versão simplificada
 */
export default function ContasBancarias() {
  // Ativa o modo mock assim que o componente for renderizado
  useEffect(() => {
    // Ativar o modo mock para garantir que a aplicação funcione sem backend
    setUseMock(true);
    console.log("🔧 Modo mock foi ativado forcadamente na página de Contas Bancárias");
  }, []);

  // Estados
  const [contas, setContas] = useState<ContaBancaria[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Definição das colunas da tabela
  const colunas: TableColumn[] = [
    {
      header: "Nome",
      accessor: "nome"
    },
    {
      header: "Banco",
      accessor: "banco"
    },
    {
      header: "Tipo",
      accessor: "tipo"
    },
    {
      header: "Agência",
      accessor: "agencia"
    },
    {
      header: "Número",
      accessor: "numero"
    },
    {
      header: "Saldo Inicial",
      accessor: "saldo_inicial",
      render: (conta: ContaBancaria) => formatarMoeda(conta.saldo_inicial)
    }
  ];

  // Efeito para carregar dados
  useEffect(() => {
    fetchData();
  }, []);

  // Buscar dados das contas bancárias
  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Como já estamos forçando o mock no useEffect inicial, não precisamos
      // desta linha:
      // if (process.env.NODE_ENV === 'development') {
      //   localStorage.setItem('modoMockAtivo', 'true');
      // }
      
      // Usamos diretamente os dados mock para simplificar
      const data = await listarContasBancariasMock();
      setContas(data);
      
      // No caso de algum problema, isso poderia ser uma alternativa:
      // const data = useMock() 
      //   ? await listarContasBancariasMock() 
      //   : await listarContasBancarias();
      // setContas(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar contas bancárias';
      setError(errorMessage);
      console.error("Erro ao carregar contas bancárias:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-content">
      <h1 className="page-title">Contas Bancárias</h1>
      
      <DataStateHandler
        loading={loading}
        error={error}
        dataLength={contas.length}
        onRetry={fetchData}
        emptyMessage="Nenhuma conta bancária encontrada."
      >
        <Table
          columns={colunas}
          data={contas}
          emptyMessage="Nenhuma conta bancária encontrada."
        />
      </DataStateHandler>
    </div>
  );
} 