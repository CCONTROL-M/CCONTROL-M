from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.produto import Produto
from app.schemas.produto import ProdutoCreate, ProdutoUpdate, EstoqueUpdate
from app.repositories.produto_repository import ProdutoRepository
from app.utils.logging_config import get_logger, log_with_context

# Configurar logger
logger = get_logger(__name__)

class ProdutoService:
    """Serviço para gerenciamento de produtos."""

    @staticmethod
    @log_with_context
    def get_produtos(
        db: Session, 
        id_empresa: UUID, 
        skip: int = 0, 
        limit: int = 100,
        busca: Optional[str] = None,
        categoria: Optional[str] = None,
        ordenar_por: Optional[str] = None,
        ordem: Optional[str] = "asc"
    ) -> Dict[str, Any]:
        """
        Busca produtos com filtros e paginação.
        
        Args:
            db: Sessão do banco de dados
            id_empresa: ID da empresa
            skip: Número de registros para pular
            limit: Limite de registros a retornar
            busca: Termo de busca para filtrar produtos
            categoria: Categoria para filtrar produtos
            ordenar_por: Campo para ordenação
            ordem: Direção da ordenação ('asc' ou 'desc')
            
        Returns:
            Dicionário com produtos e informações de paginação
        """
        logger.info(f"Buscando produtos da empresa {id_empresa}")
        try:
            return ProdutoRepository.get_all(
                db, id_empresa, skip, limit, busca, categoria, ordenar_por, ordem
            )
        except Exception as e:
            logger.error(f"Erro ao buscar produtos: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao buscar produtos"
            )

    @staticmethod
    @log_with_context
    def get_produto_by_id(db: Session, id_produto: UUID, id_empresa: UUID) -> Produto:
        """
        Busca produto por ID.
        
        Args:
            db: Sessão do banco de dados
            id_produto: ID do produto
            id_empresa: ID da empresa
            
        Returns:
            Instância do produto
        """
        logger.info(f"Buscando produto {id_produto} da empresa {id_empresa}")
        produto = ProdutoRepository.get_by_id(db, id_produto, id_empresa)
        if not produto:
            logger.warning(f"Produto {id_produto} não encontrado")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado"
            )
        return produto

    @staticmethod
    @log_with_context
    def create_produto(db: Session, produto: ProdutoCreate) -> Produto:
        """
        Cria um novo produto.
        
        Args:
            db: Sessão do banco de dados
            produto: Dados do produto a ser criado
            
        Returns:
            Produto criado
        """
        logger.info(f"Criando produto para empresa {produto.id_empresa}")
        try:
            return ProdutoRepository.create(db, produto)
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
    @log_with_context
    def update_produto(db: Session, id_produto: UUID, id_empresa: UUID, produto_data: ProdutoUpdate) -> Produto:
        """
        Atualiza um produto existente.
        
        Args:
            db: Sessão do banco de dados
            id_produto: ID do produto
            id_empresa: ID da empresa
            produto_data: Dados atualizados do produto
            
        Returns:
            Produto atualizado
        """
        logger.info(f"Atualizando produto {id_produto} da empresa {id_empresa}")
        try:
            produto = ProdutoService.get_produto_by_id(db, id_produto, id_empresa)
            return ProdutoRepository.update(db, produto, produto_data)
        except ValueError as e:
            logger.warning(f"Erro de validação ao atualizar produto: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Erro ao atualizar produto: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao atualizar produto"
            )

    @staticmethod
    @log_with_context
    def delete_produto(db: Session, id_produto: UUID, id_empresa: UUID) -> None:
        """
        Remove um produto.
        
        Args:
            db: Sessão do banco de dados
            id_produto: ID do produto
            id_empresa: ID da empresa
        """
        logger.info(f"Removendo produto {id_produto} da empresa {id_empresa}")
        produto = ProdutoService.get_produto_by_id(db, id_produto, id_empresa)
        try:
            ProdutoRepository.delete(db, produto)
        except Exception as e:
            logger.error(f"Erro ao remover produto: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao remover produto"
            )

    @staticmethod
    @log_with_context
    def update_estoque(db: Session, id_produto: UUID, id_empresa: UUID, estoque_data: EstoqueUpdate) -> Produto:
        """
        Atualiza o estoque de um produto.
        
        Args:
            db: Sessão do banco de dados
            id_produto: ID do produto
            id_empresa: ID da empresa
            estoque_data: Dados de atualização do estoque
            
        Returns:
            Produto com estoque atualizado
        """
        logger.info(f"Atualizando estoque do produto {id_produto} da empresa {id_empresa}")
        produto = ProdutoService.get_produto_by_id(db, id_produto, id_empresa)
        try:
            return ProdutoRepository.update_estoque(db, produto, estoque_data.quantidade)
        except ValueError as e:
            logger.warning(f"Erro de validação ao atualizar estoque: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Erro ao atualizar estoque: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao atualizar estoque"
            ) 