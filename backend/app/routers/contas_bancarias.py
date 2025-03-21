"""Router para operações com contas bancárias."""
from typing import List, Dict, Any, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_usuario
from app.models.usuario import Usuario
from app.schemas.conta_bancaria import (
    ContaBancaria, 
    ContaBancariaCreate, 
    ContaBancariaUpdate, 
    ContaBancariaList,
    AtualizacaoSaldo
)
from app.repositories.conta_bancaria_repository import ContaBancariaRepository


router = APIRouter(
    prefix="/contas-bancarias",
    tags=["Contas Bancárias"],
    dependencies=[Depends(get_current_usuario)]
)

conta_bancaria_repository = ContaBancariaRepository()


@router.post("/", response_model=ContaBancaria, status_code=status.HTTP_201_CREATED)
def criar_conta_bancaria(
    *,
    db: Session = Depends(get_db),
    conta_in: ContaBancariaCreate,
    usuario_atual: Usuario = Depends(get_current_usuario)
):
    """
    Cria uma nova conta bancária.
    
    - **nome**: Nome da conta bancária
    - **banco**: Nome do banco (opcional)
    - **agencia**: Número da agência (opcional)
    - **numero**: Número da conta (opcional)
    - **tipo**: Tipo da conta (corrente, poupança, carteira, investimento, outro)
    - **saldo_inicial**: Saldo inicial da conta
    - **ativa**: Se a conta está ativa (padrão: True)
    - **mostrar_dashboard**: Se a conta deve ser exibida no dashboard (padrão: True)
    """
    return conta_bancaria_repository.create(db=db, obj_in=conta_in)


@router.get("/", response_model=Dict[str, Any])
def listar_contas_bancarias(
    *,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_usuario),
    id_empresa: UUID,
    skip: int = 0,
    limit: int = 100,
    ativa: Optional[bool] = None,
    mostrar_dashboard: Optional[bool] = None,
    tipo: Optional[str] = None,
    nome: Optional[str] = None,
    banco: Optional[str] = None
):
    """
    Lista contas bancárias com filtros opcionais.
    
    - **id_empresa**: ID da empresa (obrigatório)
    - **skip**: Registros para pular (paginação)
    - **limit**: Limite de registros (paginação)
    - **ativa**: Filtrar por status (ativa/inativa)
    - **mostrar_dashboard**: Filtrar por exibição no dashboard
    - **tipo**: Filtrar por tipo de conta
    - **nome**: Filtrar por nome
    - **banco**: Filtrar por banco
    """
    # Construir filtros
    filters = {}
    if nome:
        filters["nome"] = nome
    if banco:
        filters["banco"] = banco
    
    # Buscar registros
    contas = conta_bancaria_repository.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        id_empresa=id_empresa,
        ativa=ativa,
        mostrar_dashboard=mostrar_dashboard,
        tipo=tipo,
        filters=filters
    )
    
    # Obter contagem total para paginação
    total = conta_bancaria_repository.get_count(
        db=db,
        id_empresa=id_empresa,
        ativa=ativa,
        mostrar_dashboard=mostrar_dashboard,
        tipo=tipo,
        filters=filters
    )
    
    return {
        "data": contas,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/todas", response_model=List[ContaBancariaList])
def listar_todas_contas_bancarias(
    *,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_usuario),
    id_empresa: UUID,
    ativa: Optional[bool] = True
):
    """
    Lista todas as contas bancárias de uma empresa sem paginação.
    
    - **id_empresa**: ID da empresa (obrigatório)
    - **ativa**: Filtrar por status (ativa/inativa, padrão: True)
    """
    return conta_bancaria_repository.get_by_empresa(db=db, id_empresa=id_empresa, ativa=ativa)


@router.get("/dashboard", response_model=Dict[str, Any])
def obter_dashboard_contas(
    *,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_current_usuario),
    id_empresa: UUID
):
    """
    Obtém dados do dashboard de contas bancárias.
    
    - **id_empresa**: ID da empresa (obrigatório)
    """
    return conta_bancaria_repository.get_dashboard_contas(db=db, id_empresa=id_empresa)


@router.get("/{id_conta}", response_model=ContaBancaria)
def obter_conta_bancaria(
    *,
    db: Session = Depends(get_db),
    id_conta: UUID,
    usuario_atual: Usuario = Depends(get_current_usuario)
):
    """
    Obtém uma conta bancária pelo ID.
    
    - **id_conta**: ID da conta bancária
    """
    conta = conta_bancaria_repository.get(db=db, id=id_conta)
    if not conta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta bancária não encontrada"
        )
    return conta


@router.put("/{id_conta}", response_model=ContaBancaria)
def atualizar_conta_bancaria(
    *,
    db: Session = Depends(get_db),
    id_conta: UUID,
    conta_in: ContaBancariaUpdate,
    usuario_atual: Usuario = Depends(get_current_usuario)
):
    """
    Atualiza uma conta bancária existente.
    
    - **id_conta**: ID da conta bancária
    - **nome**: Nome da conta bancária
    - **banco**: Nome do banco
    - **agencia**: Número da agência
    - **numero**: Número da conta
    - **tipo**: Tipo da conta (corrente, poupança, carteira, investimento, outro)
    - **saldo_inicial**: Saldo inicial da conta
    - **ativa**: Se a conta está ativa
    - **mostrar_dashboard**: Se a conta deve ser exibida no dashboard
    """
    conta = conta_bancaria_repository.get(db=db, id=id_conta)
    if not conta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta bancária não encontrada"
        )
    return conta_bancaria_repository.update(db=db, db_obj=conta, obj_in=conta_in)


@router.delete("/{id_conta}", response_model=ContaBancaria)
def excluir_conta_bancaria(
    *,
    db: Session = Depends(get_db),
    id_conta: UUID,
    usuario_atual: Usuario = Depends(get_current_usuario)
):
    """
    Exclui uma conta bancária.
    
    - **id_conta**: ID da conta bancária
    """
    return conta_bancaria_repository.remove(db=db, id=id_conta)


@router.post("/{id_conta}/toggle-ativa", response_model=ContaBancaria)
def alternar_status_conta_bancaria(
    *,
    db: Session = Depends(get_db),
    id_conta: UUID,
    usuario_atual: Usuario = Depends(get_current_usuario)
):
    """
    Alterna o status de ativação da conta bancária.
    
    - **id_conta**: ID da conta bancária
    """
    return conta_bancaria_repository.toggle_ativa(db=db, id=id_conta)


@router.post("/{id_conta}/toggle-dashboard", response_model=ContaBancaria)
def alternar_exibicao_dashboard(
    *,
    db: Session = Depends(get_db),
    id_conta: UUID,
    usuario_atual: Usuario = Depends(get_current_usuario)
):
    """
    Alterna a exibição da conta no dashboard.
    
    - **id_conta**: ID da conta bancária
    """
    return conta_bancaria_repository.toggle_dashboard(db=db, id=id_conta)


@router.post("/{id_conta}/atualizar-saldo", response_model=ContaBancaria)
def atualizar_saldo_conta(
    *,
    db: Session = Depends(get_db),
    id_conta: UUID,
    operacao: AtualizacaoSaldo,
    usuario_atual: Usuario = Depends(get_current_usuario)
):
    """
    Atualiza o saldo de uma conta bancária.
    
    - **id_conta**: ID da conta bancária
    - **tipo_operacao**: Tipo de operação (credito, debito, ajuste)
    - **valor**: Valor da operação
    """
    return conta_bancaria_repository.atualizar_saldo(db=db, id=id_conta, operacao=operacao) 