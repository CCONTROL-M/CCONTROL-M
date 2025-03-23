"""Schema para validação de Contas a Receber."""
import uuid
from enum import Enum
from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field, validator, condecimal

from app.schemas.base import BaseSchema


class StatusContaReceber(str, Enum):
    """Status possíveis para uma conta a receber."""
    pendente = "pendente"
    recebido = "recebido"
    parcial = "parcial"
    cancelado = "cancelado"
    atrasado = "atrasado"


class ContaReceberBase(BaseModel):
    """Base para schemas de conta a receber."""
    descricao: str = Field(..., min_length=3, max_length=255)
    valor: condecimal(gt=0, decimal_places=2) = Field(..., description="Valor da conta a receber")
    data_emissao: date = Field(..., description="Data de emissão da conta")
    data_vencimento: date = Field(..., description="Data de vencimento da conta")
    observacoes: Optional[str] = Field(None, max_length=1000)
    
    @validator("data_vencimento")
    def validar_data_vencimento(cls, v, values):
        if "data_emissao" in values and v < values["data_emissao"]:
            raise ValueError("Data de vencimento não pode ser anterior à data de emissão")
        return v


class ContaReceberCreate(ContaReceberBase):
    """Schema para criação de conta a receber."""
    id_empresa: uuid.UUID = Field(..., description="ID da empresa")
    id_cliente: Optional[uuid.UUID] = Field(None, description="ID do cliente, se houver")
    id_venda: Optional[uuid.UUID] = Field(None, description="ID da venda associada, se houver")


class ContaReceberUpdate(BaseModel):
    """Schema para atualização de conta a receber."""
    descricao: Optional[str] = Field(None, min_length=3, max_length=255)
    valor: Optional[condecimal(gt=0, decimal_places=2)] = None
    data_vencimento: Optional[date] = None
    observacoes: Optional[str] = Field(None, max_length=1000)
    status: Optional[StatusContaReceber] = None
    
    @validator("data_vencimento")
    def validar_data_vencimento(cls, v, values, **kwargs):
        # Aqui precisaria validar com a data de emissão existente no banco
        # Como é difícil acessar o contexto completo, essa validação será feita no service
        return v


class ContaReceberRecebimento(BaseModel):
    """Schema para registrar recebimento de conta."""
    data_recebimento: date = Field(..., description="Data do recebimento")
    valor_recebido: condecimal(gt=0, decimal_places=2) = Field(..., description="Valor recebido")
    observacoes: Optional[str] = Field(None, max_length=1000)


class ContaReceber(ContaReceberBase, BaseSchema):
    """Schema para resposta de conta a receber."""
    id_conta_receber: uuid.UUID
    id_empresa: uuid.UUID
    id_cliente: Optional[uuid.UUID] = None
    id_lancamento: Optional[uuid.UUID] = None
    id_venda: Optional[uuid.UUID] = None
    data_recebimento: Optional[date] = None
    status: StatusContaReceber
    
    class Config:
        from_attributes = True


# Criar alias para compatibilidade com código existente
class ContaReceberResponse(ContaReceber):
    """
    Alias para ContaReceber.
    Mantido por motivos de compatibilidade com código existente.
    """
    pass


class ContaReceberList(BaseModel):
    """Lista paginada de contas a receber."""
    items: List[ContaReceber]
    total: int
    page: int
    size: int
    pages: int 