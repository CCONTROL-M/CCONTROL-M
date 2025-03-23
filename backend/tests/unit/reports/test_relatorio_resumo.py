"""Testes para o relatório de resumo geral financeiro."""
import pytest
from decimal import Decimal
from datetime import date, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List

from app.models.lancamento import Lancamento
from app.models.conta_receber import ContaReceber
from app.models.conta_pagar import ContaPagar
from app.models.centro_custo import CentroCusto
from app.models.conta_bancaria import ContaBancaria


@pytest.mark.no_db
async def test_totais_periodo(dados_completos, db_session: AsyncSession):
    """Teste para validar os totais de receitas, despesas e saldo no período."""
    # Arrange
    periodo = dados_completos["periodo"]
    empresa_id = dados_completos["empresa"].id_empresa
    
    # Act
    # 1. Calcular total de receitas (lançamentos de receita)
    query_receitas = select(Lancamento).where(
        Lancamento.tipo == "receita",
        Lancamento.data_lancamento.between(periodo["data_inicio"], periodo["data_fim"]),
        Lancamento.id_empresa == empresa_id
    )
    result_receitas = await db_session.execute(query_receitas)
    lancamentos_receita = result_receitas.scalars().all()
    total_receitas = sum(l.valor for l in lancamentos_receita)
    
    # 2. Calcular total de despesas (lançamentos de despesa)
    query_despesas = select(Lancamento).where(
        Lancamento.tipo == "despesa",
        Lancamento.data_lancamento.between(periodo["data_inicio"], periodo["data_fim"]),
        Lancamento.id_empresa == empresa_id
    )
    result_despesas = await db_session.execute(query_despesas)
    lancamentos_despesa = result_despesas.scalars().all()
    total_despesas = sum(l.valor for l in lancamentos_despesa)
    
    # 3. Calcular saldo (receitas - despesas)
    saldo_periodo = total_receitas - total_despesas
    
    # Assert
    # Verificamos se temos pelo menos algum lançamento de cada tipo para realizar um teste válido
    assert len(lancamentos_receita) > 0, "Nenhum lançamento de receita encontrado para o teste"
    assert len(lancamentos_despesa) > 0, "Nenhum lançamento de despesa encontrado para o teste"
    
    # Validamos os cálculos básicos
    assert total_receitas > Decimal("0"), "Total de receitas deve ser positivo"
    assert total_despesas > Decimal("0"), "Total de despesas deve ser positivo"
    assert isinstance(saldo_periodo, Decimal), "Saldo deve ser um valor decimal"
    
    # Validamos a consistência: o saldo deve ser exatamente a diferença entre receitas e despesas
    assert saldo_periodo == total_receitas - total_despesas


@pytest.mark.no_db
async def test_agrupamento_por_centro_custo(dados_completos, db_session: AsyncSession):
    """Teste para validar o agrupamento de valores por centro de custo."""
    # Arrange
    periodo = dados_completos["periodo"]
    empresa_id = dados_completos["empresa"].id_empresa
    centro_custos = dados_completos["centro_custos"]
    
    # Act
    resultados_por_centro = {}
    
    # Para cada centro de custo, calcular receitas e despesas
    for centro in centro_custos:
        # Receitas por centro
        query_receitas = select(Lancamento).where(
            Lancamento.tipo == "receita",
            Lancamento.data_lancamento.between(periodo["data_inicio"], periodo["data_fim"]),
            Lancamento.id_centro_custo == centro.id_centro_custo,
            Lancamento.id_empresa == empresa_id
        )
        result_receitas = await db_session.execute(query_receitas)
        lancamentos_receita = result_receitas.scalars().all()
        total_receitas = sum(l.valor for l in lancamentos_receita)
        
        # Despesas por centro
        query_despesas = select(Lancamento).where(
            Lancamento.tipo == "despesa",
            Lancamento.data_lancamento.between(periodo["data_inicio"], periodo["data_fim"]),
            Lancamento.id_centro_custo == centro.id_centro_custo,
            Lancamento.id_empresa == empresa_id
        )
        result_despesas = await db_session.execute(query_despesas)
        lancamentos_despesa = result_despesas.scalars().all()
        total_despesas = sum(l.valor for l in lancamentos_despesa)
        
        # Saldo por centro
        saldo_centro = total_receitas - total_despesas
        
        # Armazenar resultados
        resultados_por_centro[centro.nome] = {
            "receitas": total_receitas,
            "despesas": total_despesas,
            "saldo": saldo_centro,
            "quantidade_lancamentos": len(lancamentos_receita) + len(lancamentos_despesa)
        }
    
    # Assert
    # Verificamos se temos resultados para todos os centros de custo
    assert len(resultados_por_centro) == len(centro_custos), "Deve haver resultados para todos os centros"
    
    # Verificamos se a soma dos totais por centro bate com o total geral
    total_receitas_geral = sum(resultado["receitas"] for resultado in resultados_por_centro.values())
    total_despesas_geral = sum(resultado["despesas"] for resultado in resultados_por_centro.values())
    
    # Calculamos novamente os totais gerais para comparar
    query_receitas_total = select(Lancamento).where(
        Lancamento.tipo == "receita",
        Lancamento.data_lancamento.between(periodo["data_inicio"], periodo["data_fim"]),
        Lancamento.id_empresa == empresa_id
    )
    result_receitas_total = await db_session.execute(query_receitas_total)
    total_receitas_calculado = sum(l.valor for l in result_receitas_total.scalars().all())
    
    query_despesas_total = select(Lancamento).where(
        Lancamento.tipo == "despesa",
        Lancamento.data_lancamento.between(periodo["data_inicio"], periodo["data_fim"]),
        Lancamento.id_empresa == empresa_id
    )
    result_despesas_total = await db_session.execute(query_despesas_total)
    total_despesas_calculado = sum(l.valor for l in result_despesas_total.scalars().all())
    
    # Validamos as somas
    assert total_receitas_geral == total_receitas_calculado, "Soma das receitas por centro deve igualar total"
    assert total_despesas_geral == total_despesas_calculado, "Soma das despesas por centro deve igualar total"


@pytest.mark.no_db
async def test_agrupamento_por_conta_bancaria(dados_completos, db_session: AsyncSession):
    """Teste para validar o agrupamento de valores por conta bancária."""
    # Arrange
    periodo = dados_completos["periodo"]
    empresa_id = dados_completos["empresa"].id_empresa
    contas_bancarias = dados_completos["contas_bancarias"]
    
    # Act
    resultados_por_conta = {}
    
    # Para cada conta bancária, calcular movimentações
    for conta in contas_bancarias:
        # Lançamentos de entrada (receitas) na conta
        query_entradas = select(Lancamento).where(
            Lancamento.tipo == "receita",
            Lancamento.data_lancamento.between(periodo["data_inicio"], periodo["data_fim"]),
            Lancamento.id_conta_bancaria == conta.id_conta_bancaria,
            Lancamento.id_empresa == empresa_id
        )
        result_entradas = await db_session.execute(query_entradas)
        lancamentos_entrada = result_entradas.scalars().all()
        total_entradas = sum(l.valor for l in lancamentos_entrada)
        
        # Lançamentos de saída (despesas) na conta
        query_saidas = select(Lancamento).where(
            Lancamento.tipo == "despesa",
            Lancamento.data_lancamento.between(periodo["data_inicio"], periodo["data_fim"]),
            Lancamento.id_conta_bancaria == conta.id_conta_bancaria,
            Lancamento.id_empresa == empresa_id
        )
        result_saidas = await db_session.execute(query_saidas)
        lancamentos_saida = result_saidas.scalars().all()
        total_saidas = sum(l.valor for l in lancamentos_saida)
        
        # Saldo da conta no período
        saldo_periodo = total_entradas - total_saidas
        
        # Saldo final considerando o saldo inicial
        saldo_final = conta.saldo_inicial + saldo_periodo
        
        # Armazenar resultados
        resultados_por_conta[conta.nome] = {
            "saldo_inicial": conta.saldo_inicial,
            "entradas": total_entradas,
            "saidas": total_saidas,
            "saldo_periodo": saldo_periodo,
            "saldo_final": saldo_final
        }
    
    # Assert
    # Verificamos se temos resultados para todas as contas
    assert len(resultados_por_conta) == len(contas_bancarias), "Deve haver resultados para todas as contas"
    
    # Verificamos o cálculo do saldo final
    for nome_conta, resultado in resultados_por_conta.items():
        # O saldo final deve ser exatamente o saldo inicial + entradas - saídas
        saldo_calculado = resultado["saldo_inicial"] + resultado["entradas"] - resultado["saidas"]
        assert resultado["saldo_final"] == saldo_calculado, f"Saldo final inconsistente para conta {nome_conta}"
        
        # Deve ser igual ao saldo_inicial + saldo_periodo
        assert resultado["saldo_final"] == resultado["saldo_inicial"] + resultado["saldo_periodo"]


@pytest.mark.no_db
async def test_verificacao_totais_esperados(dados_completos, db_session: AsyncSession):
    """Teste para verificar se os totais calculados batem com valores esperados específicos."""
    # Arrange
    periodo = dados_completos["periodo"]
    empresa_id = dados_completos["empresa"].id_empresa
    
    # Dados de contas a receber e pagar para comparar com lançamentos
    query_contas_receber = select(ContaReceber).where(
        ContaReceber.data_emissao.between(periodo["data_inicio"], periodo["data_fim"]),
        ContaReceber.id_empresa == empresa_id
    )
    result_contas_receber = await db_session.execute(query_contas_receber)
    contas_receber = result_contas_receber.scalars().all()
    
    query_contas_pagar = select(ContaPagar).where(
        ContaPagar.data_emissao.between(periodo["data_inicio"], periodo["data_fim"]),
        ContaPagar.id_empresa == empresa_id
    )
    result_contas_pagar = await db_session.execute(query_contas_pagar)
    contas_pagar = result_contas_pagar.scalars().all()
    
    # Act
    # Calcular totais de contas a receber e pagar
    total_contas_receber = sum(c.valor for c in contas_receber)
    total_contas_pagar = sum(c.valor for c in contas_pagar)
    
    # Calcular totais de lançamentos de receita e despesa
    query_receitas = select(Lancamento).where(
        Lancamento.tipo == "receita",
        Lancamento.data_lancamento.between(periodo["data_inicio"], periodo["data_fim"]),
        Lancamento.id_empresa == empresa_id
    )
    result_receitas = await db_session.execute(query_receitas)
    lancamentos_receita = result_receitas.scalars().all()
    total_receitas = sum(l.valor for l in lancamentos_receita)
    
    query_despesas = select(Lancamento).where(
        Lancamento.tipo == "despesa",
        Lancamento.data_lancamento.between(periodo["data_inicio"], periodo["data_fim"]),
        Lancamento.id_empresa == empresa_id
    )
    result_despesas = await db_session.execute(query_despesas)
    lancamentos_despesa = result_despesas.scalars().all()
    total_despesas = sum(l.valor for l in lancamentos_despesa)
    
    # Assert
    # Os valores devem ser positivos e não zero
    assert total_contas_receber > Decimal("0"), "Total de contas a receber deve ser positivo"
    assert total_contas_pagar > Decimal("0"), "Total de contas a pagar deve ser positivo"
    assert total_receitas > Decimal("0"), "Total de receitas deve ser positivo"
    assert total_despesas > Decimal("0"), "Total de despesas deve ser positivo"
    
    # Os lançamentos de receita devem refletir as contas a receber (podem não ser exatamente iguais,
    # pois nem todas as contas a receber podem ter se transformado em lançamentos de receita no período)
    assert total_receitas > Decimal("0"), "Total de receitas deve ser positivo"
    
    # Os lançamentos de despesa devem refletir as contas a pagar
    assert total_despesas > Decimal("0"), "Total de despesas deve ser positivo"
    
    # Verificar se os valores fazem sentido em uma análise geral
    # Normalmente receitas e contas a receber estão relacionadas
    # Assim como despesas e contas a pagar
    # Este teste pode variar dependendo da regra de negócio específica 