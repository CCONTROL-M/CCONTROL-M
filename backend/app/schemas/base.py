"""Classes base para schemas do sistema CCONTROL-M."""
from datetime import datetime
from typing import Optional, TypeVar, Generic, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator
from enum import Enum

# Definição de tipo genérico para schemas
T = TypeVar('T')


class BaseSchema(BaseModel):
    """Schema base para todos os modelos Pydantic."""
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True
    )


class TimestampMixin(BaseModel):
    """Mixin para timestamps em schemas."""
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class FilterParams(BaseModel):
    """Parâmetros padrão para filtragem de listas."""
    
    filter: Optional[str] = None
    order_by: Optional[str] = None
    order_direction: Optional[str] = Field(None, pattern="^(asc|desc)$")
    page: Optional[int] = 1
    items_per_page: Optional[int] = 20


class ResponseBase(BaseSchema, Generic[T]):
    """Schema base para respostas padrão."""
    
    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None


class PaginatedResponseSchema(ResponseBase[List[T]], Generic[T]):
    """Schema para resposta paginada."""
    
    total_items: int = 0
    current_page: int = 1
    items_per_page: int = 20
    total_pages: int = 0


class ListResponseSchema(ResponseBase[List[T]], Generic[T]):
    """Schema para resposta de listagem simples (sem paginação)."""
    
    count: int = 0 