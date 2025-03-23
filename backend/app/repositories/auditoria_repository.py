"""
Repositório para operações de auditoria no banco de dados
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from sqlalchemy import select, func, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.database import get_async_session
from app.models.auditoria import Auditoria
from app.schemas.auditoria import AuditoriaCreate, AuditoriaResponse, AuditoriaList
from app.schemas.pagination import PaginationParams
from app.repositories.base_repository import BaseRepository

class AuditoriaRepository(BaseRepository):
    """
    Repositório para operações relacionadas aos registros de auditoria.
    Permite o armazenamento e recuperação de logs de alterações no sistema.
    """
    
    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        """Inicializa o repositório com a sessão do banco de dados"""
        super().__init__(session, Auditoria)
    
    async def create(self, obj_in: AuditoriaCreate) -> AuditoriaResponse:
        """
        Cria um novo registro de auditoria.
        
        Args:
            obj_in: Dados do registro a ser criado
            
        Returns:
            Registro de auditoria criado
        """
        db_obj = Auditoria(
            entity_type=obj_in.entity_type,
            entity_id=obj_in.entity_id,
            action_type=obj_in.action_type,
            user_id=obj_in.user_id,
            empresa_id=obj_in.empresa_id,
            data_before=obj_in.data_before,
            data_after=obj_in.data_after,
            details=obj_in.details,
            timestamp=obj_in.timestamp
        )
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return AuditoriaResponse.model_validate(db_obj)
    
    async def get_by_id(self, id: int) -> Optional[AuditoriaResponse]:
        """
        Obtém um registro de auditoria por ID.
        
        Args:
            id: ID do registro
            
        Returns:
            Registro de auditoria ou None se não encontrado
        """
        stmt = select(Auditoria).where(Auditoria.id == id)
        result = await self.session.execute(stmt)
        db_obj = result.scalars().first()
        
        if not db_obj:
            return None
            
        return AuditoriaResponse.model_validate(db_obj)
    
    async def list_with_pagination(
        self,
        pagination: PaginationParams,
        filters: Dict[str, Any] = None,
        order_by: str = "-timestamp"
    ) -> AuditoriaList:
        """
        Lista registros de auditoria com paginação e filtros.
        
        Args:
            pagination: Parâmetros de paginação
            filters: Filtros a serem aplicados
            order_by: Campo para ordenação
            
        Returns:
            Lista paginada de registros de auditoria
        """
        filters = filters or {}
        
        # Construir a query
        query = select(Auditoria)
        
        # Aplicar filtros
        if "entity_type" in filters:
            query = query.where(Auditoria.entity_type == filters["entity_type"])
            
        if "action_type" in filters:
            query = query.where(Auditoria.action_type == filters["action_type"])
            
        if "timestamp_range" in filters:
            date_from, date_to = filters["timestamp_range"]
            if date_from:
                query = query.where(Auditoria.timestamp >= date_from)
            if date_to:
                query = query.where(Auditoria.timestamp <= date_to)
                
        # Contar total de registros
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query) or 0
        
        # Aplicar ordenação
        if order_by.startswith("-"):
            field = order_by[1:]
            query = query.order_by(desc(getattr(Auditoria, field)))
        else:
            query = query.order_by(asc(getattr(Auditoria, order_by)))
            
        # Aplicar paginação
        skip = (pagination.page - 1) * pagination.size
        query = query.offset(skip).limit(pagination.size)
        
        # Executar consulta
        result = await self.session.execute(query)
        items = result.scalars().all()
        
        # Calcular total de páginas
        pages = (total + pagination.size - 1) // pagination.size if pagination.size > 0 else 0
        
        # Criar resposta paginada
        return AuditoriaList(
            items=[AuditoriaResponse.model_validate(item) for item in items],
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=pages
        ) 