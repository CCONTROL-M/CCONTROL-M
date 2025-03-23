"""Router de lançamentos financeiros para o sistema CCONTROL-M."""
from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.schemas.lancamento import (
    Lancamento, 
    LancamentoCreate, 
    LancamentoUpdate, 
    LancamentoWithDetalhes,
    RelatorioFinanceiro
)
from app.schemas.usuario import Usuario
from app.services.lancamento_service import LancamentoService
from app.services.log_sistema_service import LogSistemaService
from app.schemas.log_sistema import LogSistemaCreate
from app.schemas.pagination import PaginatedResponse
from app.dependencies import get_current_user, get_current_active_user
from app.utils.pagination import paginate
from app.utils.permissions import require_permission


router = APIRouter(
    prefix="/lancamentos",
    tags=["Lançamentos"],
    responses={404: {"description": "Lançamento não encontrado"}}
)


@router.get(
    "",
    response_model=PaginatedResponse[Lancamento],
    summary="Listar lançamentos financeiros",
    description="Retorna uma lista paginada de lançamentos financeiros com filtros diversos",
    responses={
        status.HTTP_200_OK: {
            "description": "Lista de lançamentos obtida com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "items": [
                            {
                                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                "descricao": "Pagamento fornecedor XYZ",
                                "valor": 1500.00,
                                "data_lancamento": "2023-05-10",
                                "data_pagamento": "2023-05-15",
                                "tipo": "DESPESA",
                                "status": "PAGO",
                                "id_categoria": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                "id_empresa": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
                            },
                            {
                                "id": "4fa85f64-5717-4562-b3fc-2c963f66afa7",
                                "descricao": "Recebimento cliente ABC",
                                "valor": 2500.00,
                                "data_lancamento": "2023-05-12",
                                "data_pagamento": None,
                                "tipo": "RECEITA",
                                "status": "PENDENTE",
                                "id_categoria": "5fa85f64-5717-4562-b3fc-2c963f66afa8",
                                "id_empresa": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
                            }
                        ],
                        "total": 125,
                        "page": 1,
                        "pages": 13,
                        "page_size": 10
                    }
                }
            }
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Não autenticado"
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Sem permissão para acessar este recurso"
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Erro de validação nos parâmetros"
        }
    }
)
@require_permission("lancamentos", "listar")
async def listar_lancamentos(
    id_empresa: UUID = Query(..., description="ID da empresa", example="3fa85f64-5717-4562-b3fc-2c963f66afa6"),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo (RECEITA, DESPESA)", example="DESPESA"),
    id_categoria: Optional[UUID] = Query(None, description="Filtrar por categoria"),
    id_centro_custo: Optional[UUID] = Query(None, description="Filtrar por centro de custo"),
    id_conta: Optional[UUID] = Query(None, description="Filtrar por conta bancária"),
    status: Optional[str] = Query(None, description="Filtrar por status (PENDENTE, PAGO, CANCELADO)", example="PENDENTE"),
    data_inicio: Optional[str] = Query(None, description="Data inicial (formato YYYY-MM-DD)", example="2023-01-01"),
    data_fim: Optional[str] = Query(None, description="Data final (formato YYYY-MM-DD)", example="2023-12-31"),
    page: int = Query(1, ge=1, description="Página atual"),
    page_size: int = Query(10, ge=1, le=100, description="Itens por página"),
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Listar lançamentos financeiros com filtros e paginação.
    
    - **id_empresa**: ID da empresa (obrigatório)
    - **tipo**: Tipo do lançamento (receita, despesa)
    - **id_categoria**: ID da categoria
    - **id_centro_custo**: ID do centro de custo
    - **id_conta**: ID da conta bancária
    - **status**: Status do lançamento (pendente, pago, cancelado)
    - **data_inicio**: Data inicial (formato YYYY-MM-DD)
    - **data_fim**: Data final (formato YYYY-MM-DD)
    - **page**: Número da página
    - **page_size**: Tamanho da página
    """
    lancamento_service = LancamentoService(session)
    lancamentos, total = await lancamento_service.listar_lancamentos(
        id_empresa=id_empresa,
        tipo=tipo,
        id_categoria=id_categoria,
        id_centro_custo=id_centro_custo,
        id_conta=id_conta,
        status=status,
        data_inicio=data_inicio,
        data_fim=data_fim,
        page=page,
        page_size=page_size
    )
    
    return paginate(lancamentos, total, page, page_size)


@router.get("/{id_lancamento}", response_model=LancamentoWithDetalhes)
@require_permission("lancamentos", "visualizar")
async def obter_lancamento(
    id_lancamento: UUID,
    id_empresa: UUID,
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Buscar lançamento por ID.
    
    - **id_lancamento**: ID do lançamento
    - **id_empresa**: ID da empresa para verificação de acesso
    """
    lancamento_service = LancamentoService(session)
    lancamento = await lancamento_service.get_lancamento_detalhes(id_lancamento, id_empresa)
    
    return lancamento


@router.post("", response_model=LancamentoWithDetalhes, status_code=status.HTTP_201_CREATED)
@require_permission("lancamentos", "criar")
async def criar_lancamento(
    lancamento: LancamentoCreate,
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Criar novo lançamento financeiro.
    
    Realiza validações de saldo, categoria, centro de custo e conta bancária.
    
    - **lancamento**: Dados do lançamento a ser criado
    """
    lancamento_service = LancamentoService(session)
    log_service = LogSistemaService(session)
    
    novo_lancamento = await lancamento_service.criar_lancamento(
        lancamento_create=lancamento,
        id_usuario=current_user.id
    )
    
    # Registrar log de atividade
    await log_service.registrar_log(
        LogSistemaCreate(
            id_usuario=current_user.id,
            id_empresa=lancamento.id_empresa,
            acao="lancamento:criacao",
            descricao=f"Lançamento #{novo_lancamento.id} criado do tipo {novo_lancamento.tipo}"
        )
    )
    
    return novo_lancamento


@router.put("/{id_lancamento}", response_model=LancamentoWithDetalhes)
@require_permission("lancamentos", "editar")
async def atualizar_lancamento(
    id_lancamento: UUID,
    lancamento_update: LancamentoUpdate,
    id_empresa: UUID,
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Atualizar lançamento existente.
    
    Existem regras específicas de quais campos podem ser atualizados
    dependendo do status do lançamento.
    
    - **id_lancamento**: ID do lançamento
    - **id_empresa**: ID da empresa para verificação de acesso
    """
    lancamento_service = LancamentoService(session)
    log_service = LogSistemaService(session)
    
    lancamento_atualizado = await lancamento_service.atualizar_lancamento(
        id_lancamento=id_lancamento,
        id_empresa=id_empresa,
        lancamento_update=lancamento_update,
        id_usuario=current_user.id
    )
    
    # Registrar log de atividade
    await log_service.registrar_log(
        LogSistemaCreate(
            id_usuario=current_user.id,
            id_empresa=id_empresa,
            acao="lancamento:atualizacao",
            descricao=f"Lançamento #{id_lancamento} atualizado"
        )
    )
    
    return lancamento_atualizado


@router.post("/{id_lancamento}/pagar", response_model=LancamentoWithDetalhes)
@require_permission("lancamentos", "pagar")
async def pagar_lancamento(
    id_lancamento: UUID,
    id_conta: UUID,
    data_pagamento: str,
    id_empresa: UUID,
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Efetivar pagamento de um lançamento pendente.
    
    Atualiza o saldo da conta bancária conforme o tipo de lançamento.
    
    - **id_lancamento**: ID do lançamento
    - **id_conta**: ID da conta bancária para efetuar o pagamento
    - **data_pagamento**: Data do pagamento (formato YYYY-MM-DD)
    - **id_empresa**: ID da empresa para verificação de acesso
    """
    lancamento_service = LancamentoService(session)
    log_service = LogSistemaService(session)
    
    lancamento_pago = await lancamento_service.pagar_lancamento(
        id_lancamento=id_lancamento,
        id_empresa=id_empresa,
        id_conta=id_conta,
        data_pagamento=data_pagamento,
        id_usuario=current_user.id
    )
    
    # Registrar log de atividade
    await log_service.registrar_log(
        LogSistemaCreate(
            id_usuario=current_user.id,
            id_empresa=id_empresa,
            acao="lancamento:pagamento",
            descricao=f"Lançamento #{id_lancamento} pago em {data_pagamento}"
        )
    )
    
    return lancamento_pago


@router.post("/{id_lancamento}/cancelar", response_model=LancamentoWithDetalhes)
@require_permission("lancamentos", "cancelar")
async def cancelar_lancamento(
    id_lancamento: UUID,
    id_empresa: UUID,
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Cancelar lançamento.
    
    Verifica status atual e dependências antes de cancelar.
    Se o lançamento já foi pago, reverte o saldo na conta bancária.
    
    - **id_lancamento**: ID do lançamento
    - **id_empresa**: ID da empresa para verificação de acesso
    """
    lancamento_service = LancamentoService(session)
    log_service = LogSistemaService(session)
    
    lancamento_cancelado = await lancamento_service.cancelar_lancamento(
        id_lancamento=id_lancamento,
        id_empresa=id_empresa,
        id_usuario=current_user.id
    )
    
    # Registrar log de atividade
    await log_service.registrar_log(
        LogSistemaCreate(
            id_usuario=current_user.id,
            id_empresa=id_empresa,
            acao="lancamento:cancelamento",
            descricao=f"Lançamento #{id_lancamento} cancelado"
        )
    )
    
    return lancamento_cancelado


@router.get("/relatorio", response_model=RelatorioFinanceiro)
@require_permission("lancamentos", "relatorios")
async def relatorio_financeiro(
    id_empresa: UUID,
    data_inicio: str,
    data_fim: str,
    agrupar_por: str = Query("dia", description="Opções: dia, semana, mes, categoria, centro_custo"),
    tipo: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Gerar relatório financeiro por período.
    
    - **id_empresa**: ID da empresa (obrigatório)
    - **data_inicio**: Data inicial do período (formato YYYY-MM-DD)
    - **data_fim**: Data final do período (formato YYYY-MM-DD)
    - **agrupar_por**: Como agrupar os resultados (dia, semana, mes, categoria, centro_custo)
    - **tipo**: Filtrar por tipo de lançamento (receita, despesa)
    """
    lancamento_service = LancamentoService(session)
    relatorio = await lancamento_service.gerar_relatorio_financeiro(
        id_empresa=id_empresa,
        data_inicio=data_inicio,
        data_fim=data_fim,
        agrupar_por=agrupar_por,
        tipo=tipo
    )
    
    return relatorio


@router.get("/fluxo-caixa", response_model=dict)
@require_permission("lancamentos", "fluxo_caixa")
async def fluxo_caixa(
    id_empresa: UUID,
    id_conta: Optional[UUID] = None,
    data_inicio: str = Query(..., description="Data inicial (formato YYYY-MM-DD)"),
    data_fim: str = Query(..., description="Data final (formato YYYY-MM-DD)"),
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Obter fluxo de caixa para o período especificado.
    
    - **id_empresa**: ID da empresa (obrigatório)
    - **id_conta**: Filtrar por conta bancária específica
    - **data_inicio**: Data inicial (formato YYYY-MM-DD)
    - **data_fim**: Data final (formato YYYY-MM-DD)
    """
    lancamento_service = LancamentoService(session)
    fluxo = await lancamento_service.calcular_fluxo_caixa(
        id_empresa=id_empresa,
        id_conta=id_conta,
        data_inicio=data_inicio,
        data_fim=data_fim
    )
    
    return fluxo 