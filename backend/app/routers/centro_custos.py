"""
Router para centros de custo - implementa CRUD protegido por JWT,
com filtros, paginação e uso de serviço.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import logging

from app.dependencies import get_db, get_current_user, get_current_active_user
from app.schemas.centro_custo import CentroCustoCreate, CentroCustoUpdate, CentroCustoResponse
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.services.centro_custo_service import CentroCustoService
from app.schemas.usuario import UsuarioResponse

# Configuração de logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/centro-custos",
    tags=["centro_custos"],
    responses={404: {"description": "Item não encontrado"}},
)


@router.post(
    "/",
    response_model=CentroCustoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria um novo centro de custo",
    description="Cria um novo centro de custo no sistema. Requer autenticação JWT.",
)
async def create_new_centro_custo(
    centro_custo_data: CentroCustoCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: UsuarioResponse = Depends(get_current_active_user),
    centro_custo_service: CentroCustoService = Depends()
):
    """
    Cria um novo centro de custo no sistema.
    
    Args:
        centro_custo_data: Dados do centro de custo a ser criado
        current_user: Usuário autenticado
        
    Returns:
        Centro de custo criado
    """
    try:
        logger.info(f"Criando novo centro de custo: {centro_custo_data.nome}")
        
        # Criar centro de custo
        novo_centro = await centro_custo_service.criar_centro_custo(
            centro_custo_data, 
            current_user.id
        )
        
        return novo_centro
    except HTTPException as e:
        logger.error(f"Erro ao criar centro de custo: {str(e.detail)}")
        raise e
    except Exception as e:
        logger.error(f"Erro inesperado ao criar centro de custo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar a requisição"
        )


@router.get(
    "/",
    response_model=PaginatedResponse[CentroCustoResponse],
    status_code=status.HTTP_200_OK,
    summary="Lista centros de custo",
    description="Retorna uma lista paginada de centros de custo com filtros opcionais."
)
async def list_centros_custo(
    descricao: Optional[str] = Query(None, description="Filtrar por descrição"),
    ativo: Optional[bool] = Query(None, description="Filtrar por status (ativo/inativo)"),
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
    current_user: UsuarioResponse = Depends(get_current_active_user),
    centro_custo_service: CentroCustoService = Depends()
):
    """
    Lista centros de custo com paginação e filtros.
    
    Args:
        descricao: Filtrar por descrição
        ativo: Filtrar por status
        pagination: Parâmetros de paginação
        current_user: Usuário autenticado
        
    Returns:
        Lista paginada de centros de custo
    """
    try:
        logger.info(f"Listando centros de custo - Filtros: descricao={descricao}, ativo={ativo}")
        
        # Buscar centros de custo com paginação
        centros_custo, total = await centro_custo_service.listar_centros_custo(
            id_empresa=current_user.id_empresa,
            skip=pagination.skip,
            limit=pagination.limit,
            nome=descricao,
            ativo=ativo
        )
        
        # Retornar resultado paginado
        return PaginatedResponse.create(
            items=centros_custo,
            total=total,
            page=pagination.page,
            page_size=pagination.size
        )
    except HTTPException as e:
        logger.error(f"Erro ao listar centros de custo: {str(e.detail)}")
        raise e
    except Exception as e:
        logger.error(f"Erro inesperado ao listar centros de custo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar a requisição"
        )


@router.get(
    "/{id_centro_custo}",
    response_model=CentroCustoResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtém um centro de custo",
    description="Retorna os detalhes de um centro de custo específico pelo ID."
)
async def get_centro_custo(
    id_centro_custo: UUID = Path(..., description="ID do centro de custo"),
    db: Session = Depends(get_db),
    current_user: UsuarioResponse = Depends(get_current_active_user),
    centro_custo_service: CentroCustoService = Depends()
):
    """
    Obtém detalhes de um centro de custo pelo ID.
    
    Args:
        id_centro_custo: ID do centro de custo
        current_user: Usuário autenticado
        
    Returns:
        Detalhes do centro de custo
    """
    try:
        logger.info(f"Buscando centro de custo: {id_centro_custo}")
        
        # Buscar centro de custo pelo ID
        centro_custo = await centro_custo_service.get_centro_custo(
            id_centro_custo,
            current_user.id_empresa
        )
        
        return centro_custo
    except HTTPException as e:
        logger.error(f"Erro ao buscar centro de custo: {str(e.detail)}")
        raise e
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar centro de custo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar a requisição"
        )


@router.put(
    "/{id_centro_custo}",
    response_model=CentroCustoResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualiza um centro de custo",
    description="Atualiza os dados de um centro de custo existente."
)
async def update_centro_custo_endpoint(
    id_centro_custo: UUID = Path(..., description="ID do centro de custo"),
    centro_custo_data: CentroCustoUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: UsuarioResponse = Depends(get_current_active_user),
    centro_custo_service: CentroCustoService = Depends()
):
    """
    Atualiza um centro de custo existente.
    
    Args:
        id_centro_custo: ID do centro de custo
        centro_custo_data: Dados atualizados do centro de custo
        current_user: Usuário autenticado
        
    Returns:
        Centro de custo atualizado
    """
    try:
        logger.info(f"Atualizando centro de custo: {id_centro_custo}")
        
        # Atualizar centro de custo
        centro_atualizado = await centro_custo_service.atualizar_centro_custo(
            id_centro_custo,
            centro_custo_data,
            current_user.id_empresa,
            current_user.id
        )
        
        return centro_atualizado
    except HTTPException as e:
        logger.error(f"Erro ao atualizar centro de custo: {str(e.detail)}")
        raise e
    except Exception as e:
        logger.error(f"Erro inesperado ao atualizar centro de custo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar a requisição"
        )


@router.delete(
    "/{id_centro_custo}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove um centro de custo",
    description="Remove um centro de custo existente do sistema."
)
async def delete_centro_custo_endpoint(
    id_centro_custo: UUID = Path(..., description="ID do centro de custo"),
    db: Session = Depends(get_db),
    current_user: UsuarioResponse = Depends(get_current_active_user),
    centro_custo_service: CentroCustoService = Depends()
):
    """
    Remove um centro de custo do sistema.
    
    Args:
        id_centro_custo: ID do centro de custo
        current_user: Usuário autenticado
    """
    try:
        logger.info(f"Removendo centro de custo: {id_centro_custo}")
        
        # Remover o centro de custo
        await centro_custo_service.remover_centro_custo(
            id_centro_custo,
            current_user.id_empresa,
            current_user.id
        )
        
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException as e:
        logger.error(f"Erro ao remover centro de custo: {str(e.detail)}")
        raise e
    except Exception as e:
        logger.error(f"Erro inesperado ao remover centro de custo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar a requisição"
        ) 