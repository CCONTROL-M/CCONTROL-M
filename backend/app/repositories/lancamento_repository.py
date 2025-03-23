"""Repositório para operações de banco de dados relacionadas a lançamentos financeiros."""
from uuid import UUID
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date

from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.lancamento import Lancamento
from app.models.cliente import Cliente
from app.models.fornecedor import Fornecedor
from app.models.conta_bancaria import ContaBancaria
from app.models.forma_pagamento import FormaPagamento


class LancamentoRepository:
    """Repositório para operações com lançamentos financeiros."""

    def __init__(self, session: AsyncSession):
        """Inicializar repositório com sessão."""
        self.session = session

    async def get_by_id(self, id_lancamento: UUID, id_empresa: Optional[UUID] = None) -> Optional[Lancamento]:
        """
        Obter lançamento pelo ID.
        
        Args:
            id_lancamento: ID do lançamento
            id_empresa: ID da empresa para verificação (opcional)
            
        Returns:
            Lançamento se encontrado, None caso contrário
        """
        query = (
            select(Lancamento)
            .options(
                selectinload(Lancamento.cliente),
                selectinload(Lancamento.fornecedor),
                selectinload(Lancamento.conta),
                selectinload(Lancamento.forma_pagamento)
            )
            .where(Lancamento.id_lancamento == id_lancamento)
        )
        
        if id_empresa:
            query = query.where(Lancamento.id_empresa == id_empresa)
            
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_empresa(
        self, 
        id_empresa: UUID,
        skip: int = 0,
        limit: int = 100,
        tipo: Optional[str] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        id_cliente: Optional[UUID] = None,
        id_fornecedor: Optional[UUID] = None,
        id_conta: Optional[UUID] = None,
        status: Optional[str] = None
    ) -> Tuple[List[Lancamento], int]:
        """
        Listar lançamentos por empresa com filtros.
        
        Args:
            id_empresa: ID da empresa
            skip: Registros para pular na paginação
            limit: Máximo de registros para retornar
            tipo: Filtrar por tipo (receita/despesa)
            data_inicio: Filtrar por data inicial
            data_fim: Filtrar por data final
            id_cliente: Filtrar por cliente
            id_fornecedor: Filtrar por fornecedor
            id_conta: Filtrar por conta bancária
            status: Filtrar por status
            
        Returns:
            Lista de lançamentos e contagem total
        """
        # Consulta principal para lançamentos
        query = (
            select(Lancamento)
            .options(
                selectinload(Lancamento.cliente),
                selectinload(Lancamento.fornecedor),
                selectinload(Lancamento.conta),
                selectinload(Lancamento.forma_pagamento)
            )
            .where(Lancamento.id_empresa == id_empresa)
        )
        
        # Consulta para contagem
        count_query = (
            select(func.count())
            .select_from(Lancamento)
            .where(Lancamento.id_empresa == id_empresa)
        )
        
        # Aplicar filtros
        if tipo:
            query = query.where(Lancamento.tipo == tipo)
            count_query = count_query.where(Lancamento.tipo == tipo)
            
        if data_inicio:
            query = query.where(Lancamento.data_lancamento >= data_inicio)
            count_query = count_query.where(Lancamento.data_lancamento >= data_inicio)
            
        if data_fim:
            query = query.where(Lancamento.data_lancamento <= data_fim)
            count_query = count_query.where(Lancamento.data_lancamento <= data_fim)
            
        if id_cliente:
            query = query.where(Lancamento.id_cliente == id_cliente)
            count_query = count_query.where(Lancamento.id_cliente == id_cliente)
            
        if id_fornecedor:
            query = query.where(Lancamento.id_fornecedor == id_fornecedor)
            count_query = count_query.where(Lancamento.id_fornecedor == id_fornecedor)
            
        if id_conta:
            query = query.where(Lancamento.id_conta == id_conta)
            count_query = count_query.where(Lancamento.id_conta == id_conta)
            
        if status:
            query = query.where(Lancamento.status == status)
            count_query = count_query.where(Lancamento.status == status)
        
        # Ordenar por data mais recente
        query = query.order_by(desc(Lancamento.data_lancamento))
        
        # Executar consulta de contagem
        count_result = await self.session.execute(count_query)
        total_count = count_result.scalar_one() or 0
        
        # Aplicar paginação
        query = query.offset(skip).limit(limit)
        
        # Executar consulta principal
        result = await self.session.execute(query)
        lancamentos = result.scalars().all()
        
        return list(lancamentos), total_count
    
    async def get_by_venda(self, id_venda: UUID) -> List[Lancamento]:
        """
        Obter lançamentos associados a uma venda.
        
        Args:
            id_venda: ID da venda
            
        Returns:
            Lista de lançamentos
        """
        query = (
            select(Lancamento)
            .where(Lancamento.id_venda == id_venda)
        )
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, lancamento_data: Dict[str, Any]) -> Lancamento:
        """
        Criar novo lançamento.
        
        Args:
            lancamento_data: Dados do lançamento
            
        Returns:
            Lançamento criado
        """
        try:
            # Criar objeto Lancamento
            lancamento = Lancamento(**lancamento_data)
            
            # Salvar o lançamento
            self.session.add(lancamento)
            await self.session.commit()
            await self.session.refresh(lancamento)
            
            return lancamento
        except Exception as e:
            await self.session.rollback()
            raise

    async def update(self, id_lancamento: UUID, id_empresa: UUID, lancamento_data: Dict[str, Any]) -> Optional[Lancamento]:
        """
        Atualizar lançamento existente.
        
        Args:
            id_lancamento: ID do lançamento
            id_empresa: ID da empresa para verificação
            lancamento_data: Dados para atualização
            
        Returns:
            Lançamento atualizado ou None se não encontrado
        """
        try:
            # Verificar se o lançamento existe
            query = (
                select(Lancamento)
                .where(Lancamento.id_lancamento == id_lancamento)
                .where(Lancamento.id_empresa == id_empresa)
            )
            
            result = await self.session.execute(query)
            lancamento = result.scalar_one_or_none()
            
            if not lancamento:
                return None
                
            # Atualizar atributos
            for key, value in lancamento_data.items():
                if hasattr(lancamento, key):
                    setattr(lancamento, key, value)
            
            # Salvar alterações
            self.session.add(lancamento)
            await self.session.commit()
            await self.session.refresh(lancamento)
            
            return lancamento
        except Exception as e:
            await self.session.rollback()
            raise

    async def delete(self, id_lancamento: UUID, id_empresa: UUID) -> bool:
        """
        Excluir lançamento pelo ID.
        
        Args:
            id_lancamento: ID do lançamento
            id_empresa: ID da empresa para verificação
            
        Returns:
            True se removido com sucesso
        """
        try:
            # Verificar se o lançamento existe
            query = (
                select(Lancamento)
                .where(Lancamento.id_lancamento == id_lancamento)
                .where(Lancamento.id_empresa == id_empresa)
            )
            
            result = await self.session.execute(query)
            lancamento = result.scalar_one_or_none()
            
            if not lancamento:
                return False
                
            # Excluir o lançamento
            await self.session.delete(lancamento)
            await self.session.commit()
            
            return True
        except Exception as e:
            await self.session.rollback()
            raise

    async def efetivar_lancamento(self, id_lancamento: UUID, id_empresa: UUID) -> Optional[Lancamento]:
        """
        Marcar lançamento como efetivado.
        
        Args:
            id_lancamento: ID do lançamento
            id_empresa: ID da empresa para verificação
            
        Returns:
            Lançamento atualizado ou None se não encontrado
        """
        # Buscar o lançamento
        lancamento = await self.get_by_id(id_lancamento, id_empresa)
        if not lancamento:
            return None
            
        # Atualizar o status
        lancamento.status = "EFETIVADO"
        lancamento.data_efetivacao = datetime.now()
        
        # Salvar as alterações
        await self.session.commit()
        await self.session.refresh(lancamento)
        
        return lancamento
    
    async def cancelar_lancamento(self, id_lancamento: UUID, id_empresa: UUID) -> Optional[Lancamento]:
        """
        Marcar lançamento como cancelado.
        
        Args:
            id_lancamento: ID do lançamento
            id_empresa: ID da empresa para verificação
            
        Returns:
            Lançamento atualizado ou None se não encontrado
        """
        # Buscar o lançamento
        lancamento = await self.get_by_id(id_lancamento, id_empresa)
        if not lancamento:
            return None
            
        # Atualizar o status
        lancamento.status = "CANCELADO"
        lancamento.data_cancelamento = datetime.now()
        
        # Salvar as alterações
        await self.session.commit()
        await self.session.refresh(lancamento)
        
        return lancamento 