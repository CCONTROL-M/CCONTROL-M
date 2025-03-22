"""Base repository para acesso ao banco de dados com suporte a multi-tenancy."""
import logging
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic, Union, UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete, text
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel

from app.db.database import get_db_session

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Repositório base para operações de banco de dados com suporte a multi-tenancy.
    
    Esta classe implementa os métodos básicos de CRUD e é adaptada para
    trabalhar com o Row-Level Security (RLS) do PostgreSQL/Supabase.
    """
    
    def __init__(self, model: Type[ModelType]):
        """
        Inicializa o repositório com o modelo ORM.
        
        Args:
            model: Classe do modelo ORM (SQLAlchemy)
        """
        self.model = model
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def _set_tenant_context(self, session: AsyncSession, tenant_id: Optional[UUID] = None) -> None:
        """
        Define a variável de sessão para o tenant atual no PostgreSQL.
        Esta função é essencial para o funcionamento do RLS.
        
        Args:
            session: Sessão assíncrona do SQLAlchemy
            tenant_id: ID do tenant (empresa)
        """
        if tenant_id is not None:
            # Define a variável de sessão para o tenant no PostgreSQL
            # Usamos app.current_tenant para compatibilidade com Supabase
            query = text("SET app.current_tenant = :tenant_id")
            await session.execute(query, {"tenant_id": tenant_id})
    
    async def get_all(self, tenant_id: Optional[UUID] = None) -> List[ModelType]:
        """
        Recupera todos os registros do modelo.
        
        Args:
            tenant_id: ID do tenant (empresa) para filtrar os resultados
            
        Returns:
            Lista de instâncias do modelo
        """
        async with get_db_session() as session:
            await self._set_tenant_context(session, tenant_id)
            query = select(self.model)
            result = await session.execute(query)
            return list(result.scalars().all())
    
    async def get_by_id(self, id: Any, tenant_id: Optional[UUID] = None) -> Optional[ModelType]:
        """
        Recupera um registro pelo ID.
        
        Args:
            id: ID do registro
            tenant_id: ID do tenant (empresa) para filtrar os resultados
            
        Returns:
            Instância do modelo ou None se não encontrado
        """
        async with get_db_session() as session:
            await self._set_tenant_context(session, tenant_id)
            query = select(self.model).where(self.model.id == id)
            result = await session.execute(query)
            return result.scalar_one_or_none()
    
    async def create(self, obj_in: Union[CreateSchemaType, Dict[str, Any]], 
                    tenant_id: Optional[UUID] = None) -> ModelType:
        """
        Cria um novo registro.
        
        Args:
            obj_in: Dados para criar o registro (schema ou dicionário)
            tenant_id: ID do tenant (empresa) para associar ao registro
            
        Returns:
            Instância do modelo criado
        """
        try:
            async with get_db_session() as session:
                await self._set_tenant_context(session, tenant_id)
                
                # Converter schema para dicionário se necessário
                if isinstance(obj_in, BaseModel):
                    data = obj_in.model_dump()
                else:
                    data = obj_in
                
                # Se o modelo tem campo id_empresa e o tenant_id foi fornecido, adiciona ao registro
                if hasattr(self.model, 'id_empresa') and tenant_id is not None:
                    data['id_empresa'] = tenant_id
                
                stmt = insert(self.model).values(**data).returning(self.model)
                result = await session.execute(stmt)
                await session.commit()
                return result.scalar_one()
        except SQLAlchemyError as e:
            self.logger.error(f"Erro ao criar registro: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao criar registro: {str(e)}"
            )
    
    async def update(self, id: Any, obj_in: Union[UpdateSchemaType, Dict[str, Any]], 
                    tenant_id: Optional[UUID] = None) -> Optional[ModelType]:
        """
        Atualiza um registro existente.
        
        Args:
            id: ID do registro
            obj_in: Dados para atualizar (schema ou dicionário)
            tenant_id: ID do tenant (empresa) para filtrar os resultados
            
        Returns:
            Instância do modelo atualizado ou None se não encontrado
        """
        try:
            async with get_db_session() as session:
                await self._set_tenant_context(session, tenant_id)
                
                # Converter schema para dicionário se necessário
                if isinstance(obj_in, BaseModel):
                    data = obj_in.model_dump(exclude_unset=True)
                else:
                    data = obj_in
                
                # Remover id_empresa do payload de dados caso ele exista
                # para evitar que um registro seja transferido para outra empresa
                if 'id_empresa' in data:
                    data.pop('id_empresa')
                    
                stmt = (
                    update(self.model)
                    .where(self.model.id == id)
                    .values(**data)
                    .returning(self.model)
                )
                result = await session.execute(stmt)
                updated = result.scalar_one_or_none()
                
                if updated is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Registro não encontrado"
                    )
                
                await session.commit()
                return updated
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            self.logger.error(f"Erro ao atualizar registro: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao atualizar registro: {str(e)}"
            )
    
    async def delete(self, id: Any, tenant_id: Optional[UUID] = None) -> bool:
        """
        Remove um registro.
        
        Args:
            id: ID do registro
            tenant_id: ID do tenant (empresa) para filtrar os resultados
            
        Returns:
            True se o registro foi removido, False caso contrário
        """
        try:
            async with get_db_session() as session:
                await self._set_tenant_context(session, tenant_id)
                stmt = (
                    delete(self.model)
                    .where(self.model.id == id)
                    .returning(self.model.id)
                )
                result = await session.execute(stmt)
                deleted = result.scalar_one_or_none()
                
                if deleted is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Registro não encontrado"
                    )
                
                await session.commit()
                return True
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            self.logger.error(f"Erro ao excluir registro: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao excluir registro: {str(e)}"
            )
    
    async def count(self, tenant_id: Optional[UUID] = None) -> int:
        """
        Conta o número de registros.
        
        Args:
            tenant_id: ID do tenant (empresa) para filtrar os resultados
            
        Returns:
            Número de registros
        """
        async with get_db_session() as session:
            await self._set_tenant_context(session, tenant_id)
            query = select(self.model)
            result = await session.execute(query)
            return len(list(result.scalars().all())) 