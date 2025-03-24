import React from 'react';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  totalItems?: number;
  itemsPerPage?: number;
}

/**
 * Componente de paginação reutilizável
 */
const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  onPageChange,
  totalItems,
  itemsPerPage
}) => {
  // Função para criar o array de páginas a serem exibidas
  const getPageNumbers = () => {
    // Mostrar no máximo 5 páginas de cada vez
    const maxPagesToShow = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxPagesToShow / 2));
    let endPage = startPage + maxPagesToShow - 1;
    
    if (endPage > totalPages) {
      endPage = totalPages;
      startPage = Math.max(1, endPage - maxPagesToShow + 1);
    }
    
    return Array.from({ length: endPage - startPage + 1 }, (_, i) => startPage + i);
  };
  
  // Se não houver páginas, não mostrar a paginação
  if (totalPages <= 1) return null;
  
  return (
    <div className="pagination">
      <div className="pagination-info">
        {totalItems !== undefined && itemsPerPage !== undefined && (
          <span>
            Exibindo {Math.min(itemsPerPage, totalItems - (currentPage - 1) * itemsPerPage)} 
            de {totalItems} itens
          </span>
        )}
      </div>
      
      <div className="pagination-controls">
        {/* Botão para primeira página */}
        <button 
          onClick={() => onPageChange(1)} 
          disabled={currentPage === 1}
          className="pagination-button"
          aria-label="Primeira página"
        >
          &laquo;
        </button>
        
        {/* Botão para página anterior */}
        <button 
          onClick={() => onPageChange(currentPage - 1)} 
          disabled={currentPage === 1}
          className="pagination-button"
          aria-label="Página anterior"
        >
          &lsaquo;
        </button>
        
        {/* Números das páginas */}
        {getPageNumbers().map(pageNumber => (
          <button
            key={pageNumber}
            onClick={() => onPageChange(pageNumber)}
            className={`pagination-button ${pageNumber === currentPage ? 'active' : ''}`}
            aria-label={`Página ${pageNumber}`}
            aria-current={pageNumber === currentPage ? 'page' : undefined}
          >
            {pageNumber}
          </button>
        ))}
        
        {/* Botão para próxima página */}
        <button 
          onClick={() => onPageChange(currentPage + 1)} 
          disabled={currentPage === totalPages}
          className="pagination-button"
          aria-label="Próxima página"
        >
          &rsaquo;
        </button>
        
        {/* Botão para última página */}
        <button 
          onClick={() => onPageChange(totalPages)} 
          disabled={currentPage === totalPages}
          className="pagination-button"
          aria-label="Última página"
        >
          &raquo;
        </button>
      </div>
    </div>
  );
};

export default Pagination; 