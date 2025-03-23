from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime

from app.services.auditoria_service import AuditoriaService
from app.schemas.auditoria import AuditoriaCreate, AuditoriaResponse, AuditoriaList
from app.schemas.pagination import PaginationParams
from app.core.security import get_current_active_user
from app.schemas.token import TokenPayload
from app.utils.permissions import require_permission

router = APIRouter()

@router.get("/", response_model=AuditoriaList)
@require_permission("auditoria", "visualizar")
async def listar_registros_auditoria(
    pagination: PaginationParams = Depends(),
    entity_type: Optional[str] = Query(None, description="Tipo de entidade auditada"),
    action_type: Optional[str] = Query(None, description="Tipo de ação (create, update, delete)"),
    date_from: Optional[datetime] = Query(None, description="Data inicial"),
    date_to: Optional[datetime] = Query(None, description="Data final"),
    current_user: TokenPayload = Depends(get_current_active_user)
) -> AuditoriaList:
    """
    Lista registros de auditoria com filtros e paginação.
    Requer permissão de administrador.
    """
    service = AuditoriaService()
    return await service.listar_registros(
        pagination=pagination,
        entity_type=entity_type,
        action_type=action_type,
        date_from=date_from,
        date_to=date_to
    )

@router.get("/{id}", response_model=AuditoriaResponse)
@require_permission("auditoria", "visualizar")
async def obter_registro_auditoria(
    id: int,
    current_user: TokenPayload = Depends(get_current_active_user)
) -> AuditoriaResponse:
    """
    Obtém um registro de auditoria específico por ID.
    Requer permissão de administrador.
    """
    service = AuditoriaService()
    registro = await service.obter_por_id(id)
    if not registro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro de auditoria não encontrado"
        )
    return registro 