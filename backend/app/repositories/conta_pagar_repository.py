"""Repositório para acesso aos dados de contas a pagar."""
from uuid import UUID
from typing import Optional, List, Tuple
from datetime import date

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conta_pagar import ContaPagar
from app.schemas.conta_pagar import ContaPagarCreate, ContaPagarUpdate, StatusContaPagar


class ContaPagarRepository:
    """Repositório para acesso aos dados de contas a pagar."""

    def __init__(self, session: AsyncSession):
        """Inicializa o repositório com a sessão do banco de dados."""
        self.session = session

    async def create(self, conta: ContaPagarCreate, empresa_id: UUID) -> ContaPagar:
        """
        Criar uma nova conta a pagar.
        
        Args:
            conta: Dados da conta a pagar
            empresa_id: ID da empresa
            
        Returns:
            Conta a pagar criada
        """
        db_conta = ContaPagar(
            descricao=conta.descricao,
            valor=conta.valor,
            data_vencimento=conta.data_vencimento,
            data_pagamento=conta.data_pagamento,
            status=conta.status,
            observacao=conta.observacao,
            fornecedor_id=conta.fornecedor_id,
            categoria_id=conta.categoria_id,
            empresa_id=empresa_id
        )
        
        self.session.add(db_conta)
        await self.session.flush()
        
        return db_conta

    async def update(
        self,
        id_conta: UUID,
        conta: ContaPagarUpdate,
        empresa_id: UUID
    ) -> ContaPagar:
        """
        Atualizar uma conta a pagar existente.
        
        Args:
            id_conta: ID da conta a pagar
            conta: Dados para atualização
            empresa_id: ID da empresa
            
        Returns:
            Conta a pagar atualizada
        """
        db_conta = await self.get_by_id(id_conta, empresa_id)
        
        # Atualizar apenas campos fornecidos
        update_data = conta.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_conta, field, value)
            
        await self.session.flush()
        
        return db_conta

    async def delete(self, id_conta: UUID, empresa_id: UUID) -> None:
        """
        Remover uma conta a pagar.
        
        Args:
            id_conta: ID da conta a pagar
            empresa_id: ID da empresa
        """
        db_conta = await self.get_by_id(id_conta, empresa_id)
        await self.session.delete(db_conta)
        await self.session.flush()

    async def get_by_id(self, id_conta: UUID, empresa_id: UUID) -> Optional[ContaPagar]:
        """
        Buscar uma conta a pagar pelo ID.
        
        Args:
            id_conta: ID da conta a pagar
            empresa_id: ID da empresa
            
        Returns:
            Conta a pagar encontrada ou None
        """
        query = select(ContaPagar).where(
            and_(
                ContaPagar.id_conta == id_conta,
                ContaPagar.empresa_id == empresa_id
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        empresa_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status: Optional[StatusContaPagar] = None,
        data_inicial: Optional[date] = None,
        data_final: Optional[date] = None,
        fornecedor_id: Optional[UUID] = None,
        categoria_id: Optional[UUID] = None,
        busca: Optional[str] = None
    ) -> Tuple[List[ContaPagar], int]:
        """
        Buscar múltiplas contas a pagar com filtros.
        
        Args:
            empresa_id: ID da empresa
            skip: Número de registros para pular
            limit: Número máximo de registros
            status: Filtrar por status
            data_inicial: Data inicial para filtro
            data_final: Data final para filtro
            fornecedor_id: Filtrar por fornecedor
            categoria_id: Filtrar por categoria
            busca: Termo para busca
            
        Returns:
            Tupla com lista de contas a pagar e total de registros
        """
        # Construir query base
        query = select(ContaPagar).where(ContaPagar.empresa_id == empresa_id)
        
        # Aplicar filtros
        if status:
            query = query.where(ContaPagar.status == status)
            
        if data_inicial:
            query = query.where(ContaPagar.data_vencimento >= data_inicial)
            
        if data_final:
            query = query.where(ContaPagar.data_vencimento <= data_final)
            
        if fornecedor_id:
            query = query.where(ContaPagar.fornecedor_id == fornecedor_id)
            
        if categoria_id:
            query = query.where(ContaPagar.categoria_id == categoria_id)
            
        if busca:
            query = query.where(
                or_(
                    ContaPagar.descricao.ilike(f"%{busca}%"),
                    ContaPagar.observacao.ilike(f"%{busca}%")
                )
            )
        
        # Contar total
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query)
        
        # Aplicar paginação
        query = query.offset(skip).limit(limit)
        
        # Executar query
        result = await self.session.execute(query)
        contas = result.scalars().all()
        
        return list(contas), total

    async def commit(self) -> None:
        """Commit das alterações na sessão."""
        await self.session.commit()
        
    async def rollback(self) -> None:
        """Rollback das alterações na sessão."""
        await self.session.rollback() 