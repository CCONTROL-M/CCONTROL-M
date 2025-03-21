from uuid import UUID
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status, Path
from sqlalchemy.orm import Session
from decimal import Decimal

from app.database import get_db
from app.models.produto import Produto
from app.schemas.produto import Produto as ProdutoSchema, ProdutoCreate, ProdutoUpdate, ProdutosPaginados, EstoqueUpdate
from app.services.produto_service import ProdutoService
from app.dependencies import get_current_user, check_permission
from app.utils.logging_config import get_logger, log_with_context
from app.schemas.pagination import PaginatedResponse
from app.repositories.produto_repository import ProdutoRepository
from app.schemas.token import TokenPayload

# Configurar logger
logger = get_logger(__name__)

# Criar router
router = APIRouter(
    prefix="/api/produtos",
    tags=["produtos"],
    dependencies=[Depends(check_permission("produtos"))]
)

@router.get("/", response_model=ProdutosPaginados, summary="Listar produtos")
async def list_produtos(
    busca: Optional[str] = None,
    categoria: Optional[str] = None,
    page: int = Query(1, ge=1, description="Página"),
    size: int = Query(10, ge=1, le=100, description="Itens por página"),
    ordenar_por: str = Query("nome", description="Campo para ordenação"),
    ordem: str = Query("asc", description="Direção da ordenação (asc ou desc)"),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista todos os produtos com paginação e filtros.
    
    Parâmetros de filtro:
    - busca: Termo para buscar em nome ou código do produto
    - categoria: Filtra por categoria
    
    Parâmetros de paginação:
    - page: Número da página (começa em 1)
    - size: Quantidade de itens por página
    
    Parâmetros de ordenação:
    - ordenar_por: Campo para ordenação
    - ordem: Direção da ordenação (asc ou desc)
    """
    log_with_context(
        logger, 
        "info", 
        "Listando produtos", 
        user_id=str(current_user["id_usuario"]),
        empresa_id=str(current_user["id_empresa"]),
        filters={
            "busca": busca,
            "categoria": categoria
        }
    )
    
    skip = (page - 1) * size
    
    return ProdutoService.get_produtos(
        db=db,
        id_empresa=current_user["id_empresa"],
        skip=skip,
        limit=size,
        busca=busca,
        categoria=categoria,
        ordenar_por=ordenar_por,
        ordem=ordem
    )

@router.get("/{id_produto}", response_model=ProdutoSchema, summary="Obter produto por ID")
async def get_produto(
    id_produto: UUID = Path(..., description="ID do produto"),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém um produto pelo ID.
    
    Parâmetros:
    - id_produto: UUID do produto a ser obtido
    """
    log_with_context(
        logger, 
        "info", 
        f"Obtendo produto {id_produto}", 
        user_id=str(current_user["id_usuario"]),
        empresa_id=str(current_user["id_empresa"])
    )
    
    return ProdutoService.get_produto_by_id(
        db=db,
        id_produto=id_produto,
        id_empresa=current_user["id_empresa"]
    )

@router.post("/", response_model=ProdutoSchema, status_code=status.HTTP_201_CREATED, summary="Criar produto")
async def create_produto(
    produto_data: ProdutoCreate,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cria um novo produto.
    
    Parâmetros:
    - produto_data: Dados do produto a ser criado
    """
    log_with_context(
        logger, 
        "info", 
        "Criando produto", 
        user_id=str(current_user["id_usuario"]),
        empresa_id=str(current_user["id_empresa"])
    )
    
    # Garantir que o id_empresa seja o mesmo do usuário logado
    produto_data.id_empresa = current_user["id_empresa"]
    
    return ProdutoService.create_produto(db=db, produto=produto_data)

@router.put("/{id_produto}", response_model=ProdutoSchema, summary="Atualizar produto")
async def update_produto(
    produto_data: ProdutoUpdate,
    id_produto: UUID = Path(..., description="ID do produto"),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza um produto existente.
    
    Parâmetros:
    - id_produto: UUID do produto a ser atualizado
    - produto_data: Dados atualizados do produto
    """
    log_with_context(
        logger, 
        "info", 
        f"Atualizando produto {id_produto}", 
        user_id=str(current_user["id_usuario"]),
        empresa_id=str(current_user["id_empresa"])
    )
    
    return ProdutoService.update_produto(
        db=db,
        id_produto=id_produto,
        id_empresa=current_user["id_empresa"],
        produto_data=produto_data
    )

@router.patch("/{id_produto}/estoque", response_model=ProdutoSchema, summary="Atualizar estoque")
async def update_estoque(
    estoque_data: EstoqueUpdate,
    id_produto: UUID = Path(..., description="ID do produto"),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza o estoque de um produto.
    
    Parâmetros:
    - id_produto: UUID do produto
    - estoque_data: Dados de atualização do estoque (quantidade)
    
    A quantidade pode ser positiva (para adicionar ao estoque)
    ou negativa (para remover do estoque).
    """
    log_with_context(
        logger, 
        "info", 
        f"Atualizando estoque do produto {id_produto} com quantidade {estoque_data.quantidade}", 
        user_id=str(current_user["id_usuario"]),
        empresa_id=str(current_user["id_empresa"])
    )
    
    return ProdutoService.update_estoque(
        db=db,
        id_produto=id_produto,
        id_empresa=current_user["id_empresa"],
        estoque_data=estoque_data
    )

@router.delete("/{id_produto}", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir produto")
async def delete_produto(
    id_produto: UUID = Path(..., description="ID do produto"),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove um produto do sistema.
    
    Parâmetros:
    - id_produto: UUID do produto a ser removido
    """
    log_with_context(
        logger, 
        "info", 
        f"Excluindo produto {id_produto}", 
        user_id=str(current_user["id_usuario"]),
        empresa_id=str(current_user["id_empresa"])
    )
    
    ProdutoService.delete_produto(
        db=db,
        id_produto=id_produto,
        id_empresa=current_user["id_empresa"]
    )
    
    return None

@router.post("/", response_model=Produto, status_code=status.HTTP_201_CREATED)
def criar_produto(
    produto_in: ProdutoCreate,
    db: Session = Depends(get_db),
    token: TokenPayload = Depends(get_current_user),
):
    """
    Cria um novo produto no sistema.
    
    - Requer autenticação JWT
    - O produto é associado a uma empresa específica
    - Verifica duplicidade de código e código de barras
    """
    logger.info(f"Criando novo produto: {produto_in.nome} para empresa {produto_in.id_empresa}")
    try:
        repo = ProdutoRepository()
        return repo.create(db, obj_in=produto_in)
    except HTTPException as e:
        logger.error(f"Erro ao criar produto: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Erro não esperado ao criar produto: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro ao criar o produto"
        )

@router.get("/", response_model=PaginatedResponse[ProdutoList])
def listar_produtos(
    db: Session = Depends(get_db),
    token: TokenPayload = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    id_empresa: Optional[UUID] = Query(None, description="Filtrar por empresa"),
    id_categoria: Optional[UUID] = Query(None, description="Filtrar por categoria"),
    nome: Optional[str] = Query(None, description="Busca por nome"),
    codigo: Optional[str] = Query(None, description="Busca por código ou código de barras"),
    ativo: Optional[bool] = Query(None, description="Filtrar por status (ativo/inativo)"),
    estoque_baixo: Optional[bool] = Query(False, description="Filtrar produtos com estoque abaixo do mínimo"),
):
    """
    Lista produtos com paginação e filtros opcionais.
    
    - Requer autenticação JWT
    - Suporta filtro por empresa e categoria
    - Suporta busca por nome ou código
    - Suporta filtro por status (ativo/inativo)
    - Suporta filtro para produtos com estoque baixo
    - Retorna resultados paginados
    """
    logger.info(f"Listando produtos: página {page}, tamanho {page_size}")
    
    try:
        repo = ProdutoRepository()
        
        # Montar filtros
        filters = {}
        if nome:
            filters["nome"] = nome
        if codigo:
            filters["codigo"] = codigo
            
        # Calcular offset para paginação
        skip = (page - 1) * page_size
        
        # Buscar dados
        produtos = repo.get_multi(
            db, 
            skip=skip, 
            limit=page_size, 
            id_empresa=id_empresa,
            id_categoria=id_categoria,
            ativo=ativo,
            estoque_baixo=estoque_baixo,
            filters=filters
        )
        total = repo.get_count(
            db, 
            id_empresa=id_empresa,
            id_categoria=id_categoria,
            ativo=ativo,
            estoque_baixo=estoque_baixo,
            filters=filters
        )
        
        return PaginatedResponse.create(
            items=produtos,
            total=total,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        logger.error(f"Erro ao listar produtos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro ao listar produtos"
        )

@router.get("/{id_produto}", response_model=Produto)
def obter_produto(
    id_produto: UUID,
    db: Session = Depends(get_db),
    token: TokenPayload = Depends(get_current_user),
):
    """
    Obtém um produto pelo ID.
    
    - Requer autenticação JWT
    - Retorna 404 se o produto não for encontrado
    """
    logger.info(f"Buscando produto por ID: {id_produto}")
    
    try:
        repo = ProdutoRepository()
        produto = repo.get(db, id=id_produto)
        
        if not produto:
            logger.warning(f"Produto não encontrado: {id_produto}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Produto não encontrado"
            )
            
        return produto
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar produto: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro ao buscar o produto"
        )

@router.put("/{id_produto}", response_model=Produto)
def atualizar_produto(
    id_produto: UUID,
    produto_in: ProdutoUpdate,
    db: Session = Depends(get_db),
    token: TokenPayload = Depends(get_current_user),
):
    """
    Atualiza um produto existente.
    
    - Requer autenticação JWT
    - Verifica duplicidade de código e código de barras
    - Retorna 404 se o produto não for encontrado
    """
    logger.info(f"Atualizando produto: {id_produto}")
    
    try:
        repo = ProdutoRepository()
        db_produto = repo.get(db, id=id_produto)
        
        if not db_produto:
            logger.warning(f"Produto não encontrado: {id_produto}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Produto não encontrado"
            )
            
        return repo.update(db, db_obj=db_produto, obj_in=produto_in)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar produto: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro ao atualizar o produto"
        )

@router.delete("/{id_produto}", response_model=Produto)
def deletar_produto(
    id_produto: UUID,
    db: Session = Depends(get_db),
    token: TokenPayload = Depends(get_current_user),
):
    """
    Remove um produto do sistema.
    
    - Requer autenticação JWT
    - Retorna 404 se o produto não for encontrado
    """
    logger.info(f"Removendo produto: {id_produto}")
    
    try:
        repo = ProdutoRepository()
        produto = repo.delete(db, id=id_produto)
        
        if not produto:
            logger.warning(f"Produto não encontrado para remoção: {id_produto}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Produto não encontrado"
            )
            
        return produto
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao remover produto: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro ao remover o produto"
        )

@router.patch("/{id_produto}/estoque", response_model=Produto)
def atualizar_estoque(
    id_produto: UUID,
    quantidade: float = Query(..., gt=0, description="Quantidade a ser ajustada no estoque"),
    is_entrada: bool = Query(True, description="Se True, adiciona ao estoque; se False, subtrai"),
    db: Session = Depends(get_db),
    token: TokenPayload = Depends(get_current_user),
):
    """
    Atualiza o estoque de um produto.
    
    - Requer autenticação JWT
    - Adiciona ou remove quantidade do estoque atual
    - Valida estoque disponível para saídas
    """
    logger.info(f"Atualizando estoque do produto {id_produto}: {'+' if is_entrada else '-'}{quantidade}")
    
    try:
        repo = ProdutoRepository()
        return repo.atualizar_estoque(
            db, 
            id_produto=id_produto, 
            quantidade=quantidade, 
            is_entrada=is_entrada
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar estoque: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro ao atualizar o estoque"
        ) 