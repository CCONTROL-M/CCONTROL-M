"""Router de vendas para o sistema CCONTROL-M."""
from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.schemas.venda import Venda, VendaCreate, VendaUpdate, VendaDetalhes
from app.schemas.usuario import Usuario
from app.services.venda_service import VendaService
from app.services.log_sistema_service import LogSistemaService
from app.schemas.log_sistema import LogSistemaCreate
from app.utils.pagination import PaginatedResponse, paginate
from app.dependencies import get_current_user
from app.utils.permissions import require_permission


router = APIRouter(
    prefix="/vendas",
    tags=["Vendas"],
    responses={404: {"description": "Venda não encontrada"}}
)


@router.get("", response_model=PaginatedResponse[Venda])
@require_permission("vendas", "listar")
async def listar_vendas(
    id_empresa: UUID,
    id_cliente: Optional[UUID] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    status: Optional[str] = None,
    id_forma_pagamento: Optional[UUID] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Listar vendas com filtros e paginação.
    
    - **id_empresa**: ID da empresa (obrigatório)
    - **id_cliente**: Filtrar por cliente
    - **data_inicio**: Data inicial (formato YYYY-MM-DD)
    - **data_fim**: Data final (formato YYYY-MM-DD)
    - **status**: Status da venda (rascunho, confirmada, cancelada)
    - **id_forma_pagamento**: ID da forma de pagamento
    - **page**: Número da página
    - **page_size**: Tamanho da página
    """
    venda_service = VendaService(session)
    vendas, total = await venda_service.listar_vendas(
        id_empresa=id_empresa,
        id_cliente=id_cliente,
        data_inicio=data_inicio,
        data_fim=data_fim,
        status=status,
        id_forma_pagamento=id_forma_pagamento,
        page=page,
        page_size=page_size
    )
    
    return paginate(vendas, total, page, page_size)


@router.get("/{id_venda}", response_model=VendaDetalhes)
@require_permission("vendas", "visualizar")
async def obter_venda(
    id_venda: UUID,
    id_empresa: UUID,
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Buscar venda por ID.
    
    - **id_venda**: ID da venda
    - **id_empresa**: ID da empresa para verificação de acesso
    """
    venda_service = VendaService(session)
    venda = await venda_service.get_venda_completa(id_venda, id_empresa)
    
    return venda


@router.post("", response_model=VendaDetalhes, status_code=status.HTTP_201_CREATED)
@require_permission("vendas", "criar")
async def criar_venda(
    venda: VendaCreate,
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Criar nova venda.
    
    Processa:
    - Validação de itens
    - Geração de parcelas
    - Criação de lançamentos financeiros (se confirmada)
    """
    venda_service = VendaService(session)
    log_service = LogSistemaService(session)
    
    nova_venda = await venda_service.criar_venda(venda, current_user.id)
    
    # Registrar log de atividade
    await log_service.registrar_log(
        LogSistemaCreate(
            id_usuario=current_user.id,
            id_empresa=venda.id_empresa,
            acao="venda:criacao",
            descricao=f"Venda #{nova_venda.id} criada com status {nova_venda.status}"
        )
    )
    
    return nova_venda


@router.put("/{id_venda}", response_model=VendaDetalhes)
@require_permission("vendas", "editar")
async def atualizar_venda(
    id_venda: UUID,
    venda_update: VendaUpdate,
    id_empresa: UUID,
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Atualizar venda existente.
    
    Restrito a vendas em status de rascunho.
    
    - **id_venda**: ID da venda
    - **id_empresa**: ID da empresa para verificação de acesso
    """
    venda_service = VendaService(session)
    log_service = LogSistemaService(session)
    
    venda_atualizada = await venda_service.atualizar_venda(
        id_venda=id_venda,
        id_empresa=id_empresa,
        venda_update=venda_update,
        id_usuario=current_user.id
    )
    
    # Registrar log de atividade
    await log_service.registrar_log(
        LogSistemaCreate(
            id_usuario=current_user.id,
            id_empresa=id_empresa,
            acao="venda:atualizacao",
            descricao=f"Venda #{id_venda} atualizada"
        )
    )
    
    return venda_atualizada


@router.post("/{id_venda}/confirmar", response_model=VendaDetalhes)
@require_permission("vendas", "confirmar")
async def confirmar_venda(
    id_venda: UUID,
    id_empresa: UUID,
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Confirmar venda em status de rascunho.
    
    Dispara criação de parcelas e lançamentos financeiros.
    
    - **id_venda**: ID da venda
    - **id_empresa**: ID da empresa para verificação de acesso
    """
    venda_service = VendaService(session)
    log_service = LogSistemaService(session)
    
    venda_confirmada = await venda_service.confirmar_venda(
        id_venda=id_venda,
        id_empresa=id_empresa,
        id_usuario=current_user.id
    )
    
    # Registrar log de atividade
    await log_service.registrar_log(
        LogSistemaCreate(
            id_usuario=current_user.id,
            id_empresa=id_empresa,
            acao="venda:confirmacao",
            descricao=f"Venda #{id_venda} confirmada"
        )
    )
    
    return venda_confirmada


@router.post("/{id_venda}/cancelar", response_model=VendaDetalhes)
@require_permission("vendas", "cancelar")
async def cancelar_venda(
    id_venda: UUID,
    id_empresa: UUID,
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Cancelar venda.
    
    Verifica status atual e cancela parcelas e lançamentos relacionados.
    
    - **id_venda**: ID da venda
    - **id_empresa**: ID da empresa para verificação de acesso
    """
    venda_service = VendaService(session)
    log_service = LogSistemaService(session)
    
    venda_cancelada = await venda_service.cancelar_venda(
        id_venda=id_venda,
        id_empresa=id_empresa,
        id_usuario=current_user.id
    )
    
    # Registrar log de atividade
    await log_service.registrar_log(
        LogSistemaCreate(
            id_usuario=current_user.id,
            id_empresa=id_empresa,
            acao="venda:cancelamento",
            descricao=f"Venda #{id_venda} cancelada"
        )
    )
    
    return venda_cancelada 