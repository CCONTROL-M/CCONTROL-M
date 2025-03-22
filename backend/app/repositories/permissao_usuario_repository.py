"""Repositório para gerenciamento de permissões de usuário."""
import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permissao_usuario import PermissaoUsuario
from app.schemas.permissao_usuario import PermissaoUsuarioCreate, PermissaoUsuarioUpdate
from app.repositories.base_repository import BaseRepository
from app.database import db_session


class PermissaoUsuarioRepository(BaseRepository[PermissaoUsuario, PermissaoUsuarioCreate, PermissaoUsuarioUpdate]):
    """
    Repositório para operações de banco de dados relacionadas a permissões de usuário.
    """
    
    def __init__(self):
        """Inicializa o repositório com o modelo PermissaoUsuario."""
        super().__init__(PermissaoUsuario)
        self.logger = logging.getLogger(__name__)
    
    async def get_by_user_id(self, user_id: UUID, tenant_id: Optional[UUID] = None) -> List[PermissaoUsuario]:
        """
        Recupera todas as permissões de um usuário específico.
        
        Args:
            user_id: ID do usuário
            tenant_id: ID da empresa (para controle de acesso)
            
        Returns:
            Lista de permissões do usuário
        """
        async with db_session() as session:
            await self._set_tenant_context(session, tenant_id)
            query = select(self.model).where(self.model.id_usuario == user_id)
            result = await session.execute(query)
            return list(result.scalars().all())
    
    async def get_by_user_and_resource(
        self, 
        user_id: UUID, 
        recurso: str, 
        tenant_id: Optional[UUID] = None
    ) -> Optional[PermissaoUsuario]:
        """
        Recupera a permissão de um usuário para um recurso específico.
        
        Args:
            user_id: ID do usuário
            recurso: Nome do recurso
            tenant_id: ID da empresa (para controle de acesso)
            
        Returns:
            Permissão do usuário para o recurso ou None se não existir
        """
        async with db_session() as session:
            await self._set_tenant_context(session, tenant_id)
            query = select(self.model).where(
                self.model.id_usuario == user_id,
                self.model.recurso == recurso
            )
            result = await session.execute(query)
            return result.scalar_one_or_none()
    
    async def check_user_permission(
        self, 
        user_id: UUID, 
        recurso: str, 
        acao: str, 
        tenant_id: Optional[UUID] = None
    ) -> bool:
        """
        Verifica se um usuário tem permissão para realizar uma ação em um recurso.
        
        Args:
            user_id: ID do usuário
            recurso: Nome do recurso
            acao: Nome da ação (ex: 'criar', 'editar', 'listar', 'deletar')
            tenant_id: ID da empresa (para controle de acesso)
            
        Returns:
            True se o usuário tem permissão, False caso contrário
        """
        permissao = await self.get_by_user_and_resource(user_id, recurso, tenant_id)
        
        if not permissao:
            return False
            
        return acao in permissao.acoes 