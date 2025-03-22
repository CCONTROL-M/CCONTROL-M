from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from fastapi import HTTPException, status
from decimal import Decimal

from app.models.produto import Produto
from app.schemas.produto import ProdutoCreate, ProdutoUpdate, ProdutoList, EstoqueUpdate
from app.repositories.produto_repository import ProdutoRepository
from app.utils.logging_config import get_logger
from app.database import db_async_session

# Configurar logger
logger = get_logger(__name__)

class ProdutoService:
    """Serviço para gerenciamento de produtos."""

    @staticmethod
    async def listar_produtos(
        id_empresa: UUID, 
        skip: int = 0, 
        limit: int = 100,
        nome: Optional[str] = None,
        codigo: Optional[str] = None,
        id_categoria: Optional[UUID] = None,
        ativo: Optional[bool] = None,
        estoque_baixo: Optional[bool] = None,
        order_by: str = "nome",
        order_direction: str = "asc"
    ) -> Dict[str, Any]:
        """
        Busca produtos com filtros e paginação.
        
        Args:
            id_empresa: ID da empresa
            skip: Número de registros para pular
            limit: Limite de registros a retornar
            nome: Filtro pelo nome do produto
            codigo: Filtro pelo código ou código de barras
            id_categoria: Filtro por categoria
            ativo: Filtro por status (ativo/inativo)
            estoque_baixo: Filtro por produtos com estoque baixo
            order_by: Campo para ordenação
            order_direction: Direção da ordenação ('asc' ou 'desc')
            
        Returns:
            Dict[str, Any]: Produtos e informações de paginação
        """
        logger.info(f"Buscando produtos da empresa {id_empresa}")
        try:
            async with db_async_session() as session:
                repository = ProdutoRepository(session)
                produtos, total = await repository.get_multi(
                    skip=skip,
                    limit=limit,
                    id_empresa=id_empresa,
                    id_categoria=id_categoria,
                    ativo=ativo,
                    estoque_baixo=estoque_baixo,
                    nome=nome,
                    codigo=codigo,
                    order_by=order_by,
                    order_direction=order_direction
                )
                
                # Calcular informações de paginação
                page = (skip // limit) + 1 if limit > 0 else 1
                pages = (total + limit - 1) // limit if limit > 0 else 1
                
                return {
                    "items": produtos,
                    "total": total,
                    "page": page,
                    "size": limit,
                    "pages": pages
                }
        except Exception as e:
            logger.error(f"Erro ao buscar produtos: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao buscar produtos"
            )

    @staticmethod
    async def obter_produto(id_produto: UUID, id_empresa: UUID) -> Produto:
        """
        Busca produto por ID.
        
        Args:
            id_produto: ID do produto
            id_empresa: ID da empresa
            
        Returns:
            Produto: Instância do produto
            
        Raises:
            HTTPException: Se o produto não for encontrado
        """
        logger.info(f"Buscando produto {id_produto} da empresa {id_empresa}")
        async with db_async_session() as session:
            repository = ProdutoRepository(session)
            produto = await repository.get_by_id(id_produto, id_empresa)
            if not produto:
                logger.warning(f"Produto {id_produto} não encontrado")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Produto não encontrado"
                )
            return produto

    @staticmethod
    async def criar_produto(produto_data: ProdutoCreate) -> Produto:
        """
        Cria um novo produto.
        
        Args:
            produto_data: Dados do produto a ser criado
            
        Returns:
            Produto: Produto criado
            
        Raises:
            HTTPException: Se ocorrer um erro ao criar o produto
        """
        logger.info(f"Criando produto para empresa {produto_data.id_empresa}")
        try:
            async with db_async_session() as session:
                repository = ProdutoRepository(session)
                produto = await repository.create(produto_data.dict())
                return produto
        except ValueError as e:
            logger.warning(f"Erro de validação ao criar produto: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Erro ao criar produto: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao criar produto"
            )

    @staticmethod
    async def atualizar_produto(id_produto: UUID, id_empresa: UUID, produto_data: ProdutoUpdate) -> Produto:
        """
        Atualiza um produto existente.
        
        Args:
            id_produto: ID do produto
            id_empresa: ID da empresa
            produto_data: Dados atualizados do produto
            
        Returns:
            Produto: Produto atualizado
            
        Raises:
            HTTPException: Se o produto não for encontrado ou ocorrer um erro na atualização
        """
        logger.info(f"Atualizando produto {id_produto} da empresa {id_empresa}")
        try:
            # Verificar se o produto existe
            async with db_async_session() as session:
                repository = ProdutoRepository(session)
                produto = await repository.get_by_id(id_produto, id_empresa)
                
                if not produto:
                    logger.warning(f"Produto {id_produto} não encontrado para atualização")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Produto não encontrado"
                    )
                
                # Atualizar o produto
                produto_atualizado = await repository.update(
                    id_produto=id_produto,
                    id_empresa=id_empresa,
                    data=produto_data.dict(exclude_unset=True)
                )
                
                return produto_atualizado
        except ValueError as e:
            logger.warning(f"Erro de validação ao atualizar produto: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except HTTPException:
            raise  # Re-lançar exceções HTTP
        except Exception as e:
            logger.error(f"Erro ao atualizar produto: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao atualizar produto"
            )

    @staticmethod
    async def remover_produto(id_produto: UUID, id_empresa: UUID) -> None:
        """
        Remove um produto.
        
        Args:
            id_produto: ID do produto
            id_empresa: ID da empresa
            
        Raises:
            HTTPException: Se o produto não for encontrado ou ocorrer um erro na remoção
        """
        logger.info(f"Removendo produto {id_produto} da empresa {id_empresa}")
        async with db_async_session() as session:
            repository = ProdutoRepository(session)
            
            # Verificar se o produto existe
            produto = await repository.get_by_id(id_produto, id_empresa)
            if not produto:
                logger.warning(f"Produto {id_produto} não encontrado para remoção")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Produto não encontrado"
                )
            
            # Remover o produto
            try:
                resultado = await repository.delete(id_produto, id_empresa)
                if not resultado:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Erro ao remover produto"
                    )
            except Exception as e:
                logger.error(f"Erro ao remover produto: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Erro ao remover produto"
                )

    @staticmethod
    async def atualizar_estoque(id_produto: UUID, id_empresa: UUID, estoque_data: EstoqueUpdate) -> Produto:
        """
        Atualiza o estoque de um produto.
        
        Args:
            id_produto: ID do produto
            id_empresa: ID da empresa
            estoque_data: Dados de atualização do estoque
            
        Returns:
            Produto: Produto com estoque atualizado
            
        Raises:
            HTTPException: Se o produto não for encontrado ou ocorrer um erro ao atualizar o estoque
        """
        logger.info(f"Atualizando estoque do produto {id_produto} da empresa {id_empresa}")
        try:
            async with db_async_session() as session:
                repository = ProdutoRepository(session)
                
                # Verificar se o produto existe
                produto = await repository.get_by_id(id_produto, id_empresa)
                if not produto:
                    logger.warning(f"Produto {id_produto} não encontrado para atualização de estoque")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Produto não encontrado"
                    )
                
                # Determinar se é entrada ou saída
                is_entrada = estoque_data.tipo.lower() == "entrada" if estoque_data.tipo else True
                
                # Atualizar o estoque
                produto_atualizado = await repository.update_estoque(
                    id_produto=id_produto,
                    id_empresa=id_empresa,
                    quantidade=estoque_data.quantidade,
                    is_entrada=is_entrada
                )
                
                return produto_atualizado
        except ValueError as e:
            logger.warning(f"Erro de validação ao atualizar estoque: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except HTTPException:
            raise  # Re-lançar exceções HTTP
        except Exception as e:
            logger.error(f"Erro ao atualizar estoque: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao atualizar estoque"
            ) 