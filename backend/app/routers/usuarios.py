'''
Router de Usuários para o sistema CCONTROL-M.
Implementa as operações CRUD protegidas por JWT, com filtros, paginação e uso de repositório.
'''

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from app.schemas.usuario import (
    Usuario, UsuarioCreate, UsuarioUpdate, UsuarioList
)
from app.schemas.pagination import PaginatedResponse
from app.repositories.usuario_repository import UsuarioRepository
from app.database import get_db, get_async_session
from app.dependencies import get_current_user
from app.utils.permissions import require_permission
from app.schemas.token import TokenPayload

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.post("/", response_model=Usuario, status_code=status.HTTP_201_CREATED)
@require_permission("usuarios", "criar")
def criar_usuario(
    usuario_in: UsuarioCreate,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    repo = UsuarioRepository()
    return repo.create(db, obj_in=usuario_in)


@router.get("/", response_model=PaginatedResponse[UsuarioList])
@require_permission("usuarios", "listar")
def listar_usuarios(
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    repo = UsuarioRepository()
    skip = (page - 1) * page_size
    usuarios = repo.get_multi(db, skip=skip, limit=page_size)
    total = repo.get_count(db)
    return PaginatedResponse.create(
        items=usuarios,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{id_usuario}", response_model=Usuario)
@require_permission("usuarios", "visualizar")
def obter_usuario(
    id_usuario: UUID,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    repo = UsuarioRepository()
    usuario = repo.get(db, id=id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario


@router.put("/{id_usuario}", response_model=Usuario)
@require_permission("usuarios", "editar")
def atualizar_usuario(
    id_usuario: UUID,
    usuario_in: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    repo = UsuarioRepository()
    db_usuario = repo.get(db, id=id_usuario)
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return repo.update(db, db_obj=db_usuario, obj_in=usuario_in)


@router.delete("/{id_usuario}", response_model=Usuario)
@require_permission("usuarios", "deletar")
def deletar_usuario(
    id_usuario: UUID,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):
    repo = UsuarioRepository()
    return repo.delete(db, id=id_usuario) 