'''
Router de Empresas para o sistema CCONTROL-M.
Implementa as operações CRUD protegidas por JWT, com filtros, paginação e uso de repositório.
'''

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from app.schemas.empresa import (
    Empresa, EmpresaCreate, EmpresaUpdate, EmpresaList
)
from app.schemas.pagination import PaginatedResponse
from app.repositories.empresa_repository import EmpresaRepository
from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.token import TokenPayload

# Configuração de logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/empresas", tags=["Empresas"])


@router.post("/", response_model=Empresa, status_code=status.HTTP_201_CREATED)
def criar_empresa(
    empresa_in: EmpresaCreate,
    db: Session = Depends(get_db),
    _: TokenPayload = Depends(get_current_user),
):
    """
    Cria uma nova empresa no sistema.
    
    - Requer autenticação JWT
    - Valida e formata o CNPJ automaticamente
    - Verifica se o CNPJ já existe no sistema
    """
    logger.info(f"Criando nova empresa: {empresa_in.razao_social}")
    try:
        repo = EmpresaRepository()
        return repo.create(db, obj_in=empresa_in)
    except HTTPException as e:
        logger.error(f"Erro ao criar empresa: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Erro não esperado ao criar empresa: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro ao criar a empresa"
        )


@router.get("/", response_model=PaginatedResponse[EmpresaList])
def listar_empresas(
    db: Session = Depends(get_db),
    _: TokenPayload = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    nome: Optional[str] = Query(None, description="Busca por razão social ou nome fantasia"),
    cidade: Optional[str] = Query(None, description="Filtrar por cidade"),
    estado: Optional[str] = Query(None, description="Filtrar por estado (sigla)"),
):
    """
    Lista empresas com paginação e filtros opcionais.
    
    - Requer autenticação JWT
    - Suporta filtro por nome (razão social ou fantasia)
    - Suporta filtro por cidade e estado
    - Retorna resultados paginados
    """
    logger.info(f"Listando empresas: página {page}, tamanho {page_size}")
    
    try:
        repo = EmpresaRepository()
        
        # Montar filtros
        filters = {}
        if nome:
            filters["nome"] = nome
        if cidade:
            filters["cidade"] = cidade
        if estado:
            filters["estado"] = estado
            
        # Calcular offset para paginação
        skip = (page - 1) * page_size
        
        # Buscar dados
        empresas = repo.get_multi(db, skip=skip, limit=page_size, filters=filters)
        total = repo.get_count(db, filters=filters)
        
        return PaginatedResponse.create(
            items=empresas,
            total=total,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        logger.error(f"Erro ao listar empresas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro ao listar empresas"
        )


@router.get("/{id_empresa}", response_model=Empresa)
def obter_empresa(
    id_empresa: UUID,
    db: Session = Depends(get_db),
    _: TokenPayload = Depends(get_current_user),
):
    """
    Obtém uma empresa pelo ID.
    
    - Requer autenticação JWT
    - Retorna 404 se a empresa não for encontrada
    """
    logger.info(f"Buscando empresa por ID: {id_empresa}")
    
    try:
        repo = EmpresaRepository()
        empresa = repo.get(db, id=id_empresa)
        
        if not empresa:
            logger.warning(f"Empresa não encontrada: {id_empresa}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Empresa não encontrada"
            )
            
        return empresa
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar empresa: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro ao buscar a empresa"
        )


@router.put("/{id_empresa}", response_model=Empresa)
def atualizar_empresa(
    id_empresa: UUID,
    empresa_in: EmpresaUpdate,
    db: Session = Depends(get_db),
    _: TokenPayload = Depends(get_current_user),
):
    """
    Atualiza uma empresa existente.
    
    - Requer autenticação JWT
    - Valida e formata o CNPJ automaticamente, se fornecido
    - Verifica duplicidade de CNPJ
    - Retorna 404 se a empresa não for encontrada
    """
    logger.info(f"Atualizando empresa: {id_empresa}")
    
    try:
        repo = EmpresaRepository()
        db_empresa = repo.get(db, id=id_empresa)
        
        if not db_empresa:
            logger.warning(f"Empresa não encontrada: {id_empresa}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Empresa não encontrada"
            )
            
        return repo.update(db, db_obj=db_empresa, obj_in=empresa_in)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar empresa: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro ao atualizar a empresa"
        )


@router.delete("/{id_empresa}", response_model=Empresa)
def deletar_empresa(
    id_empresa: UUID,
    db: Session = Depends(get_db),
    _: TokenPayload = Depends(get_current_user),
):
    """
    Remove uma empresa do sistema.
    
    - Requer autenticação JWT
    - Retorna 404 se a empresa não for encontrada
    """
    logger.info(f"Removendo empresa: {id_empresa}")
    
    try:
        repo = EmpresaRepository()
        empresa = repo.delete(db, id=id_empresa)
        
        if not empresa:
            logger.warning(f"Empresa não encontrada para remoção: {id_empresa}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Empresa não encontrada"
            )
            
        return empresa
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao remover empresa: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro ao remover a empresa"
        ) 