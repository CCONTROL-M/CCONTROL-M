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
from app.utils.error_responses import (
    resource_not_found, 
    validation_error, 
    resource_already_exists,
    insufficient_permissions,
    ErrorDetail
)

# Configuração de logger
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"],
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Erro de requisição inválida",
            "content": {
                "application/json": {
                    "example": {
                        "status_code": 400,
                        "message": "Requisição inválida",
                        "error_code": "VAL_INVALID_FORMAT",
                        "details": {
                            "fields": {
                                "cpf_cnpj": ["CPF/CNPJ com formato inválido"]
                            }
                        }
                    }
                }
            }
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Cliente não encontrado",
            "content": {
                "application/json": {
                    "example": {
                        "status_code": 404,
                        "message": "Cliente não encontrado com ID: 123e4567-e89b-12d3-a456-426614174000",
                        "error_code": "RES_NOT_FOUND",
                        "details": {
                            "resource_type": "cliente",
                            "resource_id": "123e4567-e89b-12d3-a456-426614174000"
                        }
                    }
                }
            }
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Permissão insuficiente",
            "content": {
                "application/json": {
                    "example": {
                        "status_code": 403,
                        "message": "Permissão insuficiente para editar em clientes",
                        "error_code": "AUTH_INSUFFICIENT_PERM",
                        "details": {
                            "required_permission": "editar",
                            "resource": "clientes"
                        }
                    }
                }
            }
        },
        status.HTTP_409_CONFLICT: {
            "description": "Cliente já existe",
            "content": {
                "application/json": {
                    "example": {
                        "status_code": 409,
                        "message": "Cliente já existe com os dados fornecidos",
                        "error_code": "RES_ALREADY_EXISTS",
                        "details": {
                            "conflict_fields": {
                                "cpf_cnpj": "12345678000190"
                            }
                        }
                    }
                }
            }
        }
    }
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
    
    # Se cliente não for encontrado, lançar exceção
    if not cliente:
        raise resource_not_found("cliente", id_cliente)
        
    return cliente


@router.post("", response_model=Cliente, status_code=status.HTTP_201_CREATED)
@require_permission("clientes", "criar")
async def criar_cliente(
    cliente: ClienteCreate,
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Cria um novo cliente no sistema.
    
    - **cliente**: Dados do cliente a ser criado
    
    Retorna o cliente criado com seu ID e metadados.
    """
    # Inicializar serviço
    cliente_service = ClienteService()
    log_service = LogSistemaService()
    
    # Verificar se já existe cliente com o mesmo CPF/CNPJ
    cliente_existente = await cliente_service.buscar_por_cpf_cnpj(
        cliente.cpf_cnpj, 
        cliente.id_empresa
    )
    
    if cliente_existente:
        raise resource_already_exists("cliente", {"cpf_cnpj": cliente.cpf_cnpj})
    
    # Criar cliente
    novo_cliente = await cliente_service.criar_cliente(cliente)
    
    # Registrar log de criação
    await log_service.registrar_log(
        LogSistemaCreate(
            id_usuario=current_user.sub,
            id_empresa=cliente.id_empresa,
            operacao="CREATE",
            entidade="Cliente",
            detalhes=f"Cliente {novo_cliente.nome} (ID: {novo_cliente.id_cliente}) criado com sucesso",
            dados=dict(novo_cliente)
        )
    )
    
    return novo_cliente


@router.put("/{id_cliente}", response_model=Cliente)
@require_permission("clientes", "editar")
async def atualizar_cliente(
    id_cliente: UUID = Path(..., description="ID do cliente a ser atualizado"),
    cliente: ClienteUpdate = None,
    id_empresa: UUID = Query(..., description="ID da empresa"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Atualiza um cliente existente.
    
    - **id_cliente**: ID do cliente a ser atualizado
    - **cliente**: Dados a serem atualizados
    - **id_empresa**: ID da empresa para validação
    
    Retorna o cliente atualizado.
    """
    # Inicializar serviço
    cliente_service = ClienteService()
    log_service = LogSistemaService()
    
    # Verificar se cliente existe
    cliente_existente = await cliente_service.get_cliente(id_cliente, id_empresa)
    if not cliente_existente:
        raise resource_not_found("cliente", id_cliente)
    
    # Se estiver alterando CPF/CNPJ, verificar duplicidade
    if cliente.cpf_cnpj and cliente.cpf_cnpj != cliente_existente.cpf_cnpj:
        duplicado = await cliente_service.buscar_por_cpf_cnpj(
            cliente.cpf_cnpj, 
            id_empresa
        )
        if duplicado and duplicado.id_cliente != id_cliente:
            raise resource_already_exists("cliente", {"cpf_cnpj": cliente.cpf_cnpj})
    
    # Atualizar cliente
    cliente_atualizado = await cliente_service.atualizar_cliente(id_cliente, cliente, id_empresa)
    
    # Registrar log de atualização
    await log_service.registrar_log(
        LogSistemaCreate(
            id_usuario=current_user.sub,
            id_empresa=id_empresa,
            operacao="UPDATE",
            entidade="Cliente",
            detalhes=f"Cliente {cliente_atualizado.nome} (ID: {id_cliente}) atualizado",
            dados=dict(cliente)
        )
    )
    
    return cliente_atualizado


@router.delete("/{id_cliente}", status_code=status.HTTP_200_OK)
@require_permission("clientes", "deletar")
async def remover_cliente(
    id_cliente: UUID = Path(..., description="ID do cliente a ser removido"),
    id_empresa: UUID = Query(..., description="ID da empresa"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Remove um cliente do sistema (inativação lógica).
    
    - **id_cliente**: ID do cliente a ser removido
    - **id_empresa**: ID da empresa para validação
    
    Retorna confirmação de remoção.
    """
    # Inicializar serviço
    cliente_service = ClienteService()
    log_service = LogSistemaService()
    
    # Verificar se cliente existe
    cliente_existente = await cliente_service.get_cliente(id_cliente, id_empresa)
    if not cliente_existente:
        raise resource_not_found("cliente", id_cliente)
    
    # Remover cliente (inativação lógica)
    await cliente_service.remover_cliente(id_cliente, id_empresa)
    
    # Registrar log de remoção
    await log_service.registrar_log(
        LogSistemaCreate(
            id_usuario=current_user.sub,
            id_empresa=id_empresa,
            operacao="DELETE",
            entidade="Cliente",
            detalhes=f"Cliente {cliente_existente.nome} (ID: {id_cliente}) removido do sistema",
            dados={"id_cliente": str(id_cliente)}
        )
    )
    
    return {
        "message": "Cliente removido com sucesso",
        "id": str(id_cliente)
    } 