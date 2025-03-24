"""
Router para gerenciamento de contas bancárias no sistema CCONTROL-M.

Este módulo implementa os endpoints para criar, listar, atualizar, remover e 
gerenciar contas bancárias, com suporte a multi-tenancy e controle de permissões.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from uuid import UUID
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.schemas.conta_bancaria import (
    ContaBancaria, ContaBancariaCreate, ContaBancariaUpdate, 
    ContaBancariaList, ContaBancariaAtualizacaoSaldo
)
from app.services.conta_bancaria_service import ContaBancariaService
from app.services.log_sistema_service import LogSistemaService
from app.schemas.token import TokenPayload
from app.models.usuario import Usuario
from app.dependencies import get_current_user
from app.database import get_async_session
from app.utils.permissions import verify_permission
from app.schemas.log_sistema import LogSistemaCreate
from app.schemas.pagination import PaginatedResponse

# Configuração de logger
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/contas-bancarias",
    tags=["Contas Bancárias"],
    responses={404: {"description": "Conta bancária não encontrada"}},
)


@router.get("", response_model=PaginatedResponse[ContaBancariaList])
async def listar_contas_bancarias(
    id_empresa: UUID,
    skip: int = Query(0, ge=0, description="Registros para pular (paginação)"),
    limit: int = Query(100, ge=1, le=100, description="Limite de registros por página"),
    nome: Optional[str] = Query(None, description="Filtrar por nome da conta"),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo da conta"),
    banco: Optional[str] = Query(None, description="Filtrar por banco"),
    ativa: Optional[bool] = Query(None, description="Filtrar por status (ativa/inativa)"),
    current_user: TokenPayload = Depends(get_current_user),
    service: ContaBancariaService = Depends(),
):
    """
    Lista contas bancárias com paginação e filtros opcionais.
    
    - **id_empresa**: ID da empresa (obrigatório)
    - **skip**: Quantos registros pular (para paginação)
    - **limit**: Limite de registros por página
    - **nome**: Filtro opcional por nome da conta
    - **tipo**: Filtro opcional por tipo de conta
    - **banco**: Filtro opcional por banco
    - **ativa**: Filtro opcional por status (ativa/inativa)
    
    Retorna lista paginada de contas bancárias que correspondem aos filtros aplicados.
    """
    # Verificar permissão
    verify_permission(current_user, "contas_bancarias:listar", id_empresa)
    
    # Construir filtros
    filtros = {}
    if nome:
        filtros["nome"] = nome
    if tipo:
        filtros["tipo"] = tipo
    if banco:
        filtros["banco"] = banco
    if ativa is not None:
        filtros["ativa"] = ativa
    
    contas, total = await service.listar_contas_bancarias(
        id_empresa=id_empresa,
        skip=skip,
        limit=limit,
        filtros=filtros
    )
    
    # Calcular página atual
    page = (skip // limit) + 1 if limit > 0 else 1
    
    # Retornar resposta paginada
    return PaginatedResponse(
        items=contas,
        total=total,
        page=page,
        size=limit
    )


@router.get("/{id_conta}", response_model=ContaBancaria)
async def obter_conta_bancaria(
    id_conta: UUID = Path(..., description="ID da conta bancária"),
    id_empresa: UUID = Query(..., description="ID da empresa"),
    current_user: TokenPayload = Depends(get_current_user),
    service: ContaBancariaService = Depends(),
):
    """
    Busca uma conta bancária específica pelo ID.
    
    - **id_conta**: ID da conta bancária
    - **id_empresa**: ID da empresa para validação
    
    Retorna os dados detalhados da conta bancária.
    """
    # Verificar permissão
    verify_permission(current_user, "contas_bancarias:visualizar", id_empresa)
    
    # Buscar conta bancária
    conta_bancaria = await service.get_conta_bancaria(id_conta, id_empresa)
    
    return conta_bancaria


@router.post("", response_model=ContaBancaria, status_code=status.HTTP_201_CREATED)
async def criar_conta_bancaria(
    conta_bancaria: ContaBancariaCreate,
    current_user: TokenPayload = Depends(get_current_user),
    service: ContaBancariaService = Depends(),
    log_service: LogSistemaService = Depends(),
):
    """
    Cria uma nova conta bancária.
    
    - **conta_bancaria**: Dados da conta bancária a ser criada
    
    Retorna os dados da conta bancária criada.
    """
    # Verificar permissão
    verify_permission(current_user, "contas_bancarias:criar", conta_bancaria.id_empresa)
    
    # Criar conta bancária
    nova_conta = await service.criar_conta_bancaria(conta_bancaria, current_user.sub)
    
    # Registrar log
    await log_service.registrar_log(
        LogSistemaCreate(
            id_usuario=current_user.sub,
            id_empresa=conta_bancaria.id_empresa,
            acao="conta_bancaria:criacao",
            descricao=f"Conta Bancária {nova_conta.nome} (ID: {nova_conta.id_conta}) criada"
        )
    )
    
    return nova_conta


@router.put("/{id_conta}", response_model=ContaBancaria)
async def atualizar_conta_bancaria(
    id_conta: UUID,
    conta_bancaria: ContaBancariaUpdate,
    id_empresa: UUID = Query(..., description="ID da empresa"),
    current_user: TokenPayload = Depends(get_current_user),
    service: ContaBancariaService = Depends(),
    log_service: LogSistemaService = Depends(),
):
    """
    Atualiza dados de uma conta bancária existente.
    
    - **id_conta**: ID da conta bancária
    - **conta_bancaria**: Dados para atualização
    - **id_empresa**: ID da empresa para validação
    
    Retorna os dados atualizados da conta bancária.
    """
    # Verificar permissão
    verify_permission(current_user, "contas_bancarias:editar", id_empresa)
    
    # Buscar conta atual para o log
    conta_atual = await service.get_conta_bancaria(id_conta, id_empresa)
    
    # Atualizar conta bancária
    conta_atualizada = await service.atualizar_conta_bancaria(
        id_conta, 
        conta_bancaria, 
        id_empresa,
        current_user.sub
    )
    
    # Registrar log
    await log_service.registrar_log(
        LogSistemaCreate(
            id_usuario=current_user.sub,
            id_empresa=id_empresa,
            acao="conta_bancaria:atualizacao",
            descricao=f"Conta Bancária {conta_atual.nome} (ID: {id_conta}) atualizada"
        )
    )
    
    return conta_atualizada


@router.delete("/{id_conta}", status_code=status.HTTP_200_OK)
async def remover_conta_bancaria(
    id_conta: UUID,
    id_empresa: UUID = Query(..., description="ID da empresa"),
    current_user: TokenPayload = Depends(get_current_user),
    service: ContaBancariaService = Depends(),
    log_service: LogSistemaService = Depends(),
):
    """
    Remove uma conta bancária.
    
    - **id_conta**: ID da conta bancária
    - **id_empresa**: ID da empresa para validação
    
    Retorna mensagem de confirmação.
    """
    # Verificar permissão
    verify_permission(current_user, "contas_bancarias:excluir", id_empresa)
    
    # Buscar conta para o log antes de remover
    conta = await service.get_conta_bancaria(id_conta, id_empresa)
    
    # Remover conta bancária
    resultado = await service.remover_conta_bancaria(id_conta, id_empresa)
    
    # Registrar log
    await log_service.registrar_log(
        LogSistemaCreate(
            id_usuario=current_user.sub,
            id_empresa=id_empresa,
            acao="conta_bancaria:exclusao",
            descricao=f"Conta Bancária {conta.nome} (ID: {id_conta}) removida"
        )
    )
    
    return resultado


@router.patch("/{id_conta}/toggle", response_model=ContaBancaria)
async def alternar_status_conta(
    id_conta: UUID,
    id_empresa: UUID = Query(..., description="ID da empresa"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Alterna o status ativo/inativo de uma conta bancária.
    
    - **id_conta**: ID da conta bancária
    - **id_empresa**: ID da empresa para validação
    
    Retorna os dados atualizados da conta bancária.
    """
    # Verificar permissão
    verify_permission(current_user, "contas_bancarias:editar", id_empresa)
    
    # Inicializar serviços
    conta_bancaria_service = ContaBancariaService()
    log_service = LogSistemaService()
    
    # Alternar status da conta
    conta_atualizada = await conta_bancaria_service.alternar_status_conta(id_conta, id_empresa)
    
    # Definir status para o log
    status_descricao = "ativada" if conta_atualizada.ativa else "desativada"
    
    # Registrar log
    await log_service.registrar_log(
        LogSistemaCreate(
            id_usuario=current_user.sub,
            id_empresa=id_empresa,
            acao="conta_bancaria:alternar_status",
            descricao=f"Conta Bancária {conta_atualizada.nome} (ID: {id_conta}) {status_descricao}"
        )
    )
    
    return conta_atualizada


@router.patch("/{id_conta}/dashboard", response_model=ContaBancaria)
async def alternar_visibilidade_dashboard(
    id_conta: UUID,
    id_empresa: UUID = Query(..., description="ID da empresa"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Alterna a visibilidade no dashboard para uma conta bancária.
    
    - **id_conta**: ID da conta bancária
    - **id_empresa**: ID da empresa para validação
    
    Retorna os dados atualizados da conta bancária.
    """
    # Verificar permissão
    verify_permission(current_user, "contas_bancarias:editar", id_empresa)
    
    # Inicializar serviços
    conta_bancaria_service = ContaBancariaService()
    log_service = LogSistemaService()
    
    # Alternar visibilidade no dashboard
    conta_atualizada = await conta_bancaria_service.alternar_visibilidade_dashboard(id_conta, id_empresa)
    
    # Definir status para o log
    visibilidade = "visível" if conta_atualizada.mostrar_dashboard else "oculta"
    
    # Registrar log
    await log_service.registrar_log(
        LogSistemaCreate(
            id_usuario=current_user.sub,
            id_empresa=id_empresa,
            acao="conta_bancaria:alternar_dashboard",
            descricao=f"Conta Bancária {conta_atualizada.nome} (ID: {id_conta}) agora está {visibilidade} no dashboard"
        )
    )
    
    return conta_atualizada


@router.patch("/{id_conta}/saldo", response_model=ContaBancaria)
async def atualizar_saldo_manual(
    id_conta: UUID,
    dados_saldo: ContaBancariaAtualizacaoSaldo = Body(...),
    id_empresa: UUID = Query(..., description="ID da empresa"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Atualiza manualmente o saldo de uma conta bancária.
    
    - **id_conta**: ID da conta bancária
    - **dados_saldo**: Dados para atualização do saldo
    - **id_empresa**: ID da empresa para validação
    
    Retorna os dados atualizados da conta bancária.
    """
    # Verificar permissão
    verify_permission(current_user, "contas_bancarias:editar_saldo", id_empresa)
    
    # Inicializar serviços
    conta_bancaria_service = ContaBancariaService()
    log_service = LogSistemaService()
    
    # Buscar conta atual para o log
    conta_atual = await conta_bancaria_service.get_conta_bancaria(id_conta, id_empresa)
    
    # Atualizar saldo da conta
    conta_atualizada = await conta_bancaria_service.atualizar_saldo_manual(
        id_conta, 
        dados_saldo.saldo,
        dados_saldo.justificativa,
        id_empresa
    )
    
    # Registrar log
    await log_service.registrar_log(
        LogSistemaCreate(
            id_usuario=current_user.sub,
            id_empresa=id_empresa,
            acao="conta_bancaria:atualizacao_saldo",
            descricao=(
                f"Saldo da Conta Bancária {conta_atual.nome} (ID: {id_conta}) "
                f"atualizado de {conta_atual.saldo_atual} para {conta_atualizada.saldo_atual}. "
                f"Justificativa: {dados_saldo.justificativa}"
            )
        )
    )
    
    return conta_atualizada 