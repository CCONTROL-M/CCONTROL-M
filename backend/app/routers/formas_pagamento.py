"""Router para operações com formas de pagamento."""
from typing import List, Dict, Any, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_usuario
from app.models.usuario import Usuario
from app.schemas.forma_pagamento import (
    FormaPagamento, 
    FormaPagamentoCreate, 
    FormaPagamentoUpdate, 
    FormaPagamentoList
)
from app.repositories.forma_pagamento_repository import FormaPagamentoRepository


router = APIRouter(
    prefix="/formas-pagamento",
    tags=["Formas de Pagamento"],
    dependencies=[Depends(get_current_usuario)]
)

forma_pagamento_repository = FormaPagamentoRepository()


@router.post("/", response_model=FormaPagamento, status_code=status.HTTP_201_CREATED)
def criar_forma_pagamento(
    *,
    db: Session = Depends(get_db),
    forma_in: FormaPagamentoCreate,
    usuario_atual: Usuario = Depends(get_current_usuario)
):
    """
    Cria uma nova forma de pagamento.
    
    - **nome**: Nome da forma de pagamento
    - **descricao**: Descrição opcional
    - **icone**: URL ou identificador do ícone
    - **dias_compensacao**: Dias para compensação
    - **taxa_percentual**: Taxa percentual (opcional)
    - **taxa_fixa**: Taxa fixa (opcional)
    - **ativa**: Se a forma está ativa (padrão: True)
    """
    return forma_pagamento_repository.create(db=db, obj_in=forma_in)


@router.get("/", response_model=Dict[str, Any])
def listar_formas_pagamento(
    *,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_usuario),
    id_empresa: UUID,
    skip: int = 0,
    limit: int = 100,
    ativa: Optional[bool] = None,
    nome: Optional[str] = None
):
    """
    Lista formas de pagamento com filtros opcionais.
    
    - **id_empresa**: ID da empresa (obrigatório)
    - **skip**: Registros para pular (paginação)
    - **limit**: Limite de registros (paginação)
    - **ativa**: Filtrar por status (ativa/inativa)
    - **nome**: Filtrar por nome
    """
    # Construir filtros
    filters = {}
    if nome:
        filters["nome"] = nome
    
    # Buscar registros
    formas = forma_pagamento_repository.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        id_empresa=id_empresa,
        ativa=ativa,
        filters=filters
    )
    
    # Obter contagem total para paginação
    total = forma_pagamento_repository.get_count(
        db=db,
        id_empresa=id_empresa,
        ativa=ativa,
        filters=filters
    )
    
    return {
        "data": formas,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/todas", response_model=List[FormaPagamentoList])
def listar_todas_formas_pagamento(
    *,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_usuario),
    id_empresa: UUID,
    ativa: Optional[bool] = None
):
    """
    Lista todas as formas de pagamento de uma empresa sem paginação.
    
    - **id_empresa**: ID da empresa (obrigatório)
    - **ativa**: Filtrar por status (ativa/inativa)
    """
    return forma_pagamento_repository.get_by_empresa(db=db, id_empresa=id_empresa, ativa=ativa)


@router.get("/{id_forma}", response_model=FormaPagamento)
def obter_forma_pagamento(
    *,
    db: Session = Depends(get_db),
    id_forma: UUID,
    usuario_atual: Usuario = Depends(get_current_usuario)
):
    """
    Obtém uma forma de pagamento pelo ID.
    
    - **id_forma**: ID da forma de pagamento
    """
    forma = forma_pagamento_repository.get(db=db, id=id_forma)
    if not forma:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forma de pagamento não encontrada"
        )
    return forma


@router.put("/{id_forma}", response_model=FormaPagamento)
def atualizar_forma_pagamento(
    *,
    db: Session = Depends(get_db),
    id_forma: UUID,
    forma_in: FormaPagamentoUpdate,
    usuario_atual: Usuario = Depends(get_current_usuario)
):
    """
    Atualiza uma forma de pagamento existente.
    
    - **id_forma**: ID da forma de pagamento
    - **nome**: Nome da forma de pagamento
    - **descricao**: Descrição opcional
    - **icone**: URL ou identificador do ícone
    - **dias_compensacao**: Dias para compensação
    - **taxa_percentual**: Taxa percentual
    - **taxa_fixa**: Taxa fixa
    - **ativa**: Se a forma está ativa
    """
    forma = forma_pagamento_repository.get(db=db, id=id_forma)
    if not forma:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forma de pagamento não encontrada"
        )
    return forma_pagamento_repository.update(db=db, db_obj=forma, obj_in=forma_in)


@router.delete("/{id_forma}", response_model=FormaPagamento)
def excluir_forma_pagamento(
    *,
    db: Session = Depends(get_db),
    id_forma: UUID,
    usuario_atual: Usuario = Depends(get_current_usuario)
):
    """
    Exclui uma forma de pagamento.
    
    - **id_forma**: ID da forma de pagamento
    """
    return forma_pagamento_repository.remove(db=db, id=id_forma)


@router.post("/{id_forma}/toggle-ativa", response_model=FormaPagamento)
def alternar_status_forma_pagamento(
    *,
    db: Session = Depends(get_db),
    id_forma: UUID,
    usuario_atual: Usuario = Depends(get_current_usuario)
):
    """
    Alterna o status de ativação da forma de pagamento.
    
    - **id_forma**: ID da forma de pagamento
    """
    return forma_pagamento_repository.toggle_ativa(db=db, id=id_forma) 