"""Repositório para operações de logs do sistema."""
import logging
import datetime
from uuid import UUID
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

from app.models.log_sistema import LogSistema


logger = logging.getLogger(__name__)


class LogSistemaRepository:
    """Repositório para operações de logs do sistema."""
    
    def __init__(self, session: AsyncSession):
        """Inicializa o repositório com a sessão do banco de dados."""
        self.session = session
    
    async def criar_log(
        self,
        acao: str,
        descricao: str = '',
        dados: Optional[Dict[str, Any]] = None,
        id_empresa: Optional[UUID] = None,
        id_usuario: Optional[UUID] = None
    ) -> LogSistema:
        """
        Cria um novo registro de log no sistema.
        
        Args:
            acao: Tipo de ação realizada
            descricao: Descrição detalhada da ação (opcional para compatibilidade)
            dados: Dados adicionais relacionados à ação (opcional)
            id_empresa: ID da empresa relacionada à ação (opcional)
            id_usuario: ID do usuário que realizou a ação (opcional)
            
        Returns:
            LogSistema: Objeto do log criado
            
        Raises:
            HTTPException: Se ocorrer um erro ao criar o log
        """
        try:
            logger.info(f"Criando log de sistema. Ação: {acao}")
            
            novo_log = LogSistema(
                acao=acao,
                descricao=descricao,
                dados=dados,
                id_empresa=id_empresa,
                id_usuario=id_usuario
            )
            
            self.session.add(novo_log)
            await self.session.commit()
            await self.session.refresh(novo_log)
            
            logger.info(f"Log de sistema criado com sucesso. ID: {novo_log.id_log}")
            return novo_log
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Erro ao criar log de sistema: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao criar log de sistema: {str(e)}"
            )
    
    async def get_by_id(self, id_log: UUID) -> Optional[LogSistema]:
        """
        Busca um log específico pelo ID.
        
        Args:
            id_log: ID do log a ser buscado
            
        Returns:
            Optional[LogSistema]: Log encontrado ou None
        """
        query = select(LogSistema).where(LogSistema.id_log == id_log)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_multi(
        self,
        id_empresa: Optional[UUID] = None,
        id_usuario: Optional[UUID] = None,
        acao: Optional[str] = None,
        busca: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        ordenar_por: str = "created_at",
        ordem: str = "desc"
    ) -> Tuple[List[LogSistema], int]:
        """
        Busca logs do sistema com filtros opcionais.
        
        Args:
            id_empresa: Filtrar por empresa
            id_usuario: Filtrar por usuário
            acao: Filtrar por tipo de ação
            busca: Termo para busca em descrição
            skip: Número de registros para pular
            limit: Limite de registros a retornar
            ordenar_por: Campo para ordenação
            ordem: Direção da ordenação (asc/desc)
            
        Returns:
            Tuple[List[LogSistema], int]: Lista de logs e contagem total
        """
        query = select(LogSistema)
        count_query = select(func.count()).select_from(LogSistema)
        
        # Aplicar filtros
        filters = []
        
        if id_empresa:
            filters.append(LogSistema.id_empresa == id_empresa)
            
        if id_usuario:
            filters.append(LogSistema.id_usuario == id_usuario)
            
        if acao:
            filters.append(LogSistema.acao == acao)
            
        if busca:
            filters.append(LogSistema.descricao.ilike(f"%{busca}%"))
        
        # Aplicar todos os filtros nas queries
        if filters:
            for filter_condition in filters:
                query = query.where(filter_condition)
                count_query = count_query.where(filter_condition)
        
        # Aplicar ordenação
        if hasattr(LogSistema, ordenar_por):
            order_column = getattr(LogSistema, ordenar_por)
            if ordem.lower() == "desc":
                query = query.order_by(desc(order_column))
            else:
                query = query.order_by(order_column)
        else:
            # Ordenação padrão por data de criação decrescente
            query = query.order_by(desc(LogSistema.created_at))
        
        # Aplicar paginação
        if limit > 0:
            query = query.offset(skip).limit(limit)
        
        # Executar as queries
        result = await self.session.execute(query)
        logs = list(result.scalars().all())
        
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()
        
        return logs, total
    
    async def get_count(self, filters: Optional[List] = None) -> int:
        """
        Obtém contagem de logs com filtros opcionais.
        
        Args:
            filters: Lista de condições de filtro (opcional)
            
        Returns:
            int: Total de logs que correspondem aos filtros
        """
        filters = filters or []
        query = select(func.count()).select_from(LogSistema).where(*filters)
        result = await self.session.execute(query)
        return result.scalar_one()
    
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
            
        Raises:
            HTTPException: Se ocorrer um erro ao limpar os logs
        """
        try:
            data_limite = datetime.datetime.now() - datetime.timedelta(days=dias)
            
            # Construir a query
            query = select(LogSistema).where(LogSistema.created_at < data_limite)
            
            if id_empresa:
                query = query.where(LogSistema.id_empresa == id_empresa)
            
            result = await self.session.execute(query)
            logs_antigos = list(result.scalars().all())
            
            quantidade = len(logs_antigos)
            
            # Remover os logs
            for log in logs_antigos:
                self.session.delete(log)
            
            await self.session.commit()
            logger.info(f"Removidos {quantidade} logs antigos (mais de {dias} dias)")
            return quantidade
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Erro ao limpar logs antigos: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao limpar logs antigos: {str(e)}"
            )
    
    async def remove_all(self, id_empresa: Optional[UUID] = None) -> int:
        """
        Remove todos os logs do sistema ou de uma empresa específica.
        
        Args:
            id_empresa: ID da empresa para limitar a remoção (opcional)
            
        Returns:
            int: Número de logs removidos
            
        Raises:
            HTTPException: Se ocorrer um erro ao remover os logs
        """
        try:
            query = select(LogSistema)
            
            if id_empresa:
                query = query.where(LogSistema.id_empresa == id_empresa)
            
            result = await self.session.execute(query)
            logs = list(result.scalars().all())
            
            quantidade = len(logs)
            
            for log in logs:
                self.session.delete(log)
            
            await self.session.commit()
            logger.info(f"Removidos {quantidade} logs do sistema")
            return quantidade
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Erro ao remover todos os logs: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao remover todos os logs: {str(e)}"
            ) 