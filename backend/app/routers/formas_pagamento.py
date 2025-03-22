"""
Router para gerenciamento de formas de pagamento no sistema CCONTROL-M.

Este módulo implementa os endpoints para criar, listar, atualizar, remover e 
gerenciar formas de pagamento, com suporte a multi-tenancy e controle de permissões.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from uuid import UUID
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.forma_pagamento import (
    FormaPagamento, FormaPagamentoCreate, FormaPagamentoUpdate, FormaPagamentoList
)
from app.services.forma_pagamento_service import FormaPagamentoService
from app.services.log_sistema_service import LogSistemaService
from app.schemas.token import TokenPayload
from app.dependencies import get_current_user
from app.database import get_async_session
from app.utils.permissions import verify_permission
from app.schemas.log_sistema import LogSistemaCreate

# Configuração de logger
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/formas-pagamento",
    tags=["Formas de Pagamento"],
    responses={404: {"description": "Forma de pagamento não encontrada"}},
)


@router.get("", response_model=FormaPagamentoList)
async def listar_formas_pagamento(
    id_empresa: UUID,
    skip: int = Query(0, ge=0, description="Registros para pular (paginação)"),
    limit: int = Query(100, ge=1, le=100, description="Limite de registros por página"),
    nome: Optional[str] = Query(None, description="Filtrar por nome da forma de pagamento"),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo da forma de pagamento"),
    ativa: Optional[bool] = Query(None, description="Filtrar por status (ativa/inativa)"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Lista formas de pagamento com paginação e filtros opcionais.
    
    - **id_empresa**: ID da empresa (obrigatório)
    - **skip**: Quantos registros pular (para paginação)
    - **limit**: Limite de registros por página
    - **nome**: Filtro opcional por nome da forma de pagamento
    - **tipo**: Filtro opcional por tipo de forma de pagamento
    - **ativa**: Filtro opcional por status (ativa/inativa)
    
    Retorna lista paginada de formas de pagamento que correspondem aos filtros aplicados.
    """
    # Verificar permissão
    verify_permission(current_user, "formas_pagamento:listar", id_empresa)
    
    # Inicializar serviço
    forma_pagamento_service = FormaPagamentoService()
    
    # Construir filtros
    filtros = {}
    if nome:
        filtros["nome"] = nome
    if tipo:
        filtros["tipo"] = tipo
    if ativa is not None:
        filtros["ativa"] = ativa
    
    formas, total = await forma_pagamento_service.listar_formas_pagamento(
        id_empresa=id_empresa,
        skip=skip,
        limit=limit,
        filtros=filtros
    )
    
    # Calcular página atual
    page = (skip // limit) + 1 if limit > 0 else 1
    
    # Retornar resposta paginada
    return FormaPagamentoList(
        items=formas,
        total=total,
        page=page,
        size=limit
    )


@router.get("/{id_forma}", response_model=FormaPagamento)
async def obter_forma_pagamento(
    id_forma: UUID = Path(..., description="ID da forma de pagamento"),
    id_empresa: UUID = Query(..., description="ID da empresa"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Busca uma forma de pagamento específica pelo ID.
    
    - **id_forma**: ID da forma de pagamento
    - **id_empresa**: ID da empresa para validação
    
    Retorna os dados detalhados da forma de pagamento.
    """
    # Verificar permissão
    verify_permission(current_user, "formas_pagamento:visualizar", id_empresa)
    
    # Inicializar serviço e buscar forma de pagamento
    forma_pagamento_service = FormaPagamentoService()
    forma_pagamento = await forma_pagamento_service.get_forma_pagamento(id_forma, id_empresa)
    
    return forma_pagamento


@router.post("", response_model=FormaPagamento, status_code=status.HTTP_201_CREATED)
async def criar_forma_pagamento(
    forma_pagamento: FormaPagamentoCreate,
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Cria uma nova forma de pagamento.
    
    - **forma_pagamento**: Dados da forma de pagamento a ser criada
    
    Retorna os dados da forma de pagamento criada.
    """
    # Verificar permissão
    verify_permission(current_user, "formas_pagamento:criar", forma_pagamento.id_empresa)
    
    # Inicializar serviços
    forma_pagamento_service = FormaPagamentoService()
    log_service = LogSistemaService()
    
    # Criar forma de pagamento
    nova_forma = await forma_pagamento_service.criar_forma_pagamento(forma_pagamento)
    
    # Registrar log
    await log_service.registrar_log(
        LogSistemaCreate(
            id_usuario=current_user.sub,
            id_empresa=forma_pagamento.id_empresa,
            acao="forma_pagamento:criacao",
            descricao=f"Forma de Pagamento {nova_forma.nome} (ID: {nova_forma.id_forma}) criada"
        )
    )
    
    return nova_forma


@router.put("/{id_forma}", response_model=FormaPagamento)
async def atualizar_forma_pagamento(
    id_forma: UUID,
    forma_pagamento: FormaPagamentoUpdate,
    id_empresa: UUID = Query(..., description="ID da empresa"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Atualiza dados de uma forma de pagamento existente.
    
    - **id_forma**: ID da forma de pagamento
    - **forma_pagamento**: Dados para atualização
    - **id_empresa**: ID da empresa para validação
    
    Retorna os dados atualizados da forma de pagamento.
    """
    # Verificar permissão
    verify_permission(current_user, "formas_pagamento:editar", id_empresa)
    
    # Inicializar serviços
    forma_pagamento_service = FormaPagamentoService()
    log_service = LogSistemaService()
    
    # Buscar forma atual para o log
    forma_atual = await forma_pagamento_service.get_forma_pagamento(id_forma, id_empresa)
    
    # Atualizar forma de pagamento
    forma_atualizada = await forma_pagamento_service.atualizar_forma_pagamento(
        id_forma, 
        forma_pagamento, 
        id_empresa
    )
    
    # Registrar log
    await log_service.registrar_log(
        LogSistemaCreate(
            id_usuario=current_user.sub,
            id_empresa=id_empresa,
            acao="forma_pagamento:atualizacao",
            descricao=f"Forma de Pagamento {forma_atual.nome} (ID: {id_forma}) atualizada"
        )
    )
    
    return forma_atualizada


@router.delete("/{id_forma}", status_code=status.HTTP_200_OK)
async def remover_forma_pagamento(
    id_forma: UUID,
    id_empresa: UUID = Query(..., description="ID da empresa"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Remove uma forma de pagamento.
    
    - **id_forma**: ID da forma de pagamento
    - **id_empresa**: ID da empresa para validação
    
    Retorna mensagem de confirmação.
    """
    # Verificar permissão
    verify_permission(current_user, "formas_pagamento:excluir", id_empresa)
    
    # Inicializar serviços
    forma_pagamento_service = FormaPagamentoService()
    log_service = LogSistemaService()
    
    # Buscar forma para o log antes de remover
    forma = await forma_pagamento_service.get_forma_pagamento(id_forma, id_empresa)
    
    # Remover forma de pagamento
    resultado = await forma_pagamento_service.remover_forma_pagamento(id_forma, id_empresa)
    
    # Registrar log
    await log_service.registrar_log(
        LogSistemaCreate(
            id_usuario=current_user.sub,
            id_empresa=id_empresa,
            acao="forma_pagamento:exclusao",
            descricao=f"Forma de Pagamento {forma.nome} (ID: {id_forma}) removida"
        )
    )
    
    return resultado


@router.patch("/{id_forma}/toggle", response_model=FormaPagamento)
async def alternar_status_forma_pagamento(
    id_forma: UUID,
    id_empresa: UUID = Query(..., description="ID da empresa"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Alterna o status ativo/inativo de uma forma de pagamento.
    
    - **id_forma**: ID da forma de pagamento
    - **id_empresa**: ID da empresa para validação
    
    Retorna os dados atualizados da forma de pagamento.
    """
    # Verificar permissão
    verify_permission(current_user, "formas_pagamento:ativar", id_empresa)
    
    # Inicializar serviços
    forma_pagamento_service = FormaPagamentoService()
    log_service = LogSistemaService()
    
    # Alternar status da forma de pagamento
    forma_atualizada = await forma_pagamento_service.alternar_status_forma_pagamento(id_forma, id_empresa)
    
    # Definir status para o log
    status_descricao = "ativada" if forma_atualizada.ativa else "desativada"
    
    # Registrar log
    await log_service.registrar_log(
        LogSistemaCreate(
            id_usuario=current_user.sub,
            id_empresa=id_empresa,
            acao="forma_pagamento:alternar_status",
            descricao=f"Forma de Pagamento {forma_atualizada.nome} (ID: {id_forma}) {status_descricao}"
        )
    )
    
    return forma_atualizada 