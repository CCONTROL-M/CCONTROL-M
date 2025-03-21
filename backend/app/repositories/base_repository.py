"""Módulo com classe base para repositories."""
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID
import logging
from fastapi import HTTPException, status
from sqlalchemy import and_, select, func, desc, asc, delete, update, Column
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Define o tipo genérico para o modelo ORM
ModelType = TypeVar("ModelType")
# Define o tipo genérico para o schema de criação
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
# Define o tipo genérico para o schema de atualização
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Classe base para repositórios.
    
    Fornece métodos de CRUD genéricos que podem ser reutilizados em todos os repositórios.
    """
    
    def __init__(self, model: Type[ModelType]):
        """
        Inicializa o repositório com o modelo específico.
        
        Args:
            model: Classe do modelo SQLAlchemy
        """
        self.model = model
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def get(self, db: Session, id: UUID) -> Optional[ModelType]:
        """
        Obtém um registro pelo ID.
        
        Args:
            db: Sessão do banco de dados
            id: ID do registro
            
        Returns:
            Registro encontrado ou None
        """
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_by_field(self, db: Session, field_name: str, value: Any) -> Optional[ModelType]:
        """
        Obtém um registro pelo valor de um campo específico.
        
        Args:
            db: Sessão do banco de dados
            field_name: Nome do campo
            value: Valor do campo
            
        Returns:
            Registro encontrado ou None
        """
        return db.query(self.model).filter(getattr(self.model, field_name) == value).first()
    
    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """
        Obtém múltiplos registros, com paginação e filtragem opcional.
        
        Args:
            db: Sessão do banco de dados
            skip: Número de registros para pular (deslocamento)
            limit: Número máximo de registros para retornar
            filters: Dicionário de filtros {nome_campo: valor}
            
        Returns:
            Lista de registros
        """
        query = db.query(self.model)
        
        if filters:
            filter_conditions = []
            for field_name, value in filters.items():
                if hasattr(self.model, field_name):
                    filter_conditions.append(getattr(self.model, field_name) == value)
            
            if filter_conditions:
                query = query.filter(and_(*filter_conditions))
        
        return query.offset(skip).limit(limit).all()
    
    def get_count(
        self,
        db: Session,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Obtém a contagem total de registros, com filtragem opcional.
        
        Args:
            db: Sessão do banco de dados
            filters: Dicionário de filtros {nome_campo: valor}
            
        Returns:
            Contagem total de registros
        """
        query = db.query(func.count(self.model.id))
        
        if filters:
            filter_conditions = []
            for field_name, value in filters.items():
                if hasattr(self.model, field_name):
                    filter_conditions.append(getattr(self.model, field_name) == value)
            
            if filter_conditions:
                query = query.filter(and_(*filter_conditions))
        
        return query.scalar()
    
    def create(self, db: Session, *, obj_in: Union[CreateSchemaType, Dict[str, Any]]) -> ModelType:
        """
        Cria um novo registro.
        
        Args:
            db: Sessão do banco de dados
            obj_in: Dados para criação (schema ou dicionário)
            
        Returns:
            Registro criado
        """
        try:
            obj_data = obj_in.model_dump() if isinstance(obj_in, BaseModel) else obj_in
            db_obj = self.model(**obj_data)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            db.rollback()
            self.logger.error(f"Erro ao criar registro: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao criar registro: {str(e)}"
            )
    
    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Atualiza um registro existente.
        
        Args:
            db: Sessão do banco de dados
            db_obj: Instância existente do objeto
            obj_in: Dados para atualização (schema ou dicionário)
            
        Returns:
            Registro atualizado
        """
        try:
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.model_dump(exclude_unset=True)
            
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            db.rollback()
            self.logger.error(f"Erro ao atualizar registro: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao atualizar registro: {str(e)}"
            )
    
    def delete(self, db: Session, *, id: UUID) -> ModelType:
        """
        Remove um registro pelo ID.
        
        Args:
            db: Sessão do banco de dados
            id: ID do registro
            
        Returns:
            Registro removido
            
        Raises:
            HTTPException: Se o registro não for encontrado
        """
        try:
            obj = db.query(self.model).get(id)
            if obj is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Registro não encontrado"
                )
            
            db.delete(obj)
            db.commit()
            return obj
        except SQLAlchemyError as e:
            db.rollback()
            self.logger.error(f"Erro ao excluir registro: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao excluir registro: {str(e)}"
            ) 