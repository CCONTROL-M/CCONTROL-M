"""Repositório para operações de banco de dados relacionadas a vendas."""
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.venda import Venda
from app.models.produto import Produto
from app.models.cliente import Cliente
from app.models.item_venda import ItemVenda
from app.models.empresa import Empresa
from app.models.forma_pagamento import FormaPagamento


class VendaRepository:
    """Repositório para operações com vendas."""

    def __init__(self, session: AsyncSession):
        """Inicializar repositório com sessão."""
        self.session = session

    async def get_by_id(self, id_venda: UUID, id_empresa: Optional[UUID] = None) -> Optional[Venda]:
        """
        Obter venda pelo ID.
        
        Args:
            id_venda: ID da venda
            id_empresa: ID da empresa para verificação (opcional)
            
        Returns:
            Venda se encontrada, None caso contrário
        """
        query = (
            select(Venda)
            .options(
                selectinload(Venda.itens).selectinload(ItemVenda.produto),
                selectinload(Venda.cliente),
                selectinload(Venda.forma_pagamento)
            )
            .where(Venda.id_venda == id_venda)
        )
        
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
        Listar vendas por empresa com filtros.
        
        Args:
            id_empresa: ID da empresa
            skip: Registros para pular na paginação
            limit: Máximo de registros para retornar
            data_inicio: Filtrar por data inicial
            data_fim: Filtrar por data final
            id_cliente: Filtrar por cliente
            status: Filtrar por status
            forma_pagamento: Filtrar por forma de pagamento
            
        Returns:
            Lista de vendas e contagem total
        """
        # Consulta principal para vendas
        query = (
            select(Venda)
            .options(
                selectinload(Venda.cliente),
                selectinload(Venda.forma_pagamento)
            )
            .where(Venda.id_empresa == id_empresa)
        )
        
        # Consulta para contagem
        count_query = (
            select(func.count())
            .select_from(Venda)
            .where(Venda.id_empresa == id_empresa)
        )
        
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
        query = query.order_by(desc(Venda.data_venda))
        
        # Executar consulta de contagem
        count_result = await self.session.execute(count_query)
        total_count = count_result.scalar_one() or 0
        
        # Aplicar paginação
        query = query.offset(skip).limit(limit)
        
        # Executar consulta principal
        result = await self.session.execute(query)
        vendas = result.scalars().all()
        
        return list(vendas), total_count

    async def get_with_items(self, id_venda: UUID, id_empresa: Optional[UUID] = None) -> Optional[Venda]:
        """
        Obter venda com seus itens pelo ID.
        
        Args:
            id_venda: ID da venda
            id_empresa: ID da empresa para verificação (opcional)
            
        Returns:
            Venda com itens se encontrada, None caso contrário
        """
        query = (
            select(Venda)
            .options(
                selectinload(Venda.itens).selectinload(ItemVenda.produto),
                selectinload(Venda.cliente),
                selectinload(Venda.forma_pagamento)
            )
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
        try:
            # Criar objeto Venda
            venda = Venda(**venda_data)
            
            # Salvar a venda
            self.session.add(venda)
            await self.session.commit()
            await self.session.refresh(venda)
            
            return venda
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao criar venda: {str(e)}"
            )

    async def update(self, id_venda: UUID, id_empresa: UUID, venda_data: Dict[str, Any]) -> Optional[Venda]:
        """
        Atualizar venda existente.
        
        Args:
            id_venda: ID da venda
            id_empresa: ID da empresa para verificação
            venda_data: Dados para atualização
            
        Returns:
            Venda atualizada ou None se não encontrada
        """
        try:
            # Verificar se a venda existe
            query = (
                select(Venda)
                .where(Venda.id_venda == id_venda)
                .where(Venda.id_empresa == id_empresa)
            )
            
            result = await self.session.execute(query)
            venda = result.scalar_one_or_none()
            
            if not venda:
                return None
                
            # Atualizar atributos
            for key, value in venda_data.items():
                if hasattr(venda, key):
                    setattr(venda, key, value)
            
            # Salvar alterações
            self.session.add(venda)
            await self.session.commit()
            await self.session.refresh(venda)
            
            return venda
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao atualizar venda: {str(e)}"
            )

    async def delete(self, id_venda: UUID, id_empresa: UUID) -> bool:
        """
        Excluir venda pelo ID.
        
        Args:
            id_venda: ID da venda
            id_empresa: ID da empresa para verificação
            
        Returns:
            True se removida com sucesso
        """
        try:
            # Verificar se a venda existe
            query = (
                select(Venda)
                .where(Venda.id_venda == id_venda)
                .where(Venda.id_empresa == id_empresa)
            )
            
            result = await self.session.execute(query)
            venda = result.scalar_one_or_none()
            
            if not venda:
                return False
                
            # Excluir a venda
            await self.session.delete(venda)
            await self.session.commit()
            
            return True
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao excluir venda: {str(e)}"
            )

    async def create_item_venda(self, id_venda: UUID, id_empresa: UUID, item_data: Dict[str, Any]) -> ItemVenda:
        """
        Adicionar item à venda.
        
        Args:
            id_venda: ID da venda
            id_empresa: ID da empresa para verificação
            item_data: Dados do item
            
        Returns:
            Item criado
        """
        try:
            # Verificar se a venda existe
            query = (
                select(Venda)
                .where(Venda.id_venda == id_venda)
                .where(Venda.id_empresa == id_empresa)
            )
            
            result = await self.session.execute(query)
            venda = result.scalar_one_or_none()
            
            if not venda:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Venda não encontrada"
                )
                
            # Criar o item da venda
            item_venda_data = item_data.copy()
            item_venda_data["id_venda"] = id_venda
            
            # Criar item
            item = ItemVenda(**item_venda_data)
            
            # Salvar o item
            self.session.add(item)
            await self.session.commit()
            await self.session.refresh(item)
            
            # Recalcular valor total da venda
            await self.recalcular_valor_venda(id_venda)
            
            return item
        except HTTPException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao criar item: {str(e)}"
            )

    async def update_item_venda(
        self, 
        id_venda: UUID, 
        id_item: UUID, 
        id_empresa: UUID, 
        item_data: Dict[str, Any]
    ) -> ItemVenda:
        """
        Atualizar item da venda.
        
        Args:
            id_venda: ID da venda
            id_item: ID do item
            id_empresa: ID da empresa para verificação
            item_data: Dados para atualização
            
        Returns:
            Item atualizado
        """
        try:
            # Verificar se a venda existe e pertence à empresa
            query_venda = (
                select(Venda)
                .where(Venda.id_venda == id_venda)
                .where(Venda.id_empresa == id_empresa)
            )
            
            result_venda = await self.session.execute(query_venda)
            venda = result_venda.scalar_one_or_none()
            
            if not venda:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Venda não encontrada"
                )
                
            # Verificar se o item existe
            query_item = (
                select(ItemVenda)
                .where(ItemVenda.id_item_venda == id_item)
                .where(ItemVenda.id_venda == id_venda)
            )
            
            result_item = await self.session.execute(query_item)
            item = result_item.scalar_one_or_none()
            
            if not item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Item não encontrado"
                )
                
            # Atualizar atributos do item
            for key, value in item_data.items():
                if hasattr(item, key):
                    setattr(item, key, value)
            
            # Salvar alterações
            self.session.add(item)
            await self.session.commit()
            await self.session.refresh(item)
            
            # Recalcular valor total da venda
            await self.recalcular_valor_venda(id_venda)
            
            return item
        except HTTPException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao atualizar item: {str(e)}"
            )

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
        try:
            # Verificar se a venda existe e pertence à empresa
            query_venda = (
                select(Venda)
                .where(Venda.id_venda == id_venda)
                .where(Venda.id_empresa == id_empresa)
            )
            
            result_venda = await self.session.execute(query_venda)
            venda = result_venda.scalar_one_or_none()
            
            if not venda:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Venda não encontrada"
                )
                
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
            await self.session.commit()
            
            # Recalcular valor total da venda
            await self.recalcular_valor_venda(id_venda)
            
            return True
        except HTTPException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao excluir item: {str(e)}"
            )

    async def recalcular_valor_venda(self, id_venda: UUID) -> None:
        """
        Recalcular o valor total da venda com base em seus itens.
        
        Args:
            id_venda: ID da venda
        """
        try:
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
                await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao recalcular valor da venda: {str(e)}"
            )

    async def cancelar_venda(self, id_venda: UUID, id_empresa: UUID) -> Venda:
        """
        Cancelar uma venda.
        
        Args:
            id_venda: ID da venda
            id_empresa: ID da empresa para verificação
            
        Returns:
            Venda cancelada
        """
        try:
            # Verificar se a venda existe
            query = (
                select(Venda)
                .where(Venda.id_venda == id_venda)
                .where(Venda.id_empresa == id_empresa)
            )
            
            result = await self.session.execute(query)
            venda = result.scalar_one_or_none()
            
            if not venda:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Venda não encontrada"
                )
                
            # Alterar status para cancelado
            venda.status = "cancelado"
            venda.data_cancelamento = datetime.now()
            
            # Salvar alterações
            self.session.add(venda)
            await self.session.commit()
            await self.session.refresh(venda)
            
            return venda
        except HTTPException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao cancelar venda: {str(e)}"
            ) 