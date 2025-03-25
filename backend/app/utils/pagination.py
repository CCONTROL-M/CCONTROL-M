"""Utilitários para paginação na API."""
from typing import Generic, TypeVar, List, Dict, Any, Sequence, Optional
from pydantic import BaseModel, Field
from fastapi import Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from math import ceil

T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Resposta paginada da API."""
    items: List[T] = Field(..., description="Lista de itens")
    total: int = Field(..., description="Total de itens")
    page: int = Field(..., description="Página atual")
    page_size: int = Field(..., description="Itens por página")
    pages: int = Field(..., description="Total de páginas")
    
    @property
    def has_previous(self) -> bool:
        """Verifica se há página anterior."""
        return self.page > 1

    @property
    def has_next(self) -> bool:
        """Verifica se há próxima página."""
        return self.page < self.pages


async def paginate(
    query,
    page: int = Query(1, ge=1, description="Página atual"),
    page_size: int = Query(10, ge=1, le=100, description="Itens por página"),
    session: AsyncSession = None,
) -> Dict[str, Any]:
    """
    Pagina uma consulta SQLAlchemy.
    
    Args:
        query: Consulta SQLAlchemy para paginar
        page: Número da página (a partir de 1)
        page_size: Itens por página
        session: Sessão assíncrona do SQLAlchemy
        
    Returns:
        Dicionário com items, total, page, page_size e pages
    """
    # Calcular offset
    offset = (page - 1) * page_size
    
    # Obter contagem total
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await session.execute(count_query)
    total = count_result.scalar() or 0
    
    # Aplicar paginação
    result = await session.execute(query.offset(offset).limit(page_size))
    items = result.scalars().all()
    
    # Calcular total de páginas
    pages = ceil(total / page_size) if total > 0 else 1
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages
    }


def paginate_list(
    items: Sequence[Any],
    page: int = 1,
    page_size: int = 10
) -> Dict[str, Any]:
    """
    Pagina uma lista Python.
    
    Args:
        items: Lista a ser paginada
        page: Número da página (a partir de 1)
        page_size: Itens por página
        
    Returns:
        Dicionário com items, total, page, page_size e pages
    """
    # Validar parâmetros
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 10
    
    # Calcular total
    total = len(items)
    
    # Calcular offset e limit
    offset = (page - 1) * page_size
    end = offset + page_size
    
    # Aplicar paginação
    page_items = items[offset:end]
    
    # Calcular total de páginas
    pages = ceil(total / page_size) if total > 0 else 1
    
    return {
        "items": page_items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages
    }


def paginate(items: List[Any], total: int, page: int, page_size: int) -> dict:
    """
    Cria uma resposta paginada a partir de uma lista de itens.
    
    Args:
        items: Lista de itens para paginar
        total: Total de itens (sem paginação)
        page: Página atual (começando de 1)
        page_size: Tamanho da página
    
    Returns:
        Dicionário com os itens paginados e metadados
    """
    # Cálculo do total de páginas
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    
    # Ajuste da página atual se estiver fora dos limites
    page = max(1, min(page, pages))
    
    # Cálculo dos índices iniciais e finais para a página atual
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, total)
    
    # Se estamos usando slice direto
    if len(items) > end_idx:
        page_items = items[start_idx:end_idx]
    else:
        # Se os itens já vieram paginados do banco de dados
        page_items = items
    
    return {
        "items": page_items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages
    } 