"""Serviço especializado para consultas de produtos no sistema CCONTROL-M."""
from uuid import UUID
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from decimal import Decimal

from app.repositories.produto_repository import ProdutoRepository
from app.schemas.produto import Produto as ProdutoSchema
from app.schemas.pagination import PaginatedResponse


class ProdutoQueryService:
    """
    Serviço especializado para consultas de produtos.
    
    Esta classe implementa métodos de busca e listagem de produtos,
    centralizando a lógica de consulta.
    """
    
    def __init__(self, session: AsyncSession):
        """Inicializar serviço com repositório."""
        self.repository = ProdutoRepository(session)
        self.logger = logging.getLogger(__name__)
    
    async def get_by_id(
        self,
        id_produto: UUID,
        empresa_id: Optional[UUID] = None
    ) -> ProdutoSchema:
        """
        Buscar um produto pelo ID.
        
        Args:
            id_produto: ID do produto a ser buscado
            empresa_id: ID da empresa (opcional para verificação adicional)
            
        Returns:
            Produto encontrado
        """
        return await self.repository.get_by_id(id_produto, empresa_id)
    
    async def get_by_codigo(
        self,
        codigo: str,
        empresa_id: UUID
    ) -> Optional[ProdutoSchema]:
        """
        Buscar um produto pelo código.
        
        Args:
            codigo: Código do produto
            empresa_id: ID da empresa
            
        Returns:
            Produto encontrado ou None
        """
        return await self.repository.get_by_codigo(codigo, empresa_id)
    
    async def get_multi(
        self,
        empresa_id: UUID,
        skip: int = 0,
        limit: int = 100,
        categoria: Optional[str] = None,
        status: Optional[str] = None,
        busca: Optional[str] = None,
        order_by: str = "nome",
        order_direction: str = "asc"
    ) -> PaginatedResponse[ProdutoSchema]:
        """
        Buscar múltiplos produtos com filtros.
        
        Args:
            empresa_id: ID da empresa
            skip: Número de registros para pular
            limit: Número máximo de registros
            categoria: Filtrar por categoria
            status: Filtrar por status
            busca: Termo para busca
            order_by: Campo para ordenação
            order_direction: Direção da ordenação
            
        Returns:
            Lista paginada de produtos
        """
        try:
            # Construir filtros
            filtros = {
                "id_empresa": empresa_id
            }
            
            if categoria:
                filtros["categoria"] = categoria
                
            if status:
                filtros["ativo"] = status.lower() == "ativo"
            
            # Buscar produtos com filtros
            resultado = await self.repository.list_produtos(
                skip=skip,
                limit=limit,
                filtros=filtros,
                busca=busca,
                order_by=order_by,
                order_direction=order_direction
            )
            
            # Transformar em resposta paginada
            total = await self.repository.count_produtos(filtros, busca)
            page = skip // limit + 1
            
            return PaginatedResponse(
                items=resultado,
                total=total,
                page=page,
                size=limit if limit < total else total
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao listar produtos: {str(e)}")
            raise
    
    async def listar_produtos_estoque_baixo(
        self,
        empresa_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> PaginatedResponse[ProdutoSchema]:
        """
        Listar produtos com estoque abaixo do mínimo.
        
        Args:
            empresa_id: ID da empresa
            skip: Número de registros para pular
            limit: Número máximo de registros
            
        Returns:
            Lista paginada de produtos com estoque baixo
        """
        try:
            produtos, total = await self.repository.get_multi(
                empresa_id=empresa_id,
                skip=skip,
                limit=limit,
                estoque_baixo=True
            )
            
            return PaginatedResponse(
                items=produtos,
                total=total,
                page=skip // limit + 1 if limit > 0 else 1,
                size=limit,
                pages=(total + limit - 1) // limit if limit > 0 else 1
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar produtos com estoque baixo: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao buscar produtos com estoque baixo"
            ) 