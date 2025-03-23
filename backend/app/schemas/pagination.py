"""Schemas para paginação de resultados."""
from typing import Generic, List, TypeVar
from fastapi import Query, Depends
from pydantic import BaseModel

# Definir tipo genérico para os itens
T = TypeVar('T')


class PaginationParams:
    """Parâmetros de paginação para ser usado como dependência."""
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Número da página"),
        size: int = Query(20, ge=1, le=100, description="Itens por página"),
    ):
        self.page = page
        self.size = size
        self.skip = (page - 1) * size
        self.limit = size


class PaginatedResponse(BaseModel, Generic[T]):
    """Schema para resposta paginada."""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

    @classmethod
    def create(cls, items: List[T], total: int, page: int, page_size: int) -> "PaginatedResponse[T]":
        """
        Cria uma resposta paginada.
        
        Args:
            items: Lista de itens da página atual
            total: Total de itens em todas as páginas
            page: Número da página atual
            page_size: Número de itens por página
            
        Returns:
            PaginatedResponse: Resposta paginada com metadados
        """
        pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        
        return cls(
            items=items,
            total=total,
            page=page,
            size=page_size,
            pages=pages,
        ) 