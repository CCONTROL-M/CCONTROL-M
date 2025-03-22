"""Repositório para operações com usuários."""
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate
from app.utils.security import get_password_hash


class UsuarioRepository:
    """Repositório para operações com usuários."""
    
    def __init__(self, session: AsyncSession):
        """
        Inicializa o repositório com a sessão assíncrona do SQLAlchemy.
        
        Args:
            session: Sessão assíncrona do SQLAlchemy
        """
        self.session = session
    
    async def get_by_id(self, id_usuario: UUID) -> Optional[Usuario]:
        """
        Obtém um usuário pelo ID.
        
        Args:
            id_usuario: ID do usuário
            
        Returns:
            Usuario: Usuário encontrado ou None
        """
        query = select(Usuario).where(Usuario.id_usuario == id_usuario)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[Usuario]:
        """
        Obtém um usuário pelo email.
        
        Args:
            email: Email do usuário
            
        Returns:
            Usuario: Usuário encontrado ou None
        """
        query = select(Usuario).where(Usuario.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_field(self, field_name: str, value: Any) -> Optional[Usuario]:
        """
        Obtém um usuário pelo valor de um campo específico.
        
        Args:
            field_name: Nome do campo
            value: Valor do campo
            
        Returns:
            Usuario: Usuário encontrado ou None
        """
        query = select(Usuario).where(getattr(Usuario, field_name) == value)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters
    ) -> Tuple[List[Usuario], int]:
        """
        Obtém múltiplos usuários com paginação e filtragem opcional.
        
        Args:
            skip: Registros para pular
            limit: Limite de registros
            **filters: Filtros adicionais
            
        Returns:
            Tuple[List[Usuario], int]: Lista de usuários e contagem total
        """
        query = select(Usuario)
        count_query = select(func.count()).select_from(Usuario)
        
        # Aplicar filtros nas duas queries
        for field, value in filters.items():
            if hasattr(Usuario, field) and value is not None:
                if field in ["nome", "email"]:
                    # Busca por substring para campos de texto
                    field_filter = getattr(Usuario, field).ilike(f"%{value}%")
                else:
                    field_filter = getattr(Usuario, field) == value
                
                query = query.where(field_filter)
                count_query = count_query.where(field_filter)
        
        # Aplicar paginação
        query = query.offset(skip).limit(limit)
        
        # Executar consultas
        result = await self.session.execute(query)
        usuarios = list(result.scalars().all())
        
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()
        
        return usuarios, total
    
    async def get_count(self, **filters) -> int:
        """
        Obtém a contagem total de usuários com filtros opcionais.
        
        Args:
            **filters: Filtros adicionais
            
        Returns:
            int: Contagem de usuários
        """
        query = select(func.count()).select_from(Usuario)
        
        # Aplicar filtros
        for field, value in filters.items():
            if hasattr(Usuario, field) and value is not None:
                if field in ["nome", "email"]:
                    # Busca por substring para campos de texto
                    query = query.where(getattr(Usuario, field).ilike(f"%{value}%"))
                else:
                    query = query.where(getattr(Usuario, field) == value)
        
        result = await self.session.execute(query)
        return result.scalar_one()
    
    async def create(self, usuario: UsuarioCreate) -> Usuario:
        """
        Cria um novo usuário.
        
        Args:
            usuario: Dados do usuário
            
        Returns:
            Usuario: Usuário criado
            
        Raises:
            HTTPException: Se o email já estiver em uso
        """
        try:
            # Verificar se o email já existe
            existente = await self.get_by_email(usuario.email)
            if existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email já está em uso por outro usuário"
                )
            
            # Criar objeto de dados com senha hasheada
            db_obj = Usuario(
                id_empresa=usuario.id_empresa,
                nome=usuario.nome,
                email=usuario.email,
                senha_hash=get_password_hash(usuario.senha),
                tipo_usuario=usuario.tipo_usuario,
                telas_permitidas=usuario.telas_permitidas
            )
            
            self.session.add(db_obj)
            await self.session.commit()
            await self.session.refresh(db_obj)
            
            return db_obj
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao criar usuário: {str(e)}"
            )
    
    async def update(self, id_usuario: UUID, usuario: UsuarioUpdate) -> Optional[Usuario]:
        """
        Atualiza um usuário existente.
        
        Args:
            id_usuario: ID do usuário
            usuario: Dados para atualizar
            
        Returns:
            Usuario: Usuário atualizado
            
        Raises:
            HTTPException: Se o email já estiver em uso por outro usuário
            HTTPException: Se o usuário não for encontrado
        """
        try:
            # Buscar usuário existente
            db_obj = await self.get_by_id(id_usuario)
            if not db_obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuário não encontrado"
                )
                
            # Verificar se o email está sendo alterado e já existe
            if usuario.email and usuario.email != db_obj.email:
                existente = await self.get_by_email(usuario.email)
                if existente and existente.id_usuario != id_usuario:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email já está em uso por outro usuário"
                    )
            
            # Atualizar os campos
            update_data = usuario.model_dump(exclude_unset=True)
            
            # Tratar a senha separadamente
            if "senha" in update_data:
                senha = update_data.pop("senha")
                if senha:
                    db_obj.senha_hash = get_password_hash(senha)
            
            # Atualizar os demais campos
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            
            await self.session.commit()
            await self.session.refresh(db_obj)
            
            return db_obj
        except HTTPException:
            await self.session.rollback()
            raise
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao atualizar usuário: {str(e)}"
            )
        
    async def delete(self, id_usuario: UUID) -> bool:
        """
        Remove um usuário.
        
        Args:
            id_usuario: ID do usuário
            
        Returns:
            bool: True se removido com sucesso
            
        Raises:
            HTTPException: Se o usuário não for encontrado
            HTTPException: Se ocorrer um erro ao excluir
        """
        try:
            db_obj = await self.get_by_id(id_usuario)
            if not db_obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuário não encontrado"
                )
                
            await self.session.delete(db_obj)
            await self.session.commit()
            
            return True
        except HTTPException:
            await self.session.rollback()
            raise
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao excluir usuário: {str(e)}"
            ) 