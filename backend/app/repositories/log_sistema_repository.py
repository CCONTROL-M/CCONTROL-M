"""Repositório para operações de logs do sistema."""
import logging
from uuid import UUID
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func, desc, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.log_sistema import LogSistema
from app.repositories.base_repository import BaseRepository


logger = logging.getLogger(__name__)


class LogSistemaRepository(BaseRepository):
    """Repositório para operações de logs do sistema."""
    
    async def criar_log(
        self,
        session: AsyncSession,
        acao: str,
        descricao: str = '',
        dados: Optional[Dict[str, Any]] = None,
        id_empresa: Optional[UUID] = None,
        id_usuario: Optional[UUID] = None
    ) -> LogSistema:
        """
        Cria um novo registro de log no sistema.
        
        Args:
            session: Sessão do banco de dados
            acao: Tipo de ação realizada
            descricao: Descrição detalhada da ação (opcional para compatibilidade)
            dados: Dados adicionais relacionados à ação (opcional)
            id_empresa: ID da empresa relacionada à ação (opcional)
            id_usuario: ID do usuário que realizou a ação (opcional)
            
        Returns:
            LogSistema: Objeto do log criado
        """
        logger.info(f"Criando log de sistema. Ação: {acao}")
        
        novo_log = LogSistema(
            acao=acao,
            descricao=descricao,
            dados=dados,
            id_empresa=id_empresa,
            id_usuario=id_usuario
        )
        
        session.add(novo_log)
        await session.flush()
        
        logger.info(f"Log de sistema criado com sucesso. ID: {novo_log.id_log}")
        return novo_log
    
    async def buscar_logs(
        self,
        session: AsyncSession,
        id_empresa: Optional[UUID] = None,
        id_usuario: Optional[UUID] = None,
        acao: Optional[str] = None,
        busca: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        ordenar_por: str = "created_at",
        ordem: str = "desc"
    ) -> tuple[List[LogSistema], int]:
        """
        Busca logs do sistema com filtros opcionais.
        
        Args:
            session: Sessão do banco de dados
            id_empresa: Filtrar por empresa
            id_usuario: Filtrar por usuário
            acao: Filtrar por tipo de ação
            busca: Termo para busca em descrição
            skip: Número de registros para pular
            limit: Limite de registros a retornar
            ordenar_por: Campo para ordenação
            ordem: Direção da ordenação (asc/desc)
            
        Returns:
            tuple: Lista de logs e contagem total
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
            
        if busca and hasattr(LogSistema, 'descricao'):
            filters.append(LogSistema.descricao.ilike(f"%{busca}%"))
        elif busca:
            # Fallback para busca no campo acao se descricao não existir
            filters.append(LogSistema.acao.ilike(f"%{busca}%"))
        
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
        result = await session.execute(query)
        logs = result.scalars().all()
        
        count_result = await session.execute(count_query)
        total = count_result.scalar()
        
        return logs, total
    
    async def buscar_log_por_id(
        self,
        session: AsyncSession,
        id_log: UUID
    ) -> Optional[LogSistema]:
        """
        Busca um log específico pelo ID.
        
        Args:
            session: Sessão do banco de dados
            id_log: ID do log a ser buscado
            
        Returns:
            Optional[LogSistema]: Log encontrado ou None
        """
        query = select(LogSistema).where(LogSistema.id_log == id_log)
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    async def limpar_logs_antigos(
        self,
        session: AsyncSession,
        dias: int = 90,
        id_empresa: Optional[UUID] = None
    ) -> int:
        """
        Remove logs mais antigos que o período especificado.
        
        Args:
            session: Sessão do banco de dados
            dias: Número de dias para manter logs (padrão: 90)
            id_empresa: ID da empresa para limitar a limpeza (opcional)
            
        Returns:
            int: Número de logs removidos
        """
        import datetime
        
        data_limite = datetime.datetime.now() - datetime.timedelta(days=dias)
        
        # Construir a query
        query = select(LogSistema).where(LogSistema.created_at < data_limite)
        
        if id_empresa:
            query = query.where(LogSistema.id_empresa == id_empresa)
        
        result = await session.execute(query)
        logs_antigos = result.scalars().all()
        
        quantidade = len(logs_antigos)
        
        # Remover os logs
        for log in logs_antigos:
            await session.delete(log)
        
        logger.info(f"Removidos {quantidade} logs antigos (mais de {dias} dias)")
        return quantidade 