"""Schema para validação e serialização de categorias no sistema CCONTROL-M."""
from uuid import UUID
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from .pagination import PaginatedResponse


class CategoriaBase(BaseModel):
    """Schema base para categorias."""
    nome: str
    tipo: str
    descricao: Optional[str] = None
    cor: Optional[str] = None


class CategoriaCreate(CategoriaBase):
    """Schema para criação de categorias."""
    id_empresa: UUID
    subcategorias: Optional[List[Dict[str, Any]]] = None


class CategoriaUpdate(BaseModel):
    """Schema para atualização parcial de categorias."""
    nome: Optional[str] = None
    tipo: Optional[str] = None
    descricao: Optional[str] = None
    cor: Optional[str] = None
    ativo: Optional[bool] = None
    subcategorias: Optional[List[Dict[str, Any]]] = None


class CategoriaInDB(CategoriaBase):
    """Schema para representação de categorias no banco de dados."""
    id_categoria: UUID
    id_empresa: UUID
    ativo: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    subcategorias: Optional[List[Dict[str, Any]]] = None

    class Config:
        from_attributes = True


class Categoria(CategoriaInDB):
    """Schema para representação de categorias nas respostas da API."""
    
    class Config:
        from_attributes = True


class CategoriaList(PaginatedResponse):
    """Schema para listagem paginada de categorias."""
    items: List[Categoria]


# Resolver referência circular
Categoria.update_forward_refs() 