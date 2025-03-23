"""Repositório para Contas a Receber."""
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from sqlalchemy import select, update, delete, and_, or_, func, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import Select
from uuid import UUID

from app.models.conta_receber import ContaReceber
from app.schemas.conta_receber import ContaReceberCreate, ContaReceberUpdate, StatusContaReceber
from app.repositories.base_repository import BaseRepository


class ContaReceberRepository(BaseRepository):
    """Repositório para operações com Contas a Receber."""

    def __init__(self, session: AsyncSession):
        """Inicializa o repositório com a sessão do banco de dados."""
        self.session = session
        self.model = ContaReceber

    async def create(self, conta_receber: ContaReceberCreate) -> ContaReceber:
        """
        Cria uma nova conta a receber.
        
        Args:
            conta_receber: Dados da conta a receber a ser criada
            
        Returns:
            Objeto ContaReceber criado
        """
        # Verificar status inicial baseado na data de vencimento
        status = StatusContaReceber.pendente
        if date.today() > conta_receber.data_vencimento:
            status = StatusContaReceber.atrasado
            
        # Criar objeto do modelo
        db_conta_receber = ContaReceber(
            id_empresa=conta_receber.id_empresa,
            id_cliente=conta_receber.id_cliente,
            id_venda=conta_receber.id_venda,
            descricao=conta_receber.descricao,
            valor=float(conta_receber.valor),
            data_emissao=conta_receber.data_emissao,
            data_vencimento=conta_receber.data_vencimento,
            observacoes=conta_receber.observacoes,
            status=status
        )
        
        # Adicionar à sessão e persistir
        self.session.add(db_conta_receber)
        await self.session.flush()
        
        return db_conta_receber

    async def update(self, id_conta_receber: UUID, conta_receber: ContaReceberUpdate) -> Optional[ContaReceber]:
        """
        Atualiza uma conta a receber existente.
        
        Args:
            id_conta_receber: ID da conta a receber a ser atualizada
            conta_receber: Dados a serem atualizados
            
        Returns:
            Objeto ContaReceber atualizado ou None se não encontrado
        """
        # Obter a conta existente
        db_conta_receber = await self.get_by_id(id_conta_receber)
        if not db_conta_receber:
            return None
            
        # Atualizar atributos
        update_data = conta_receber.dict(exclude_unset=True)
        
        # Se o valor ou data de vencimento foram alterados, recalcular o status
        recalcular_status = False
        if "status" not in update_data and ("valor" in update_data or "data_vencimento" in update_data):
            recalcular_status = True
        
        # Atualizar cada campo
        for key, value in update_data.items():
            setattr(db_conta_receber, key, value)
            
        # Recalcular status se necessário
        if recalcular_status:
            hoje = date.today()
            if db_conta_receber.status == StatusContaReceber.pendente and hoje > db_conta_receber.data_vencimento:
                db_conta_receber.status = StatusContaReceber.atrasado
            elif db_conta_receber.status == StatusContaReceber.atrasado and hoje <= db_conta_receber.data_vencimento:
                db_conta_receber.status = StatusContaReceber.pendente
        
        await self.session.flush()
        return db_conta_receber
        
    async def get_by_id(self, id_conta_receber: UUID) -> Optional[ContaReceber]:
        """
        Obtém uma conta a receber pelo ID.
        
        Args:
            id_conta_receber: ID da conta a receber
            
        Returns:
            Objeto ContaReceber ou None se não encontrado
        """
        query = select(ContaReceber).where(ContaReceber.id_conta_receber == id_conta_receber)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
        
    async def delete(self, id_conta_receber: UUID) -> bool:
        """
        Remove uma conta a receber.
        
        Args:
            id_conta_receber: ID da conta a receber a ser removida
            
        Returns:
            True se removido com sucesso, False caso contrário
        """
        conta = await self.get_by_id(id_conta_receber)
        if not conta:
            return False
            
        await self.session.delete(conta)
        await self.session.flush()
        return True
        
    async def list(
        self,
        id_empresa: UUID,
        skip: int = 0,
        limit: int = 100,
        status: Optional[StatusContaReceber] = None,
        cliente_id: Optional[UUID] = None,
        venda_id: Optional[UUID] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        apenas_vencidas: bool = False,
        ordenar_por: str = "data_vencimento",
        ordem: str = "asc"
    ) -> tuple[List[ContaReceber], int]:
        """
        Lista contas a receber com filtros.
        
        Args:
            id_empresa: ID da empresa
            skip: Registros para pular
            limit: Limite de registros
            status: Filtrar por status
            cliente_id: Filtrar por cliente
            venda_id: Filtrar por venda
            data_inicio: Data inicial para filtro
            data_fim: Data final para filtro
            apenas_vencidas: Mostrar apenas contas vencidas
            ordenar_por: Campo para ordenação
            ordem: Direção da ordenação (asc/desc)
            
        Returns:
            Lista de objetos ContaReceber e contagem total
        """
        # Construir consulta base
        query = select(ContaReceber).where(ContaReceber.id_empresa == id_empresa)
        
        # Aplicar filtros
        if status:
            query = query.where(ContaReceber.status == status)
        
        if cliente_id:
            query = query.where(ContaReceber.id_cliente == cliente_id)
            
        if venda_id:
            query = query.where(ContaReceber.id_venda == venda_id)
            
        if data_inicio:
            query = query.where(ContaReceber.data_vencimento >= data_inicio)
            
        if data_fim:
            query = query.where(ContaReceber.data_vencimento <= data_fim)
            
        if apenas_vencidas:
            hoje = date.today()
            query = query.where(
                and_(
                    ContaReceber.data_vencimento < hoje,
                    or_(
                        ContaReceber.status == StatusContaReceber.pendente,
                        ContaReceber.status == StatusContaReceber.atrasado
                    )
                )
            )
        
        # Ordenação
        if ordenar_por:
            direction = desc if ordem.lower() == "desc" else asc
            if hasattr(ContaReceber, ordenar_por):
                query = query.order_by(direction(getattr(ContaReceber, ordenar_por)))
        
        # Obter contagem total
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query)
        
        # Aplicar paginação
        query = query.offset(skip).limit(limit)
        
        # Executar consulta
        result = await self.session.execute(query)
        items = result.scalars().all()
        
        return items, total 