'''
Router de Clientes para o sistema CCONTROL-M.
Implementa as operações CRUD protegidas por JWT, com filtros, paginação e uso de repositório.
'''

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from app.schemas.cliente import (
    Cliente, ClienteCreate, ClienteUpdate, ClienteList
)
from app.schemas.pagination import PaginatedResponse
from app.repositories.cliente_repository import ClienteRepository
from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.token import TokenPayload

# Configuração de logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.post("/", response_model=Cliente, status_code=status.HTTP_201_CREATED)
def criar_cliente(
    cliente_in: ClienteCreate,
    db: Session = Depends(get_db),
    token: TokenPayload = Depends(get_current_user),
):
    """
    Cria um novo cliente no sistema.
    
    - Requer autenticação JWT
    - O cliente é associado a uma empresa específica
    - Verifica duplicidade de CPF/CNPJ dentro da mesma empresa
    """
    logger.info(f"Criando novo cliente: {cliente_in.nome} para empresa {cliente_in.id_empresa}")
    try:
        repo = ClienteRepository()
        return repo.create(db, obj_in=cliente_in)
    except HTTPException as e:
        logger.error(f"Erro ao criar cliente: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Erro não esperado ao criar cliente: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro ao criar o cliente"
        )


@router.get("/", response_model=PaginatedResponse[ClienteList])
def listar_clientes(
    db: Session = Depends(get_db),
    token: TokenPayload = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    id_empresa: Optional[UUID] = Query(None, description="Filtrar por empresa"),
    nome: Optional[str] = Query(None, description="Busca por nome"),
    cpf_cnpj: Optional[str] = Query(None, description="Busca por CPF/CNPJ"),
):
    """
    Lista clientes com paginação e filtros opcionais.
    
    - Requer autenticação JWT
    - Suporta filtro por empresa específica
    - Suporta busca por nome ou CPF/CNPJ
    - Retorna resultados paginados
    """
    logger.info(f"Listando clientes: página {page}, tamanho {page_size}")
    
    try:
        repo = ClienteRepository()
        
        # Montar filtros
        filters = {}
        if nome:
            filters["nome"] = nome
        if cpf_cnpj:
            filters["cpf_cnpj"] = cpf_cnpj
            
        # Calcular offset para paginação
        skip = (page - 1) * page_size
        
        # Buscar dados
        clientes = repo.get_multi(
            db, 
            skip=skip, 
            limit=page_size, 
            id_empresa=id_empresa,
            filters=filters
        )
        total = repo.get_count(
            db, 
            id_empresa=id_empresa,
            filters=filters
        )
        
        return PaginatedResponse.create(
            items=clientes,
            total=total,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        logger.error(f"Erro ao listar clientes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro ao listar clientes"
        )


@router.get("/{id_cliente}", response_model=Cliente)
def obter_cliente(
    id_cliente: UUID,
    db: Session = Depends(get_db),
    token: TokenPayload = Depends(get_current_user),
):
    """
    Obtém um cliente pelo ID.
    
    - Requer autenticação JWT
    - Retorna 404 se o cliente não for encontrado
    """
    logger.info(f"Buscando cliente por ID: {id_cliente}")
    
    try:
        repo = ClienteRepository()
        cliente = repo.get(db, id=id_cliente)
        
        if not cliente:
            logger.warning(f"Cliente não encontrado: {id_cliente}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Cliente não encontrado"
            )
            
        return cliente
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar cliente: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro ao buscar o cliente"
        )


@router.put("/{id_cliente}", response_model=Cliente)
def atualizar_cliente(
    id_cliente: UUID,
    cliente_in: ClienteUpdate,
    db: Session = Depends(get_db),
    token: TokenPayload = Depends(get_current_user),
):
    """
    Atualiza um cliente existente.
    
    - Requer autenticação JWT
    - Verifica duplicidade de CPF/CNPJ
    - Retorna 404 se o cliente não for encontrado
    """
    logger.info(f"Atualizando cliente: {id_cliente}")
    
    try:
        repo = ClienteRepository()
        db_cliente = repo.get(db, id=id_cliente)
        
        if not db_cliente:
            logger.warning(f"Cliente não encontrado: {id_cliente}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Cliente não encontrado"
            )
            
        return repo.update(db, db_obj=db_cliente, obj_in=cliente_in)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar cliente: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro ao atualizar o cliente"
        )


@router.delete("/{id_cliente}", response_model=Cliente)
def deletar_cliente(
    id_cliente: UUID,
    db: Session = Depends(get_db),
    token: TokenPayload = Depends(get_current_user),
):
    """
    Remove um cliente do sistema.
    
    - Requer autenticação JWT
    - Retorna 404 se o cliente não for encontrado
    """
    logger.info(f"Removendo cliente: {id_cliente}")
    
    try:
        repo = ClienteRepository()
        cliente = repo.delete(db, id=id_cliente)
        
        if not cliente:
            logger.warning(f"Cliente não encontrado para remoção: {id_cliente}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Cliente não encontrado"
            )
            
        return cliente
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao remover cliente: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro ao remover o cliente"
        ) 