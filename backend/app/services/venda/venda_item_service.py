"""Serviço especializado para gerenciamento de itens de venda."""
from uuid import UUID
from typing import Dict, Any, List, Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.venda_repository import VendaRepository
from app.repositories.produto_repository import ProdutoRepository
from app.schemas.venda import ItemVenda
from app.services.auditoria_service import AuditoriaService


class VendaItemService:
    """Serviço especializado para gerenciamento de itens de venda."""

    def __init__(
        self,
        session: AsyncSession,
        auditoria_service: AuditoriaService
    ):
        """Inicializa o serviço com a sessão do banco de dados."""
        self.repository = VendaRepository(session)
        self.produto_repository = ProdutoRepository(session)
        self.auditoria_service = auditoria_service
        
    async def _validar_acesso_venda(self, id_venda: UUID, id_empresa: UUID) -> None:
        """
        Valida se a venda existe e pertence à empresa.
        
        Args:
            id_venda: ID da venda
            id_empresa: ID da empresa
            
        Raises:
            HTTPException: Se a venda não existir ou não pertencer à empresa
        """
        venda = await self.repository.get_by_id(id_venda)
        
        if not venda:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Venda não encontrada"
            )
            
        if venda.id_empresa != id_empresa:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso não autorizado a esta venda"
            )
    
    async def _validar_produto(self, id_produto: UUID, id_empresa: UUID) -> None:
        """
        Valida se o produto existe e pertence à empresa.
        
        Args:
            id_produto: ID do produto
            id_empresa: ID da empresa
            
        Raises:
            HTTPException: Se o produto não existir ou não pertencer à empresa
        """
        produto = await self.produto_repository.get_by_id(id_produto)
        
        if not produto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado"
            )
            
        if produto.id_empresa != id_empresa:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso não autorizado a este produto"
            )
    
    async def adicionar_item_venda(
        self, 
        id_venda: UUID, 
        id_empresa: UUID, 
        item: ItemVenda
    ) -> ItemVenda:
        """
        Adicionar item a uma venda.
        
        Args:
            id_venda: ID da venda
            id_empresa: ID da empresa para validação de acesso
            item: Dados do item a ser adicionado
            
        Returns:
            Item adicionado
            
        Raises:
            HTTPException: Se ocorrer algum erro durante a operação
        """
        # Validar acesso à venda
        await self._validar_acesso_venda(id_venda, id_empresa)
        
        # Validar produto
        await self._validar_produto(item.id_produto, id_empresa)
        
        # Adicionar item
        try:
            # Obter item anterior para auditoria (se existir)
            item_anterior = None
            if hasattr(item, "id") and item.id:
                item_anterior = await self.repository.get_item_venda(id_venda, item.id)
            
            # Adicionar item à venda
            item_adicionado = await self.repository.adicionar_item_venda(id_venda, item)
            
            # Registrar auditoria
            await self.auditoria_service.registrar_acao(
                entidade="item_venda",
                acao="create",
                id_registro=str(item_adicionado.id),
                dados_anteriores={} if not item_anterior else item_anterior.dict(),
                dados_novos=item_adicionado.dict(),
                id_usuario=None  # Idealmente deveria ser passado como parâmetro
            )
            
            return item_adicionado
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erro ao adicionar item à venda: {str(e)}"
            )
    
    async def atualizar_item_venda(
        self, 
        id_venda: UUID, 
        id_item: UUID, 
        id_empresa: UUID, 
        item: ItemVenda
    ) -> ItemVenda:
        """
        Atualizar item de uma venda.
        
        Args:
            id_venda: ID da venda
            id_item: ID do item a ser atualizado
            id_empresa: ID da empresa para validação de acesso
            item: Dados atualizados do item
            
        Returns:
            Item atualizado
            
        Raises:
            HTTPException: Se ocorrer algum erro durante a operação
        """
        # Validar acesso à venda
        await self._validar_acesso_venda(id_venda, id_empresa)
        
        # Validar produto
        await self._validar_produto(item.id_produto, id_empresa)
        
        # Verificar se o item existe
        item_atual = await self.repository.get_item_venda(id_venda, id_item)
        if not item_atual:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item não encontrado na venda"
            )
        
        # Atualizar item
        try:
            item_atualizado = await self.repository.atualizar_item_venda(
                id_venda, 
                id_item, 
                item
            )
            
            # Registrar auditoria
            await self.auditoria_service.registrar_acao(
                entidade="item_venda",
                acao="update",
                id_registro=str(id_item),
                dados_anteriores=item_atual.dict(),
                dados_novos=item_atualizado.dict(),
                id_usuario=None  # Idealmente deveria ser passado como parâmetro
            )
            
            return item_atualizado
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erro ao atualizar item da venda: {str(e)}"
            )
    
    async def remover_item_venda(
        self, 
        id_venda: UUID, 
        id_item: UUID, 
        id_empresa: UUID
    ) -> Dict[str, Any]:
        """
        Remover item de uma venda.
        
        Args:
            id_venda: ID da venda
            id_item: ID do item a ser removido
            id_empresa: ID da empresa para validação de acesso
            
        Returns:
            Mensagem de sucesso
            
        Raises:
            HTTPException: Se ocorrer algum erro durante a operação
        """
        # Validar acesso à venda
        await self._validar_acesso_venda(id_venda, id_empresa)
        
        # Verificar se o item existe
        item = await self.repository.get_item_venda(id_venda, id_item)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item não encontrado na venda"
            )
        
        # Remover item
        try:
            resultado = await self.repository.remover_item_venda(id_venda, id_item)
            
            # Registrar auditoria
            await self.auditoria_service.registrar_acao(
                entidade="item_venda",
                acao="delete",
                id_registro=str(id_item),
                dados_anteriores=item.dict(),
                dados_novos={},
                id_usuario=None  # Idealmente deveria ser passado como parâmetro
            )
            
            return resultado
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erro ao remover item da venda: {str(e)}"
            ) 