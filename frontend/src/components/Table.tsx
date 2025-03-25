import React from 'react';
import LoadingOverlay from './LoadingOverlay';

export interface TableColumn {
  header: string;
  accessor: string;
  render?: (item: any, index?: number) => React.ReactNode;
  /**
   * Responsividade da coluna
   * - true: coluna sempre visível
   * - false: coluna nunca visível em mobile (< 768px)
   * - 'sm': coluna visível apenas em telas maiores que 576px
   * - 'md': coluna visível apenas em telas maiores que 768px
   * - 'lg': coluna visível apenas em telas maiores que 992px
   * - 'xl': coluna visível apenas em telas maiores que 1200px
   * @default true
   */
  responsive?: boolean | 'sm' | 'md' | 'lg' | 'xl';
  /**
   * Largura da coluna (em px ou %)
   * @example '150px' ou '15%'
   */
  width?: string;
  /**
   * Alinhamento do conteúdo da coluna
   */
  align?: 'left' | 'center' | 'right';
}

interface TableProps {
  columns: TableColumn[];
  data: any[];
  emptyMessage?: string;
  loading?: boolean;
  onRowClick?: (item: any) => void;
  /**
   * Largura máxima da tabela, se definido, a tabela terá scroll horizontal
   * @example '100%' ou '800px'
   */
  maxWidth?: string;
  /**
   * Define se deve aplicar regras responsivas para esconder colunas em dispositivos móveis
   * @default true
   */
  responsive?: boolean;
}

/**
 * Componente reutilizável para renderizar tabelas com colunas dinâmicas
 * Utiliza os tokens visuais padronizados do sistema
 * Suporta responsividade com ocultação de colunas em dispositivos móveis
 * 
 * @param columns - Array de definições de colunas com header, accessor e função render opcional
 * @param data - Array de dados a serem exibidos na tabela
 * @param emptyMessage - Mensagem a ser exibida quando não houver dados
 * @param loading - Indica se os dados estão carregando
 * @param onRowClick - Função opcional para lidar com cliques em linhas da tabela
 * @param maxWidth - Largura máxima da tabela
 * @param responsive - Define se deve aplicar regras responsivas
 */
const Table: React.FC<TableProps> = ({
  columns,
  data,
  emptyMessage = "Nenhum item encontrado.",
  loading = false,
  onRowClick,
  maxWidth,
  responsive = true
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

  // Determinar classe de responsividade para cada coluna
  const getColumnClassName = (columnResponsive?: boolean | 'sm' | 'md' | 'lg' | 'xl') => {
    if (!responsive) return '';
    
    if (columnResponsive === false) return 'hide-on-mobile';
    if (columnResponsive === 'sm') return 'hide-on-sm';
    if (columnResponsive === 'md') return 'hide-on-md';
    if (columnResponsive === 'lg') return 'hide-on-lg';
    if (columnResponsive === 'xl') return 'hide-on-xl';
    
    return '';
  };

  // Obter estilo de alinhamento para cada coluna
  const getColumnStyle = (column: TableColumn) => {
    const style: React.CSSProperties = {};
    
    if (column.width) {
      style.width = column.width;
    }
    
    if (column.align) {
      style.textAlign = column.align;
    }
    
    return style;
  };

  // Se não houver dados e não estiver carregando, exibe mensagem vazia
  if (!loading && (!data || data.length === 0)) {
    return (
      <div className="data-state-empty">
        <p className="placeholder-text">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="table-container" style={maxWidth ? { maxWidth } : undefined}>
      <LoadingOverlay visible={loading} />
      
      <table>
        <thead>
          <tr>
            {columns.map((column, index) => (
              <th 
                key={index} 
                className={getColumnClassName(column.responsive)}
                style={getColumnStyle(column)}
              >
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.length > 0 ? (
            data.map((item, rowIndex) => (
              <tr 
                key={rowIndex} 
                onClick={() => onRowClick && onRowClick(item)}
                className={onRowClick ? 'hoverable-row' : ''}
              >
                {columns.map((column, colIndex) => (
                  <td 
                    key={`${rowIndex}-${colIndex}`}
                    className={getColumnClassName(column.responsive)}
                    style={getColumnStyle(column)}
                  >
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