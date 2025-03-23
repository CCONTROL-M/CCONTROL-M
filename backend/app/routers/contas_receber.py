"""Router para Contas a Receber."""
import logging
from uuid import UUID
from typing import Optional, List
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.conta_receber import (
    ContaReceber, ContaReceberCreate, ContaReceberUpdate, 
    ContaReceberList, StatusContaReceber, ContaReceberRecebimento
)
from app.services.conta_receber_service import ContaReceberService
from app.services.log_sistema_service import LogSistemaService
from app.schemas.token import TokenPayload
from app.dependencies import get_current_user
from app.database import get_async_session
from app.utils.permissions import require_permission
from app.schemas.log_sistema import LogSistemaCreate

# Configuração do logger
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/contas-receber",
    tags=["Contas a Receber"],
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Requisição inválida ou dados inconsistentes",
            "content": {
                "application/json": {
                    "example": {
                        "status_code": 400,
                        "message": "Valor inválido para conta a receber",
                        "error_code": "VAL_INVALID_FORMAT",
                        "details": {
                            "valor": ["Deve ser maior que zero"]
                        }
                    }
                }
            }
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Permissão negada para acessar este recurso",
            "content": {
                "application/json": {
                    "example": {
                        "status_code": 403,
                        "message": "Permissão negada para acessar esta conta",
                        "error_code": "AUTH_INSUFFICIENT_PERM",
                        "details": {
                            "required_permission": "contas",
                            "required_action": "editar"
                        }
                    }
                }
            }
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Conta a receber não encontrada",
            "content": {
                "application/json": {
                    "example": {
                        "status_code": 404,
                        "message": "Conta a receber não encontrada",
                        "error_code": "RES_NOT_FOUND",
                        "details": {
                            "resource_id": "id-da-conta-aqui",
                            "resource_type": "conta_receber"
                        }
                    }
                }
            }
        }
    }
)


@router.post("", response_model=ContaReceber, status_code=status.HTTP_201_CREATED,
            summary="Criar nova conta a receber",
            response_description="Conta a receber criada com sucesso")
@require_permission("contas", "criar")
async def criar_conta_receber(
    conta: ContaReceberCreate = Body(..., 
                                    example={
                                        "descricao": "Venda para cliente ABC",
                                        "valor": 2500.00,
                                        "data_emissao": "2023-12-01",
                                        "data_vencimento": "2023-12-30",
                                        "observacoes": "Venda de produtos",
                                        "id_cliente": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                        "id_empresa": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                        "id_venda": None
                                    }),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Cria uma nova conta a receber no sistema.
    
    ## Parâmetros:
    - **descricao**: Descrição da conta (obrigatório, 3-255 caracteres)
    - **valor**: Valor da conta em decimal (obrigatório, maior que zero)
    - **data_emissao**: Data de emissão no formato YYYY-MM-DD (obrigatório)
    - **data_vencimento**: Data de vencimento no formato YYYY-MM-DD (obrigatório)
    - **id_empresa**: ID da empresa (obrigatório, UUID)
    - **id_cliente**: ID do cliente associado (opcional, UUID)
    - **id_venda**: ID da venda associada (opcional, UUID)
    - **observacoes**: Observações adicionais (opcional, máx 1000 caracteres)
    
    ## Retorno:
    - Objeto completo da conta a receber criada, incluindo ID gerado
    
    ## Possíveis erros:
    - **400**: Dados inválidos (ex: valor negativo, descrição muito curta)
    - **403**: Usuário sem permissão para criar contas a receber
    - **422**: Erro de validação nos dados enviados (ex: data de vencimento anterior à data de emissão)
    """
    try:
        service = ContaReceberService(session)
        log_service = LogSistemaService(session)
        
        # Criar conta a receber
        nova_conta = await service.create(
            conta,
            usuario_id=current_user.id,
            empresa_id=conta.id_empresa
        )
        
        # Registrar log
        await log_service.registrar_atividade(
            id_usuario=current_user.id,
            id_empresa=conta.id_empresa,
            acao="CRIAR_CONTA_RECEBER",
            descricao=f"Conta a receber criada: {nova_conta.descricao}"
        )
        
        return nova_conta
    except Exception as e:
        logger.error(f"Erro ao criar conta a receber: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{id_conta}", response_model=ContaReceber,
           summary="Atualizar conta a receber",
           response_description="Conta a receber atualizada com sucesso")
@require_permission("contas", "editar")
async def atualizar_conta_receber(
    id_conta: UUID = Path(..., description="ID da conta a receber", example="3fa85f64-5717-4562-b3fc-2c963f66afa6"),
    conta: ContaReceberUpdate = Body(..., 
                                   example={
                                       "descricao": "Venda para cliente ABC (atualizado)",
                                       "valor": 2750.00,
                                       "data_vencimento": "2024-01-15",
                                       "status": "pendente",
                                       "observacoes": "Valor atualizado conforme acordo"
                                   }),
    id_empresa: UUID = Query(..., description="ID da empresa", example="3fa85f64-5717-4562-b3fc-2c963f66afa6"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Atualiza uma conta a receber existente.
    
    ## Parâmetros:
    - **id_conta**: ID da conta a receber (obrigatório, no path)
    - **id_empresa**: ID da empresa (obrigatório, query param)
    - **conta**: Dados para atualização (no body)
      - Apenas os campos enviados serão atualizados
      - Campos não enviados permanecerão inalterados
    
    ## Campos atualizáveis:
    - **descricao**: Descrição da conta (3-255 caracteres)
    - **valor**: Valor da conta em decimal (maior que zero)
    - **data_vencimento**: Data de vencimento no formato YYYY-MM-DD
    - **status**: Status da conta (pendente, recebido, parcial, cancelado, atrasado)
    - **observacoes**: Observações adicionais (máx 1000 caracteres)
    
    ## Possíveis erros:
    - **403**: Usuário sem permissão para editar contas a receber
    - **404**: Conta a receber não encontrada
    - **400**: Dados inválidos para atualização
    """
    try:
        service = ContaReceberService(session)
        log_service = LogSistemaService(session)
        
        # Verificar se a conta existe
        conta_atual = await service.get_by_id(id_conta)
        if not conta_atual:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conta a receber não encontrada"
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
            acao="ATUALIZAR_CONTA_RECEBER",
            descricao=f"Conta a receber atualizada: {conta_atualizada.descricao}"
        )
        
        return conta_atualizada
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar conta a receber: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{id_conta}", status_code=status.HTTP_200_OK,
              summary="Remover conta a receber",
              response_description="Conta a receber removida com sucesso")
@require_permission("contas", "deletar")
async def remover_conta_receber(
    id_conta: UUID = Path(..., description="ID da conta a receber", example="3fa85f64-5717-4562-b3fc-2c963f66afa6"),
    id_empresa: UUID = Query(..., description="ID da empresa", example="3fa85f64-5717-4562-b3fc-2c963f66afa6"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Remove uma conta a receber do sistema.
    
    ## Parâmetros:
    - **id_conta**: ID da conta a receber (obrigatório, no path)
    - **id_empresa**: ID da empresa (obrigatório, query param)
    
    ## Retorno:
    - Mensagem de confirmação da remoção
    
    ## Restrições:
    - Contas com status "recebido" não podem ser removidas, apenas canceladas
    - Apenas usuários com permissão de deletar em contas podem executar esta ação
    
    ## Possíveis erros:
    - **403**: Usuário sem permissão para remover contas a receber
    - **404**: Conta a receber não encontrada
    - **400**: Conta não pode ser removida devido ao seu status atual
    """
    try:
        service = ContaReceberService(session)
        log_service = LogSistemaService(session)
        
        # Verificar se a conta existe
        conta = await service.get_by_id(id_conta)
        if not conta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conta a receber não encontrada"
            )
            
        # Verificar permissão para a empresa
        if conta.id_empresa != id_empresa:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão negada para esta conta"
            )
            
        # Verificar se a conta já foi recebida
        if conta.status == StatusContaReceber.recebido:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Conta já recebida não pode ser removida, apenas cancelada"
            )
            
        # Remover conta
        await service.delete(id_conta)
        
        # Registrar log
        await log_service.registrar_atividade(
            id_usuario=current_user.id,
            id_empresa=id_empresa,
            acao="REMOVER_CONTA_RECEBER",
            descricao=f"Conta a receber removida: {conta.descricao}"
        )
        
        return {"message": "Conta a receber removida com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao remover conta a receber: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=ContaReceberList,
           summary="Listar contas a receber",
           response_description="Lista paginada de contas a receber")
@require_permission("contas", "listar")
async def listar_contas_receber(
    id_empresa: UUID = Query(..., description="ID da empresa", example="3fa85f64-5717-4562-b3fc-2c963f66afa6"),
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=100, description="Limite de registros por página"),
    status: Optional[StatusContaReceber] = Query(None, description="Filtrar por status"),
    cliente_id: Optional[UUID] = Query(None, description="Filtrar por cliente"),
    data_inicio: Optional[date] = Query(None, description="Filtrar por data de vencimento inicial"),
    data_fim: Optional[date] = Query(None, description="Filtrar por data de vencimento final"),
    search: Optional[str] = Query(None, description="Buscar por descrição"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Lista contas a receber com filtros e paginação.
    
    ## Parâmetros:
    - **id_empresa**: ID da empresa (obrigatório)
    - **skip**: Número de registros para pular (paginação)
    - **limit**: Limite de registros por página (máx: 100)
    
    ## Filtros opcionais:
    - **status**: Filtrar por status (pendente, recebido, parcial, cancelado, atrasado)
    - **cliente_id**: Filtrar por cliente específico
    - **data_inicio**: Filtrar contas a partir desta data de vencimento
    - **data_fim**: Filtrar contas até esta data de vencimento
    - **search**: Buscar por termo na descrição da conta
    
    ## Retorno:
    - Lista paginada de contas a receber
    - Metadados de paginação (total, página atual, etc.)
    
    ## Exemplo de resposta:
    ```json
    {
        "items": [
            {
                "id_conta_receber": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "descricao": "Venda para cliente XYZ",
                "valor": 2500.00,
                "data_emissao": "2023-12-01",
                "data_vencimento": "2023-12-30",
                "status": "pendente",
                ...
            }
        ],
        "total": 45,
        "page": 1,
        "size": 10,
        "pages": 5
    }
    ```
    """
    try:
        service = ContaReceberService(session)
        
        # Listar contas a receber
        contas, total = await service.list(
            empresa_id=id_empresa,
            status=status,
            cliente_id=cliente_id,
            data_inicio=data_inicio,
            data_fim=data_fim,
            search=search,
            skip=skip,
            limit=limit
        )
        
        # Calcular página atual e total de páginas
        page = (skip // limit) + 1 if limit > 0 else 1
        pages = (total + limit - 1) // limit if limit > 0 else 1
        
        return ContaReceberList(
            items=contas,
            total=total,
            page=page,
            size=limit,
            pages=pages
        )
    except Exception as e:
        logger.error(f"Erro ao listar contas a receber: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{id_conta}", response_model=ContaReceber,
           summary="Buscar conta a receber por ID",
           response_description="Detalhes da conta a receber")
@require_permission("contas", "visualizar")
async def buscar_conta_receber(
    id_conta: UUID = Path(..., description="ID da conta a receber", example="3fa85f64-5717-4562-b3fc-2c963f66afa6"),
    id_empresa: UUID = Query(..., description="ID da empresa", example="3fa85f64-5717-4562-b3fc-2c963f66afa6"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Busca detalhes de uma conta a receber específica pelo ID.
    
    ## Parâmetros:
    - **id_conta**: ID da conta a receber (obrigatório, no path)
    - **id_empresa**: ID da empresa (obrigatório, query param)
    
    ## Retorno:
    - Objeto detalhado da conta a receber
    
    ## Possíveis erros:
    - **403**: Usuário sem permissão para visualizar contas a receber
    - **404**: Conta a receber não encontrada
    """
    try:
        service = ContaReceberService(session)
        log_service = LogSistemaService(session)
        
        # Buscar conta
        conta = await service.get_by_id(id_conta)
        if not conta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conta a receber não encontrada"
            )
            
        # Verificar permissão para a empresa
        if conta.id_empresa != id_empresa:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão negada para esta conta"
            )
            
        # Registrar log
        await log_service.registrar_atividade(
            id_usuario=current_user.id,
            id_empresa=id_empresa,
            acao="VISUALIZAR_CONTA_RECEBER",
            descricao=f"Conta a receber visualizada: {conta.descricao}"
        )
        
        return conta
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar conta a receber: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{id_conta}/receber", response_model=ContaReceber,
            summary="Registrar recebimento de conta",
            response_description="Conta atualizada com recebimento registrado")
@require_permission("contas", "editar")
async def registrar_recebimento(
    id_conta: UUID = Path(..., description="ID da conta a receber", example="3fa85f64-5717-4562-b3fc-2c963f66afa6"),
    recebimento: ContaReceberRecebimento = Body(..., 
                                               example={
                                                   "data_recebimento": "2023-12-20",
                                                   "valor_recebido": 2500.00,
                                                   "observacoes": "Pagamento via PIX"
                                               }),
    id_empresa: UUID = Query(..., description="ID da empresa", example="3fa85f64-5717-4562-b3fc-2c963f66afa6"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Registra o recebimento de uma conta a receber.
    
    ## Parâmetros:
    - **id_conta**: ID da conta a receber (obrigatório, no path)
    - **id_empresa**: ID da empresa (obrigatório, query param)
    - **recebimento**: Dados do recebimento (no body)
      - **data_recebimento**: Data em que o recebimento foi realizado (obrigatório)
      - **valor_recebido**: Valor recebido (obrigatório, maior que zero)
      - **observacoes**: Observações sobre o recebimento (opcional)
    
    ## Retorno:
    - Objeto atualizado da conta a receber com status alterado para "recebido" ou "parcial"
    
    ## Restrições:
    - Apenas contas com status "pendente" ou "atrasado" podem receber pagamento
    - Contas com status "cancelado" não podem ser recebidas
    - Se o valor recebido for menor que o valor da conta, o status será "parcial"
    
    ## Possíveis erros:
    - **403**: Usuário sem permissão para registrar recebimentos
    - **404**: Conta a receber não encontrada
    - **400**: Operação inválida (ex: conta já recebida, valor inválido)
    """
    try:
        service = ContaReceberService(session)
        log_service = LogSistemaService(session)
        
        # Verificar se a conta existe
        conta = await service.get_by_id(id_conta)
        if not conta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conta a receber não encontrada"
            )
            
        # Verificar permissão para a empresa
        if conta.id_empresa != id_empresa:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão negada para esta conta"
            )
            
        # Verificar se a conta já foi recebida
        if conta.status == StatusContaReceber.recebido:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Conta já recebida não pode ser recebida novamente"
            )
            
        # Verificar se a conta foi cancelada
        if conta.status == StatusContaReceber.cancelado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Conta cancelada não pode ser recebida"
            )
            
        # Registrar recebimento
        conta_recebida = await service.registrar_recebimento(
            id_conta=id_conta,
            data_recebimento=recebimento.data_recebimento,
            valor_recebido=recebimento.valor_recebido,
            observacoes=recebimento.observacoes,
            usuario_id=current_user.id
        )
        
        # Registrar log
        await log_service.registrar_atividade(
            id_usuario=current_user.id,
            id_empresa=id_empresa,
            acao="RECEBER_CONTA",
            descricao=f"Recebimento registrado para conta: {conta.descricao}. Valor: {recebimento.valor_recebido}"
        )
        
        return conta_recebida
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao registrar recebimento: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{id_conta}/cancelar", response_model=ContaReceber,
            summary="Cancelar conta a receber",
            response_description="Conta atualizada com status CANCELADO")
@require_permission("contas", "editar")
async def cancelar_conta(
    id_conta: UUID = Path(..., description="ID da conta a receber", example="3fa85f64-5717-4562-b3fc-2c963f66afa6"),
    dados_cancelamento: dict = Body(..., 
                                  example={
                                      "motivo_cancelamento": "Cliente desistiu da compra",
                                      "observacoes": "Será emitida nota de cancelamento"
                                  }),
    id_empresa: UUID = Query(..., description="ID da empresa", example="3fa85f64-5717-4562-b3fc-2c963f66afa6"),
    current_user: TokenPayload = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Cancela uma conta a receber, alterando seu status para "cancelado".
    
    ## Parâmetros:
    - **id_conta**: ID da conta a receber (obrigatório, no path)
    - **id_empresa**: ID da empresa (obrigatório, query param)
    - **dados_cancelamento**: Dados do cancelamento (no body)
      - **motivo_cancelamento**: Motivo do cancelamento (obrigatório)
      - **observacoes**: Observações adicionais (opcional)
    
    ## Retorno:
    - Objeto atualizado da conta a receber com status alterado para "cancelado"
    
    ## Restrições:
    - Contas com status "recebido" não podem ser canceladas
    - Apenas usuários com permissão de editar contas podem cancelar
    
    ## Possíveis erros:
    - **403**: Usuário sem permissão para cancelar contas
    - **404**: Conta a receber não encontrada
    - **400**: Operação inválida (ex: conta já recebida)
    """
    try:
        service = ContaReceberService(session)
        log_service = LogSistemaService(session)
        
        # Verificar se a conta existe
        conta = await service.get_by_id(id_conta)
        if not conta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conta a receber não encontrada"
            )
            
        # Verificar permissão para a empresa
        if conta.id_empresa != id_empresa:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão negada para esta conta"
            )
            
        # Verificar se a conta já foi recebida
        if conta.status == StatusContaReceber.recebido:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Conta já recebida não pode ser cancelada"
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
            acao="CANCELAR_CONTA_RECEBER",
            descricao=f"Conta a receber cancelada: {conta.descricao}. Motivo: {dados_cancelamento['motivo_cancelamento']}"
        )
        
        return conta_cancelada
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao cancelar conta a receber: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 