"""Serviço para operações com compras."""
from uuid import UUID
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.compra import Compra, ItemCompra
from app.repositories.compra_repository import CompraRepository
from app.utils.format import parse_date


class CompraService:
    """Serviço para gerenciamento de compras."""
    
    def __init__(self, session: AsyncSession):
        """Inicializa o serviço com sessão de banco de dados."""
        self.session = session
        self.repository = CompraRepository(session)
    
    async def create(self, compra_data: Dict[str, Any]) -> Compra:
        """
        Criar nova compra.
        
        Args:
            compra_data: Dados da compra
            
        Returns:
            Compra criada
        """
        # Extrair itens para criar separadamente
        itens = compra_data.pop("itens", []) if hasattr(compra_data, "itens") else []
        
        # Criar a compra
        compra = await self.repository.create(
            {k: v for k, v in compra_data.dict().items() if k != "itens"}
        )
        
        # Se houver itens, criar um a um
        if itens:
            for item_data in itens:
                await self.repository.create_item_compra(
                    compra.id_compra, 
                    compra.id_empresa, 
                    item_data
                )
        
        # Commit para persistir alterações
        await self.repository.commit()
        
        return compra
    
    async def get_compra(
        self, 
        id_compra: UUID, 
        id_empresa: Optional[UUID] = None
    ) -> Optional[Compra]:
        """
        Buscar compra pelo ID.
        
        Args:
            id_compra: ID da compra
            id_empresa: ID da empresa para validação (opcional)
            
        Returns:
            Compra se encontrada, None caso contrário
        """
        compra = await self.repository.get_by_id(id_compra, id_empresa)
        
        if not compra:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Compra não encontrada"
            )
            
        return compra
    
    async def get_compra_completa(
        self, 
        id_compra: UUID, 
        id_empresa: Optional[UUID] = None
    ) -> Optional[Compra]:
        """
        Buscar compra pelo ID com itens e relacionamentos.
        
        Args:
            id_compra: ID da compra
            id_empresa: ID da empresa para validação (opcional)
            
        Returns:
            Compra se encontrada, None caso contrário
        """
        compra = await self.repository.get_with_items(id_compra, id_empresa)
        
        if not compra:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Compra não encontrada"
            )
            
        return compra
    
    async def get_compras(
        self, 
        id_empresa: UUID,
        id_fornecedor: Optional[UUID] = None,
        status: Optional[str] = None,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Compra], int]:
        """
        Buscar compras de uma empresa com filtros.
        
        Args:
            id_empresa: ID da empresa
            id_fornecedor: ID do fornecedor para filtro
            status: Status da compra para filtro
            data_inicio: Data inicial no formato YYYY-MM-DD
            data_fim: Data final no formato YYYY-MM-DD
            skip: Itens para pular
            limit: Itens por página
            
        Returns:
            Tuple com lista de compras e contagem total
        """
        # Converter strings de data para objetos datetime
        data_inicio_dt = parse_date(data_inicio) if data_inicio else None
        data_fim_dt = parse_date(data_fim, end_of_day=True) if data_fim else None
        
        # Buscar compras
        return await self.repository.get_by_empresa(
            id_empresa=id_empresa,
            id_fornecedor=id_fornecedor,
            status=status,
            data_inicio=data_inicio_dt,
            data_fim=data_fim_dt,
            skip=skip,
            limit=limit
        )
    
    async def update(
        self, 
        id_compra: UUID, 
        id_empresa: UUID, 
        compra_data: Dict[str, Any]
    ) -> Optional[Compra]:
        """
        Atualizar compra existente.
        
        Args:
            id_compra: ID da compra
            id_empresa: ID da empresa para validação
            compra_data: Dados para atualização
            
        Returns:
            Compra atualizada
        """
        # Verificar se a compra existe
        compra = await self.repository.get_by_id(id_compra, id_empresa)
        
        if not compra:
            return None
            
        # Atualizar compra
        dados_atualizacao = compra_data
        if hasattr(compra_data, "dict"):
            dados_atualizacao = {k: v for k, v in compra_data.dict(exclude_unset=True).items() if k != "itens"}
            
        compra = await self.repository.update(id_compra, id_empresa, dados_atualizacao)
        
        # Commit para persistir alterações
        await self.repository.commit()
        
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
        # Verificar se a compra existe
        compra = await self.repository.get_by_id(id_compra, id_empresa)
        
        if not compra:
            return False
            
        # Verificar se a compra já tem lançamentos associados
        # Aqui poderia ter verificação de lançamentos
        
        # Excluir compra
        sucesso = await self.repository.delete(id_compra, id_empresa)
        
        # Commit para persistir alterações
        await self.repository.commit()
        
        return sucesso
    
    async def cancelar_compra(self, id_compra: UUID, id_empresa: UUID) -> Optional[Compra]:
        """
        Cancelar uma compra.
        
        Args:
            id_compra: ID da compra
            id_empresa: ID da empresa para verificação
            
        Returns:
            Compra cancelada ou None se não encontrada
        """
        # Cancelar a compra
        compra = await self.repository.cancelar_compra(id_compra, id_empresa)
        
        if not compra:
            return None
            
        # Commit para persistir alterações
        await self.repository.commit()
        
        return compra
    
    async def create_item(
        self, 
        id_compra: UUID, 
        id_empresa: UUID, 
        item_data: Dict[str, Any]
    ) -> Optional[ItemCompra]:
        """
        Adicionar item à compra.
        
        Args:
            id_compra: ID da compra
            id_empresa: ID da empresa para validação
            item_data: Dados do item
            
        Returns:
            Item criado ou None
        """
        # Criar item
        item = await self.repository.create_item_compra(
            id_compra, 
            id_empresa, 
            item_data
        )
        
        if not item:
            return None
            
        # Commit para persistir alterações
        await self.repository.commit()
        
        return item
    
    async def update_item(
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
            id_empresa: ID da empresa para validação
            item_data: Dados para atualização
            
        Returns:
            Item atualizado ou None
        """
        # Atualizar item
        item = await self.repository.update_item_compra(
            id_compra, 
            id_item, 
            id_empresa, 
            item_data
        )
        
        if not item:
            return None
            
        # Commit para persistir alterações
        await self.repository.commit()
        
        return item
    
    async def delete_item(
        self, 
        id_compra: UUID, 
        id_item: UUID, 
        id_empresa: UUID
    ) -> bool:
        """
        Excluir item da compra.
        
        Args:
            id_compra: ID da compra
            id_item: ID do item
            id_empresa: ID da empresa para validação
            
        Returns:
            True se excluído com sucesso
        """
        # Excluir item
        sucesso = await self.repository.delete_item_compra(
            id_compra, 
            id_item, 
            id_empresa
        )
        
        if not sucesso:
            return False
            
        # Commit para persistir alterações
        await self.repository.commit()
        
        return True 