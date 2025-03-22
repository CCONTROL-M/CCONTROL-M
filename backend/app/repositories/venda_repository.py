"""Repositório para operações de banco de dados relacionadas a vendas."""
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy import or_, select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.venda import Venda, ItemVenda
from app.models.cliente import Cliente
from app.models.produto import Produto

class VendaRepository:
    """Repositório para operações com vendas."""
    
    def __init__(self, session: AsyncSession):
        """Inicializar repositório com sessão."""
        self.session = session
    
    async def get_by_id(self, id_venda: UUID, id_empresa: Optional[UUID] = None) -> Optional[Venda]:
        """
        Buscar venda pelo ID.
        
        Args:
            id_venda: ID da venda
            id_empresa: ID da empresa para validação (opcional)
            
        Returns:
            Venda se encontrada, None caso contrário
        """
        query = select(Venda).where(Venda.id_venda == id_venda)
        
        if id_empresa:
            query = query.where(Venda.id_empresa == id_empresa)
            
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_empresa(
        self, 
        id_empresa: UUID,
        skip: int = 0,
        limit: int = 100,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        id_cliente: Optional[UUID] = None,
        status: Optional[str] = None,
        forma_pagamento: Optional[UUID] = None
    ) -> Tuple[List[Venda], int]:
        """
        Buscar vendas de uma empresa com filtros.
        
        Args:
            id_empresa: ID da empresa
            skip: Registros para pular
            limit: Limite de registros
            data_inicio: Data inicial para filtro
            data_fim: Data final para filtro
            id_cliente: ID do cliente para filtro
            status: Status da venda para filtro
            forma_pagamento: ID da forma de pagamento para filtro
            
        Returns:
            Tuple com lista de vendas e contagem total
        """
        # Consulta para lista
        query = select(Venda).where(Venda.id_empresa == id_empresa)
        
        # Consulta para contagem
        count_query = select(func.count()).select_from(Venda).where(Venda.id_empresa == id_empresa)
        
        # Aplicar filtros
        if data_inicio:
            query = query.where(Venda.data_venda >= data_inicio)
            count_query = count_query.where(Venda.data_venda >= data_inicio)
            
        if data_fim:
            query = query.where(Venda.data_venda <= data_fim)
            count_query = count_query.where(Venda.data_venda <= data_fim)
            
        if id_cliente:
            query = query.where(Venda.id_cliente == id_cliente)
            count_query = count_query.where(Venda.id_cliente == id_cliente)
            
        if status:
            query = query.where(Venda.status == status)
            count_query = count_query.where(Venda.status == status)
            
        if forma_pagamento:
            query = query.where(Venda.id_forma_pagamento == forma_pagamento)
            count_query = count_query.where(Venda.id_forma_pagamento == forma_pagamento)
        
        # Ordenar por data mais recente
        query = query.order_by(Venda.data_venda.desc())
        
        # Buscar contagem
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one() or 0
        
        # Aplicar paginação
        query = query.offset(skip).limit(limit)
        
        # Executar consulta principal
        result = await self.session.execute(query)
        vendas = result.scalars().all()
        
        return list(vendas), total
    
    async def get_with_items(self, id_venda: UUID, id_empresa: Optional[UUID] = None) -> Optional[Venda]:
        """
        Buscar venda pelo ID com itens inclusos.
        
        Args:
            id_venda: ID da venda
            id_empresa: ID da empresa para validação (opcional)
            
        Returns:
            Venda se encontrada, None caso contrário
        """
        query = (
            select(Venda)
            .options(selectinload(Venda.itens))
            .where(Venda.id_venda == id_venda)
        )
        
        if id_empresa:
            query = query.where(Venda.id_empresa == id_empresa)
            
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def create(self, venda_data: Dict[str, Any]) -> Venda:
        """
        Criar nova venda.
        
        Args:
            venda_data: Dados da venda
            
        Returns:
            Venda criada
        """
        # Criar objeto Venda
        venda = Venda(**venda_data)
        
        # Salvar venda
        self.session.add(venda)
        await self.session.flush()
        
        return venda
    
    async def update(self, id_venda: UUID, id_empresa: UUID, venda_data: Dict[str, Any]) -> Optional[Venda]:
        """
        Atualizar venda existente.
        
        Args:
            id_venda: ID da venda
            id_empresa: ID da empresa para validação
            venda_data: Dados para atualização
            
        Returns:
            Venda atualizada
        """
        # Buscar venda
        venda = await self.get_by_id(id_venda, id_empresa)
        
        if not venda:
            return None
            
        # Atualizar campos
        for key, value in venda_data.items():
            if hasattr(venda, key):
                setattr(venda, key, value)
        
        # Salvar alterações
        self.session.add(venda)
        await self.session.flush()
        
        return venda
    
    async def delete(self, id_venda: UUID, id_empresa: UUID) -> bool:
        """
        Excluir venda pelo ID.
        
        Args:
            id_venda: ID da venda
            id_empresa: ID da empresa para validação
            
        Returns:
            True se excluído com sucesso
        """
        # Buscar venda
        venda = await self.get_by_id(id_venda, id_empresa)
        
        if not venda:
            return False
            
        # Excluir venda
        await self.session.delete(venda)
        await self.session.flush()
        
        return True
    
    async def create_item_venda(self, id_venda: UUID, id_empresa: UUID, item_data: Dict[str, Any]) -> ItemVenda:
        """
        Criar item para uma venda.
        
        Args:
            id_venda: ID da venda
            id_empresa: ID da empresa para validação
            item_data: Dados do item
            
        Returns:
            Item criado
        """
        # Verificar se a venda existe e pertence à empresa
        venda = await self.get_by_id(id_venda, id_empresa)
        
        if not venda:
            return None
            
        # Adicionar ID da venda ao item
        item_data["id_venda"] = id_venda
        
        # Criar item
        item = ItemVenda(**item_data)
        
        # Salvar o item
        self.session.add(item)
        await self.session.flush()
        
        # Recalcular valor total da venda
        await self.recalcular_valor_venda(id_venda)
        
        return item

    async def update_item_venda(
        self, 
        id_venda: UUID, 
        id_item: UUID, 
        id_empresa: UUID, 
        item_data: Dict[str, Any]
    ) -> Optional[ItemVenda]:
        """
        Atualizar item da venda.
        
        Args:
            id_venda: ID da venda
            id_item: ID do item
            id_empresa: ID da empresa para verificação
            item_data: Dados para atualização
            
        Returns:
            Item atualizado ou None se não encontrado
        """
        # Verificar se a venda existe e pertence à empresa
        venda = await self.get_by_id(id_venda, id_empresa)
        
        if not venda:
            return None
                
        # Verificar se o item existe
        query_item = (
            select(ItemVenda)
            .where(ItemVenda.id_item_venda == id_item)
            .where(ItemVenda.id_venda == id_venda)
        )
        
        result_item = await self.session.execute(query_item)
        item = result_item.scalar_one_or_none()
        
        if not item:
            return None
                
        # Atualizar atributos do item
        for key, value in item_data.items():
            if hasattr(item, key):
                setattr(item, key, value)
        
        # Salvar alterações
        self.session.add(item)
        await self.session.flush()
        
        # Recalcular valor total da venda
        await self.recalcular_valor_venda(id_venda)
        
        return item

    async def delete_item_venda(self, id_venda: UUID, id_item: UUID, id_empresa: UUID) -> bool:
        """
        Remover item da venda.
        
        Args:
            id_venda: ID da venda
            id_item: ID do item
            id_empresa: ID da empresa para verificação
            
        Returns:
            True se removido com sucesso
        """
        # Verificar se a venda existe e pertence à empresa
        venda = await self.get_by_id(id_venda, id_empresa)
        
        if not venda:
            return False
                
        # Verificar se o item existe
        query_item = (
            select(ItemVenda)
            .where(ItemVenda.id_item_venda == id_item)
            .where(ItemVenda.id_venda == id_venda)
        )
        
        result_item = await self.session.execute(query_item)
        item = result_item.scalar_one_or_none()
        
        if not item:
            return False
                
        # Excluir o item
        await self.session.delete(item)
        await self.session.flush()
        
        # Recalcular valor total da venda
        await self.recalcular_valor_venda(id_venda)
        
        return True

    async def recalcular_valor_venda(self, id_venda: UUID) -> None:
        """
        Recalcular o valor total da venda com base em seus itens.
        
        Args:
            id_venda: ID da venda
        """
        # Buscar todos os itens da venda
        query_itens = (
            select(ItemVenda)
            .where(ItemVenda.id_venda == id_venda)
        )
        
        result_itens = await self.session.execute(query_itens)
        itens = result_itens.scalars().all()
        
        # Calcular valor total
        valor_total = sum(item.valor_unitario * item.quantidade for item in itens)
        
        # Buscar a venda
        query_venda = select(Venda).where(Venda.id_venda == id_venda)
        result_venda = await self.session.execute(query_venda)
        venda = result_venda.scalar_one_or_none()
        
        if venda:
            # Atualizar valor total
            venda.valor_total = valor_total
            self.session.add(venda)
            await self.session.flush()

    async def cancelar_venda(self, id_venda: UUID, id_empresa: UUID) -> Optional[Venda]:
        """
        Cancelar uma venda.
        
        Args:
            id_venda: ID da venda
            id_empresa: ID da empresa para verificação
            
        Returns:
            Venda cancelada ou None se não encontrada
        """
        # Verificar se a venda existe
        venda = await self.get_by_id(id_venda, id_empresa)
        
        if not venda:
            return None
                
        # Alterar status para cancelado
        venda.status = "cancelado"
        venda.data_cancelamento = datetime.now()
        
        # Salvar alterações
        self.session.add(venda)
        await self.session.flush()
        
        return venda

    async def commit(self):
        """Comitar as alterações pendentes."""
        await self.session.commit()
        
    async def rollback(self):
        """Reverter alterações pendentes."""
        await self.session.rollback() 