"""Serviço para gerenciamento de logs do sistema CCONTROL-M."""
from uuid import UUID
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
import logging

from app.schemas.log_sistema import LogSistemaCreate, LogSistema
from app.repositories.log_sistema_repository import LogSistemaRepository
from app.database import get_async_session


class LogSistemaService:
    """Serviço para gerenciamento de logs do sistema."""
    
    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        """Inicializar serviço com repositório."""
        self.repository = LogSistemaRepository(session)
        self.logger = logging.getLogger(__name__)
        
    async def registrar_log(self, log: LogSistemaCreate) -> LogSistema:
        """
        Registrar um novo log no sistema.
        
        Args:
            log: Dados do log a ser registrado
            
        Returns:
            Log registrado
        """
        self.logger.info(f"Registrando log: {log.acao} - {log.descricao}")
        
        # Converter para dicionário para enviar ao repositório
        log_data = log.model_dump()
        
        # Criar log no repositório
        try:
            return await self.repository.create(log_data)
        except Exception as e:
            self.logger.error(f"Erro ao registrar log: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao registrar log"
            )
        
    async def listar_logs(
        self,
        id_empresa: Optional[UUID] = None,
        id_usuario: Optional[UUID] = None,
        acao: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[LogSistema], int]:
        """
        Listar logs com paginação e filtros.
        
        Args:
            id_empresa: ID da empresa para filtrar
            id_usuario: ID do usuário para filtrar
            acao: Filtrar por tipo de ação
            skip: Número de registros a pular
            limit: Número máximo de registros a retornar
            
        Returns:
            Lista de logs e contagem total
        """
        self.logger.info(f"Buscando logs com filtros: empresa={id_empresa}, usuario={id_usuario}, acao={acao}")
        
        filters = []
        
        if id_empresa:
            filters.append({"id_empresa": id_empresa})
            
        if id_usuario:
            filters.append({"id_usuario": id_usuario})
            
        if acao:
            filters.append({"acao": acao})
            
        return await self.repository.list_with_filters(
            skip=skip,
            limit=limit,
            filters=filters
        )
        
    async def get_log(self, id_log: UUID) -> LogSistema:
        """
        Obter log pelo ID.
        
        Args:
            id_log: ID do log
            
        Returns:
            Log encontrado
            
        Raises:
            HTTPException: Se o log não for encontrado
        """
        self.logger.info(f"Buscando log ID: {id_log}")
        
        log = await self.repository.get_by_id(id_log)
        if not log:
            self.logger.warning(f"Log não encontrado: {id_log}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Log não encontrado"
            )
        return log
    
    async def limpar_logs_antigos(
        self,
        dias: int = 90,
        id_empresa: Optional[UUID] = None
    ) -> int:
        """
        Remove logs mais antigos que o período especificado.
        
        Args:
            dias: Número de dias para manter logs (padrão: 90)
            id_empresa: ID da empresa para limitar a limpeza (opcional)
            
        Returns:
            int: Número de logs removidos
        """
        self.logger.info(f"Limpando logs antigos (mais de {dias} dias)")
        
        try:
            quantidade = await self.repository.limpar_logs_antigos(
                dias=dias,
                id_empresa=id_empresa
            )
            
            return quantidade
            
        except Exception as e:
            self.logger.error(f"Erro ao limpar logs antigos: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao limpar logs antigos: {str(e)}"
            ) 