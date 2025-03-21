"""Schemas Pydantic para Vendas no sistema CCONTROL-M."""
from datetime import date, datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, model_validator


class StatusVenda(str, Enum):
    """Status possíveis para vendas."""
    PENDENTE = "pendente"
    CONCLUIDA = "concluida"
    CANCELADA = "cancelada"


class ItemVenda(BaseModel):
    """Schema para representar um item de venda."""
    id_produto: UUID = Field(..., description="ID do produto")
    nome_produto: str = Field(..., description="Nome do produto")
    quantidade: float = Field(..., description="Quantidade vendida", gt=0)
    valor_unitario: float = Field(..., description="Valor unitário do produto", gt=0)
    valor_total: float = Field(..., description="Valor total do item (quantidade * valor_unitário)", gt=0)
    desconto: float = Field(0, description="Valor do desconto no item", ge=0)
    valor_liquido: float = Field(..., description="Valor líquido após desconto", gt=0)
    observacao: Optional[str] = Field(None, description="Observação sobre o item")
    
    @model_validator(mode='after')
    def validar_valores(self) -> 'ItemVenda':
        """Valida os cálculos dos valores do item."""
        # Verifica se o valor total está correto
        valor_total_calculado = self.quantidade * self.valor_unitario
        if abs(self.valor_total - valor_total_calculado) > 0.01:  # Margem de erro para arredondamento
            raise ValueError("Valor total deve ser igual a quantidade * valor unitário")
        
        # Verifica se o valor líquido está correto
        valor_liquido_calculado = self.valor_total - self.desconto
        if abs(self.valor_liquido - valor_liquido_calculado) > 0.01:  # Margem de erro para arredondamento
            raise ValueError("Valor líquido deve ser igual a valor total - desconto")
        
        # Verifica se o desconto não é maior que o valor total
        if self.desconto > self.valor_total:
            raise ValueError("Desconto não pode ser maior que o valor total")
        
        return self


class VendaBase(BaseModel):
    """Schema base com campos comuns para Vendas."""
    descricao: str = Field(..., description="Descrição da venda", min_length=3, max_length=255)
    data_venda: date = Field(..., description="Data da venda")
    valor_total: float = Field(..., description="Valor total da venda", gt=0)
    valor_desconto: float = Field(0, description="Valor do desconto", ge=0)
    valor_liquido: float = Field(..., description="Valor líquido após desconto", gt=0)
    parcelado: bool = Field(False, description="Indica se a venda foi parcelada")
    observacao: Optional[str] = Field(None, description="Observações adicionais sobre a venda", max_length=1000)
    
    @field_validator('valor_total', 'valor_liquido')
    def validar_valores_positivos(cls, v: float) -> float:
        """Valida que os valores são positivos."""
        if v <= 0:
            raise ValueError("O valor deve ser maior que zero")
        return v
    
    @field_validator('valor_desconto')
    def validar_desconto(cls, v: float) -> float:
        """Valida que o desconto é não-negativo."""
        if v < 0:
            raise ValueError("O desconto não pode ser negativo")
        return v
    
    @model_validator(mode='after')
    def validar_total_liquido(self) -> 'VendaBase':
        """Valida que o valor líquido é consistente com o valor total e desconto."""
        # Verifica se o valor líquido está correto
        valor_liquido_calculado = self.valor_total - self.valor_desconto
        if abs(self.valor_liquido - valor_liquido_calculado) > 0.01:  # Margem de erro para arredondamento
            raise ValueError("Valor líquido deve ser igual a valor total - valor desconto")
        
        # Verifica se o desconto não é maior que o valor total
        if self.valor_desconto > self.valor_total:
            raise ValueError("Desconto não pode ser maior que o valor total")
        
        return self


class VendaCreate(VendaBase):
    """Schema para criação de vendas."""
    id_empresa: UUID = Field(..., description="ID da empresa associada à venda")
    id_cliente: Optional[UUID] = Field(None, description="ID do cliente associado (opcional)")
    numero_venda: Optional[str] = Field(None, description="Número da venda (opcional)")
    total_parcelas: Optional[int] = Field(None, description="Total de parcelas (se for parcelado)")
    status: StatusVenda = Field(StatusVenda.PENDENTE, description="Status da venda")
    nota_fiscal: Optional[str] = Field(None, description="Número da nota fiscal (opcional)")
    itens_venda: List[ItemVenda] = Field(..., description="Itens da venda", min_items=1)
    
    @model_validator(mode='after')
    def validar_parcelamento(self) -> 'VendaCreate':
        """Valida as informações de parcelamento."""
        if self.parcelado and not self.total_parcelas:
            raise ValueError("Total de parcelas é obrigatório para vendas parceladas")
        
        if self.total_parcelas and self.total_parcelas <= 0:
            raise ValueError("Total de parcelas deve ser maior que zero")
            
        if not self.parcelado and self.total_parcelas:
            raise ValueError("Total de parcelas só deve ser informado para vendas parceladas")
        
        return self
    
    @model_validator(mode='after')
    def validar_valores_itens(self) -> 'VendaCreate':
        """Valida que os valores dos itens são consistentes com o valor total da venda."""
        # Calcula o total dos itens
        valor_total_itens = sum(item.valor_total for item in self.itens_venda)
        valor_desconto_itens = sum(item.desconto for item in self.itens_venda)
        valor_liquido_itens = sum(item.valor_liquido for item in self.itens_venda)
        
        # Verifica a consistência com os valores da venda
        if abs(self.valor_total - valor_total_itens) > 0.01:  # Margem de erro para arredondamento
            raise ValueError("Valor total da venda deve ser igual à soma dos valores totais dos itens")
        
        # Verifica a consistência com os valores líquidos
        if abs(self.valor_liquido - valor_liquido_itens) > 0.01:  # Margem de erro para arredondamento
            raise ValueError("Valor líquido da venda deve ser igual à soma dos valores líquidos dos itens")
        
        return self


class VendaUpdate(BaseModel):
    """Schema para atualização de vendas (todos campos opcionais)."""
    descricao: Optional[str] = Field(None, description="Descrição da venda", min_length=3, max_length=255)
    data_venda: Optional[date] = Field(None, description="Data da venda")
    id_cliente: Optional[UUID] = Field(None, description="ID do cliente associado")
    numero_venda: Optional[str] = Field(None, description="Número da venda")
    status: Optional[StatusVenda] = Field(None, description="Status da venda")
    nota_fiscal: Optional[str] = Field(None, description="Número da nota fiscal")
    observacao: Optional[str] = Field(None, description="Observações adicionais sobre a venda", max_length=1000)


class VendaInDB(VendaBase):
    """Schema para venda com campos específicos do banco de dados."""
    id_venda: UUID
    id_empresa: UUID
    id_cliente: Optional[UUID] = None
    numero_venda: Optional[str] = None
    total_parcelas: Optional[int] = None
    status: StatusVenda
    nota_fiscal: Optional[str] = None
    itens_venda: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Venda(VendaInDB):
    """Schema completo de venda para resposta da API."""
    pass


class VendaList(BaseModel):
    """Schema reduzido para listagem de vendas."""
    id_venda: UUID
    numero_venda: Optional[str]
    descricao: str
    data_venda: date
    valor_total: float
    valor_liquido: float
    status: StatusVenda
    parcelado: bool
    total_parcelas: Optional[int]
    cliente_nome: Optional[str] = None
    
    class Config:
        from_attributes = True


class VendaDetalhes(VendaInDB):
    """Schema detalhado de venda com informações relacionadas."""
    cliente_nome: Optional[str] = None
    empresa_nome: str
    itens: List[ItemVenda]
    lancamentos: List[Dict[str, Any]] = []
    
    class Config:
        from_attributes = True


class VendaTotais(BaseModel):
    """Schema para retornar totais de vendas (por status)."""
    total_pendentes: float = Field(0, description="Total de vendas pendentes")
    total_concluidas: float = Field(0, description="Total de vendas concluídas")
    total_canceladas: float = Field(0, description="Total de vendas canceladas")
    total_geral: float = Field(0, description="Total geral de vendas")
    total_itens_vendidos: int = Field(0, description="Total de itens vendidos")
    periodo_inicio: Optional[date] = Field(None, description="Data de início do período")
    periodo_fim: Optional[date] = Field(None, description="Data de fim do período") 