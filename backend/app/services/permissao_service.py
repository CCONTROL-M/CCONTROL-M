"""Serviço para gerenciamento de permissões de usuários."""
from uuid import UUID
from typing import Dict, Any, List, Optional, Tuple
from fastapi import Depends, HTTPException, status
import logging

from app.schemas.permissao_usuario import PermissaoUsuarioCreate, PermissaoUsuarioUpdate, PermissaoUsuario
from app.repositories.permissao_usuario_repository import PermissaoUsuarioRepository
from app.services.log_sistema_service import LogSistemaService
from app.schemas.log_sistema import LogSistemaCreate
from app.database import db_session


class PermissaoService:
    """Serviço para gerenciamento de permissões de usuário."""
    
    def __init__(self):
        """Inicializar serviço."""
        self.logger = logging.getLogger(__name__)
        
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
        
        async with db_session() as session:
            # Verificar se já existe permissão para este usuário e recurso
            permissao_repo = PermissaoUsuarioRepository()
            
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
                
                # Registrar log da operação
                await self._registrar_log(
                    id_empresa=id_empresa,
                    id_usuario=id_usuario_admin,
                    acao="permissao:criacao",
                    descricao=f"Permissão criada para usuário {permissao.id_usuario} no recurso {permissao.recurso}"
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
        
        async with db_session() as session:
            permissao_repo = PermissaoUsuarioRepository()
            
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
                
                # Registrar log da operação
                await self._registrar_log(
                    id_empresa=id_empresa,
                    id_usuario=id_usuario_admin,
                    acao="permissao:atualizacao",
                    descricao=(
                        f"Permissão {id_permissao} atualizada. "
                        f"Recurso: {permissao.recurso if permissao.recurso else existing.recurso}"
                    )
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
        
        async with db_session() as session:
            permissao_repo = PermissaoUsuarioRepository()
            
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
            
            # Armazenar informações para log antes de remover
            id_usuario = existing.id_usuario
            recurso = existing.recurso
            
            # Remover a permissão
            try:
                await permissao_repo.delete(
                    id=id_permissao,
                    tenant_id=id_empresa
                )
                
                # Registrar log da operação
                await self._registrar_log(
                    id_empresa=id_empresa,
                    id_usuario=id_usuario_admin,
                    acao="permissao:remocao",
                    descricao=f"Permissão removida para usuário {id_usuario} no recurso {recurso}"
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
        
        async with db_session() as session:
            permissao_repo = PermissaoUsuarioRepository()
            
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
        
        async with db_session() as session:
            permissao_repo = PermissaoUsuarioRepository()
            
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
        
        async with db_session() as session:
            permissao_repo = PermissaoUsuarioRepository()
            
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
        
        async with db_session() as session:
            permissao_repo = PermissaoUsuarioRepository()
            
            # Verificar permissão
            tem_permissao = await permissao_repo.check_user_permission(
                user_id=id_usuario,
                recurso=recurso,
                acao=acao,
                tenant_id=id_empresa
            )
            
            return tem_permissao
    
    async def _registrar_log(
        self,
        id_empresa: UUID,
        id_usuario: UUID,
        acao: str,
        descricao: str
    ) -> None:
        """
        Registrar um log de operação.
        
        Args:
            id_empresa: ID da empresa
            id_usuario: ID do usuário que realizou a ação
            acao: Tipo de ação realizada
            descricao: Descrição detalhada da ação
        """
        try:
            log_service = LogSistemaService()
            
            log_data = LogSistemaCreate(
                id_empresa=id_empresa,
                id_usuario=id_usuario,
                acao=acao,
                descricao=descricao,
                ip="sistema",
                user_agent="sistema"
            )
            
            await log_service.registrar_log(log_data)
        except Exception as e:
            self.logger.error(f"Erro ao registrar log: {str(e)}")
            # Não lançar exceção para não interromper o fluxo principal 