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