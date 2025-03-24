import React from 'react';
import LoadingOverlay from './LoadingOverlay';

export interface TableColumn {
  header: string;
  accessor: string;
  render?: (item: any, index?: number) => React.ReactNode;
}

interface TableProps {
  columns: TableColumn[];
  data: any[];
  emptyMessage?: string;
  loading?: boolean;
  onRowClick?: (item: any) => void;
}

/**
 * Componente reutilizável para renderizar tabelas com colunas dinâmicas
 * 
 * @param columns - Array de definições de colunas com header, accessor e função render opcional
 * @param data - Array de dados a serem exibidos na tabela
 * @param emptyMessage - Mensagem a ser exibida quando não houver dados
 * @param loading - Indica se os dados estão carregando
 * @param onRowClick - Função opcional para lidar com cliques em linhas da tabela
 */
const Table: React.FC<TableProps> = ({
  columns,
  data,
  emptyMessage = "Nenhum item encontrado.",
  loading = false,
  onRowClick
}) => {
  // Função para extrair valor com base no accessor
  const getValue = (item: any, accessor: string) => {
    // Suporta acessos aninhados como "usuario.nome"
    const accessorParts = accessor.split('.');
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
          {data.length > 0 ? (
            data.map((item, rowIndex) => (
              <tr 
                key={rowIndex} 
                onClick={() => onRowClick && onRowClick(item)}
                className={onRowClick ? 'clickable-row' : ''}
              >
                {columns.map((column, colIndex) => (
                  <td key={`${rowIndex}-${colIndex}`}>
                    {column.render 
                      ? column.render(item, rowIndex) 
                      : getValue(item, column.accessor)}
                  </td>
                ))}
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan={columns.length} className="empty-message">
                {emptyMessage}
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};

export default Table; 