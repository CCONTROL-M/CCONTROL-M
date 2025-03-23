"""
Serviço para gerenciamento de registros de auditoria
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging

from app.repositories.auditoria_repository import AuditoriaRepository
from app.schemas.auditoria import AuditoriaCreate, AuditoriaResponse, AuditoriaList
from app.schemas.pagination import PaginationParams
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

class AuditoriaService:
    """
    Serviço para gerenciamento de registros de auditoria no sistema.
    Permite rastrear ações de usuários e alterações em entidades.
    """
    
    def __init__(self):
        """Inicializa o serviço com um repositório de auditoria."""
        self.repository = AuditoriaRepository()
    
    async def registrar_acao(self, 
                            entity_type: str,
                            entity_id: int,
                            action_type: str,
                            user_id: int,
                            empresa_id: int,
                            data_before: Optional[Dict[str, Any]] = None,
                            data_after: Optional[Dict[str, Any]] = None,
                            details: Optional[str] = None) -> AuditoriaResponse:
        """
        Registra uma ação de auditoria no sistema.
        
        Args:
            entity_type: Tipo de entidade (cliente, venda, etc)
            entity_id: ID da entidade
            action_type: Tipo de ação (create, update, delete)
            user_id: ID do usuário que realizou a ação
            empresa_id: ID da empresa
            data_before: Dados antes da alteração
            data_after: Dados após a alteração
            details: Detalhes adicionais da ação
            
        Returns:
            AuditoriaResponse: Registro de auditoria criado
        """
        try:
            registro = AuditoriaCreate(
                entity_type=entity_type,
                entity_id=entity_id,
                action_type=action_type,
                user_id=user_id,
                empresa_id=empresa_id,
                data_before=data_before,
                data_after=data_after,
                details=details,
                timestamp=datetime.now()
            )
            
            result = await self.repository.create(registro)
            logger.info(f"Ação registrada: {action_type} em {entity_type} {entity_id} por usuário {user_id}")
            return result
        except Exception as e:
            logger.error(f"Erro ao registrar ação: {str(e)}")
            # Não propagar exceção para não afetar a operação principal
            return None
    
    async def listar_registros(self,
                             pagination: PaginationParams,
                             entity_type: Optional[str] = None,
                             action_type: Optional[str] = None,
                             date_from: Optional[datetime] = None,
                             date_to: Optional[datetime] = None) -> AuditoriaList:
        """
        Lista registros de auditoria com filtros e paginação.
        
        Args:
            pagination: Parâmetros de paginação
            entity_type: Filtro por tipo de entidade
            action_type: Filtro por tipo de ação
            date_from: Data inicial
            date_to: Data final
            
        Returns:
            AuditoriaList: Lista paginada de registros de auditoria
        """
        filters = {}
        
        if entity_type:
            filters["entity_type"] = entity_type
        
        if action_type:
            filters["action_type"] = action_type
        
        if date_from and date_to:
            filters["timestamp_range"] = (date_from, date_to)
        elif date_from:
            filters["timestamp_range"] = (date_from, None)
        elif date_to:
            filters["timestamp_range"] = (None, date_to)
        
        return await self.repository.list_with_pagination(
            pagination=pagination,
            filters=filters,
            order_by="-timestamp"  # Ordenar do mais recente para o mais antigo
        )
    
    async def obter_por_id(self, id: int) -> Optional[AuditoriaResponse]:
        """
        Obtém um registro de auditoria por ID.
        
        Args:
            id: ID do registro de auditoria
            
        Returns:
            Optional[AuditoriaResponse]: Registro de auditoria ou None se não encontrado
        """
        return await self.repository.get_by_id(id) 