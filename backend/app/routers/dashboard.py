"""
Router para o dashboard do sistema CCONTROL-M.

Este módulo implementa os endpoints para o dashboard financeiro,
agregando dados relevantes para exibição no painel inicial.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import date, datetime

from app.database import get_async_session
from app.schemas.token import TokenPayload
from app.dependencies import get_current_user
from app.utils.permissions import require_permission as verify_permission
from app.repositories.conta_bancaria_repository import ContaBancariaRepository
from app.services.conta_pagar.conta_pagar_query_service import ContaPagarQueryService
from app.services.parcela_service import ParcelaService
from app.models.usuario import Usuario
from app.models.empresa import Empresa
from app.schemas.relatorio import ResumoDashboard
from app.utils.verificacoes import verificar_permissao_empresa

# Configuração de logger
logger = logging.getLogger(__name__)

# Schema de resposta para o resumo do dashboard
class ResumoDashboard(BaseModel):
    """Schema para o resumo do dashboard financeiro."""
    caixa_atual: float = 0
    total_receber: float = 0
    total_pagar: float = 0
    recebimentos_hoje: float = 0
    pagamentos_hoje: float = 0

# Router
router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
    responses={404: {"description": "Dados não encontrados"}}
)

@router.get("/resumo", response_model=ResumoDashboard)
async def get_dashboard_resumo(
    id_empresa: UUID,
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Obtém resumo financeiro para o dashboard.
    
    Args:
        id_empresa: ID da empresa
        current_user: Usuário autenticado
        session: Sessão do banco de dados
        
    Returns:
        ResumoDashboard: Resumo financeiro para o dashboard
    """
    try:
        # Verificar permissão do usuário para a empresa
        await verificar_permissao_empresa(session, id_empresa, current_user)
        
        # Inicializar serviços e repositórios
        conta_bancaria_repository = ContaBancariaRepository(session)
        parcela_service = ParcelaService(session)
        conta_pagar_service = ContaPagarQueryService(session)
        
        # Data atual
        hoje = date.today()
        
        # Obter saldo atual
        caixa_atual = await conta_bancaria_repository.get_saldo_total(id_empresa)
        
        # Obter total a receber
        parcelas_dashboard = await parcela_service.get_dashboard_parcelas(
            id_empresa=id_empresa,
            dias_vencidas=0,  # Todas vencidas
            dias_proximas=365  # Próximos 12 meses
        )
        total_receber = sum(float(parcela.valor) for parcela in parcelas_dashboard.vencidas + parcelas_dashboard.proximas)
        
        # Obter total a pagar
        # TODO: Implementar método para buscar contas a pagar pendentes
        total_pagar = 0.0  # Valor temporário
        
        # Obter recebimentos do dia
        recebimentos_hoje = await parcela_service.get_recebimentos_dia(
            id_empresa=id_empresa,
            data=hoje
        )
        
        # Obter pagamentos do dia
        pagamentos_hoje = await conta_pagar_service.get_pagamentos_dia(
            empresa_id=id_empresa,
            data=hoje
        )
        
        # Montar o resumo
        resumo = ResumoDashboard(
            caixa_atual=caixa_atual,
            total_receber=total_receber,
            total_pagar=total_pagar,
            recebimentos_hoje=recebimentos_hoje,
            pagamentos_hoje=pagamentos_hoje
        )
        
        return resumo
    
    except Exception as e:
        logging.error(f"Erro ao obter resumo do dashboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter resumo do dashboard: {str(e)}"
        ) 