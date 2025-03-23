"""Serviço para gerenciamento de usuários no sistema CCONTROL-M."""
from uuid import UUID
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
import logging
from passlib.hash import bcrypt
from datetime import datetime

from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.database import get_async_session
from app.utils.validators import validar_email
from app.schemas.pagination import PaginatedResponse
from app.services.auditoria_service import AuditoriaService
from app.utils.security import get_password_hash


# Configurar logger
logger = logging.getLogger(__name__)


class UsuarioService:
    """Serviço para gerenciamento de usuários."""
    
    def __init__(self, 
                 session: AsyncSession = Depends(get_async_session),
                 auditoria_service: AuditoriaService = Depends()):
        """Inicializar serviço com repositórios."""
        self.repository = UsuarioRepository(session)
        self.auditoria_service = auditoria_service
        self.logger = logger
        
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

    async def create(
        self,
        usuario: UsuarioCreate,
        usuario_id: UUID,
        empresa_id: UUID
    ) -> Usuario:
        """
        Criar um novo usuário.
        
        Args:
            usuario: Dados do usuário a ser criado
            usuario_id: ID do usuário que está criando
            empresa_id: ID da empresa
            
        Returns:
            Usuário criado
            
        Raises:
            HTTPException: Se houver erro na criação
        """
        try:
            # Verificar se email já existe
            if await self.repository.get_by_email(usuario.email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email já cadastrado"
                )
            
            # Hash da senha
            usuario.senha = get_password_hash(usuario.senha)
            
            # Criar usuário
            novo_usuario = await self.repository.create(usuario, empresa_id)
            
            # Registrar ação
            await self.auditoria_service.registrar_acao(
                usuario_id=usuario_id,
                acao="CRIAR_USUARIO",
                detalhes={
                    "id_usuario": str(novo_usuario.id_usuario),
                    "nome": novo_usuario.nome,
                    "email": novo_usuario.email,
                    "tipo": novo_usuario.tipo
                },
                empresa_id=empresa_id
            )
            
            return novo_usuario
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Erro ao criar usuário: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao criar usuário"
            )

    async def update(
        self,
        id_usuario: UUID,
        usuario: UsuarioUpdate,
        usuario_id: UUID,
        empresa_id: UUID
    ) -> Usuario:
        """
        Atualizar um usuário existente.
        
        Args:
            id_usuario: ID do usuário a ser atualizado
            usuario: Dados atualizados do usuário
            usuario_id: ID do usuário que está atualizando
            empresa_id: ID da empresa
            
        Returns:
            Usuário atualizado
            
        Raises:
            HTTPException: Se houver erro na atualização
        """
        try:
            # Buscar usuário existente
            usuario_atual = await self.repository.get_by_id(id_usuario)
            if not usuario_atual:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuário não encontrado"
                )
            
            # Verificar email se alterado
            if usuario.email and usuario.email != usuario_atual.email:
                if await self.repository.get_by_email(usuario.email):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email já cadastrado"
                    )
            
            # Hash da senha se alterada
            if usuario.senha:
                usuario.senha = get_password_hash(usuario.senha)
            
            # Atualizar usuário
            usuario_atualizado = await self.repository.update(id_usuario, usuario)
            
            # Registrar ação
            await self.auditoria_service.registrar_acao(
                usuario_id=usuario_id,
                acao="ATUALIZAR_USUARIO",
                detalhes={
                    "id_usuario": str(id_usuario),
                    "alteracoes": usuario.model_dump(exclude={"senha"}, exclude_unset=True)
                },
                empresa_id=empresa_id
            )
            
            return usuario_atualizado
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Erro ao atualizar usuário: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao atualizar usuário"
            )

    async def delete(
        self,
        id_usuario: UUID,
        usuario_id: UUID,
        empresa_id: UUID
    ) -> None:
        """
        Excluir um usuário.
        
        Args:
            id_usuario: ID do usuário a ser excluído
            usuario_id: ID do usuário que está excluindo
            empresa_id: ID da empresa
            
        Raises:
            HTTPException: Se houver erro na exclusão
        """
        try:
            # Buscar usuário
            usuario = await self.repository.get_by_id(id_usuario)
            if not usuario:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuário não encontrado"
                )
            
            # Excluir usuário
            await self.repository.delete(id_usuario)
            
            # Registrar ação
            await self.auditoria_service.registrar_acao(
                usuario_id=usuario_id,
                acao="EXCLUIR_USUARIO",
                detalhes={
                    "id_usuario": str(id_usuario),
                    "nome": usuario.nome,
                    "email": usuario.email,
                    "tipo": usuario.tipo
                },
                empresa_id=empresa_id
            )
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Erro ao excluir usuário: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao excluir usuário"
            )

    async def get_by_id(
        self,
        id_usuario: UUID,
        usuario_id: UUID,
        empresa_id: UUID
    ) -> Usuario:
        """
        Buscar um usuário pelo ID.
        
        Args:
            id_usuario: ID do usuário a ser buscado
            usuario_id: ID do usuário que está buscando
            empresa_id: ID da empresa
            
        Returns:
            Usuário encontrado
            
        Raises:
            HTTPException: Se o usuário não for encontrado
        """
        try:
            usuario = await self.repository.get_by_id(id_usuario)
            if not usuario:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuário não encontrado"
                )
                
            # Registrar ação de consulta
            await self.auditoria_service.registrar_acao(
                usuario_id=usuario_id,
                acao="CONSULTAR_USUARIO",
                detalhes={"id_usuario": str(id_usuario)},
                empresa_id=empresa_id
            )
                
            return usuario
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Erro ao buscar usuário: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao buscar usuário"
            )

    async def get_multi(
        self,
        empresa_id: UUID,
        skip: int = 0,
        limit: int = 100,
        tipo: Optional[str] = None,
        status: Optional[str] = None,
        busca: Optional[str] = None
    ) -> PaginatedResponse[Usuario]:
        """
        Buscar múltiplos usuários com filtros.
        
        Args:
            empresa_id: ID da empresa
            skip: Número de registros para pular
            limit: Número máximo de registros
            tipo: Filtrar por tipo de usuário
            status: Filtrar por status
            busca: Termo para busca
            
        Returns:
            Lista paginada de usuários
        """
        try:
            usuarios, total = await self.repository.get_multi(
                empresa_id=empresa_id,
                skip=skip,
                limit=limit,
                tipo=tipo,
                status=status,
                busca=busca
            )
            
            return PaginatedResponse(
                items=usuarios,
                total=total,
                page=skip // limit + 1 if limit > 0 else 1,
                size=limit,
                pages=(total + limit - 1) // limit if limit > 0 else 1
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar usuários: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao buscar usuários"
            ) 