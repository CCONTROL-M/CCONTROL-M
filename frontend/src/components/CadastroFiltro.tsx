import React, { useState } from 'react';

interface CadastroFiltroProps {
  onBuscar: (termo: string) => void;
  onLimpar: () => void;
  totalPaginas?: number;
  paginaAtual?: number;
  onMudarPagina?: (pagina: number) => void;
  placeholder?: string;
  isLoading?: boolean;
}

/**
 * Componente reutilizável para filtros de cadastros básicos.
 * Inclui campo de busca e controles de paginação.
 */
const CadastroFiltro: React.FC<CadastroFiltroProps> = ({
  onBuscar,
  onLimpar,
  totalPaginas = 0,
  paginaAtual = 1,
  onMudarPagina,
  placeholder = "Buscar por nome ou código...",
  isLoading = false
}) => {
  const [termoBusca, setTermoBusca] = useState<string>("");

  // Função para lidar com a submissão do formulário de busca
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onBuscar(termoBusca);
  };

  // Função para limpar o filtro
  const handleLimpar = () => {
    setTermoBusca("");
    onLimpar();
  };

  // Função para avançar para a próxima página
  const handleProximaPagina = () => {
    if (onMudarPagina && paginaAtual < totalPaginas) {
      onMudarPagina(paginaAtual + 1);
    }
  };

  // Função para voltar para a página anterior
  const handlePaginaAnterior = () => {
    if (onMudarPagina && paginaAtual > 1) {
      onMudarPagina(paginaAtual - 1);
    }
  };

  return (
    <div className="filtro-container mb-4">
      <form onSubmit={handleSubmit} className="flex flex-col md:flex-row gap-2 mb-3">
        <div className="flex-grow">
          <input
            type="text"
            value={termoBusca}
            onChange={(e) => setTermoBusca(e.target.value)}
            placeholder={placeholder}
            className="input-padrao w-full"
            disabled={isLoading}
          />
        </div>
        <div className="flex gap-2">
          <button
            type="submit"
            className="btn-primary px-4"
            disabled={isLoading}
          >
            Buscar
          </button>
          <button
            type="button"
            className="btn-outline px-4"
            onClick={handleLimpar}
            disabled={isLoading}
          >
            Limpar
          </button>
        </div>
      </form>

      {onMudarPagina && totalPaginas > 0 && (
        <div className="flex justify-between items-center mt-2">
          <span className="text-sm text-gray-600">
            Página {paginaAtual} de {totalPaginas}
          </span>
          <div className="flex gap-2">
            <button
              type="button"
              className="btn-outline px-3 py-1 text-sm"
              onClick={handlePaginaAnterior}
              disabled={paginaAtual <= 1 || isLoading}
            >
              Anterior
            </button>
            <button
              type="button"
              className="btn-outline px-3 py-1 text-sm"
              onClick={handleProximaPagina}
              disabled={paginaAtual >= totalPaginas || isLoading}
            >
              Próxima
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default CadastroFiltro; 