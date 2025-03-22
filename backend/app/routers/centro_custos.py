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
from app.services.centro_custo_service import (
    create_centro_custo,
    get_all_centros_custo,
    get_centro_custo_by_id,
    update_centro_custo,
    delete_centro_custo
)
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
):
    """
    Cria um novo centro de custo com os dados fornecidos.
    
    O centro de custo pertencerá à empresa do usuário autenticado.
    """
    logger.info(f"Criando centro de custo: {centro_custo_data.descricao}")
    
    try:
        # Garantir que o centro de custo será criado para a empresa do usuário
        centro_custo_dict = centro_custo_data.model_dump()
        centro_custo_dict["id_empresa"] = current_user.id_empresa
        
        result = create_centro_custo(db, centro_custo_dict)
        return result
    except HTTPException as e:
        # Repassar exceções HTTP
        logger.warning(f"Erro ao criar centro de custo: {str(e)}")
        raise
    except Exception as e:
        # Outras exceções viram 500
        logger.error(f"Erro inesperado ao criar centro de custo: {str(e)}", exc_info=True)
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
):
    """
    Lista centros de custo da empresa do usuário com suporte a paginação e filtros.
    """
    logger.info(f"Listando centros de custo. Filtros: descricao={descricao}, ativo={ativo}")
    
    try:
        # Montar filtros
        filters = {
            "id_empresa": current_user.id_empresa,
        }
        
        if descricao:
            filters["descricao"] = descricao
            
        if ativo is not None:
            filters["ativo"] = ativo
        
        # Buscar centros de custo com paginação
        centros_custo, total = get_all_centros_custo(
            db, 
            skip=pagination.skip, 
            limit=pagination.limit,
            filters=filters
        )
        
        # Montar resposta paginada
        return {
            "items": centros_custo,
            "total": total,
            "page": pagination.page,
            "size": pagination.limit
        }
    except Exception as e:
        logger.error(f"Erro ao listar centros de custo: {str(e)}", exc_info=True)
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
):
    """
    Obtém os detalhes de um centro de custo específico pelo ID.
    
    Verifica se o centro de custo pertence à empresa do usuário.
    """
    logger.info(f"Buscando centro de custo ID: {id_centro_custo}")
    
    try:
        centro_custo = get_centro_custo_by_id(db, id_centro_custo)
        
        if not centro_custo:
            logger.warning(f"Centro de custo ID {id_centro_custo} não encontrado")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Centro de custo não encontrado"
            )
        
        # Verificar se o centro de custo pertence à empresa do usuário
        if centro_custo.id_empresa != current_user.id_empresa:
            logger.warning(f"Acesso negado ao centro de custo ID {id_centro_custo} para usuário da empresa {current_user.id_empresa}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado a este recurso"
            )
            
        return centro_custo
    except HTTPException as e:
        # Repassar exceções HTTP
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar centro de custo: {str(e)}", exc_info=True)
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
):
    """
    Atualiza os dados de um centro de custo existente.
    
    Verifica se o centro de custo pertence à empresa do usuário.
    """
    logger.info(f"Atualizando centro de custo ID: {id_centro_custo}")
    
    try:
        # Verificar se o centro de custo existe e pertence à empresa do usuário
        centro_custo = get_centro_custo_by_id(db, id_centro_custo)
        
        if not centro_custo:
            logger.warning(f"Centro de custo ID {id_centro_custo} não encontrado")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Centro de custo não encontrado"
            )
        
        if centro_custo.id_empresa != current_user.id_empresa:
            logger.warning(f"Acesso negado ao centro de custo ID {id_centro_custo} para usuário da empresa {current_user.id_empresa}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado a este recurso"
            )
        
        # Atualizar o centro de custo
        updated = update_centro_custo(db, id_centro_custo, centro_custo_data.model_dump(exclude_unset=True))
        return updated
    except HTTPException as e:
        # Repassar exceções HTTP
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar centro de custo: {str(e)}", exc_info=True)
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
):
    """
    Remove um centro de custo existente do sistema.
    
    Verifica se o centro de custo pertence à empresa do usuário e se não há registros associados.
    """
    logger.info(f"Removendo centro de custo ID: {id_centro_custo}")
    
    try:
        # Verificar se o centro de custo existe e pertence à empresa do usuário
        centro_custo = get_centro_custo_by_id(db, id_centro_custo)
        
        if not centro_custo:
            logger.warning(f"Centro de custo ID {id_centro_custo} não encontrado")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Centro de custo não encontrado"
            )
        
        if centro_custo.id_empresa != current_user.id_empresa:
            logger.warning(f"Acesso negado ao centro de custo ID {id_centro_custo} para usuário da empresa {current_user.id_empresa}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado a este recurso"
            )
        
        # Remover o centro de custo
        delete_centro_custo(db, id_centro_custo)
        
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException as e:
        # Repassar exceções HTTP
        raise
    except Exception as e:
        logger.error(f"Erro ao remover centro de custo: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar a requisição"
        ) 