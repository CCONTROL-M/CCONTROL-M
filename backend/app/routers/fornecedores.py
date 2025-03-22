"""
Router de Fornecedores para o sistema CCONTROL-M.
Implementa as operações CRUD protegidas por JWT, com filtros, paginação e uso de serviço.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from uuid import UUID
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.fornecedor import (
    Fornecedor, FornecedorCreate, FornecedorUpdate, FornecedorList
)
from app.schemas.pagination import PaginatedResponse
from app.services.fornecedor_service import FornecedorService
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
    prefix="/fornecedores",
    tags=["fornecedores"],
    responses={404: {"description": "Fornecedor não encontrado"}},
)


@router.get("", response_model=FornecedorList)
@require_permission("fornecedores", "listar")
async def listar_fornecedores(
    id_empresa: UUID,
    skip: int = Query(0, ge=0, description="Registros para pular (paginação)"),
    limit: int = Query(100, ge=1, le=100, description="Limite de registros por página"),
    nome: Optional[str] = Query(None, description="Filtrar por nome do fornecedor"),
    cnpj: Optional[str] = Query(None, description="Filtrar por CNPJ"),
    avaliacao: Optional[int] = Query(None, ge=1, le=5, description="Filtrar por avaliação"),
    ativo: Optional[bool] = Query(None, description="Filtrar por status (ativo/inativo)"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Lista fornecedores com paginação e filtros opcionais.
    
    - **id_empresa**: ID da empresa (obrigatório)
    - **skip**: Quantos registros pular (para paginação)
    - **limit**: Limite de registros por página
    - **nome**: Filtro opcional por nome do fornecedor
    - **cnpj**: Filtro opcional por CNPJ
    - **avaliacao**: Filtro opcional por avaliação (1-5)
    - **ativo**: Filtro opcional por status (ativo/inativo)
    
    Retorna lista paginada de fornecedores que correspondem aos filtros aplicados.
    """
    # Inicializar serviço e buscar fornecedores
    fornecedor_service = FornecedorService()
    
    # Construir filtros
    filtros = {}
    if nome:
        filtros["nome"] = nome
    if cnpj:
        filtros["cnpj"] = cnpj
    if avaliacao is not None:
        filtros["avaliacao"] = avaliacao
    if ativo is not None:
        filtros["ativo"] = ativo
    
    fornecedores, total = await fornecedor_service.listar_fornecedores(
        id_empresa=id_empresa,
        skip=skip,
        limit=limit,
        filtros=filtros
    )
    
    # Calcular página atual
    page = (skip // limit) + 1 if limit > 0 else 1
    
    # Retornar resposta paginada
    return FornecedorList(
        items=fornecedores,
        total=total,
        page=page,
        size=limit
    )


@router.get("/{id_fornecedor}", response_model=Fornecedor)
@require_permission("fornecedores", "visualizar")
async def obter_fornecedor(
    id_fornecedor: UUID = Path(..., description="ID do fornecedor"),
    id_empresa: UUID = Query(..., description="ID da empresa"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Busca um fornecedor específico pelo ID.
    
    - **id_fornecedor**: ID do fornecedor
    - **id_empresa**: ID da empresa para validação
    
    Retorna os dados detalhados do fornecedor.
    """
    # Inicializar serviço e buscar fornecedor
    fornecedor_service = FornecedorService()
    fornecedor = await fornecedor_service.get_fornecedor(id_fornecedor, id_empresa)
    
    return fornecedor


@router.post("", response_model=Fornecedor, status_code=status.HTTP_201_CREATED)
@require_permission("fornecedores", "criar")
async def criar_fornecedor(
    fornecedor: FornecedorCreate,
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Cria um novo fornecedor.
    
    - **fornecedor**: Dados do fornecedor a ser criado
    
    Retorna os dados do fornecedor criado.
    """
    # Inicializar serviços
    fornecedor_service = FornecedorService()
    log_service = LogSistemaService()
    
    # Criar fornecedor
    novo_fornecedor = await fornecedor_service.criar_fornecedor(fornecedor)
    
    # Registrar log
    await log_service.registrar_log(
        LogSistemaCreate(
            id_usuario=current_user.sub,
            id_empresa=fornecedor.id_empresa,
            acao="fornecedor:criacao",
            descricao=f"Fornecedor {novo_fornecedor.nome} (ID: {novo_fornecedor.id_fornecedor}) criado"
        )
    )
    
    return novo_fornecedor


@router.put("/{id_fornecedor}", response_model=Fornecedor)
@require_permission("fornecedores", "editar")
async def atualizar_fornecedor(
    id_fornecedor: UUID,
    fornecedor: FornecedorUpdate,
    id_empresa: UUID = Query(..., description="ID da empresa"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Atualiza dados de um fornecedor existente.
    
    - **id_fornecedor**: ID do fornecedor
    - **fornecedor**: Dados para atualização
    - **id_empresa**: ID da empresa para validação
    
    Retorna os dados atualizados do fornecedor.
    """
    # Inicializar serviços
    fornecedor_service = FornecedorService()
    log_service = LogSistemaService()
    
    # Buscar fornecedor atual para o log
    fornecedor_atual = await fornecedor_service.get_fornecedor(id_fornecedor, id_empresa)
    
    # Atualizar fornecedor
    fornecedor_atualizado = await fornecedor_service.atualizar_fornecedor(
        id_fornecedor, 
        fornecedor, 
        id_empresa
    )
    
    # Registrar log
    await log_service.registrar_log(
        LogSistemaCreate(
            id_usuario=current_user.sub,
            id_empresa=id_empresa,
            acao="fornecedor:atualizacao",
            descricao=f"Fornecedor {fornecedor_atual.nome} (ID: {id_fornecedor}) atualizado"
        )
    )
    
    return fornecedor_atualizado


@router.delete("/{id_fornecedor}", status_code=status.HTTP_200_OK)
@require_permission("fornecedores", "excluir")
async def remover_fornecedor(
    id_fornecedor: UUID,
    id_empresa: UUID = Query(..., description="ID da empresa"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Remove um fornecedor.
    
    - **id_fornecedor**: ID do fornecedor
    - **id_empresa**: ID da empresa para validação
    
    Retorna mensagem de confirmação.
    """
    # Inicializar serviços
    fornecedor_service = FornecedorService()
    log_service = LogSistemaService()
    
    # Buscar fornecedor para o log antes de remover
    fornecedor = await fornecedor_service.get_fornecedor(id_fornecedor, id_empresa)
    
    # Remover fornecedor
    resultado = await fornecedor_service.remover_fornecedor(id_fornecedor, id_empresa)
    
    # Registrar log
    await log_service.registrar_log(
        LogSistemaCreate(
            id_usuario=current_user.sub,
            id_empresa=id_empresa,
            acao="fornecedor:exclusao",
            descricao=f"Fornecedor {fornecedor.nome} (ID: {id_fornecedor}) removido"
        )
    )
    
    return resultado 