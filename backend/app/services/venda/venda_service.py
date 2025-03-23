"""Serviço principal para gerenciamento de vendas."""
from uuid import UUID
from typing import Optional, Dict, Any, List, Tuple
from decimal import Decimal
from datetime import datetime, date

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.repositories.venda_repository import VendaRepository
from app.schemas.venda import (
    VendaCreate,
    VendaUpdate,
    Venda,
    StatusVenda,
    ItemVenda,
    VendaDetalhes,
    VendaTotais
)
from app.schemas.pagination import PaginatedResponse
from app.services.auditoria_service import AuditoriaService
from app.services.venda.venda_item_service import VendaItemService
from app.services.venda.venda_status_service import VendaStatusService
from app.services.venda.venda_query_service import VendaQueryService


class VendaService:
    """
    Serviço para manipulação de vendas.
    
    Esta classe funciona como uma fachada para os serviços especializados de venda,
    delegando as operações para os serviços apropriados:
    - VendaQueryService: consultas e listagens
    - VendaItemService: gerenciamento de itens de venda
    - VendaStatusService: transições de estado (cancelar, concluir)
    """

    def __init__(
        self,
        session: AsyncSession = Depends(get_async_session),
        auditoria_service: AuditoriaService = Depends()
    ):
        """Inicializa o serviço com a sessão do banco de dados e seus subserviços."""
        self.repository = VendaRepository(session)
        self.auditoria_service = auditoria_service
        
        # Inicializar serviços especializados
        self.query_service = VendaQueryService(session, auditoria_service)
        self.item_service = VendaItemService(session, auditoria_service)
        self.status_service = VendaStatusService(session, auditoria_service)
        
    # Métodos de consulta
    
    async def get_venda(self, id_venda: UUID, id_empresa: UUID) -> Venda:
        """
        Obter venda pelo ID.
        
        Args:
            id_venda: ID da venda
            id_empresa: ID da empresa para validação de acesso
            
        Returns:
            Venda encontrada
        """
        return await self.query_service.get_venda(id_venda, id_empresa)
    
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
        return await self.query_service.listar_vendas(
            id_empresa=id_empresa,
            skip=skip,
            limit=limit,
            cliente=cliente,
            data_inicio=data_inicio,
            data_fim=data_fim,
            status=status,
            produto=produto,
            forma_pagamento=forma_pagamento,
            valor_min=valor_min,
            valor_max=valor_max
        )
    
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
        return await self.query_service.get_multi(
            empresa_id=empresa_id,
            skip=skip,
            limit=limit,
            id_cliente=id_cliente,
            status=status,
            tipo=tipo,
            data_inicial=data_inicial,
            data_final=data_final,
            busca=busca
        )
    
    # Métodos de CRUD
    
    async def criar_venda(self, venda: VendaCreate, id_usuario: UUID) -> Venda:
        """
        Criar uma nova venda.
        
        Args:
            venda: Dados da venda a ser criada
            id_usuario: ID do usuário que está criando a venda
            
        Returns:
            Venda criada
        """
        # Validações e criação da venda são delegadas ao repository
        return await self.repository.criar_venda(venda, id_usuario)
    
    async def atualizar_venda(
        self, 
        id_venda: UUID, 
        venda: VendaUpdate, 
        id_empresa: UUID, 
        id_usuario: UUID
    ) -> Venda:
        """
        Atualizar uma venda existente.
        
        Args:
            id_venda: ID da venda a ser atualizada
            venda: Dados atualizados da venda
            id_empresa: ID da empresa para validação de acesso
            id_usuario: ID do usuário que está atualizando a venda
            
        Returns:
            Venda atualizada
        """
        # Obter venda para validações de acesso
        venda_atual = await self.get_venda(id_venda, id_empresa)
        
        # Atualizar venda
        venda_atualizada = await self.repository.atualizar_venda(
            id_venda, 
            venda, 
            id_usuario
        )
        
        # Registrar auditoria
        await self.auditoria_service.registrar_acao(
            entidade="venda",
            acao="update",
            id_registro=str(id_venda),
            dados_anteriores=venda_atual.dict(),
            dados_novos=venda_atualizada.dict(),
            id_usuario=id_usuario
        )
        
        return venda_atualizada
    
    async def remover_venda(
        self, 
        id_venda: UUID, 
        id_empresa: UUID, 
        id_usuario: UUID
    ) -> Dict[str, Any]:
        """
        Remover uma venda.
        
        Args:
            id_venda: ID da venda a ser removida
            id_empresa: ID da empresa para validação de acesso
            id_usuario: ID do usuário que está removendo a venda
            
        Returns:
            Mensagem de sucesso
        """
        # Obter venda para validações de acesso
        venda = await self.get_venda(id_venda, id_empresa)
        
        # Remover venda
        result = await self.repository.remover_venda(id_venda)
        
        # Registrar auditoria
        await self.auditoria_service.registrar_acao(
            entidade="venda",
            acao="delete",
            id_registro=str(id_venda),
            dados_anteriores=venda.dict(),
            dados_novos={},
            id_usuario=id_usuario
        )
        
        return result
    
    # Métodos para transições de estado
    
    async def cancelar_venda(
        self, 
        id_venda: UUID, 
        id_empresa: UUID, 
        id_usuario: UUID, 
        motivo: str
    ) -> Venda:
        """
        Cancelar uma venda.
        
        Args:
            id_venda: ID da venda a ser cancelada
            id_empresa: ID da empresa para validação de acesso
            id_usuario: ID do usuário que está cancelando a venda
            motivo: Motivo do cancelamento
            
        Returns:
            Venda cancelada
        """
        return await self.status_service.cancelar_venda(
            id_venda=id_venda,
            id_empresa=id_empresa,
            id_usuario=id_usuario,
            motivo=motivo
        )
    
    async def concluir_venda(
        self, 
        id_venda: UUID, 
        id_empresa: UUID, 
        id_usuario: UUID
    ) -> Venda:
        """
        Concluir uma venda.
        
        Args:
            id_venda: ID da venda a ser concluída
            id_empresa: ID da empresa para validação de acesso
            id_usuario: ID do usuário que está concluindo a venda
            
        Returns:
            Venda concluída
        """
        return await self.status_service.concluir_venda(
            id_venda=id_venda,
            id_empresa=id_empresa,
            id_usuario=id_usuario
        )
    
    # Métodos para itens de venda
    
    async def adicionar_item_venda(
        self, 
        id_venda: UUID, 
        id_empresa: UUID, 
        item: ItemVenda
    ) -> ItemVenda:
        """
        Adicionar item a uma venda.
        
        Args:
            id_venda: ID da venda
            id_empresa: ID da empresa para validação de acesso
            item: Dados do item a ser adicionado
            
        Returns:
            Item adicionado
        """
        return await self.item_service.adicionar_item_venda(
            id_venda=id_venda,
            id_empresa=id_empresa,
            item=item
        )
    
    async def atualizar_item_venda(
        self, 
        id_venda: UUID, 
        id_item: UUID, 
        id_empresa: UUID, 
        item: ItemVenda
    ) -> ItemVenda:
        """
        Atualizar item de uma venda.
        
        Args:
            id_venda: ID da venda
            id_item: ID do item a ser atualizado
            id_empresa: ID da empresa para validação de acesso
            item: Dados atualizados do item
            
        Returns:
            Item atualizado
        """
        return await self.item_service.atualizar_item_venda(
            id_venda=id_venda,
            id_item=id_item,
            id_empresa=id_empresa,
            item=item
        )
    
    async def remover_item_venda(
        self, 
        id_venda: UUID, 
        id_item: UUID, 
        id_empresa: UUID
    ) -> Dict[str, Any]:
        """
        Remover item de uma venda.
        
        Args:
            id_venda: ID da venda
            id_item: ID do item a ser removido
            id_empresa: ID da empresa para validação de acesso
            
        Returns:
            Mensagem de sucesso
        """
        return await self.item_service.remover_item_venda(
            id_venda=id_venda,
            id_item=id_item,
            id_empresa=id_empresa
        ) 