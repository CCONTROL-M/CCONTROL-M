"""
Schemas para manipulação de categorias.
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, RootModel


class CategoriaBase(BaseModel):
    """Schema base para categorias."""
    descricao: str = Field(..., min_length=2, max_length=100, examples=["Alimentação"])
    ativo: Optional[bool] = Field(True, description="Indica se a categoria está ativa")


class CategoriaCreate(CategoriaBase):
    """Schema para criação de categorias."""
    pass


class CategoriaUpdate(BaseModel):
    """Schema para atualização de categorias."""
    descricao: Optional[str] = Field(None, min_length=2, max_length=100, examples=["Alimentação"])
    ativo: Optional[bool] = Field(None, description="Indica se a categoria está ativa")
    
    class Config:
        from_attributes = True


class CategoriaResponse(CategoriaBase):
    """Schema para resposta de categorias."""
    id_categoria: UUID
    id_empresa: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CategoriaInDB(CategoriaResponse):
    """
    Schema para representação interna da categoria no banco de dados.
    Mantido por motivos de compatibilidade com código existente.
    """
    pass


class Categoria(CategoriaResponse):
    """
    Alias para CategoriaResponse.
    Mantido por motivos de compatibilidade com código existente.
    """
    pass


class CategoriaList(RootModel):
    """Schema para listar categorias."""
    root: List[Categoria] 