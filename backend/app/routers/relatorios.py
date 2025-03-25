"""Router de relatórios financeiros para o sistema CCONTROL-M."""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from datetime import datetime, date, timedelta
from uuid import UUID
from pydantic import BaseModel
from sqlalchemy import select, func, and_, or_, desc, extract, case, literal_column, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import expression
from collections import defaultdict

# Importação de modelos e utilitários
from app.models.lancamento import Lancamento
from app.models.categoria import Categoria
from app.models.cliente import Cliente
from app.models.parcela import Parcela, ParcelaVenda
from app.models.venda import Venda
from app.models.compra import Compra
from app.models.usuario import Usuario
from app.models.empresa import Empresa
from app.database import get_async_session
from app.dependencies import get_current_user
from app.utils.verificacoes import verificar_permissao_empresa

# Definição simples dos schemas de relatórios
class CategoriaValor(BaseModel):
    categoria: str
    valor: float

class RelatorioInadimplencia(BaseModel):
    cliente: str
    documento: str
    contato: str
    valor_total: float
    dias_atraso: int
    parcelas_atrasadas: int

class RelatorioFluxoCaixa(BaseModel):
    data: str
    entradas: float
    saidas: float
    saldo_dia: float
    saldo_acumulado: float

class RelatorioDRE(BaseModel):
    receitas: List[CategoriaValor]
    despesas: List[CategoriaValor]
    lucro_prejuizo: float

class RelatorioCicloOperacional(BaseModel):
    mes: str
    ano: int
    pme: int
    pmr: int
    pmp: int
    ciclo_operacional: int
    ciclo_financeiro: int

router = APIRouter(
    prefix="/relatorios",
    tags=["Relatórios"],
    responses={404: {"description": "Relatório não encontrado"}}
)

@router.get(
    "/inadimplencia",
    response_model=List[RelatorioInadimplencia],
    summary="Relatório de Inadimplência",
    description="Retorna dados para o relatório de inadimplência."
)
async def obter_relatorio_inadimplencia(
    id_empresa: UUID = Query(..., description="ID da empresa"),
    data_inicio: Optional[date] = Query(None, description="Data inicial do período"),
    data_fim: Optional[date] = Query(None, description="Data final do período"),
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Relatório de Inadimplência."""
    try:
        # Verificar permissão de acesso à empresa
        await verificar_permissao_empresa(id_empresa, current_user, session)
        
        # Definir datas padrão se não informadas
        if not data_inicio:
            data_inicio = date.today() - timedelta(days=365)
        if not data_fim:
            data_fim = date.today()
            
        # Consultar parcelas vencidas e não pagas
        hoje = date.today()
        
        query = (
            select(
                Cliente.nome.label("cliente"),
                Cliente.cpf_cnpj.label("documento"),
                Cliente.telefone.label("contato"),
                func.sum(Parcela.valor).label("valor_total"),
                func.count(Parcela.id_parcela).label("parcelas_atrasadas"),
                func.max(func.date_part('day', hoje - Parcela.data_vencimento)).label("dias_atraso")
            )
            .join(Lancamento, Parcela.id_lancamento == Lancamento.id_lancamento)
            .join(Cliente, Lancamento.id_cliente == Cliente.id_cliente)
            .where(
                and_(
                    Lancamento.id_empresa == id_empresa,
                    Parcela.data_vencimento >= data_inicio,
                    Parcela.data_vencimento <= data_fim,
                    Parcela.data_vencimento < hoje,
                    Parcela.status == "pendente"
                )
            )
            .group_by(Cliente.nome, Cliente.cpf_cnpj, Cliente.telefone)
            .order_by(desc("dias_atraso"))
        )
        
        result = await session.execute(query)
        dados_inadimplencia = []
        
        for row in result.mappings():
            dados_inadimplencia.append(
                RelatorioInadimplencia(
                    cliente=row["cliente"],
                    documento=row["documento"] or "Não informado",
                    contato=row["contato"] or "Não informado",
                    valor_total=float(row["valor_total"]),
                    dias_atraso=int(row["dias_atraso"]),
                    parcelas_atrasadas=int(row["parcelas_atrasadas"])
                )
            )
        
        return dados_inadimplencia
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar relatório de inadimplência: {str(e)}"
        )

@router.get(
    "/fluxo-caixa",
    response_model=List[RelatorioFluxoCaixa],
    summary="Relatório de Fluxo de Caixa",
    description="Retorna dados para o relatório de fluxo de caixa."
)
async def obter_relatorio_fluxo_caixa(
    id_empresa: UUID = Query(..., description="ID da empresa"),
    dataInicio: Optional[date] = Query(None, description="Data inicial do período"),
    dataFim: Optional[date] = Query(None, description="Data final do período"),
    id_conta: Optional[UUID] = Query(None, description="ID da conta bancária"),
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Relatório de Fluxo de Caixa."""
    try:
        # Verificar permissão de acesso à empresa
        await verificar_permissao_empresa(id_empresa, current_user, session)
        
        # Definir datas padrão se não informadas (últimos 30 dias)
        hoje = date.today()
        if not dataInicio:
            dataInicio = hoje - timedelta(days=30)
        if not dataFim:
            dataFim = hoje
            
        # Consulta base
        query_condicoes = [
            Lancamento.id_empresa == id_empresa,
            Lancamento.data_lancamento >= dataInicio,
            Lancamento.data_lancamento <= dataFim
        ]
        
        # Adicionar filtro por conta bancária se especificado
        if id_conta:
            query_condicoes.append(Lancamento.id_conta == id_conta)
        
        # Consulta para entradas (receitas)
        query_entradas = (
            select(
                Lancamento.data_lancamento.label("data"),
                func.sum(Lancamento.valor).label("valor")
            )
            .where(
                and_(
                    *query_condicoes,
                    Lancamento.tipo == "entrada"
                )
            )
            .group_by(Lancamento.data_lancamento)
        )
        
        # Consulta para saídas (despesas)
        query_saidas = (
            select(
                Lancamento.data_lancamento.label("data"),
                func.sum(Lancamento.valor).label("valor")
            )
            .where(
                and_(
                    *query_condicoes,
                    Lancamento.tipo == "saida"
                )
            )
            .group_by(Lancamento.data_lancamento)
        )
        
        # Executar consultas
        result_entradas = await session.execute(query_entradas)
        result_saidas = await session.execute(query_saidas)
        
        # Processar os resultados
        entradas_por_data = {row["data"]: float(row["valor"]) for row in result_entradas.mappings()}
        saidas_por_data = {row["data"]: float(row["valor"]) for row in result_saidas.mappings()}
        
        # Criar conjunto de todas as datas no período
        todas_datas = set()
        data_atual = dataInicio
        while data_atual <= dataFim:
            todas_datas.add(data_atual)
            data_atual += timedelta(days=1)
        
        # Gerar o relatório por dia
        fluxo_caixa = []
        saldo_acumulado = 0.0
        
        for data in sorted(todas_datas):
            entradas = entradas_por_data.get(data, 0.0)
            saidas = saidas_por_data.get(data, 0.0)
            saldo_dia = entradas - saidas
            saldo_acumulado += saldo_dia
            
            fluxo_caixa.append(
                RelatorioFluxoCaixa(
                    data=data.strftime("%Y-%m-%d"),
                    entradas=entradas,
                    saidas=saidas,
                    saldo_dia=saldo_dia,
                    saldo_acumulado=saldo_acumulado
                )
            )
        
        return fluxo_caixa
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar relatório de fluxo de caixa: {str(e)}"
        )

@router.get(
    "/dre",
    response_model=RelatorioDRE,
    summary="Relatório DRE",
    description="Retorna dados para o relatório DRE."
)
async def obter_relatorio_dre(
    id_empresa: UUID = Query(..., description="ID da empresa"),
    dataInicio: Optional[date] = Query(None, description="Data inicial do período"),
    dataFim: Optional[date] = Query(None, description="Data final do período"),
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Relatório DRE."""
    try:
        # Verificar permissão de acesso à empresa
        await verificar_permissao_empresa(id_empresa, current_user, session)
        
        # Definir datas padrão se não informadas (mês atual)
        hoje = date.today()
        if not dataInicio:
            dataInicio = date(hoje.year, hoje.month, 1)
        if not dataFim:
            if hoje.month == 12:
                dataFim = date(hoje.year, 12, 31)
            else:
                dataFim = date(hoje.year, hoje.month + 1, 1) - timedelta(days=1)
                
        # Consulta para receitas por categoria
        query_receitas = (
            select(
                Categoria.descricao.label("categoria"),
                func.sum(Lancamento.valor).label("valor")
            )
            .join(Lancamento, Lancamento.id_categoria == Categoria.id_categoria)
            .where(
                and_(
                    Lancamento.id_empresa == id_empresa,
                    Lancamento.data_lancamento >= dataInicio,
                    Lancamento.data_lancamento <= dataFim,
                    Lancamento.tipo == "entrada"
                )
            )
            .group_by(Categoria.descricao)
            .order_by(desc("valor"))
        )
        
        # Consulta para despesas por categoria
        query_despesas = (
            select(
                Categoria.descricao.label("categoria"),
                func.sum(Lancamento.valor).label("valor")
            )
            .join(Lancamento, Lancamento.id_categoria == Categoria.id_categoria)
            .where(
                and_(
                    Lancamento.id_empresa == id_empresa,
                    Lancamento.data_lancamento >= dataInicio,
                    Lancamento.data_lancamento <= dataFim,
                    Lancamento.tipo == "saida"
                )
            )
            .group_by(Categoria.descricao)
            .order_by(desc("valor"))
        )
        
        # Executar consultas
        result_receitas = await session.execute(query_receitas)
        result_despesas = await session.execute(query_despesas)
        
        # Processar resultados
        receitas = []
        despesas = []
        total_receitas = 0.0
        total_despesas = 0.0
        
        # Processar receitas
        for row in result_receitas.mappings():
            valor = float(row["valor"])
            receitas.append(
                CategoriaValor(
                    categoria=row["categoria"],
                    valor=valor
                )
            )
            total_receitas += valor
            
        # Processar despesas
        for row in result_despesas.mappings():
            valor = float(row["valor"])
            despesas.append(
                CategoriaValor(
                    categoria=row["categoria"],
                    valor=valor
                )
            )
            total_despesas += valor
            
        # Calcular lucro/prejuízo
        lucro_prejuizo = total_receitas - total_despesas
        
        # Montar resultado
        return RelatorioDRE(
            receitas=receitas,
            despesas=despesas,
            lucro_prejuizo=lucro_prejuizo
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar relatório DRE: {str(e)}"
        )

@router.get(
    "/ciclo-operacional",
    response_model=List[RelatorioCicloOperacional],
    summary="Relatório de Ciclo Operacional",
    description="Retorna dados para análise do ciclo operacional."
)
async def obter_relatorio_ciclo_operacional(
    id_empresa: UUID = Query(..., description="ID da empresa"),
    periodo: Optional[int] = Query(3, description="Período em meses para análise"),
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Relatório de Ciclo Operacional."""
    try:
        # Verificar permissão de acesso à empresa
        await verificar_permissao_empresa(id_empresa, current_user, session)
        
        # Definir período de análise (padrão: últimos 3 meses)
        hoje = date.today()
        meses_analise = periodo or 3
        data_inicio = date(hoje.year, hoje.month, 1) - timedelta(days=1)
        
        # Variáveis para armazenar os resultados
        resultados = []
        
        # Analisar cada mês
        for i in range(meses_analise):
            # Calcular primeiro e último dia do mês
            if i == 0:
                ultimo_dia_mes = data_inicio
            else:
                ultimo_dia_mes = date(data_inicio.year, data_inicio.month, 1) - timedelta(days=1)
                
            primeiro_dia_mes = date(ultimo_dia_mes.year, ultimo_dia_mes.month, 1)
            mes_str = primeiro_dia_mes.strftime("%B")
            ano = primeiro_dia_mes.year
            
            # 1. PME - Prazo Médio de Estocagem (dias entre compra e venda)
            # Simular cálculo - em um sistema real, seria baseado em histórico de compras e vendas
            # Na ausência de dados reais, estimar com base em lançamentos de compra e venda
            
            # 2. PMR - Prazo Médio de Recebimento (dias entre venda e recebimento)
            query_pmr = (
                select(
                    func.avg(
                        func.date_part('day', ParcelaVenda.data_recebimento - Venda.data_venda)
                    ).label("pmr")
                )
                .join(Venda, ParcelaVenda.id_venda == Venda.id_venda)
                .where(
                    and_(
                        Venda.id_empresa == id_empresa,
                        Venda.data_venda >= primeiro_dia_mes,
                        Venda.data_venda <= ultimo_dia_mes,
                        ParcelaVenda.data_recebimento.isnot(None),
                        ParcelaVenda.status == "recebido"
                    )
                )
            )
            
            # 3. PMP - Prazo Médio de Pagamento (dias entre compra e pagamento)
            query_pmp = (
                select(
                    func.avg(
                        func.date_part('day', Lancamento.data_pagamento - Lancamento.data_lancamento)
                    ).label("pmp")
                )
                .where(
                    and_(
                        Lancamento.id_empresa == id_empresa,
                        Lancamento.data_lancamento >= primeiro_dia_mes,
                        Lancamento.data_lancamento <= ultimo_dia_mes,
                        Lancamento.tipo == "saida",
                        Lancamento.data_pagamento.isnot(None),
                        Lancamento.status == "pago"
                    )
                )
            )
            
            # Executar consultas
            result_pmr = await session.execute(query_pmr)
            result_pmp = await session.execute(query_pmp)
            
            # Obter resultados
            pmr_valor = result_pmr.scalar() or 0
            pmp_valor = result_pmp.scalar() or 0
            
            # Estimar PME (na ausência de dados reais)
            pme_valor = 20  # Valor padrão em dias (ajustar conforme necessário)
            
            # Converter para inteiros
            pmr = int(pmr_valor)
            pmp = int(pmp_valor)
            pme = pme_valor
            
            # Calcular ciclo operacional e ciclo financeiro
            ciclo_operacional = pme + pmr
            ciclo_financeiro = ciclo_operacional - pmp
            
            # Adicionar ao resultado
            resultados.append(
                RelatorioCicloOperacional(
                    mes=mes_str,
                    ano=ano,
                    pme=pme,
                    pmr=pmr,
                    pmp=pmp,
                    ciclo_operacional=ciclo_operacional,
                    ciclo_financeiro=ciclo_financeiro
                )
            )
            
            # Avançar para o mês anterior
            data_inicio = primeiro_dia_mes - timedelta(days=1)
        
        return resultados
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar relatório de ciclo operacional: {str(e)}"
        ) 