"""Endpoints para gerenciamento de permissões de usuário."""
from uuid import UUID
from typing import List, Optional, Dict

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.permissao_usuario import (
    PermissaoUsuario, 
    PermissaoUsuarioCreate, 
    PermissaoUsuarioUpdate, 
    PermissaoUsuarioList
)
from app.schemas.token import TokenPayload
from app.dependencies import get_current_user
from app.database import get_async_session
from app.utils.permissions import require_permission
from app.services.permissao_service import PermissaoService


router = APIRouter(
    prefix="/permissoes-usuario",
    tags=["Permissões de Usuário"],
    responses={404: {"description": "Permissão não encontrada"}}
)


@router.get("/", response_model=List[PermissaoUsuario])
@require_permission("permissoes", "listar")
async def listar_permissoes_usuario(
    id_usuario: Optional[UUID] = Query(None, description="Filtrar por ID do usuário"),
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=100, description="Número máximo de registros"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Lista todas as permissões de usuário com filtro opcional por ID de usuário.
    
    Apenas administradores podem visualizar permissões de todos os usuários.
    Usuários comuns só podem ver suas próprias permissões.
    """
    # Verificar se o usuário atual está tentando acessar permissões de outro usuário
    if (id_usuario and id_usuario != current_user.sub 
            and current_user.tipo_usuario != "ADMIN"):
        raise HTTPException(
            status_code=403,
            detail="Sem permissão para visualizar permissões de outros usuários"
        )
    
    # Se não for admin e não especificar ID, assume o ID do usuário atual
    if not id_usuario and current_user.tipo_usuario != "ADMIN":
        id_usuario = current_user.sub
    
    permissao_service = PermissaoService()
    
    if id_usuario:
        permissoes, total = await permissao_service.listar_permissoes_por_usuario(
            id_usuario=id_usuario, 
            id_empresa=current_user.empresa_id,
            skip=skip,
            limit=limit
        )
    else:
        # Para admin sem filtro, buscar todas as permissões
        permissoes, total = await permissao_service.listar_todas_permissoes(
            id_empresa=current_user.empresa_id,
            skip=skip,
            limit=limit
        )
    
    return permissoes


@router.get("/{id_permissao}", response_model=PermissaoUsuario)
@require_permission("permissoes", "visualizar")
async def obter_permissao(
    id_permissao: UUID = Path(..., description="ID da permissão"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Obtém detalhes de uma permissão específica.
    
    Apenas administradores e o próprio usuário podem visualizar suas permissões.
    """
    permissao_service = PermissaoService()
    
    permissao = await permissao_service.obter_permissao(
        id_permissao=id_permissao, 
        id_empresa=current_user.empresa_id
    )
    
    # Verificar se o usuário atual está tentando acessar permissão de outro usuário
    if (permissao.id_usuario != current_user.sub 
            and current_user.tipo_usuario != "ADMIN"):
        raise HTTPException(
            status_code=403,
            detail="Sem permissão para visualizar permissões de outros usuários"
        )
    
    return permissao


@router.post("/", response_model=PermissaoUsuario, status_code=status.HTTP_201_CREATED)
@require_permission("permissoes", "criar")
async def criar_permissao(
    permissao_in: PermissaoUsuarioCreate,
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Cria uma nova permissão para um usuário.
    
    Apenas administradores podem criar permissões.
    """
    # Apenas admin pode criar permissões
    if current_user.tipo_usuario != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Apenas administradores podem criar permissões"
        )
    
    permissao_service = PermissaoService()
    
    # Criar nova permissão
    nova_permissao = await permissao_service.criar_permissao(
        permissao=permissao_in,
        id_empresa=current_user.empresa_id,
        id_usuario_admin=current_user.sub
    )
    
    return nova_permissao


@router.put("/{id_permissao}", response_model=PermissaoUsuario)
@require_permission("permissoes", "editar")
async def atualizar_permissao(
    id_permissao: UUID,
    permissao_in: PermissaoUsuarioUpdate,
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Atualiza uma permissão existente.
    
    Apenas administradores podem atualizar permissões.
    """
    # Apenas admin pode atualizar permissões
    if current_user.tipo_usuario != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Apenas administradores podem atualizar permissões"
        )
    
    permissao_service = PermissaoService()
    
    # Atualizar a permissão
    permissao_atualizada = await permissao_service.atualizar_permissao(
        id_permissao=id_permissao,
        permissao=permissao_in,
        id_empresa=current_user.empresa_id,
        id_usuario_admin=current_user.sub
    )
    
    return permissao_atualizada


@router.delete("/{id_permissao}", status_code=status.HTTP_204_NO_CONTENT)
@require_permission("permissoes", "deletar")
async def remover_permissao(
    id_permissao: UUID,
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Remove uma permissão existente.
    
    Apenas administradores podem remover permissões.
    """
    # Apenas admin pode remover permissões
    if current_user.tipo_usuario != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Apenas administradores podem remover permissões"
        )
    
    permissao_service = PermissaoService()
    
    # Remover a permissão
    await permissao_service.remover_permissao(
        id_permissao=id_permissao,
        id_empresa=current_user.empresa_id,
        id_usuario_admin=current_user.sub
    )
    
    return None 