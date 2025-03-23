"""Repositório para gerenciamento de permissões."""
from uuid import UUID
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permissao import Permissao
from app.schemas.permissao import PermissaoCreate, PermissaoUpdate
from app.repositories.base_repository import BaseRepository


class PermissaoRepository(BaseRepository[Permissao, PermissaoCreate, PermissaoUpdate]):
    """Repositório para operações com permissões."""

    def __init__(self, session: AsyncSession):
        """Inicializa o repositório com a sessão do banco de dados."""
        super().__init__(Permissao, session)

    async def get_by_id(self, id: UUID, tenant_id: UUID) -> Optional[Permissao]:
        """
        Buscar permissão por ID.
        
        Args:
            id: ID da permissão
            tenant_id: ID da empresa
            
        Returns:
            Permissão encontrada ou None
        """
        query = select(self.model).where(
            and_(
                self.model.id_permissao == id,
                self.model.id_empresa == tenant_id
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: UUID, tenant_id: UUID) -> List[Permissao]:
        """
        Buscar todas as permissões de um usuário.
        
        Args:
            user_id: ID do usuário
            tenant_id: ID da empresa
            
        Returns:
            Lista de permissões do usuário
        """
        query = select(self.model).where(
            and_(
                self.model.id_usuario == user_id,
                self.model.id_empresa == tenant_id
            )
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_user_and_resource(
        self, 
        user_id: UUID, 
        recurso: str, 
        tenant_id: UUID
    ) -> Optional[Permissao]:
        """
        Buscar permissão específica de um usuário para um recurso.
        
        Args:
            user_id: ID do usuário
            recurso: Nome do recurso
            tenant_id: ID da empresa
            
        Returns:
            Permissão encontrada ou None
        """
        query = select(self.model).where(
            and_(
                self.model.id_usuario == user_id,
                self.model.recurso == recurso,
                self.model.id_empresa == tenant_id
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, tenant_id: UUID) -> List[Permissao]:
        """
        Buscar todas as permissões de uma empresa.
        
        Args:
            tenant_id: ID da empresa
            
        Returns:
            Lista de permissões
        """
        query = select(self.model).where(self.model.id_empresa == tenant_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def check_user_permission(
        self, 
        user_id: UUID, 
        recurso: str, 
        acao: str, 
        tenant_id: UUID
    ) -> bool:
        """
        Verificar se um usuário tem permissão para realizar uma ação em um recurso.
        
        Args:
            user_id: ID do usuário
            recurso: Nome do recurso
            acao: Nome da ação
            tenant_id: ID da empresa
            
        Returns:
            True se o usuário tem permissão, False caso contrário
        """
        permissao = await self.get_by_user_and_resource(user_id, recurso, tenant_id)
        if not permissao:
            return False
        
        return acao in permissao.acoes

    async def get_multi(
        self,
        tenant_id: UUID,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[UUID] = None,
        recurso: Optional[str] = None,
        busca: Optional[str] = None
    ) -> Tuple[List[Permissao], int]:
        """
        Buscar múltiplas permissões com filtros.
        
        Args:
            tenant_id: ID da empresa
            skip: Número de registros para pular
            limit: Número máximo de registros
            user_id: Filtrar por usuário
            recurso: Filtrar por recurso
            busca: Termo para busca
            
        Returns:
            Tupla com lista de permissões e contagem total
        """
        filters = [self.model.id_empresa == tenant_id]
        
        if user_id:
            filters.append(self.model.id_usuario == user_id)
        
        if recurso:
            filters.append(self.model.recurso == recurso)
        
        if busca:
            filters.append(
                or_(
                    self.model.recurso.ilike(f"%{busca}%"),
                    self.model.descricao.ilike(f"%{busca}%")
                )
            )
        
        # Query para contagem total
        count_query = select(self.model).where(and_(*filters))
        total = len((await self.session.execute(count_query)).scalars().all())
        
        # Query para buscar registros com paginação
        query = (
            select(self.model)
            .where(and_(*filters))
            .offset(skip)
            .limit(limit)
        )
        
        result = await self.session.execute(query)
        items = list(result.scalars().all())
        
        return items, total 