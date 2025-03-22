'''
Router de Clientes para o sistema CCONTROL-M.
Implementa as operações CRUD protegidas por JWT, com filtros, paginação e uso de serviço.
'''

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from uuid import UUID
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.cliente import (
    Cliente, ClienteCreate, ClienteUpdate, ClienteList
)
from app.schemas.pagination import PaginatedResponse
from app.services.cliente_service import ClienteService
from app.services.log_sistema_service import LogSistemaService
from app.schemas.token import TokenPayload
from app.models.usuario import Usuario
from app.dependencies import get_current_user
from app.database import get_async_session
from app.utils.permissions import require_permission
from app.schemas.log_sistema import LogSistemaCreate

# Configuração de logger
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"],
    responses={404: {"description": "Cliente não encontrado"}},
)


@router.get("", response_model=ClienteList)
@require_permission("clientes", "listar")
async def listar_clientes(
    id_empresa: UUID,
    skip: int = Query(0, ge=0, description="Registros para pular (paginação)"),
    limit: int = Query(100, ge=1, le=100, description="Limite de registros por página"),
    nome: Optional[str] = Query(None, description="Filtrar por nome do cliente"),
    cpf_cnpj: Optional[str] = Query(None, description="Filtrar por CPF/CNPJ"),
    ativo: Optional[bool] = Query(None, description="Filtrar por status (ativo/inativo)"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Lista clientes com paginação e filtros opcionais.
    
    - **id_empresa**: ID da empresa (obrigatório)
    - **skip**: Quantos registros pular (para paginação)
    - **limit**: Limite de registros por página
    - **nome**: Filtro opcional por nome do cliente
    - **cpf_cnpj**: Filtro opcional por CPF/CNPJ
    - **ativo**: Filtro opcional por status (ativo/inativo)
    
    Retorna lista paginada de clientes que correspondem aos filtros aplicados.
    """
    # Inicializar serviço e buscar clientes
    cliente_service = ClienteService()
    clientes, total = await cliente_service.listar_clientes(
        id_empresa=id_empresa,
        skip=skip,
        limit=limit,
        nome=nome,
        cpf_cnpj=cpf_cnpj,
        ativo=ativo
    )
    
    # Calcular página atual
    page = (skip // limit) + 1 if limit > 0 else 1
    
    # Retornar resposta paginada
    return ClienteList(
        items=clientes,
        total=total,
        page=page,
        size=limit
    )


@router.get("/{id_cliente}", response_model=Cliente)
@require_permission("clientes", "visualizar")
async def obter_cliente(
    id_cliente: UUID = Path(..., description="ID do cliente"),
    id_empresa: UUID = Query(..., description="ID da empresa"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Busca um cliente específico pelo ID.
    
    - **id_cliente**: ID do cliente
    - **id_empresa**: ID da empresa para validação
    
    Retorna os dados detalhados do cliente.
    """
    # Inicializar serviço e buscar cliente
    cliente_service = ClienteService()
    cliente = await cliente_service.get_cliente(id_cliente, id_empresa)
    
    return cliente


@router.post("", response_model=Cliente, status_code=status.HTTP_201_CREATED)
@require_permission("clientes", "criar")
async def criar_cliente(
    cliente: ClienteCreate,
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Cria um novo cliente.
    
    - **cliente**: Dados do cliente a ser criado
    
    Retorna os dados do cliente criado.
    """
    # Inicializar serviços
    cliente_service = ClienteService()
    log_service = LogSistemaService()
    
    # Criar cliente
    novo_cliente = await cliente_service.criar_cliente(cliente)
    
    # Registrar log
    await log_service.registrar_log(
        LogSistemaCreate(
            id_usuario=current_user.sub,
            id_empresa=cliente.id_empresa,
            acao="cliente:criacao",
            descricao=f"Cliente {novo_cliente.nome} (ID: {novo_cliente.id_cliente}) criado"
        )
    )
    
    return novo_cliente


@router.put("/{id_cliente}", response_model=Cliente)
@require_permission("clientes", "editar")
async def atualizar_cliente(
    id_cliente: UUID,
    cliente: ClienteUpdate,
    id_empresa: UUID = Query(..., description="ID da empresa"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Atualiza dados de um cliente existente.
    
    - **id_cliente**: ID do cliente
    - **cliente**: Dados para atualização
    - **id_empresa**: ID da empresa para validação
    
    Retorna os dados atualizados do cliente.
    """
    # Inicializar serviços
    cliente_service = ClienteService()
    log_service = LogSistemaService()
    
    # Buscar cliente atual para o log
    cliente_atual = await cliente_service.get_cliente(id_cliente, id_empresa)
    
    # Atualizar cliente
    cliente_atualizado = await cliente_service.atualizar_cliente(id_cliente, cliente, id_empresa)
    
    # Registrar log
    await log_service.registrar_log(
        LogSistemaCreate(
            id_usuario=current_user.sub,
            id_empresa=id_empresa,
            acao="cliente:atualizacao",
            descricao=f"Cliente {cliente_atual.nome} (ID: {id_cliente}) atualizado"
        )
    )
    
    return cliente_atualizado


@router.delete("/{id_cliente}", status_code=status.HTTP_200_OK)
@require_permission("clientes", "deletar")
async def remover_cliente(
    id_cliente: UUID,
    id_empresa: UUID = Query(..., description="ID da empresa"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Remove um cliente.
    
    - **id_cliente**: ID do cliente
    - **id_empresa**: ID da empresa para validação
    
    Retorna mensagem de confirmação.
    """
    # Inicializar serviços
    cliente_service = ClienteService()
    log_service = LogSistemaService()
    
    # Buscar cliente para o log antes de remover
    cliente = await cliente_service.get_cliente(id_cliente, id_empresa)
    
    # Remover cliente
    resultado = await cliente_service.remover_cliente(id_cliente, id_empresa)
    
    # Registrar log
    await log_service.registrar_log(
        LogSistemaCreate(
            id_usuario=current_user.sub,
            id_empresa=id_empresa,
            acao="cliente:exclusao",
            descricao=f"Cliente {cliente.nome} (ID: {id_cliente}) removido"
        )
    )
    
    return resultado 