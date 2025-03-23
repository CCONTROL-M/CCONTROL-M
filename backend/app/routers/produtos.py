from uuid import UUID
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status, Path
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.produto import Produto as ProdutoSchema, ProdutoCreate, ProdutoUpdate, ProdutoList, EstoqueUpdate
from app.services.produto import ProdutoService
from app.dependencies import get_current_user
from app.database import get_async_session
from app.utils.logging_config import get_logger
from app.utils.permissions import require_permission
from app.schemas.pagination import PaginatedResponse
from app.schemas.token import TokenPayload

# Configurar logger
logger = get_logger(__name__)

# Criar router
router = APIRouter(
    prefix="/produtos",
    tags=["Produtos"]
)

@router.get("/", response_model=ProdutoList, summary="Listar produtos")
@require_permission("produtos", "listar")
async def listar_produtos(
    nome: Optional[str] = None,
    codigo: Optional[str] = None,
    id_categoria: Optional[UUID] = None,
    ativo: Optional[bool] = None,
    estoque_baixo: Optional[bool] = Query(None, description="Filtrar produtos com estoque abaixo do mínimo"),
    page: int = Query(1, ge=1, description="Página"),
    size: int = Query(10, ge=1, le=100, description="Itens por página"),
    order_by: str = Query("nome", description="Campo para ordenação"),
    order_direction: str = Query("asc", description="Direção da ordenação (asc ou desc)"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Lista todos os produtos com paginação e filtros.
    
    Parâmetros de filtro:
    - nome: Filtra por nome do produto
    - codigo: Filtra por código ou código de barras
    - id_categoria: Filtra por categoria
    - ativo: Filtra por status (ativo/inativo)
    - estoque_baixo: Filtra produtos com estoque abaixo do mínimo
    
    Parâmetros de paginação:
    - page: Número da página (começa em 1)
    - size: Quantidade de itens por página
    
    Parâmetros de ordenação:
    - order_by: Campo para ordenação
    - order_direction: Direção da ordenação (asc ou desc)
    """
    logger.info(
        "Listando produtos", 
        extra={
            "user_id": current_user.sub,
            "empresa_id": str(current_user.empresa_id),
            "filters": {
                "nome": nome,
                "codigo": codigo,
                "id_categoria": str(id_categoria) if id_categoria else None,
                "ativo": ativo
            }
        }
    )
    
    skip = (page - 1) * size
    
    return await ProdutoService.listar_produtos(
        id_empresa=current_user.empresa_id,
        skip=skip,
        limit=size,
        nome=nome,
        codigo=codigo,
        id_categoria=id_categoria,
        ativo=ativo,
        estoque_baixo=estoque_baixo,
        order_by=order_by,
        order_direction=order_direction
    )

@router.get("/{id_produto}", response_model=ProdutoSchema, summary="Obter produto por ID")
@require_permission("produtos", "visualizar")
async def obter_produto(
    id_produto: UUID = Path(..., description="ID do produto"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Obtém um produto pelo ID.
    
    Parâmetros:
    - id_produto: UUID do produto a ser obtido
    """
    logger.info(
        f"Obtendo produto {id_produto}", 
        extra={
            "user_id": current_user.sub,
            "empresa_id": str(current_user.empresa_id)
        }
    )
    
    return await ProdutoService.obter_produto(
        id_produto=id_produto,
        id_empresa=current_user.empresa_id
    )

@router.post("/", response_model=ProdutoSchema, status_code=status.HTTP_201_CREATED, summary="Criar produto")
@require_permission("produtos", "criar")
async def criar_produto(
    produto: ProdutoCreate,
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Cria um novo produto.
    
    Parâmetros:
    - produto: Dados do produto a ser criado
    """
    # Garantir que o produto pertence à empresa do usuário
    produto.id_empresa = current_user.empresa_id
    
    logger.info(
        f"Criando produto {produto.nome}", 
        extra={
            "user_id": current_user.sub,
            "empresa_id": str(current_user.empresa_id)
        }
    )
    
    return await ProdutoService.criar_produto(produto_data=produto)

@router.put("/{id_produto}", response_model=ProdutoSchema, summary="Atualizar produto")
@require_permission("produtos", "editar")
async def atualizar_produto(
    produto: ProdutoUpdate,
    id_produto: UUID = Path(..., description="ID do produto"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Atualiza um produto existente.
    
    Parâmetros:
    - id_produto: UUID do produto a ser atualizado
    - produto: Dados atualizados do produto
    """
    logger.info(
        f"Atualizando produto {id_produto}", 
        extra={
            "user_id": current_user.sub,
            "empresa_id": str(current_user.empresa_id)
        }
    )
    
    return await ProdutoService.atualizar_produto(
        id_produto=id_produto,
        id_empresa=current_user.empresa_id,
        produto_data=produto
    )

@router.delete("/{id_produto}", status_code=status.HTTP_204_NO_CONTENT, summary="Remover produto")
@require_permission("produtos", "deletar")
async def remover_produto(
    id_produto: UUID = Path(..., description="ID do produto"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Remove um produto.
    
    Parâmetros:
    - id_produto: UUID do produto a ser removido
    """
    logger.info(
        f"Removendo produto {id_produto}", 
        extra={
            "user_id": current_user.sub,
            "empresa_id": str(current_user.empresa_id)
        }
    )
    
    await ProdutoService.remover_produto(
        id_produto=id_produto,
        id_empresa=current_user.empresa_id
    )
    
    return None

@router.patch("/{id_produto}/estoque", response_model=ProdutoSchema, summary="Atualizar estoque")
@require_permission("produtos", "editar")
async def atualizar_estoque(
    estoque: EstoqueUpdate,
    id_produto: UUID = Path(..., description="ID do produto"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Atualiza o estoque de um produto.
    
    Parâmetros:
    - id_produto: UUID do produto a ter o estoque atualizado
    - estoque: Dados para atualização do estoque
      - quantidade: Quantidade a ser ajustada
      - tipo: 'entrada' ou 'saida' (default: 'entrada')
    """
    logger.info(
        f"Atualizando estoque do produto {id_produto}", 
        extra={
            "user_id": current_user.sub,
            "empresa_id": str(current_user.empresa_id),
            "data": {
                "quantidade": float(estoque.quantidade),
                "tipo": estoque.tipo
            }
        }
    )
    
    return await ProdutoService.atualizar_estoque(
        id_produto=id_produto,
        id_empresa=current_user.empresa_id,
        estoque_data=estoque
    ) 