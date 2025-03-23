"""Rotas para gerenciamento de contas a pagar."""
from uuid import UUID
from typing import Optional
from datetime import date

from fastapi import APIRouter, Depends, Query
from fastapi.security import OAuth2PasswordBearer

from app.core.auth import get_current_user
from app.schemas.usuario import Usuario
from app.schemas.conta_pagar import (
    ContaPagarCreate,
    ContaPagarUpdate,
    ContaPagar,
    StatusContaPagar
)
from app.schemas.pagination import PaginatedResponse
from app.services.conta_pagar_service import ContaPagarService


router = APIRouter(prefix="/contas-pagar", tags=["Contas a Pagar"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("", response_model=ContaPagar)
async def criar_conta_pagar(
    conta: ContaPagarCreate,
    current_user: Usuario = Depends(get_current_user),
    service: ContaPagarService = Depends()
) -> ContaPagar:
    """
    Criar uma nova conta a pagar.
    
    Args:
        conta: Dados da conta a pagar
        current_user: Usuário autenticado
        service: Serviço de contas a pagar
        
    Returns:
        Conta a pagar criada
    """
    return await service.create(conta, current_user.id_usuario, current_user.empresa_id)


@router.put("/{id_conta}", response_model=ContaPagar)
async def atualizar_conta_pagar(
    id_conta: UUID,
    conta: ContaPagarUpdate,
    current_user: Usuario = Depends(get_current_user),
    service: ContaPagarService = Depends()
) -> ContaPagar:
    """
    Atualizar uma conta a pagar existente.
    
    Args:
        id_conta: ID da conta a pagar
        conta: Dados para atualização
        current_user: Usuário autenticado
        service: Serviço de contas a pagar
        
    Returns:
        Conta a pagar atualizada
    """
    return await service.update(id_conta, conta, current_user.id_usuario, current_user.empresa_id)


@router.delete("/{id_conta}")
async def remover_conta_pagar(
    id_conta: UUID,
    current_user: Usuario = Depends(get_current_user),
    service: ContaPagarService = Depends()
) -> dict:
    """
    Remover uma conta a pagar.
    
    Args:
        id_conta: ID da conta a pagar
        current_user: Usuário autenticado
        service: Serviço de contas a pagar
        
    Returns:
        Mensagem de confirmação
    """
    return await service.delete(id_conta, current_user.id_usuario, current_user.empresa_id)


@router.get("/{id_conta}", response_model=ContaPagar)
async def buscar_conta_pagar(
    id_conta: UUID,
    current_user: Usuario = Depends(get_current_user),
    service: ContaPagarService = Depends()
) -> ContaPagar:
    """
    Buscar uma conta a pagar pelo ID.
    
    Args:
        id_conta: ID da conta a pagar
        current_user: Usuário autenticado
        service: Serviço de contas a pagar
        
    Returns:
        Conta a pagar encontrada
    """
    return await service.get_by_id(id_conta, current_user.empresa_id)


@router.get("", response_model=PaginatedResponse[ContaPagar])
async def listar_contas_pagar(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[StatusContaPagar] = None,
    data_inicial: Optional[date] = None,
    data_final: Optional[date] = None,
    fornecedor_id: Optional[UUID] = None,
    categoria_id: Optional[UUID] = None,
    busca: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    service: ContaPagarService = Depends()
) -> PaginatedResponse[ContaPagar]:
    """
    Listar contas a pagar com filtros.
    
    Args:
        skip: Número de registros para pular
        limit: Número máximo de registros
        status: Filtrar por status
        data_inicial: Data inicial para filtro
        data_final: Data final para filtro
        fornecedor_id: Filtrar por fornecedor
        categoria_id: Filtrar por categoria
        busca: Termo para busca
        current_user: Usuário autenticado
        service: Serviço de contas a pagar
        
    Returns:
        Lista paginada de contas a pagar
    """
    return await service.get_multi(
        empresa_id=current_user.empresa_id,
        skip=skip,
        limit=limit,
        status=status,
        data_inicial=data_inicial,
        data_final=data_final,
        fornecedor_id=fornecedor_id,
        categoria_id=categoria_id,
        busca=busca
    ) 