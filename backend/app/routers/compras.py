"""Router de compras para o sistema CCONTROL-M."""
from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.schemas.compra import Compra, CompraCreate, CompraUpdate, CompraDetalhes
from app.schemas.usuario import Usuario
from app.services.compra_service import CompraService
from app.services.log_sistema_service import LogSistemaService
from app.schemas.log_sistema import LogSistemaCreate
from app.utils.pagination import PaginatedResponse, paginate
from app.dependencies import get_current_user
from app.utils.permissions import require_permission


router = APIRouter(
    prefix="/compras",
    tags=["Compras"],
    responses={404: {"description": "Compra não encontrada"}}
)


@router.post("/", response_model=Compra)
@require_permission("compras", "criar")
async def criar_compra(
    compra: CompraCreate,
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Criar nova compra.
    
    - **compra**: Dados da compra
    """
    compra_service = CompraService(session)
    nova_compra = await compra_service.create(compra)
    
    # Registrar log
    log_service = LogSistemaService(session)
    await log_service.registrar_acao(
        LogSistemaCreate(
            id_usuario=current_user.id,
            id_empresa=compra.id_empresa,
            acao="Compra criada",
            modulo="compras",
            detalhes=f"Criou a compra {nova_compra.id_compra}"
        )
    )
    
    return nova_compra


@router.get("/", response_model=PaginatedResponse[Compra])
@require_permission("compras", "visualizar")
async def listar_compras(
    id_empresa: UUID,
    id_fornecedor: Optional[UUID] = None,
    status: Optional[str] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Listar compras com filtros.
    
    - **id_empresa**: ID da empresa
    - **id_fornecedor**: Filtrar por fornecedor (opcional)
    - **status**: Filtrar por status (opcional)
    - **data_inicio**: Data inicial no formato YYYY-MM-DD (opcional)
    - **data_fim**: Data final no formato YYYY-MM-DD (opcional)
    - **skip**: Itens para pular
    - **limit**: Itens por página
    """
    compra_service = CompraService(session)
    compras, total = await compra_service.get_compras(
        id_empresa=id_empresa,
        id_fornecedor=id_fornecedor,
        status=status,
        data_inicio=data_inicio,
        data_fim=data_fim,
        skip=skip,
        limit=limit
    )
    
    return paginate(compras, total, skip, limit)


@router.get("/{id_compra}", response_model=CompraDetalhes)
@require_permission("compras", "visualizar")
async def obter_compra(
    id_compra: UUID,
    id_empresa: UUID,
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Buscar compra por ID.
    
    - **id_compra**: ID da compra
    - **id_empresa**: ID da empresa para verificação de acesso
    """
    compra_service = CompraService(session)
    compra = await compra_service.get_compra_completa(id_compra, id_empresa)
    
    return compra


@router.put("/{id_compra}", response_model=Compra)
@require_permission("compras", "editar")
async def atualizar_compra(
    id_compra: UUID,
    compra: CompraUpdate,
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Atualizar compra existente.
    
    - **id_compra**: ID da compra
    - **compra**: Novos dados da compra
    """
    compra_service = CompraService(session)
    compra_atualizada = await compra_service.update(id_compra, compra.id_empresa, compra)
    
    if not compra_atualizada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compra não encontrada"
        )
    
    # Registrar log
    log_service = LogSistemaService(session)
    await log_service.registrar_acao(
        LogSistemaCreate(
            id_usuario=current_user.id,
            id_empresa=compra.id_empresa,
            acao="Compra atualizada",
            modulo="compras",
            detalhes=f"Atualizou a compra {id_compra}"
        )
    )
    
    return compra_atualizada


@router.delete("/{id_compra}", status_code=status.HTTP_204_NO_CONTENT)
@require_permission("compras", "excluir")
async def excluir_compra(
    id_compra: UUID,
    id_empresa: UUID,
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Excluir compra.
    
    - **id_compra**: ID da compra
    - **id_empresa**: ID da empresa para verificação de acesso
    """
    compra_service = CompraService(session)
    sucesso = await compra_service.delete(id_compra, id_empresa)
    
    if not sucesso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compra não encontrada"
        )
    
    # Registrar log
    log_service = LogSistemaService(session)
    await log_service.registrar_acao(
        LogSistemaCreate(
            id_usuario=current_user.id,
            id_empresa=id_empresa,
            acao="Compra excluída",
            modulo="compras",
            detalhes=f"Excluiu a compra {id_compra}"
        )
    )


@router.post("/{id_compra}/cancelar", response_model=Compra)
@require_permission("compras", "editar")
async def cancelar_compra(
    id_compra: UUID,
    id_empresa: UUID,
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Cancelar compra.
    
    - **id_compra**: ID da compra
    - **id_empresa**: ID da empresa para verificação de acesso
    """
    compra_service = CompraService(session)
    compra = await compra_service.cancelar_compra(id_compra, id_empresa)
    
    if not compra:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compra não encontrada"
        )
    
    # Registrar log
    log_service = LogSistemaService(session)
    await log_service.registrar_acao(
        LogSistemaCreate(
            id_usuario=current_user.id,
            id_empresa=id_empresa,
            acao="Compra cancelada",
            modulo="compras",
            detalhes=f"Cancelou a compra {id_compra}"
        )
    )
    
    return compra 