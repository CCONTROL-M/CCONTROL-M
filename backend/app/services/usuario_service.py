"""Serviço para gerenciamento de usuários no sistema CCONTROL-M."""
from uuid import UUID
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
import logging
from passlib.hash import bcrypt

from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.database import get_async_session
from app.utils.validators import validar_email


class UsuarioService:
    """Serviço para gerenciamento de usuários."""
    
    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        """Inicializar serviço com repositório."""
        self.repository = UsuarioRepository(session)
        self.logger = logging.getLogger(__name__)
        
    async def get_usuario(self, id_usuario: UUID, id_empresa: Optional[UUID] = None) -> Usuario:
        """
        Obter usuário pelo ID.
        
        Args:
            id_usuario: ID do usuário
            id_empresa: ID da empresa para validação de acesso (opcional para admin)
            
        Returns:
            Usuário encontrado
            
        Raises:
            HTTPException: Se o usuário não for encontrado
        """
        self.logger.info(f"Buscando usuário ID: {id_usuario}")
        
        if id_empresa:
            usuario = await self.repository.get_by_id(id_usuario, id_empresa)
        else:
            usuario = await self.repository.get_by_id(id_usuario)
            
        if not usuario:
            self.logger.warning(f"Usuário não encontrado: {id_usuario}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        return usuario
        
    async def get_by_email(self, email: str) -> Optional[Usuario]:
        """
        Obter usuário pelo email.
        
        Args:
            email: Email do usuário
            
        Returns:
            Usuário encontrado ou None
        """
        self.logger.info(f"Buscando usuário por email: {email}")
        return await self.repository.get_by_email(email)
        
    async def listar_usuarios(
        self,
        id_empresa: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100,
        nome: Optional[str] = None,
        email: Optional[str] = None,
        ativo: Optional[bool] = None,
        perfil: Optional[str] = None
    ) -> Tuple[List[Usuario], int]:
        """
        Listar usuários com paginação e filtros.
        
        Args:
            id_empresa: ID da empresa para filtrar (None lista todos para admin)
            skip: Número de registros a pular
            limit: Número máximo de registros a retornar
            nome: Filtrar por nome
            email: Filtrar por email
            ativo: Filtrar por status
            perfil: Filtrar por tipo de perfil
            
        Returns:
            Lista de usuários e contagem total
        """
        self.logger.info(f"Buscando usuários com filtros: empresa={id_empresa}, nome={nome}, email={email}")
        
        filters = []
        
        if id_empresa:
            filters.append({"id_empresa": id_empresa})
            
        if nome:
            filters.append({"nome__ilike": f"%{nome}%"})
            
        if email:
            filters.append({"email__ilike": f"%{email}%"})
            
        if ativo is not None:
            filters.append({"ativo": ativo})
            
        if perfil:
            filters.append({"perfil": perfil})
            
        return await self.repository.list_with_filters(
            skip=skip,
            limit=limit,
            filters=filters
        )
        
    async def criar_usuario(self, usuario: UsuarioCreate) -> Usuario:
        """
        Criar novo usuário.
        
        Args:
            usuario: Dados do usuário a ser criado
            
        Returns:
            Usuário criado
            
        Raises:
            HTTPException: Se ocorrer um erro na validação
        """
        self.logger.info(f"Criando novo usuário: {usuario.nome} ({usuario.email})")
        
        # Validar email
        if not validar_email(usuario.email):
            self.logger.warning(f"Email inválido: {usuario.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email inválido"
            )
        
        # Verificar se já existe usuário com o mesmo email
        usuario_existente = await self.repository.get_by_email(usuario.email)
        if usuario_existente:
            self.logger.warning(f"Email já cadastrado: {usuario.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um usuário cadastrado com este email"
            )
        
        # Validar senha (mínimo 8 caracteres)
        if len(usuario.senha) < 8:
            self.logger.warning("Senha muito curta")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha deve ter no mínimo 8 caracteres"
            )
        
        # Converter para dicionário para enviar ao repositório
        usuario_data = usuario.model_dump()
        
        # Criptografar senha
        usuario_data["senha_hash"] = bcrypt.hash(usuario_data.pop("senha"))
        
        # Criar usuário no repositório
        try:
            return await self.repository.create(usuario_data)
        except HTTPException as e:
            self.logger.warning(f"Erro ao criar usuário: {e.detail}")
            raise
        except Exception as e:
            self.logger.error(f"Erro inesperado ao criar usuário: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao criar usuário"
            )
        
    async def atualizar_usuario(self, id_usuario: UUID, usuario: UsuarioUpdate, id_empresa: Optional[UUID] = None) -> Usuario:
        """
        Atualizar usuário existente.
        
        Args:
            id_usuario: ID do usuário a ser atualizado
            usuario: Dados para atualização
            id_empresa: ID da empresa para validação de acesso (opcional para admin)
            
        Returns:
            Usuário atualizado
            
        Raises:
            HTTPException: Se o usuário não for encontrado ou ocorrer erro na validação
        """
        self.logger.info(f"Atualizando usuário: {id_usuario}")
        
        # Verificar se o usuário existe
        await self.get_usuario(id_usuario, id_empresa)
        
        # Validar email se estiver sendo atualizado
        if usuario.email and not validar_email(usuario.email):
            self.logger.warning(f"Email inválido: {usuario.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email inválido"
            )
            
        # Verificar se já existe outro usuário com o mesmo email
        if usuario.email:
            usuario_existente = await self.repository.get_by_email(usuario.email)
            if usuario_existente and usuario_existente.id_usuario != id_usuario:
                self.logger.warning(f"Email já cadastrado em outro usuário: {usuario.email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Já existe um usuário cadastrado com este email"
                )
        
        # Remover campos None do modelo de atualização
        update_data = {k: v for k, v in usuario.model_dump().items() if v is not None}
        
        # Se estiver atualizando a senha, criptografá-la
        if "senha" in update_data:
            if len(update_data["senha"]) < 8:
                self.logger.warning("Senha muito curta")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Senha deve ter no mínimo 8 caracteres"
                )
            update_data["senha_hash"] = bcrypt.hash(update_data.pop("senha"))
        
        # Atualizar usuário
        try:
            if id_empresa:
                usuario_atualizado = await self.repository.update(id_usuario, update_data, id_empresa)
            else:
                usuario_atualizado = await self.repository.update(id_usuario, update_data)
            
            if not usuario_atualizado:
                self.logger.warning(f"Usuário não encontrado após tentativa de atualização: {id_usuario}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuário não encontrado"
                )
            
            return usuario_atualizado
        except HTTPException as e:
            self.logger.warning(f"Erro ao atualizar usuário: {e.detail}")
            raise
        except Exception as e:
            self.logger.error(f"Erro inesperado ao atualizar usuário: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao atualizar usuário"
            )
        
    async def desativar_usuario(self, id_usuario: UUID, id_empresa: Optional[UUID] = None) -> Dict[str, Any]:
        """
        Desativar usuário pelo ID.
        
        Args:
            id_usuario: ID do usuário a ser desativado
            id_empresa: ID da empresa para validação de acesso (opcional para admin)
            
        Returns:
            Mensagem de confirmação
            
        Raises:
            HTTPException: Se o usuário não for encontrado
        """
        self.logger.info(f"Desativando usuário: {id_usuario}")
        
        # Verificar se o usuário existe
        usuario = await self.get_usuario(id_usuario, id_empresa)
        
        # Verificar se já está inativo
        if not usuario.ativo:
            self.logger.warning(f"Usuário já está inativo: {id_usuario}")
            return {"detail": "Usuário já está inativo"}
        
        # Desativar usuário
        update_data = {"ativo": False}
        
        if id_empresa:
            await self.repository.update(id_usuario, update_data, id_empresa)
        else:
            await self.repository.update(id_usuario, update_data)
        
        self.logger.info(f"Usuário desativado com sucesso: {id_usuario}")
        return {"detail": "Usuário desativado com sucesso"}
        
    async def ativar_usuario(self, id_usuario: UUID, id_empresa: Optional[UUID] = None) -> Dict[str, Any]:
        """
        Ativar usuário pelo ID.
        
        Args:
            id_usuario: ID do usuário a ser ativado
            id_empresa: ID da empresa para validação de acesso (opcional para admin)
            
        Returns:
            Mensagem de confirmação
            
        Raises:
            HTTPException: Se o usuário não for encontrado
        """
        self.logger.info(f"Ativando usuário: {id_usuario}")
        
        # Verificar se o usuário existe
        usuario = await self.get_usuario(id_usuario, id_empresa)
        
        # Verificar se já está ativo
        if usuario.ativo:
            self.logger.warning(f"Usuário já está ativo: {id_usuario}")
            return {"detail": "Usuário já está ativo"}
        
        # Ativar usuário
        update_data = {"ativo": True}
        
        if id_empresa:
            await self.repository.update(id_usuario, update_data, id_empresa)
        else:
            await self.repository.update(id_usuario, update_data)
        
        self.logger.info(f"Usuário ativado com sucesso: {id_usuario}")
        return {"detail": "Usuário ativado com sucesso"}
        
    async def verificar_senha(self, email: str, senha: str) -> Optional[Usuario]:
        """
        Verificar se a senha está correta para o usuário.
        
        Args:
            email: Email do usuário
            senha: Senha a ser verificada
            
        Returns:
            Usuário se autenticado, None caso contrário
        """
        self.logger.info(f"Verificando senha para usuário: {email}")
        
        usuario = await self.repository.get_by_email(email)
        if not usuario:
            self.logger.warning(f"Usuário não encontrado para email: {email}")
            return None
            
        if not bcrypt.verify(senha, usuario.senha_hash):
            self.logger.warning(f"Senha incorreta para usuário: {email}")
            return None
            
        return usuario 