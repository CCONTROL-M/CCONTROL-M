"""Repositório base para todos os repositórios do sistema."""
from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.models.base import Base


ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Repositório base com operações CRUD comuns.
    
    Args:
        model: Classe do modelo SQLAlchemy
        session: Sessão assíncrona do SQLAlchemy
    """

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        """Inicializa o repositório com o modelo e a sessão."""
        self.model = model
        self.session = session

    async def get_by_id(self, id: UUID, tenant_id: UUID) -> Optional[ModelType]:
        """
        Buscar registro por ID.
        
        Args:
            id: ID do registro
            tenant_id: ID da empresa
            
        Returns:
            Registro encontrado ou None
        """
        query = select(self.model).where(
            and_(
                self.model.id == id,
                self.model.id_empresa == tenant_id
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, tenant_id: UUID) -> List[ModelType]:
        """
        Buscar todos os registros.
        
        Args:
            tenant_id: ID da empresa
            
        Returns:
            Lista de registros
        """
        query = select(self.model).where(self.model.id_empresa == tenant_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, obj_in: CreateSchemaType, tenant_id: UUID) -> ModelType:
        """
        Criar novo registro.
        
        Args:
            obj_in: Dados para criação
            tenant_id: ID da empresa
            
        Returns:
            Registro criado
        """
        obj_data = obj_in.model_dump()
        db_obj = self.model(**obj_data)
        db_obj.id_empresa = tenant_id
        
        self.session.add(db_obj)
        await self.session.flush()
        
        return db_obj

    async def update(self, id: UUID, obj_in: UpdateSchemaType, tenant_id: UUID) -> Optional[ModelType]:
        """
        Atualizar registro existente.
        
        Args:
            id: ID do registro
            obj_in: Dados para atualização
            tenant_id: ID da empresa
            
        Returns:
            Registro atualizado ou None
        """
        db_obj = await self.get_by_id(id, tenant_id)
        if not db_obj:
            return None
        
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        await self.session.flush()
        return db_obj

    async def delete(self, id: UUID, tenant_id: UUID) -> bool:
        """
        Remover registro.
        
        Args:
            id: ID do registro
            tenant_id: ID da empresa
            
        Returns:
            True se removido com sucesso, False caso contrário
        """
        db_obj = await self.get_by_id(id, tenant_id)
        if not db_obj:
            return False
        
        await self.session.delete(db_obj)
        await self.session.flush()
        return True

    async def get_multi(
        self,
        tenant_id: UUID,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """
        Buscar múltiplos registros com paginação e filtros.
        
        Args:
            tenant_id: ID da empresa
            skip: Número de registros para pular
            limit: Número máximo de registros
            filters: Filtros adicionais
            
        Returns:
            Lista de registros
        """
        query = select(self.model).where(self.model.id_empresa == tenant_id)
        
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)
        
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def commit(self) -> None:
        """Comitar alterações na sessão."""
        await self.session.commit()

    async def rollback(self) -> None:
        """Desfazer alterações na sessão."""
        await self.session.rollback() 