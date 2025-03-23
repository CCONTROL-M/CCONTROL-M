"""Serviço para gerenciamento de permissões de usuários."""
from uuid import UUID
from typing import Dict, Any, List, Optional, Tuple
from fastapi import Depends, HTTPException, status
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.permissao_usuario import PermissaoUsuarioCreate, PermissaoUsuarioUpdate, PermissaoUsuario
from app.repositories.permissao_usuario_repository import PermissaoUsuarioRepository
from app.services.auditoria_service import AuditoriaService
from app.repositories.permissao_repository import PermissaoRepository
from app.schemas.permissao import PermissaoCreate, PermissaoUpdate, Permissao
from app.schemas.pagination import PaginatedResponse
from app.database import get_async_session, db_async_session

logger = logging.getLogger(__name__)


class PermissaoService:
    """Serviço para gerenciamento de permissões de usuário."""
    
    def __init__(self, 
                 session: AsyncSession = Depends(get_async_session),
                 auditoria_service: AuditoriaService = Depends()):
        """Inicializar serviço com repositórios."""
        self.repository = PermissaoUsuarioRepository(session)
        self.auditoria_service = auditoria_service
        self.logger = logger
        
    async def criar_permissao(
        self, 
        permissao: PermissaoUsuarioCreate, 
        id_empresa: UUID,
        id_usuario_admin: UUID
    ) -> PermissaoUsuario:
        """
        Criar uma nova permissão para um usuário.
        
        Args:
            permissao: Dados da permissão a ser criada
            id_empresa: ID da empresa
            id_usuario_admin: ID do usuário administrador que está criando a permissão
            
        Returns:
            Permissão criada
            
        Raises:
            HTTPException: Se já existir uma permissão para o usuário e recurso
        """
        self.logger.info(f"Criando permissão para usuário {permissao.id_usuario} no recurso {permissao.recurso}")
        
        async with get_async_session() as session:
            # Verificar se já existe permissão para este usuário e recurso
            permissao_repo = PermissaoUsuarioRepository(session)
            
            existing = await permissao_repo.get_by_user_and_resource(
                user_id=permissao.id_usuario,
                recurso=permissao.recurso,
                tenant_id=id_empresa
            )
            
            if existing:
                self.logger.warning(
                    f"Já existe uma permissão para o usuário {permissao.id_usuario} "
                    f"no recurso {permissao.recurso}"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Já existe uma permissão para o usuário no recurso '{permissao.recurso}'"
                )
            
            # Criar nova permissão
            try:
                nova_permissao = await permissao_repo.create(
                    obj_in=permissao,
                    tenant_id=id_empresa
                )
                
                # Registrar ação
                await self.auditoria_service.registrar_acao(
                    usuario_id=id_usuario_admin,
                    acao="CRIAR_PERMISSAO",
                    detalhes={
                        "id_permissao": str(nova_permissao.id_permissao),
                        "id_usuario": str(nova_permissao.id_usuario),
                        "recurso": nova_permissao.recurso,
                        "acoes": nova_permissao.acoes,
                        "descricao": f"Permissão criada para usuário {permissao.id_usuario} no recurso {permissao.recurso}"
                    },
                    empresa_id=id_empresa
                )
                
                return nova_permissao
            except Exception as e:
                self.logger.error(f"Erro ao criar permissão: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Erro ao criar permissão: {str(e)}"
                )
    
    async def atualizar_permissao(
        self, 
        id_permissao: UUID, 
        permissao: PermissaoUsuarioUpdate, 
        id_empresa: UUID,
        id_usuario_admin: UUID
    ) -> PermissaoUsuario:
        """
        Atualizar uma permissão existente.
        
        Args:
            id_permissao: ID da permissão a ser atualizada
            permissao: Dados da permissão a serem atualizados
            id_empresa: ID da empresa
            id_usuario_admin: ID do usuário administrador que está atualizando a permissão
            
        Returns:
            Permissão atualizada
            
        Raises:
            HTTPException: Se a permissão não for encontrada
        """
        self.logger.info(f"Atualizando permissão {id_permissao}")
        
        async with get_async_session() as session:
            permissao_repo = PermissaoUsuarioRepository(session)
            
            # Verificar se a permissão existe
            existing = await permissao_repo.get_by_id(
                id=id_permissao,
                tenant_id=id_empresa
            )
            
            if not existing:
                self.logger.warning(f"Permissão {id_permissao} não encontrada")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Permissão não encontrada"
                )
            
            # Atualizar a permissão
            try:
                permissao_atualizada = await permissao_repo.update(
                    id=id_permissao,
                    obj_in=permissao,
                    tenant_id=id_empresa
                )
                
                # Registrar no log
                await self.auditoria_service.registrar_acao(
                    usuario_id=id_usuario_admin,
                    acao="ATUALIZAR_PERMISSAO",
                    detalhes={
                        "id_permissao": str(id_permissao),
                        "id_usuario": str(permissao_atualizada.id_usuario),
                        "recurso": permissao_atualizada.recurso,
                        "acoes": permissao_atualizada.acoes,
                        "descricao": f"Permissão atualizada para usuário {permissao_atualizada.id_usuario} no recurso {permissao_atualizada.recurso}"
                    },
                    empresa_id=id_empresa
                )
                
                return permissao_atualizada
            except Exception as e:
                self.logger.error(f"Erro ao atualizar permissão: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Erro ao atualizar permissão: {str(e)}"
                )
    
    async def remover_permissao(
        self, 
        id_permissao: UUID, 
        id_empresa: UUID,
        id_usuario_admin: UUID
    ) -> Dict[str, str]:
        """
        Remover uma permissão existente.
        
        Args:
            id_permissao: ID da permissão a ser removida
            id_empresa: ID da empresa
            id_usuario_admin: ID do usuário administrador que está removendo a permissão
            
        Returns:
            Mensagem de confirmação
            
        Raises:
            HTTPException: Se a permissão não for encontrada
        """
        self.logger.info(f"Removendo permissão {id_permissao}")
        
        async with get_async_session() as session:
            permissao_repo = PermissaoUsuarioRepository(session)
            
            # Verificar se a permissão existe
            existing = await permissao_repo.get_by_id(
                id=id_permissao,
                tenant_id=id_empresa
            )
            
            if not existing:
                self.logger.warning(f"Permissão {id_permissao} não encontrada")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Permissão não encontrada"
                )
            
            # Registrar log
            await self.auditoria_service.registrar_acao(
                usuario_id=id_usuario_admin,
                acao="EXCLUIR_PERMISSAO",
                detalhes={
                    "id_permissao": str(id_permissao),
                    "id_usuario": str(existing.id_usuario),
                    "recurso": existing.recurso,
                    "descricao": f"Permissão excluída para usuário {existing.id_usuario} no recurso {existing.recurso}"
                },
                empresa_id=id_empresa
            )
            
            # Remover a permissão
            try:
                await permissao_repo.delete(
                    id=id_permissao,
                    tenant_id=id_empresa
                )
                
                return {"detail": "Permissão removida com sucesso"}
            except Exception as e:
                self.logger.error(f"Erro ao remover permissão: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Erro ao remover permissão: {str(e)}"
                )
    
    async def listar_permissoes_por_usuario(
        self, 
        id_usuario: UUID, 
        id_empresa: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[PermissaoUsuario], int]:
        """
        Listar todas as permissões de um usuário.
        
        Args:
            id_usuario: ID do usuário
            id_empresa: ID da empresa
            skip: Número de registros a pular
            limit: Número máximo de registros a retornar
            
        Returns:
            Lista de permissões e contagem total
        """
        self.logger.info(f"Listando permissões para usuário {id_usuario}")
        
        async with get_async_session() as session:
            permissao_repo = PermissaoUsuarioRepository(session)
            
            # Obter todas as permissões do usuário
            permissoes = await permissao_repo.get_by_user_id(
                user_id=id_usuario,
                tenant_id=id_empresa
            )
            
            # Aplicar paginação manual
            total = len(permissoes)
            permissoes_paginadas = permissoes[skip:skip + limit]
            
            return permissoes_paginadas, total
    
    async def listar_todas_permissoes(
        self, 
        id_empresa: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[PermissaoUsuario], int]:
        """
        Listar todas as permissões de uma empresa.
        
        Args:
            id_empresa: ID da empresa
            skip: Número de registros a pular
            limit: Número máximo de registros a retornar
            
        Returns:
            Lista de permissões e contagem total
        """
        self.logger.info(f"Listando todas as permissões para empresa {id_empresa}")
        
        async with get_async_session() as session:
            permissao_repo = PermissaoUsuarioRepository(session)
            
            # Obter todas as permissões
            todas_permissoes = await permissao_repo.get_all(tenant_id=id_empresa)
            
            # Aplicar paginação manual
            total = len(todas_permissoes)
            permissoes_paginadas = todas_permissoes[skip:skip + limit]
            
            return permissoes_paginadas, total
    
    async def obter_permissao(
        self, 
        id_permissao: UUID, 
        id_empresa: UUID
    ) -> PermissaoUsuario:
        """
        Obter uma permissão pelo ID.
        
        Args:
            id_permissao: ID da permissão
            id_empresa: ID da empresa
            
        Returns:
            Permissão encontrada
            
        Raises:
            HTTPException: Se a permissão não for encontrada
        """
        self.logger.info(f"Obtendo permissão {id_permissao}")
        
        async with get_async_session() as session:
            permissao_repo = PermissaoUsuarioRepository(session)
            
            permissao = await permissao_repo.get_by_id(
                id=id_permissao,
                tenant_id=id_empresa
            )
            
            if not permissao:
                self.logger.warning(f"Permissão {id_permissao} não encontrada")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Permissão não encontrada"
                )
            
            return permissao
    
    async def verificar_permissao(
        self, 
        id_usuario: UUID, 
        recurso: str, 
        acao: str, 
        id_empresa: UUID
    ) -> bool:
        """
        Verificar se um usuário tem permissão para realizar uma ação em um recurso.
        
        Args:
            id_usuario: ID do usuário
            recurso: Nome do recurso
            acao: Nome da ação
            id_empresa: ID da empresa
            
        Returns:
            True se o usuário tem permissão, False caso contrário
        """
        self.logger.info(
            f"Verificando permissão para usuário {id_usuario} "
            f"no recurso {recurso}, ação {acao}"
        )
        
        async with get_async_session() as session:
            permissao_repo = PermissaoUsuarioRepository(session)
            
            # Verificar permissão
            tem_permissao = await permissao_repo.check_user_permission(
                user_id=id_usuario,
                recurso=recurso,
                acao=acao,
                tenant_id=id_empresa
            )
            
            return tem_permissao 