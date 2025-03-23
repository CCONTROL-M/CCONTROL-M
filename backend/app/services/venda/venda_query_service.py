"""Serviço especializado para consultas e listagens de vendas."""
from uuid import UUID
from typing import Optional, Dict, Any, List, Tuple
from decimal import Decimal
from datetime import datetime, date

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.venda_repository import VendaRepository
from app.schemas.venda import (
    Venda,
    StatusVenda,
    VendaList
)
from app.schemas.pagination import PaginatedResponse
from app.services.auditoria_service import AuditoriaService


class VendaQueryService:
    """Serviço especializado para consultas e listagens de vendas."""

    def __init__(
        self,
        session: AsyncSession,
        auditoria_service: AuditoriaService
    ):
        """Inicializa o serviço com a sessão do banco de dados."""
        self.repository = VendaRepository(session)
        self.auditoria_service = auditoria_service

    async def get_venda(self, id_venda: UUID, id_empresa: UUID) -> Venda:
        """
        Obter venda pelo ID.
        
        Args:
            id_venda: ID da venda
            id_empresa: ID da empresa para validação de acesso
            
        Returns:
            Venda encontrada
            
        Raises:
            HTTPException: Se a venda não for encontrada ou não pertencer à empresa
        """
        venda = await self.repository.get_by_id(id_venda)
        
        if not venda or venda.id_empresa != id_empresa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Venda não encontrada"
            )
            
        return venda
        
    async def listar_vendas(
        self,
        id_empresa: UUID,
        skip: int = 0,
        limit: int = 100,
        cliente: Optional[str] = None,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        status: Optional[StatusVenda] = None,
        produto: Optional[str] = None,
        forma_pagamento: Optional[str] = None,
        valor_min: Optional[float] = None,
        valor_max: Optional[float] = None
    ) -> Tuple[List[Venda], int]:
        """
        Listar vendas com filtros opcionais.
        
        Args:
            id_empresa: ID da empresa
            skip: Número de registros para pular
            limit: Limite de registros por página
            cliente: Filtro por nome/documento do cliente
            data_inicio: Filtro por data inicial
            data_fim: Filtro por data final
            status: Filtro por status da venda
            produto: Filtro por nome/código do produto
            forma_pagamento: Filtro por forma de pagamento
            valor_min: Filtro por valor mínimo
            valor_max: Filtro por valor máximo
            
        Returns:
            Tupla com lista de vendas e contagem total
        """
        # Construir filtros
        filtros = {
            "id_empresa": id_empresa
        }
        
        if cliente:
            filtros["cliente"] = cliente
            
        if data_inicio:
            filtros["data_inicio"] = data_inicio
            
        if data_fim:
            filtros["data_fim"] = data_fim
            
        if status:
            filtros["status"] = status
            
        if produto:
            filtros["produto"] = produto
            
        if forma_pagamento:
            filtros["forma_pagamento"] = forma_pagamento
            
        if valor_min is not None:
            filtros["valor_min"] = Decimal(str(valor_min))
            
        if valor_max is not None:
            filtros["valor_max"] = Decimal(str(valor_max))
            
        # Executar consulta
        vendas, total = await self.repository.listar_com_filtros(
            skip=skip,
            limit=limit,
            filtros=filtros
        )
        
        return vendas, total
        
    async def get_multi(
        self,
        empresa_id: UUID,
        skip: int = 0,
        limit: int = 100,
        id_cliente: Optional[UUID] = None,
        status: Optional[str] = None,
        tipo: Optional[str] = None,
        data_inicial: Optional[date] = None,
        data_final: Optional[date] = None,
        busca: Optional[str] = None
    ) -> PaginatedResponse[Venda]:
        """
        Listar vendas com paginação e filtros.
        
        Args:
            empresa_id: ID da empresa
            skip: Número de registros para pular
            limit: Limite de registros por página
            id_cliente: Filtro por ID do cliente
            status: Filtro por status
            tipo: Filtro por tipo de venda
            data_inicial: Filtro por data inicial
            data_final: Filtro por data final
            busca: Texto para busca geral
            
        Returns:
            Resposta paginada com vendas
        """
        # Construir filtros para paginação
        filtros = {
            "empresa_id": empresa_id
        }
        
        if id_cliente:
            filtros["id_cliente"] = id_cliente
            
        if status:
            filtros["status"] = status
            
        if tipo:
            filtros["tipo"] = tipo
            
        if data_inicial:
            filtros["data_inicial"] = data_inicial
            
        if data_final:
            filtros["data_final"] = data_final
            
        if busca:
            filtros["busca"] = busca
            
        # Executar consulta paginada
        vendas, total = await self.repository.get_multi_paginado(
            skip=skip,
            limit=limit,
            filtros=filtros
        )
        
        # Montar resposta paginada
        return PaginatedResponse(
            items=vendas,
            total=total,
            page=skip // limit + 1 if limit > 0 else 1,
            size=limit
        ) 