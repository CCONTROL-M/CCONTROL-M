import React, { useEffect, useState } from 'react';
import { Categoria } from "../types";
import { listarCategorias } from "../services/categoriaService";
import { listarCategoriasMock } from "../services/categoriaServiceMock";
import { useMock } from '../utils/mock';
import Table, { TableColumn } from "../components/Table";
import DataStateHandler from "../components/DataStateHandler";

export default function Categorias() {
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Definição das colunas da tabela
  const colunas: TableColumn[] = [
    {
      header: "Nome",
      accessor: "nome"
    }
  ];

  useEffect(() => {
    fetchCategorias();
  }, []);

  const fetchCategorias = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Usa o utilitário useMock() para determinar se deve usar mock ou dados reais
      const data = useMock() 
        ? await listarCategoriasMock()
        : await listarCategorias();
      
      setCategorias(data);
    } catch (err) {
      console.error('Erro ao carregar categorias:', err);
      setError('Não foi possível carregar as categorias. Tente novamente mais tarde.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="page-title">Categorias</h1>
      
      <DataStateHandler
        loading={loading}
        error={error}
        dataLength={categorias.length}
        onRetry={fetchCategorias}
        emptyMessage="Nenhuma categoria encontrada."
      >
        <Table
          columns={colunas}
          data={categorias}
          emptyMessage="Nenhuma categoria encontrada."
        />
      </DataStateHandler>
    </div>
  );
} 