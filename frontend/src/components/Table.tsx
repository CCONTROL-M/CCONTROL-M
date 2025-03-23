import React from 'react';
import LoadingOverlay from './LoadingOverlay';

export interface TableColumn {
  header: string;
  accessor: string;
  render?: (item: any) => React.ReactNode;
}

interface TableProps {
  columns: TableColumn[];
  data: any[];
  emptyMessage?: string;
  loading?: boolean;
}

/**
 * Componente reutilizável para renderizar tabelas com colunas dinâmicas
 * 
 * @param columns - Array de definições de colunas com header, accessor e função render opcional
 * @param data - Array de dados a serem exibidos na tabela
 * @param emptyMessage - Mensagem a ser exibida quando não houver dados
 * @param loading - Indica se os dados estão carregando
 */
const Table: React.FC<TableProps> = ({
  columns,
  data,
  emptyMessage = "Nenhum item encontrado.",
  loading = false
}) => {
  // Renderiza o valor da célula com base no accessor e função render opcional
  const renderCell = (item: any, column: TableColumn) => {
    // Se a coluna tiver uma função render, usa ela
    if (column.render) {
      return column.render(item);
    }
    
    // Extrai o valor usando o accessor
    // Suporta acessos aninhados como "usuario.nome"
    const accessorParts = column.accessor.split('.');
    let value = item;
    
    for (const part of accessorParts) {
      if (value === null || value === undefined) return '';
      value = value[part];
    }
    
    return value;
  };

  // Se não houver dados e não estiver carregando, exibe mensagem vazia
  if (!loading && (!data || data.length === 0)) {
    return <p className="placeholder-text">{emptyMessage}</p>;
  }

  return (
    <div className="table-container">
      <LoadingOverlay visible={loading} />
      
      <table>
        <thead>
          <tr>
            {columns.map((column, index) => (
              <th key={index}>{column.header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((item, rowIndex) => (
            <tr key={rowIndex}>
              {columns.map((column, colIndex) => (
                <td key={`${rowIndex}-${colIndex}`}>
                  {renderCell(item, column)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Table; 