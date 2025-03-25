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
from sqlalchemy import func, and_, extract, select

from app.database import get_async_session
from app.schemas.token import TokenPayload
from app.dependencies import get_current_user
from app.utils.permissions import require_permission as verify_permission
from app.repositories.conta_bancaria_repository import ContaBancariaRepository
from app.services.conta_pagar.conta_pagar_query_service import ContaPagarQueryService
from app.services.parcela_service import ParcelaService
from app.models.usuario import Usuario
from app.models.empresa import Empresa
from app.models.cliente import Cliente
from app.models.fornecedor import Fornecedor
from app.models.lancamento import Lancamento
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

# Schema de resposta para o novo resumo do dashboard
class ResumoDashboardApi(BaseModel):
    """Schema para o resumo do dashboard financeiro da API v1."""
    total_receitas_mes_atual: float = 0
    total_despesas_mes_atual: float = 0
    saldo_mensal_atual: float = 0
    quantidade_clientes: int = 0
    quantidade_fornecedores: int = 0
    quantidade_lancamentos_mes: int = 0

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
) -> ResumoDashboard:
    """
    Retorna um resumo financeiro para o dashboard.
    
    Este endpoint agrega dados como saldo atual, valores a pagar e receber,
    bem como movimentações previstas para o dia atual.
    """
    logger.info(f"Obtendo resumo do dashboard para empresa {id_empresa}")
    
    try:
        # Verificar permissão de acesso à empresa
        await verificar_permissao_empresa(id_empresa, current_user, session)
        
        # Inicializar resposta
        response = ResumoDashboard()
        
        # Obter saldo atual
        saldo_contas = await ContaBancariaRepository(session).get_saldo_total(id_empresa)
        response.caixa_atual = saldo_contas if saldo_contas else 0.0
        
        # Inicializar serviços e repositórios
        conta_bancaria_repository = ContaBancariaRepository(session)
        parcela_service = ParcelaService(session)
        conta_pagar_service = ContaPagarQueryService(session)
        
        # Data atual
        hoje = date.today()
        
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
        response.caixa_atual = saldo_contas if saldo_contas else 0.0
        response.total_receber = total_receber
        response.total_pagar = total_pagar
        response.recebimentos_hoje = recebimentos_hoje
        response.pagamentos_hoje = pagamentos_hoje
        
        return response
    
    except Exception as e:
        logging.error(f"Erro ao obter resumo do dashboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter resumo do dashboard: {str(e)}"
        ) 

@router.get("/resumo", response_model=ResumoDashboardApi)
async def get_dashboard_resumo_api_v1(
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> ResumoDashboardApi:
    """
    Retorna dados consolidados para o dashboard da empresa do usuário autenticado.
    
    Este endpoint agrega dados como receitas e despesas do mês atual, saldo mensal,
    quantidades de clientes, fornecedores e lançamentos do mês.
    """
    logger.info(f"Obtendo resumo do dashboard para usuário {current_user.id_usuario}")
    
    try:
        # Obter id_empresa do usuário autenticado
        id_empresa = current_user.id_empresa
        
        # Verificar permissão de acesso à empresa
        await verificar_permissao_empresa(id_empresa, current_user, session)
        
        # Inicializar resposta
        response = ResumoDashboardApi()
        
        # Obter data atual com timezone
        hoje = datetime.now()
        mes_atual = hoje.month
        ano_atual = hoje.year
        
        # Consultar receitas do mês atual (lancamentos de tipo 'entrada')
        query_receitas = (
            select(func.sum(Lancamento.valor))
            .where(
                and_(
                    Lancamento.id_empresa == id_empresa,
                    Lancamento.tipo == "entrada",
                    extract('month', Lancamento.data_lancamento) == mes_atual,
                    extract('year', Lancamento.data_lancamento) == ano_atual
                )
            )
        )
        result_receitas = await session.execute(query_receitas)
        total_receitas = result_receitas.scalar_one_or_none() or 0.0
        
        # Consultar despesas do mês atual (lancamentos de tipo 'saida')
        query_despesas = (
            select(func.sum(Lancamento.valor))
            .where(
                and_(
                    Lancamento.id_empresa == id_empresa,
                    Lancamento.tipo == "saida",
                    extract('month', Lancamento.data_lancamento) == mes_atual,
                    extract('year', Lancamento.data_lancamento) == ano_atual
                )
            )
        )
        result_despesas = await session.execute(query_despesas)
        total_despesas = result_despesas.scalar_one_or_none() or 0.0
        
        # Calcular saldo mensal
        saldo_mensal = total_receitas - total_despesas
        
        # Consultar quantidade de clientes
        query_clientes = (
            select(func.count())
            .select_from(Cliente)
            .where(Cliente.id_empresa == id_empresa)
        )
        result_clientes = await session.execute(query_clientes)
        qtd_clientes = result_clientes.scalar_one_or_none() or 0
        
        # Consultar quantidade de fornecedores
        query_fornecedores = (
            select(func.count())
            .select_from(Fornecedor)
            .where(Fornecedor.id_empresa == id_empresa)
        )
        result_fornecedores = await session.execute(query_fornecedores)
        qtd_fornecedores = result_fornecedores.scalar_one_or_none() or 0
        
        # Consultar quantidade de lançamentos do mês
        query_lancamentos = (
            select(func.count())
            .select_from(Lancamento)
            .where(
                and_(
                    Lancamento.id_empresa == id_empresa,
                    extract('month', Lancamento.data_lancamento) == mes_atual,
                    extract('year', Lancamento.data_lancamento) == ano_atual
                )
            )
        )
        result_lancamentos = await session.execute(query_lancamentos)
        qtd_lancamentos = result_lancamentos.scalar_one_or_none() or 0
        
        # Montar o resumo
        response.total_receitas_mes_atual = float(total_receitas)
        response.total_despesas_mes_atual = float(total_despesas)
        response.saldo_mensal_atual = float(saldo_mensal)
        response.quantidade_clientes = qtd_clientes
        response.quantidade_fornecedores = qtd_fornecedores
        response.quantidade_lancamentos_mes = qtd_lancamentos
        
        return response
    
    except Exception as e:
        logging.error(f"Erro ao obter resumo do dashboard API v1: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter resumo do dashboard: {str(e)}"
        ) 