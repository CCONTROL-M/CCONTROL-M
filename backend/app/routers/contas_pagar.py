"""Router para Contas a Pagar."""
import logging
from uuid import UUID
from typing import Optional, List, Dict, Any, Tuple
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.conta_pagar import (
    ContaPagar, ContaPagarCreate, ContaPagarUpdate, 
    ContaPagarList, StatusContaPagar, ContaPagarPagamento
)
from app.services.conta_pagar_service import ContaPagarService
from app.services.log_sistema_service import LogSistemaService
from app.schemas.token import TokenPayload
from app.dependencies import get_current_user
from app.database import get_async_session
from app.utils.permissions import require_permission
from app.schemas.log_sistema import LogSistemaCreate

# Configuração de logger
logger = logging.getLogger(__name__)

# Router
router = APIRouter(
    prefix="/contas-pagar",
    tags=["Contas a Pagar"],
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Parâmetros inválidos"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Não autenticado"},
        status.HTTP_403_FORBIDDEN: {"description": "Sem permissão para o recurso"},
        status.HTTP_404_NOT_FOUND: {"description": "Conta a pagar não encontrada"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Erro interno do servidor"}
    }
)

# Funções de controle (anteriormente em contas_pagar_controllers.py)
async def listar_contas_controlador(
    id_empresa: UUID,
    skip: int = 0,
    limit: int = 100,
    status: Optional[StatusContaPagar] = None,
    fornecedor_id: Optional[UUID] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    search: Optional[str] = None,
    current_user: TokenPayload = None,
    session: AsyncSession = None
) -> ContaPagarList:
    """
    Lista contas a pagar com filtros e paginação.
    
    Args:
        id_empresa: ID da empresa
        skip: Número de registros para pular (paginação)
        limit: Limite de registros por página
        status: Filtrar por status (PENDENTE, PAGO, VENCIDO, CANCELADO)
        fornecedor_id: Filtrar por fornecedor específico
        data_inicio: Filtrar contas a partir desta data de vencimento
        data_fim: Filtrar contas até esta data de vencimento
        search: Buscar por termo na descrição da conta
        current_user: Dados do usuário atual
        session: Sessão do banco de dados
        
    Returns:
        ContaPagarList: Lista paginada de contas a pagar
        
    Raises:
        HTTPException: Se ocorrer algum erro durante a operação
    """
    try:
        service = ContaPagarService(session)
        
        # Listar contas com filtros
        contas, total = await service.list(
            id_empresa=id_empresa,
            status=status,
            fornecedor_id=fornecedor_id,
            data_inicio=data_inicio,
            data_fim=data_fim,
            search=search,
            skip=skip,
            limit=limit
        )
        
        # Montar resposta paginada
        return {
            "items": contas,
            "total": total,
            "page": skip // limit + 1 if limit > 0 else 1,
            "size": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 1
        }
    except Exception as e:
        logger.error(f"Erro ao listar contas a pagar: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


async def buscar_conta_controlador(
    id_conta: UUID,
    id_empresa: UUID,
    current_user: TokenPayload = None,
    session: AsyncSession = None
) -> ContaPagar:
    """
    Busca detalhes de uma conta a pagar específica pelo ID.
    
    Args:
        id_conta: ID da conta a pagar
        id_empresa: ID da empresa
        current_user: Dados do usuário atual
        session: Sessão do banco de dados
        
    Returns:
        ContaPagar: Objeto da conta a pagar
        
    Raises:
        HTTPException: Se a conta não for encontrada ou o usuário não tiver permissão
    """
    try:
        service = ContaPagarService(session)
        
        # Buscar conta pelo ID
        conta = await service.get_by_id(id_conta)
        if not conta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conta a pagar não encontrada"
            )
            
        # Verificar permissão para a empresa
        if conta.id_empresa != id_empresa:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão negada para esta conta"
            )
            
        return conta
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar conta a pagar: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Criar nova conta a pagar
@router.post("", response_model=ContaPagar, status_code=status.HTTP_201_CREATED, 
            summary="Criar nova conta a pagar",
            response_description="Conta a pagar criada com sucesso")
@require_permission("contas", "criar")
async def criar_conta_pagar(
    conta: ContaPagarCreate = Body(..., 
                                   example={
                                       "descricao": "Pagamento fornecedor ABC",
                                       "valor": 1250.75,
                                       "data_vencimento": "2023-12-30",
                                       "data_pagamento": None,
                                       "status": "PENDENTE",
                                       "observacao": "Referente a compra #123",
                                       "fornecedor_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                       "categoria_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                       "id_empresa": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
                                   }),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Cria uma nova conta a pagar no sistema.
    
    ## Parâmetros:
    - **descricao**: Descrição da conta (obrigatório, 3-100 caracteres)
    - **valor**: Valor da conta em decimal (obrigatório, maior que zero)
    - **data_vencimento**: Data de vencimento no formato YYYY-MM-DD (obrigatório)
    - **id_empresa**: ID da empresa (obrigatório, UUID)
    - **fornecedor_id**: ID do fornecedor associado (opcional, UUID)
    - **categoria_id**: ID da categoria para classificação (opcional, UUID)
    - **observacao**: Observações adicionais (opcional, máx 500 caracteres)
    
    ## Retorno:
    - Objeto completo da conta a pagar criada, incluindo ID gerado
    
    ## Possíveis erros:
    - **400**: Dados inválidos (ex: valor negativo, descrição muito curta)
    - **403**: Usuário sem permissão para criar contas a pagar
    - **422**: Erro de validação nos dados enviados
    """
    try:
        service = ContaPagarService(session)
        log_service = LogSistemaService(session)
        
        # Criar conta a pagar
        nova_conta = await service.create(
            conta,
            usuario_id=current_user.id,
            empresa_id=conta.id_empresa
        )
        
        # Registrar log
        await log_service.registrar_atividade(
            id_usuario=current_user.id,
            id_empresa=conta.id_empresa,
            acao="CRIAR_CONTA_PAGAR",
            descricao=f"Conta a pagar criada: {nova_conta.descricao}"
        )
        
        return nova_conta
    except Exception as e:
        logger.error(f"Erro ao criar conta a pagar: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Listar contas a pagar
@router.get("", response_model=ContaPagarList,
           summary="Listar contas a pagar",
           response_description="Lista paginada de contas a pagar")
@require_permission("contas", "listar")
async def listar_contas_pagar(
    id_empresa: UUID = Query(..., description="ID da empresa", example="3fa85f64-5717-4562-b3fc-2c963f66afa6"),
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=100, description="Limite de registros por página"),
    status: Optional[StatusContaPagar] = Query(None, description="Filtrar por status"),
    fornecedor_id: Optional[UUID] = Query(None, description="Filtrar por fornecedor"),
    data_inicio: Optional[date] = Query(None, description="Filtrar por data de vencimento inicial"),
    data_fim: Optional[date] = Query(None, description="Filtrar por data de vencimento final"),
    search: Optional[str] = Query(None, description="Buscar por descrição"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    return await listar_contas_controlador(
        id_empresa=id_empresa,
        skip=skip,
        limit=limit,
        status=status,
        fornecedor_id=fornecedor_id,
        data_inicio=data_inicio,
        data_fim=data_fim,
        search=search,
        current_user=current_user,
        session=session
    )


# Buscar conta por ID
@router.get("/{id_conta}", response_model=ContaPagar,
           summary="Buscar conta a pagar por ID",
           response_description="Detalhes da conta a pagar")
@require_permission("contas", "visualizar")
async def buscar_conta_pagar(
    id_conta: UUID = Path(..., description="ID da conta a pagar", example="3fa85f64-5717-4562-b3fc-2c963f66afa6"),
    id_empresa: UUID = Query(..., description="ID da empresa", example="3fa85f64-5717-4562-b3fc-2c963f66afa6"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    return await buscar_conta_controlador(
        id_conta=id_conta,
        id_empresa=id_empresa,
        current_user=current_user,
        session=session
    )


@router.put("/{id_conta}", response_model=ContaPagar, 
           summary="Atualizar conta a pagar",
           response_description="Conta a pagar atualizada com sucesso")
@require_permission("contas", "editar")
async def atualizar_conta_pagar(
    id_conta: UUID = Path(..., description="ID da conta a pagar", example="3fa85f64-5717-4562-b3fc-2c963f66afa6"),
    conta: ContaPagarUpdate = Body(..., 
                                  example={
                                      "descricao": "Pagamento fornecedor ABC (atualizado)",
                                      "valor": 1300.00,
                                      "data_vencimento": "2023-12-31",
                                      "status": "PENDENTE",
                                      "observacao": "Valor atualizado conforme acordo"
                                  }),
    id_empresa: UUID = Query(..., description="ID da empresa", example="3fa85f64-5717-4562-b3fc-2c963f66afa6"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Atualiza uma conta a pagar existente.
    
    ## Parâmetros:
    - **id_conta**: ID da conta a pagar (obrigatório, no path)
    - **id_empresa**: ID da empresa (obrigatório, query param)
    - **conta**: Dados para atualização (no body)
      - Apenas os campos enviados serão atualizados
      - Campos não enviados permanecerão inalterados
    
    ## Campos atualizáveis:
    - **descricao**: Descrição da conta (3-100 caracteres)
    - **valor**: Valor da conta em decimal (maior que zero)
    - **data_vencimento**: Data de vencimento no formato YYYY-MM-DD
    - **data_pagamento**: Data de pagamento no formato YYYY-MM-DD
    - **status**: Status da conta (PENDENTE, PAGO, VENCIDO, CANCELADO)
    - **observacao**: Observações adicionais (máx 500 caracteres)
    - **fornecedor_id**: ID do fornecedor
    - **categoria_id**: ID da categoria
    
    ## Possíveis erros:
    - **403**: Usuário sem permissão para editar contas a pagar
    - **404**: Conta a pagar não encontrada
    - **400**: Dados inválidos para atualização
    """
    try:
        service = ContaPagarService(session)
        log_service = LogSistemaService(session)
        
        # Verificar se a conta existe
        conta_atual = await service.get_by_id(id_conta)
        if not conta_atual:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conta a pagar não encontrada"
            )
            
        # Verificar permissão para a empresa
        if conta_atual.id_empresa != id_empresa:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão negada para esta conta"
            )
            
        # Atualizar conta
        conta_atualizada = await service.update(
            id_conta,
            conta,
            usuario_id=current_user.id,
            empresa_id=id_empresa
        )
        
        # Registrar log
        await log_service.registrar_atividade(
            id_usuario=current_user.id,
            id_empresa=id_empresa,
            acao="ATUALIZAR_CONTA_PAGAR",
            descricao=f"Conta a pagar atualizada: {conta_atualizada.descricao}"
        )
        
        return conta_atualizada
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar conta a pagar: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{id_conta}", status_code=status.HTTP_200_OK,
              summary="Remover conta a pagar",
              response_description="Conta a pagar removida com sucesso")
@require_permission("contas", "deletar")
async def remover_conta_pagar(
    id_conta: UUID = Path(..., description="ID da conta a pagar", example="3fa85f64-5717-4562-b3fc-2c963f66afa6"),
    id_empresa: UUID = Query(..., description="ID da empresa", example="3fa85f64-5717-4562-b3fc-2c963f66afa6"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Remove uma conta a pagar do sistema.
    
    ## Parâmetros:
    - **id_conta**: ID da conta a pagar (obrigatório, no path)
    - **id_empresa**: ID da empresa (obrigatório, query param)
    
    ## Retorno:
    - Mensagem de confirmação da remoção
    
    ## Restrições:
    - Contas com status PAGO não podem ser removidas, apenas canceladas
    - Apenas usuários com permissão de deletar em contas podem executar esta ação
    
    ## Possíveis erros:
    - **403**: Usuário sem permissão para remover contas a pagar
    - **404**: Conta a pagar não encontrada
    - **400**: Conta não pode ser removida devido ao seu status atual
    """
    try:
        service = ContaPagarService(session)
        log_service = LogSistemaService(session)
        
        # Verificar se a conta existe
        conta_atual = await service.get_by_id(id_conta)
        if not conta_atual:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conta a pagar não encontrada"
            )
            
        # Verificar permissão para a empresa
        if conta_atual.id_empresa != id_empresa:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão negada para esta conta"
            )
            
        # Remover conta
        sucesso = await service.delete(id_conta, current_user.id)
        if not sucesso:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não foi possível remover a conta"
            )
            
        # Registrar log
        await log_service.registrar_atividade(
            id_usuario=current_user.id,
            id_empresa=id_empresa,
            acao="REMOVER_CONTA_PAGAR",
            descricao=f"Conta a pagar removida: {conta_atual.descricao}"
        )
        
        return {"message": "Conta a pagar removida com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao remover conta a pagar: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{id_conta}/pagar", response_model=ContaPagar,
            summary="Registrar pagamento de conta",
            response_description="Conta atualizada com pagamento registrado")
@require_permission("contas", "editar")
async def registrar_pagamento(
    id_conta: UUID = Path(..., description="ID da conta a pagar", example="3fa85f64-5717-4562-b3fc-2c963f66afa6"),
    pagamento: ContaPagarPagamento = Body(..., 
                                         example={
                                             "data_pagamento": "2023-12-10",
                                             "valor_pago": 1250.75,
                                             "observacoes": "Pagamento via transferência bancária"
                                         }),
    id_empresa: UUID = Query(..., description="ID da empresa", example="3fa85f64-5717-4562-b3fc-2c963f66afa6"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Registra o pagamento de uma conta a pagar.
    
    ## Parâmetros:
    - **id_conta**: ID da conta a pagar (obrigatório, no path)
    - **id_empresa**: ID da empresa (obrigatório, query param)
    - **pagamento**: Dados do pagamento (no body)
      - **data_pagamento**: Data em que o pagamento foi realizado (obrigatório)
      - **valor_pago**: Valor pago (obrigatório, maior que zero)
      - **observacoes**: Observações sobre o pagamento (opcional)
    
    ## Retorno:
    - Objeto atualizado da conta a pagar com status alterado para PAGO
    
    ## Restrições:
    - Apenas contas com status PENDENTE ou VENCIDO podem receber pagamento
    - Contas com status CANCELADO não podem ser pagas
    
    ## Possíveis erros:
    - **403**: Usuário sem permissão para registrar pagamentos
    - **404**: Conta a pagar não encontrada
    - **400**: Operação inválida (ex: conta já paga, valor inválido)
    """
    try:
        service = ContaPagarService(session)
        log_service = LogSistemaService(session)
        
        # Verificar se a conta existe
        conta_atual = await service.get_by_id(id_conta)
        if not conta_atual:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conta a pagar não encontrada"
            )
            
        # Verificar permissão para a empresa
        if conta_atual.id_empresa != id_empresa:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão negada para esta conta"
            )
            
        # Verificar se a conta já está paga
        if conta_atual.status == StatusContaPagar.pago:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Conta já está paga"
            )
            
        # Verificar se a conta está cancelada
        if conta_atual.status == StatusContaPagar.cancelado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível pagar uma conta cancelada"
            )
            
        # Registrar pagamento
        conta_paga = await service.registrar_pagamento(
            id_conta=id_conta,
            data_pagamento=pagamento.data_pagamento,
            valor_pago=pagamento.valor_pago,
            observacoes=pagamento.observacoes,
            usuario_id=current_user.id
        )
        
        # Registrar log
        await log_service.registrar_atividade(
            id_usuario=current_user.id,
            id_empresa=id_empresa,
            acao="REGISTRAR_PAGAMENTO",
            descricao=f"Pagamento registrado para conta: {conta_paga.descricao}"
        )
        
        return conta_paga
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao registrar pagamento: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{id_conta}/cancelar", response_model=ContaPagar,
            summary="Cancelar conta a pagar",
            response_description="Conta atualizada com status CANCELADO")
@require_permission("contas", "editar")
async def cancelar_conta(
    id_conta: UUID = Path(..., description="ID da conta a pagar", example="3fa85f64-5717-4562-b3fc-2c963f66afa6"),
    dados_cancelamento: dict = Body(..., 
                                  example={
                                      "motivo_cancelamento": "Fatura emitida incorretamente",
                                      "observacoes": "Será substituída por nova fatura"
                                  }),
    id_empresa: UUID = Query(..., description="ID da empresa", example="3fa85f64-5717-4562-b3fc-2c963f66afa6"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Cancela uma conta a pagar, alterando seu status para CANCELADO.
    
    ## Parâmetros:
    - **id_conta**: ID da conta a pagar (obrigatório, no path)
    - **id_empresa**: ID da empresa (obrigatório, query param)
    - **dados_cancelamento**: Dados do cancelamento (no body)
      - **motivo_cancelamento**: Motivo do cancelamento (obrigatório)
      - **observacoes**: Observações adicionais (opcional)
    
    ## Retorno:
    - Objeto atualizado da conta a pagar com status alterado para CANCELADO
    
    ## Restrições:
    - Contas com status PAGO não podem ser canceladas
    - Apenas usuários com permissão de editar contas podem cancelar
    
    ## Possíveis erros:
    - **403**: Usuário sem permissão para cancelar contas
    - **404**: Conta a pagar não encontrada
    - **400**: Operação inválida (ex: conta já paga)
    """
    try:
        service = ContaPagarService(session)
        log_service = LogSistemaService(session)
        
        # Verificar se a conta existe
        conta_atual = await service.get_by_id(id_conta)
        if not conta_atual:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conta a pagar não encontrada"
            )
            
        # Verificar permissão para a empresa
        if conta_atual.id_empresa != id_empresa:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão negada para esta conta"
            )
            
        # Verificar se a conta já está cancelada
        if conta_atual.status == StatusContaPagar.cancelado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Conta já está cancelada"
            )
        
        # Cancelar conta
        conta_cancelada = await service.cancelar(
            id_conta=id_conta,
            motivo=dados_cancelamento["motivo_cancelamento"],
            observacoes=dados_cancelamento["observacoes"],
            usuario_id=current_user.id
        )
        
        # Registrar log
        await log_service.registrar_atividade(
            id_usuario=current_user.id,
            id_empresa=id_empresa,
            acao="CANCELAR_CONTA_PAGAR",
            descricao=f"Conta a pagar cancelada: {conta_cancelada.descricao}. Motivo: {dados_cancelamento['motivo_cancelamento']}"
        )
        
        return conta_cancelada
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao cancelar conta a pagar: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 