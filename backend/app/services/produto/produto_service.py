"""Serviço principal para gerenciamento de produtos no sistema CCONTROL-M."""
from uuid import UUID
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, Depends
import logging

from app.database import get_async_session
from app.schemas.produto import ProdutoCreate, ProdutoUpdate, Produto as ProdutoSchema, EstoqueUpdate
from app.repositories.produto_repository import ProdutoRepository
from app.services.auditoria_service import AuditoriaService
from app.schemas.pagination import PaginatedResponse

# Importar serviços especializados
from app.services.produto.produto_query_service import ProdutoQueryService
from app.services.produto.produto_estoque_service import ProdutoEstoqueService


class ProdutoService:
    """
    Serviço principal para gerenciamento de produtos.
    
    Esta classe atua como uma fachada para os serviços especializados,
    coordenando as operações e delegando para implementações específicas.
    """
    
    def __init__(
        self, 
        session: AsyncSession = Depends(get_async_session),
        auditoria_service: AuditoriaService = Depends()
    ):
        """Inicializar serviço com repositórios e dependências."""
        self.repository = ProdutoRepository(session)
        self.auditoria_service = auditoria_service
        self.logger = logging.getLogger(__name__)
        
        # Inicializar serviços especializados
        self.query_service = ProdutoQueryService(session)
        self.estoque_service = ProdutoEstoqueService(session)
        
    # Métodos de consulta - delegados para o query_service
    
    async def get_by_id(
        self,
        id_produto: UUID,
        usuario_id: UUID,
        empresa_id: UUID
    ) -> ProdutoSchema:
        """
        Buscar um produto pelo ID.
        
        Args:
            id_produto: ID do produto a ser buscado
            usuario_id: ID do usuário que está buscando
            empresa_id: ID da empresa
            
        Returns:
            Produto encontrado
        """
        produto = await self.query_service.get_by_id(id_produto, empresa_id)
        
        # Registrar ação de consulta
        await self.auditoria_service.registrar_acao(
            usuario_id=usuario_id,
            acao="CONSULTAR_PRODUTO",
            detalhes={"id_produto": str(id_produto)},
            empresa_id=empresa_id
        )
        
        return produto
    
    async def get_multi(
        self,
        empresa_id: UUID,
        skip: int = 0,
        limit: int = 100,
        categoria: Optional[str] = None,
        status: Optional[str] = None,
        busca: Optional[str] = None
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
            
        Returns:
            Lista paginada de produtos
        """
        return await self.query_service.get_multi(
            empresa_id=empresa_id,
            skip=skip,
            limit=limit,
            categoria=categoria,
            status=status,
            busca=busca
        )
    
    # Métodos de manipulação de dados
    
    async def create(
        self,
        produto: ProdutoCreate,
        usuario_id: UUID,
        empresa_id: UUID
    ) -> ProdutoSchema:
        """
        Criar um novo produto.
        
        Args:
            produto: Dados do produto a ser criado
            usuario_id: ID do usuário que está criando
            empresa_id: ID da empresa
            
        Returns:
            Produto criado
        """
        try:
            # Verificar se código já existe
            if await self.query_service.get_by_codigo(produto.codigo, empresa_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Código já cadastrado"
                )
            
            # Criar produto
            novo_produto = await self.repository.create(produto, empresa_id)
            
            # Registrar ação
            await self.auditoria_service.registrar_acao(
                usuario_id=usuario_id,
                acao="CRIAR_PRODUTO",
                detalhes={
                    "id_produto": str(novo_produto.id_produto),
                    "nome": novo_produto.nome,
                    "codigo": novo_produto.codigo,
                    "valor": str(novo_produto.preco_venda)
                },
                empresa_id=empresa_id
            )
            
            return novo_produto
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Erro ao criar produto: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao criar produto"
            )
    
    async def update(
        self,
        id_produto: UUID,
        produto: ProdutoUpdate,
        usuario_id: UUID,
        empresa_id: UUID
    ) -> ProdutoSchema:
        """
        Atualizar um produto existente.
        
        Args:
            id_produto: ID do produto a ser atualizado
            produto: Dados atualizados do produto
            usuario_id: ID do usuário que está atualizando
            empresa_id: ID da empresa
            
        Returns:
            Produto atualizado
        """
        try:
            # Buscar produto existente
            produto_atual = await self.query_service.get_by_id(id_produto, empresa_id)
            
            # Verificar código se alterado
            if produto.codigo and produto.codigo != produto_atual.codigo:
                if await self.query_service.get_by_codigo(produto.codigo, empresa_id):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Código já cadastrado"
                    )
            
            # Atualizar produto
            produto_atualizado = await self.repository.update(id_produto, produto)
            
            # Registrar ação
            await self.auditoria_service.registrar_acao(
                usuario_id=usuario_id,
                acao="ATUALIZAR_PRODUTO",
                detalhes={
                    "id_produto": str(id_produto),
                    "alteracoes": produto.model_dump(exclude_unset=True)
                },
                empresa_id=empresa_id
            )
            
            return produto_atualizado
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Erro ao atualizar produto: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao atualizar produto"
            )
    
    async def delete(
        self,
        id_produto: UUID,
        usuario_id: UUID,
        empresa_id: UUID
    ) -> None:
        """
        Excluir um produto.
        
        Args:
            id_produto: ID do produto a ser excluído
            usuario_id: ID do usuário que está excluindo
            empresa_id: ID da empresa
        """
        try:
            # Buscar produto
            produto = await self.query_service.get_by_id(id_produto, empresa_id)
            
            # Excluir produto
            await self.repository.delete(id_produto)
            
            # Registrar ação
            await self.auditoria_service.registrar_acao(
                usuario_id=usuario_id,
                acao="EXCLUIR_PRODUTO",
                detalhes={
                    "id_produto": str(id_produto),
                    "nome": produto.nome
                },
                empresa_id=empresa_id
            )
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Erro ao excluir produto: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao excluir produto"
            )
    
    # Métodos de estoque - delegados para estoque_service
    
    async def atualizar_estoque(
        self,
        id_produto: UUID,
        estoque_data: EstoqueUpdate,
        usuario_id: UUID,
        empresa_id: UUID
    ) -> ProdutoSchema:
        """
        Atualizar o estoque de um produto.
        
        Args:
            id_produto: ID do produto a ter o estoque atualizado
            estoque_data: Dados de atualização do estoque
            usuario_id: ID do usuário que está realizando a operação
            empresa_id: ID da empresa
            
        Returns:
            Produto com estoque atualizado
        """
        try:
            # Atualizar estoque
            produto = await self.estoque_service.atualizar_estoque(
                id_produto=id_produto,
                id_empresa=empresa_id,
                estoque_data=estoque_data
            )
            
            # Registrar ação
            await self.auditoria_service.registrar_acao(
                usuario_id=usuario_id,
                acao="ATUALIZAR_ESTOQUE_PRODUTO",
                detalhes={
                    "id_produto": str(id_produto),
                    "quantidade": str(estoque_data.quantidade),
                    "tipo": estoque_data.tipo or "entrada"
                },
                empresa_id=empresa_id
            )
            
            return produto
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Erro ao atualizar estoque: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao atualizar estoque"
            ) 