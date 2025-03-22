"""Repositório para operações de banco de dados relacionadas a compras."""
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy import or_, select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.compra import Compra, ItemCompra
from app.models.fornecedor import Fornecedor
from app.models.produto import Produto

class CompraRepository:
    """Repositório para operações com compras."""
    
    def __init__(self, session: AsyncSession):
        """Inicializar repositório com sessão."""
        self.session = session
    
    async def get_by_id(self, id_compra: UUID, id_empresa: Optional[UUID] = None) -> Optional[Compra]:
        """
        Buscar compra pelo ID.
        
        Args:
            id_compra: ID da compra
            id_empresa: ID da empresa para validação (opcional)
            
        Returns:
            Compra se encontrada, None caso contrário
        """
        query = select(Compra).where(Compra.id_compra == id_compra)
        
        if id_empresa:
            query = query.where(Compra.id_empresa == id_empresa)
            
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_empresa(
        self, 
        id_empresa: UUID,
        skip: int = 0,
        limit: int = 100,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        id_fornecedor: Optional[UUID] = None,
        status: Optional[str] = None
    ) -> Tuple[List[Compra], int]:
        """
        Buscar compras de uma empresa com filtros.
        
        Args:
            id_empresa: ID da empresa
            skip: Registros para pular
            limit: Limite de registros
            data_inicio: Data inicial para filtro
            data_fim: Data final para filtro
            id_fornecedor: ID do fornecedor para filtro
            status: Status da compra para filtro
            
        Returns:
            Tuple com lista de compras e contagem total
        """
        # Consulta para lista
        query = select(Compra).where(Compra.id_empresa == id_empresa)
        
        # Consulta para contagem
        count_query = select(func.count()).select_from(Compra).where(Compra.id_empresa == id_empresa)
        
        # Aplicar filtros
        if data_inicio:
            query = query.where(Compra.data_compra >= data_inicio)
            count_query = count_query.where(Compra.data_compra >= data_inicio)
            
        if data_fim:
            query = query.where(Compra.data_compra <= data_fim)
            count_query = count_query.where(Compra.data_compra <= data_fim)
            
        if id_fornecedor:
            query = query.where(Compra.id_fornecedor == id_fornecedor)
            count_query = count_query.where(Compra.id_fornecedor == id_fornecedor)
            
        if status:
            query = query.where(Compra.status == status)
            count_query = count_query.where(Compra.status == status)
        
        # Ordenar por data mais recente
        query = query.order_by(Compra.data_compra.desc())
        
        # Buscar contagem
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one() or 0
        
        # Aplicar paginação
        query = query.offset(skip).limit(limit)
        
        # Executar consulta principal
        result = await self.session.execute(query)
        compras = result.scalars().all()
        
        return list(compras), total
    
    async def get_with_items(self, id_compra: UUID, id_empresa: Optional[UUID] = None) -> Optional[Compra]:
        """
        Buscar compra pelo ID com itens inclusos.
        
        Args:
            id_compra: ID da compra
            id_empresa: ID da empresa para validação (opcional)
            
        Returns:
            Compra se encontrada, None caso contrário
        """
        query = (
            select(Compra)
            .options(selectinload(Compra.itens))
            .where(Compra.id_compra == id_compra)
        )
        
        if id_empresa:
            query = query.where(Compra.id_empresa == id_empresa)
            
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def create(self, compra_data: Dict[str, Any]) -> Compra:
        """
        Criar nova compra.
        
        Args:
            compra_data: Dados da compra
            
        Returns:
            Compra criada
        """
        # Criar objeto Compra
        compra = Compra(**compra_data)
        
        # Salvar compra
        self.session.add(compra)
        await self.session.flush()
        
        return compra
    
    async def update(self, id_compra: UUID, id_empresa: UUID, compra_data: Dict[str, Any]) -> Optional[Compra]:
        """
        Atualizar compra existente.
        
        Args:
            id_compra: ID da compra
            id_empresa: ID da empresa para validação
            compra_data: Dados para atualização
            
        Returns:
            Compra atualizada
        """
        # Buscar compra
        compra = await self.get_by_id(id_compra, id_empresa)
        
        if not compra:
            return None
            
        # Atualizar campos
        for key, value in compra_data.items():
            if hasattr(compra, key):
                setattr(compra, key, value)
        
        # Salvar alterações
        self.session.add(compra)
        await self.session.flush()
        
        return compra
    
    async def delete(self, id_compra: UUID, id_empresa: UUID) -> bool:
        """
        Excluir compra pelo ID.
        
        Args:
            id_compra: ID da compra
            id_empresa: ID da empresa para validação
            
        Returns:
            True se excluído com sucesso
        """
        # Buscar compra
        compra = await self.get_by_id(id_compra, id_empresa)
        
        if not compra:
            return False
            
        # Excluir compra
        await self.session.delete(compra)
        await self.session.flush()
        
        return True
    
    async def create_item_compra(self, id_compra: UUID, id_empresa: UUID, item_data: Dict[str, Any]) -> ItemCompra:
        """
        Criar item para uma compra.
        
        Args:
            id_compra: ID da compra
            id_empresa: ID da empresa para validação
            item_data: Dados do item
            
        Returns:
            Item criado
        """
        # Verificar se a compra existe e pertence à empresa
        compra = await self.get_by_id(id_compra, id_empresa)
        
        if not compra:
            return None
            
        # Adicionar ID da compra ao item
        item_data["id_compra"] = id_compra
        
        # Criar item
        item = ItemCompra(**item_data)
        
        # Salvar o item
        self.session.add(item)
        await self.session.flush()
        
        # Recalcular valor total da compra
        await self.recalcular_valor_compra(id_compra)
        
        return item

    async def update_item_compra(
        self, 
        id_compra: UUID, 
        id_item: UUID, 
        id_empresa: UUID, 
        item_data: Dict[str, Any]
    ) -> Optional[ItemCompra]:
        """
        Atualizar item da compra.
        
        Args:
            id_compra: ID da compra
            id_item: ID do item
            id_empresa: ID da empresa para verificação
            item_data: Dados para atualização
            
        Returns:
            Item atualizado ou None se não encontrado
        """
        # Verificar se a compra existe e pertence à empresa
        compra = await self.get_by_id(id_compra, id_empresa)
        
        if not compra:
            return None
                
        # Verificar se o item existe
        query_item = (
            select(ItemCompra)
            .where(ItemCompra.id_item_compra == id_item)
            .where(ItemCompra.id_compra == id_compra)
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
        
        # Recalcular valor total da compra
        await self.recalcular_valor_compra(id_compra)
        
        return item

    async def delete_item_compra(self, id_compra: UUID, id_item: UUID, id_empresa: UUID) -> bool:
        """
        Remover item da compra.
        
        Args:
            id_compra: ID da compra
            id_item: ID do item
            id_empresa: ID da empresa para verificação
            
        Returns:
            True se removido com sucesso
        """
        # Verificar se a compra existe e pertence à empresa
        compra = await self.get_by_id(id_compra, id_empresa)
        
        if not compra:
            return False
                
        # Verificar se o item existe
        query_item = (
            select(ItemCompra)
            .where(ItemCompra.id_item_compra == id_item)
            .where(ItemCompra.id_compra == id_compra)
        )
        
        result_item = await self.session.execute(query_item)
        item = result_item.scalar_one_or_none()
        
        if not item:
            return False
                
        # Excluir o item
        await self.session.delete(item)
        await self.session.flush()
        
        # Recalcular valor total da compra
        await self.recalcular_valor_compra(id_compra)
        
        return True

    async def recalcular_valor_compra(self, id_compra: UUID) -> None:
        """
        Recalcular o valor total da compra com base em seus itens.
        
        Args:
            id_compra: ID da compra
        """
        # Buscar todos os itens da compra
        query_itens = (
            select(ItemCompra)
            .where(ItemCompra.id_compra == id_compra)
        )
        
        result_itens = await self.session.execute(query_itens)
        itens = result_itens.scalars().all()
        
        # Calcular valor total
        valor_total = sum(item.valor_unitario * item.quantidade for item in itens)
        
        # Buscar a compra
        query_compra = select(Compra).where(Compra.id_compra == id_compra)
        result_compra = await self.session.execute(query_compra)
        compra = result_compra.scalar_one_or_none()
        
        if compra:
            # Atualizar valor total
            compra.valor_total = valor_total
            self.session.add(compra)
            await self.session.flush()

    async def cancelar_compra(self, id_compra: UUID, id_empresa: UUID) -> Optional[Compra]:
        """
        Cancelar uma compra.
        
        Args:
            id_compra: ID da compra
            id_empresa: ID da empresa para verificação
            
        Returns:
            Compra cancelada ou None se não encontrada
        """
        # Verificar se a compra existe
        compra = await self.get_by_id(id_compra, id_empresa)
        
        if not compra:
            return None
                
        # Alterar status para cancelado
        compra.status = "cancelada"
        
        # Salvar alterações
        self.session.add(compra)
        await self.session.flush()
        
        return compra

    async def commit(self):
        """Comitar as alterações pendentes."""
        await self.session.commit()
        
    async def rollback(self):
        """Reverter alterações pendentes."""
        await self.session.rollback() 