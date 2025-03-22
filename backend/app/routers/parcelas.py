"""Router de parcelas para o sistema CCONTROL-M."""
from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.schemas.parcela import Parcela, ParcelaUpdate, ParcelaPagamento, ParcelaDashboard
from app.schemas.usuario import Usuario
from app.services.parcela_service import ParcelaService
from app.services.log_sistema_service import LogSistemaService
from app.schemas.log_sistema import LogSistemaCreate
from app.utils.pagination import PaginatedResponse, paginate
from app.auth.dependencies import get_current_user, verify_permission


router = APIRouter(
    prefix="/parcelas",
    tags=["Parcelas"],
    responses={404: {"description": "Parcela não encontrada"}}
)


@router.get("", response_model=PaginatedResponse[Parcela])
async def listar_parcelas(
    id_empresa: UUID,
    id_venda: Optional[UUID] = None,
    status: Optional[str] = None,
    data_vencimento_inicio: Optional[str] = None,
    data_vencimento_fim: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Listar parcelas com filtros e paginação.
    
    - **id_empresa**: ID da empresa (obrigatório)
    - **id_venda**: Filtrar por venda específica
    - **status**: Filtrar por status (pendente, paga, cancelada)
    - **data_vencimento_inicio**: Data inicial de vencimento (formato YYYY-MM-DD)
    - **data_vencimento_fim**: Data final de vencimento (formato YYYY-MM-DD)
    - **page**: Número da página
    - **page_size**: Tamanho da página
    """
    verify_permission(current_user, "parcelas:listar", id_empresa)
    
    parcela_service = ParcelaService(session)
    parcelas, total = await parcela_service.listar_parcelas(
        id_empresa=id_empresa,
        id_venda=id_venda,
        status=status,
        data_vencimento_inicio=data_vencimento_inicio,
        data_vencimento_fim=data_vencimento_fim,
        page=page,
        page_size=page_size
    )
    
    return paginate(parcelas, total, page, page_size)


@router.get("/{id_parcela}", response_model=Parcela)
async def obter_parcela(
    id_parcela: UUID,
    id_empresa: UUID,
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Buscar parcela por ID.
    
    - **id_parcela**: ID da parcela
    - **id_empresa**: ID da empresa para verificação de acesso
    """
    verify_permission(current_user, "parcelas:visualizar", id_empresa)
    
    parcela_service = ParcelaService(session)
    parcela = await parcela_service.get_parcela(id_parcela, id_empresa)
    
    return parcela


@router.put("/{id_parcela}", response_model=Parcela)
async def atualizar_parcela(
    id_parcela: UUID,
    parcela_update: ParcelaUpdate,
    id_empresa: UUID,
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Atualizar parcela existente.
    
    Restrito a alterações em parcelas pendentes.
    Apenas campos como data de vencimento e valor podem ser alterados.
    
    - **id_parcela**: ID da parcela
    - **id_empresa**: ID da empresa para verificação de acesso
    """
    verify_permission(current_user, "parcelas:editar", id_empresa)
    
    parcela_service = ParcelaService(session)
    log_service = LogSistemaService(session)
    
    parcela_atualizada = await parcela_service.atualizar_parcela(
        id_parcela=id_parcela,
        id_empresa=id_empresa,
        parcela_update=parcela_update,
        id_usuario=current_user.id
    )
    
    # Registrar log de atividade
    await log_service.registrar_log(
        LogSistemaCreate(
            id_usuario=current_user.id,
            id_empresa=id_empresa,
            acao="parcela:atualizacao",
            descricao=f"Parcela #{id_parcela} atualizada"
        )
    )
    
    return parcela_atualizada


@router.post("/{id_parcela}/pagar", response_model=Parcela)
async def pagar_parcela(
    id_parcela: UUID,
    dados_pagamento: ParcelaPagamento,
    id_empresa: UUID,
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Realizar pagamento de parcela individual.
    
    Atualiza o saldo da conta bancária e status da parcela.
    
    - **id_parcela**: ID da parcela
    - **id_empresa**: ID da empresa para verificação de acesso
    - **dados_pagamento**: Dados para o pagamento (data, id_conta, valor efetivo, etc)
    """
    verify_permission(current_user, "parcelas:pagar", id_empresa)
    
    parcela_service = ParcelaService(session)
    log_service = LogSistemaService(session)
    
    parcela_paga = await parcela_service.pagar_parcela(
        id_parcela=id_parcela,
        id_empresa=id_empresa,
        dados_pagamento=dados_pagamento,
        id_usuario=current_user.id
    )
    
    # Registrar log de atividade
    await log_service.registrar_log(
        LogSistemaCreate(
            id_usuario=current_user.id,
            id_empresa=id_empresa,
            acao="parcela:pagamento",
            descricao=f"Parcela #{id_parcela} paga no valor de {dados_pagamento.valor_pago}"
        )
    )
    
    return parcela_paga


@router.post("/{id_parcela}/cancelar", response_model=Parcela)
async def cancelar_parcela(
    id_parcela: UUID,
    id_empresa: UUID,
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Cancelar parcela.
    
    Verifica status atual e cancela lançamentos relacionados.
    
    - **id_parcela**: ID da parcela
    - **id_empresa**: ID da empresa para verificação de acesso
    """
    verify_permission(current_user, "parcelas:cancelar", id_empresa)
    
    parcela_service = ParcelaService(session)
    log_service = LogSistemaService(session)
    
    parcela_cancelada = await parcela_service.cancelar_parcela(
        id_parcela=id_parcela,
        id_empresa=id_empresa,
        id_usuario=current_user.id
    )
    
    # Registrar log de atividade
    await log_service.registrar_log(
        LogSistemaCreate(
            id_usuario=current_user.id,
            id_empresa=id_empresa,
            acao="parcela:cancelamento",
            descricao=f"Parcela #{id_parcela} cancelada"
        )
    )
    
    return parcela_cancelada


@router.get("/dashboard", response_model=ParcelaDashboard)
async def dashboard_parcelas(
    id_empresa: UUID,
    dias_vencidas: int = Query(30, ge=0),
    dias_proximas: int = Query(15, ge=0),
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Dashboard de parcelas vencidas e próximas.
    
    Retorna resumo financeiro para visualização rápida.
    
    - **id_empresa**: ID da empresa (obrigatório)
    - **dias_vencidas**: Quantidade de dias para considerar parcelas vencidas
    - **dias_proximas**: Quantidade de dias para considerar próximas parcelas
    """
    verify_permission(current_user, "parcelas:dashboard", id_empresa)
    
    parcela_service = ParcelaService(session)
    dashboard = await parcela_service.get_dashboard_parcelas(
        id_empresa=id_empresa,
        dias_vencidas=dias_vencidas,
        dias_proximas=dias_proximas
    )
    
    return dashboard 