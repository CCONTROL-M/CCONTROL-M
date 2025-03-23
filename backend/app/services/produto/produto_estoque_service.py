"""Serviço especializado para gestão de estoque de produtos no sistema CCONTROL-M."""
from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
import logging
from decimal import Decimal

from app.repositories.produto_repository import ProdutoRepository
from app.schemas.produto import Produto as ProdutoSchema, EstoqueUpdate, MovimentacaoEstoque


class ProdutoEstoqueService:
    """
    Serviço especializado para gestão de estoque de produtos.
    
    Esta classe implementa todas as operações relacionadas ao estoque de produtos,
    incluindo entrada, saída, ajustes e validações.
    """
    
    def __init__(self, session: AsyncSession):
        """Inicializar serviço com repositório."""
        self.repository = ProdutoRepository(session)
        self.logger = logging.getLogger(__name__)
    
    async def atualizar_estoque(
        self,
        id_produto: UUID,
        id_empresa: UUID,
        estoque_data: EstoqueUpdate
    ) -> ProdutoSchema:
        """
        Atualizar o estoque de um produto.
        
        Args:
            id_produto: ID do produto
            id_empresa: ID da empresa
            estoque_data: Dados para atualização de estoque
            
        Returns:
            Produto com estoque atualizado
        """
        try:
            # Verificar se o produto existe
            produto = await self.repository.get_by_id(id_produto, id_empresa)
            if not produto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Produto não encontrado"
                )
            
            # Verificar tipo de operação
            tipo = estoque_data.tipo.lower() if estoque_data.tipo else "entrada"
            is_entrada = tipo == "entrada"
            
            # Se for saída, verificar se há estoque suficiente
            if not is_entrada and produto.estoque_atual < estoque_data.quantidade:
                raise ValueError(
                    f"Estoque insuficiente. Disponível: {produto.estoque_atual}, Solicitado: {estoque_data.quantidade}"
                )
            
            # Atualizar estoque
            produto_atualizado = await self.repository.update_estoque(
                id_produto=id_produto,
                id_empresa=id_empresa,
                quantidade=estoque_data.quantidade,
                is_entrada=is_entrada
            )
            
            # Registrar movimentação de estoque
            await self._registrar_movimentacao(
                id_produto=id_produto,
                id_empresa=id_empresa,
                quantidade=estoque_data.quantidade,
                tipo=estoque_data.tipo or "entrada",
                observacao=estoque_data.observacao
            )
            
            return produto_atualizado
            
        except ValueError as e:
            self.logger.warning(f"Erro de validação ao atualizar estoque: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except HTTPException:
            raise  # Re-lançar exceções HTTP
        except Exception as e:
            self.logger.error(f"Erro ao atualizar estoque: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao atualizar estoque"
            )
    
    async def verificar_estoque_disponivel(
        self,
        id_produto: UUID,
        id_empresa: UUID,
        quantidade: Decimal
    ) -> bool:
        """
        Verificar se há estoque disponível para um produto.
        
        Args:
            id_produto: ID do produto
            id_empresa: ID da empresa
            quantidade: Quantidade a verificar
            
        Returns:
            True se houver estoque suficiente, False caso contrário
        """
        try:
            produto = await self.repository.get_by_id(id_produto, id_empresa)
            if not produto:
                return False
                
            return produto.estoque_atual >= quantidade
            
        except Exception as e:
            self.logger.error(f"Erro ao verificar estoque disponível: {str(e)}")
            return False
    
    async def _registrar_movimentacao(
        self,
        id_produto: UUID,
        id_empresa: UUID,
        quantidade: Decimal,
        tipo: str,
        observacao: Optional[str] = None
    ) -> None:
        """
        Registrar movimentação de estoque.
        
        Args:
            id_produto: ID do produto
            id_empresa: ID da empresa
            quantidade: Quantidade movimentada
            tipo: Tipo de movimentação (entrada/saída)
            observacao: Observação opcional
        """
        try:
            # Criar objeto de movimentação
            movimentacao = MovimentacaoEstoque(
                id_produto=id_produto,
                id_empresa=id_empresa,
                quantidade=quantidade,
                tipo=tipo,
                observacao=observacao or ""
            )
            
            # Registrar no repositório
            await self.repository.registrar_movimentacao_estoque(movimentacao)
            
        except Exception as e:
            # Apenas logamos erro, não interrompemos o fluxo
            self.logger.error(f"Erro ao registrar movimentação de estoque: {str(e)}")
    
    async def ajustar_estoque(
        self,
        id_produto: UUID,
        id_empresa: UUID,
        quantidade_atual: Decimal,
        observacao: Optional[str] = None
    ) -> ProdutoSchema:
        """
        Ajusta o estoque de um produto para uma quantidade específica.
        
        Args:
            id_produto: ID do produto
            id_empresa: ID da empresa
            quantidade_atual: Nova quantidade do estoque
            observacao: Observação opcional
            
        Returns:
            Produto com estoque ajustado
        """
        try:
            # Verificar se o produto existe
            produto = await self.repository.get_by_id(id_produto, id_empresa)
            if not produto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Produto não encontrado"
                )
            
            # Calcular a diferença para ajustar
            diferenca = quantidade_atual - produto.estoque_atual
            
            # Determinar se é entrada ou saída com base na diferença
            is_entrada = diferenca >= 0
            quantidade_ajuste = abs(diferenca)
            
            # Aplicar o ajuste
            produto_atualizado = await self.repository.update_estoque(
                id_produto=id_produto,
                id_empresa=id_empresa,
                quantidade=quantidade_ajuste,
                is_entrada=is_entrada
            )
            
            # Registrar movimentação
            await self._registrar_movimentacao(
                id_produto=id_produto,
                id_empresa=id_empresa,
                quantidade=quantidade_ajuste,
                tipo="ajuste",
                observacao=observacao or "Ajuste manual de estoque"
            )
            
            return produto_atualizado
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Erro ao ajustar estoque: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao ajustar estoque"
            ) 