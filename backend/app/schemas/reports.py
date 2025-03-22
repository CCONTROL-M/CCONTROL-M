"""
Schemas para relatórios.
"""
from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ReportType(str, Enum):
    """Tipos de relatório disponíveis."""
    PRODUTOS = "produtos"
    CENTROS_CUSTO = "centros_custo"
    CATEGORIAS = "categorias"

class ReportFormat(str, Enum):
    """Formatos de exportação disponíveis."""
    PDF = "pdf"
    EXCEL = "excel"

class ReportFilter(BaseModel):
    """Filtros para relatórios."""
    search: Optional[str] = Field(None, description="Termo de busca geral")
    categoria_id: Optional[int] = Field(None, description="ID da categoria para filtrar")
    data_inicio: Optional[datetime] = Field(None, description="Data inicial do período")
    data_fim: Optional[datetime] = Field(None, description="Data final do período")
    status: Optional[str] = Field(None, description="Status para filtrar (ex: ativo, inativo)")
    
    class Config:
        """Configurações do modelo."""
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d") if v else None
        } 