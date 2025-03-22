"""
Router para gerenciamento de categorias no sistema CCONTROL-M.

Este módulo implementa os endpoints para criar, listar, atualizar, remover e 
gerenciar categorias, com suporte a multi-tenancy e controle de permissões.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from uuid import UUID
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.categoria import (
    Categoria, CategoriaCreate, CategoriaUpdate, CategoriaList
)
from app.services.categoria_service import CategoriaService
from app.services.log_sistema_service import LogSistemaService
from app.schemas.token import TokenPayload
from app.dependencies import get_current_user
from app.database import get_async_session
from app.utils.permissions import require_permission
from app.schemas.log_sistema import LogSistemaCreate

# Configuração de logger
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/categorias",
    tags=["Categorias"],
    responses={404: {"description": "Categoria não encontrada"}},
)


@router.get("", response_model=CategoriaList)
@require_permission("categorias", "listar")
async def listar_categorias(
    id_empresa: UUID,
    skip: int = Query(0, ge=0, description="Registros para pular (paginação)"),
    limit: int = Query(100, ge=1, le=100, description="Limite de registros por página"),
    nome: Optional[str] = Query(None, description="Filtrar por nome da categoria"),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo da categoria"),
    ativo: Optional[bool] = Query(None, description="Filtrar por status (ativo/inativo)"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Lista categorias com paginação e filtros opcionais.
    
    - **id_empresa**: ID da empresa (obrigatório)
    - **skip**: Quantos registros pular (para paginação)
    - **limit**: Limite de registros por página
    - **nome**: Filtro opcional por nome da categoria
    - **tipo**: Filtro opcional por tipo da categoria
    - **ativo**: Filtro opcional por status (ativo/inativo)
    
    Retorna lista paginada de categorias que correspondem aos filtros aplicados.
    """
    # Inicializar serviço
    categoria_service = CategoriaService(session)
    
    # Listar categorias com filtros
    categorias, total = await categoria_service.listar_categorias(
        id_empresa=id_empresa,
        skip=skip,
        limit=limit,
        nome=nome,
        tipo=tipo,
        ativo=ativo
    )
    
    # Calcular página atual
    page = (skip // limit) + 1 if limit > 0 else 1
    
    # Retornar resposta paginada
    return CategoriaList(
        items=categorias,
        total=total,
        page=page,
        size=limit
    )


@router.get("/{id_categoria}", response_model=Categoria)
@require_permission("categorias", "visualizar")
async def obter_categoria(
    id_categoria: UUID = Path(..., description="ID da categoria"),
    id_empresa: UUID = Query(..., description="ID da empresa"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Busca uma categoria específica pelo ID.
    
    - **id_categoria**: ID da categoria
    - **id_empresa**: ID da empresa para validação
    
    Retorna os dados detalhados da categoria.
    """
    # Inicializar serviço e buscar categoria
    categoria_service = CategoriaService(session)
    categoria = await categoria_service.get_categoria(id_categoria, id_empresa)
    
    return categoria


@router.post("", response_model=Categoria, status_code=status.HTTP_201_CREATED)
@require_permission("categorias", "criar")
async def criar_categoria(
    categoria: CategoriaCreate,
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Cria uma nova categoria.
    
    - **categoria**: Dados da categoria a ser criada
    
    Retorna os dados da categoria criada.
    """
    # Inicializar serviço
    categoria_service = CategoriaService(session)
    log_service = LogSistemaService(session)
    
    # Criar categoria
    nova_categoria = await categoria_service.criar_categoria(categoria, current_user.sub)
    
    # Registrar log
    await log_service.registrar_log(
        LogSistemaCreate(
            id_usuario=current_user.sub,
            id_empresa=categoria.id_empresa,
            acao="categorias:criacao",
            descricao=f"Categoria {nova_categoria.nome} (ID: {nova_categoria.id_categoria}) criada"
        )
    )
    
    return nova_categoria


@router.put("/{id_categoria}", response_model=Categoria)
@require_permission("categorias", "editar")
async def atualizar_categoria(
    id_categoria: UUID,
    categoria: CategoriaUpdate,
    id_empresa: UUID = Query(..., description="ID da empresa"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Atualiza dados de uma categoria existente.
    
    - **id_categoria**: ID da categoria
    - **categoria**: Dados para atualização
    - **id_empresa**: ID da empresa para validação
    
    Retorna os dados atualizados da categoria.
    """
    # Inicializar serviços
    categoria_service = CategoriaService(session)
    log_service = LogSistemaService(session)
    
    # Buscar categoria atual para o log
    categoria_atual = await categoria_service.get_categoria(id_categoria, id_empresa)
    
    # Atualizar categoria
    categoria_atualizada = await categoria_service.atualizar_categoria(
        id_categoria, 
        categoria, 
        id_empresa,
        current_user.sub
    )
    
    # Registrar log
    await log_service.registrar_log(
        LogSistemaCreate(
            id_usuario=current_user.sub,
            id_empresa=id_empresa,
            acao="categorias:atualizacao",
            descricao=f"Categoria {categoria_atual.nome} (ID: {id_categoria}) atualizada"
        )
    )
    
    return categoria_atualizada


@router.delete("/{id_categoria}", status_code=status.HTTP_200_OK)
@require_permission("categorias", "deletar")
async def remover_categoria(
    id_categoria: UUID,
    id_empresa: UUID = Query(..., description="ID da empresa"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Remove uma categoria.
    
    - **id_categoria**: ID da categoria
    - **id_empresa**: ID da empresa para validação
    
    Retorna mensagem de confirmação.
    """
    # Inicializar serviços
    categoria_service = CategoriaService(session)
    log_service = LogSistemaService(session)
    
    # Buscar categoria para o log antes de remover
    categoria = await categoria_service.get_categoria(id_categoria, id_empresa)
    
    # Remover categoria
    resultado = await categoria_service.remover_categoria(id_categoria, id_empresa)
    
    # Registrar log
    await log_service.registrar_log(
        LogSistemaCreate(
            id_usuario=current_user.sub,
            id_empresa=id_empresa,
            acao="categorias:exclusao",
            descricao=f"Categoria {categoria.nome} (ID: {id_categoria}) removida"
        )
    )
    
    return {"message": "Categoria removida com sucesso"}


@router.patch("/{id_categoria}/toggle", response_model=Categoria)
@require_permission("categorias", "editar")
async def alternar_status_categoria(
    id_categoria: UUID,
    id_empresa: UUID = Query(..., description="ID da empresa"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Alterna o status ativo/inativo de uma categoria.
    
    - **id_categoria**: ID da categoria
    - **id_empresa**: ID da empresa para validação
    
    Retorna os dados atualizados da categoria.
    """
    # Inicializar serviços
    categoria_service = CategoriaService(session)
    log_service = LogSistemaService(session)
    
    # Alternar status da categoria
    categoria_atualizada = await categoria_service.ativar_categoria(
        id_categoria, 
        id_empresa,
        current_user.sub
    )
    
    # Definir status para o log
    status_descricao = "ativada" if categoria_atualizada.ativo else "desativada"
    
    # Registrar log
    await log_service.registrar_log(
        LogSistemaCreate(
            id_usuario=current_user.sub,
            id_empresa=id_empresa,
            acao="categorias:alternar_status",
            descricao=f"Categoria {categoria_atualizada.nome} (ID: {id_categoria}) {status_descricao}"
        )
    )
    
    return categoria_atualizada 