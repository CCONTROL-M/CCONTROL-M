"""Esquemas para paginação de resultados."""
from typing import Generic, List, TypeVar, Optional, Any
from pydantic import BaseModel, Field

from app.config.settings import settings

T = TypeVar('T')


class Pagination(BaseModel):
    """Parâmetros de paginação para consultas."""
    
    page: Optional[int] = Field(1, ge=1, description="Número da página")
    page_size: Optional[int] = Field(
        settings.DEFAULT_PAGE_SIZE, 
        ge=1, 
        le=settings.MAX_PAGE_SIZE,
        description="Itens por página"
    )
    

class PaginatedResponse(BaseModel, Generic[T]):
    """Resposta paginada genérica para endpoints que retornam listas."""
    
    items: List[T]
    total: int
    page: int
    page_size: int
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
            page_size=page_size,
            pages=pages
        ) 