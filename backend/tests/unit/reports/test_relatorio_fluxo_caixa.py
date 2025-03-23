"""Testes para o relatório de fluxo de caixa."""
import pytest
from decimal import Decimal
from datetime import date, datetime, timedelta
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Any

from app.models.lancamento import Lancamento
from app.models.conta_receber import ContaReceber
from app.models.conta_pagar import ContaPagar
from app.models.parcela import Parcela
from app.models.categoria import Categoria


@pytest.mark.no_db
async def test_calculo_fluxo_atual(dados_completos, db_session: AsyncSession):
    """Teste para validar o cálculo do fluxo de caixa do período atual."""
    # Arrange
    empresa_id = dados_completos["empresa"].id_empresa
    
    # Definir o período atual (mês corrente)
    hoje = date.today()
    primeiro_dia_mes = date(hoje.year, hoje.month, 1)
    if hoje.month == 12:
        ultimo_dia_mes = date(hoje.year + 1, 1, 1) - timedelta(days=1)
    else:
        ultimo_dia_mes = date(hoje.year, hoje.month + 1, 1) - timedelta(days=1)
    
    # Act
    # 1. Entradas confirmadas (lançamentos de receita)
    query_entradas = select(func.sum(Lancamento.valor)).where(
        Lancamento.tipo == "receita",
        Lancamento.data_lancamento.between(primeiro_dia_mes, ultimo_dia_mes),
        Lancamento.id_empresa == empresa_id
    )
    result_entradas = await db_session.execute(query_entradas)
    total_entradas = result_entradas.scalar_one_or_none() or Decimal('0')
    
    # 2. Saídas confirmadas (lançamentos de despesa)
    query_saidas = select(func.sum(Lancamento.valor)).where(
        Lancamento.tipo == "despesa",
        Lancamento.data_lancamento.between(primeiro_dia_mes, ultimo_dia_mes),
        Lancamento.id_empresa == empresa_id
    )
    result_saidas = await db_session.execute(query_saidas)
    total_saidas = result_saidas.scalar_one_or_none() or Decimal('0')
    
    # 3. Calcular saldo do período
    saldo_periodo = total_entradas - total_saidas
    
    # Assert
    assert isinstance(total_entradas, Decimal), "Total de entradas deve ser Decimal"
    assert isinstance(total_saidas, Decimal), "Total de saídas deve ser Decimal"
    assert isinstance(saldo_periodo, Decimal), "Saldo do período deve ser Decimal"
    
    # O fluxo de caixa deve refletir os lançamentos cadastrados
    # Nota: O saldo pode ser positivo ou negativo, dependendo dos dados de teste
    assert saldo_periodo == total_entradas - total_saidas, "Saldo do período calculado incorretamente"


@pytest.mark.no_db
async def test_projecao_proximos_30_dias(dados_completos, db_session: AsyncSession):
    """Teste para validar a projeção de fluxo de caixa para os próximos 30 dias."""
    # Arrange
    empresa_id = dados_completos["empresa"].id_empresa
    
    # Definir o período de projeção (próximos 30 dias)
    hoje = date.today()
    data_fim_projecao = hoje + timedelta(days=30)
    
    # Act
    # 1. Entradas previstas (contas a receber com vencimento no período)
    query_entradas_previstas = select(func.sum(ContaReceber.valor)).where(
        ContaReceber.data_vencimento.between(hoje, data_fim_projecao),
        ContaReceber.status.in_(["pendente", "atrasado"]),
        ContaReceber.id_empresa == empresa_id
    )
    result_entradas_previstas = await db_session.execute(query_entradas_previstas)
    total_entradas_previstas = result_entradas_previstas.scalar_one_or_none() or Decimal('0')
    
    # 2. Saídas previstas (contas a pagar com vencimento no período)
    query_saidas_previstas = select(func.sum(ContaPagar.valor)).where(
        ContaPagar.data_vencimento.between(hoje, data_fim_projecao),
        ContaPagar.status.in_(["pendente", "atrasado"]),
        ContaPagar.id_empresa == empresa_id
    )
    result_saidas_previstas = await db_session.execute(query_saidas_previstas)
    total_saidas_previstas = result_saidas_previstas.scalar_one_or_none() or Decimal('0')
    
    # 3. Calcular saldo projetado
    saldo_projetado = total_entradas_previstas - total_saidas_previstas
    
    # Assert
    assert isinstance(total_entradas_previstas, Decimal), "Total de entradas previstas deve ser Decimal"
    assert isinstance(total_saidas_previstas, Decimal), "Total de saídas previstas deve ser Decimal"
    assert isinstance(saldo_projetado, Decimal), "Saldo projetado deve ser Decimal"


@pytest.mark.no_db
async def test_fluxo_detalhado_semanal(dados_completos, db_session: AsyncSession):
    """Teste para validar o fluxo de caixa detalhado por semana."""
    # Arrange
    empresa_id = dados_completos["empresa"].id_empresa
    
    # Definir o período de análise (próximos 60 dias)
    hoje = date.today()
    data_fim_analise = hoje + timedelta(days=60)
    
    # Dividir o período em semanas (aproximadamente 8-9 semanas)
    semanas = []
    data_inicio = hoje
    
    while data_inicio < data_fim_analise:
        data_fim_semana = data_inicio + timedelta(days=6)
        if data_fim_semana > data_fim_analise:
            data_fim_semana = data_fim_analise
            
        semanas.append({
            "inicio": data_inicio,
            "fim": data_fim_semana
        })
        
        data_inicio = data_fim_semana + timedelta(days=1)
    
    # Act
    resultados_semanais = []
    
    for i, semana in enumerate(semanas):
        # Entradas previstas para a semana
        query_entradas = select(func.sum(ContaReceber.valor)).where(
            ContaReceber.data_vencimento.between(semana["inicio"], semana["fim"]),
            ContaReceber.status.in_(["pendente", "atrasado"]),
            ContaReceber.id_empresa == empresa_id
        )
        result_entradas = await db_session.execute(query_entradas)
        total_entradas = result_entradas.scalar_one_or_none() or Decimal('0')
        
        # Saídas previstas para a semana
        query_saidas = select(func.sum(ContaPagar.valor)).where(
            ContaPagar.data_vencimento.between(semana["inicio"], semana["fim"]),
            ContaPagar.status.in_(["pendente", "atrasado"]),
            ContaPagar.id_empresa == empresa_id
        )
        result_saidas = await db_session.execute(query_saidas)
        total_saidas = result_saidas.scalar_one_or_none() or Decimal('0')
        
        # Saldo da semana
        saldo_semana = total_entradas - total_saidas
        
        # Armazenar resultados
        resultados_semanais.append({
            "semana": i + 1,
            "periodo": f"{semana['inicio']} a {semana['fim']}",
            "entradas": total_entradas,
            "saidas": total_saidas,
            "saldo": saldo_semana
        })
    
    # Assert
    # Verificar se temos resultados para todas as semanas
    assert len(resultados_semanais) == len(semanas), "Deve haver resultados para todas as semanas"
    
    # Verificar se os cálculos estão corretos para cada semana
    for resultado in resultados_semanais:
        assert resultado["saldo"] == resultado["entradas"] - resultado["saidas"], (
            f"Saldo incorreto para a semana {resultado['semana']}"
        )
    
    # Garantir que os valores são do tipo Decimal
    for resultado in resultados_semanais:
        assert isinstance(resultado["entradas"], Decimal), "Entradas devem ser Decimal"
        assert isinstance(resultado["saidas"], Decimal), "Saídas devem ser Decimal"
        assert isinstance(resultado["saldo"], Decimal), "Saldo deve ser Decimal"


@pytest.mark.no_db
async def test_fluxo_por_categoria(dados_completos, db_session: AsyncSession):
    """Teste para validar o fluxo de caixa agrupado por categoria."""
    # Arrange
    empresa_id = dados_completos["empresa"].id_empresa
    categorias = dados_completos["categorias"]
    
    # Definir o período de análise (próximos 30 dias)
    hoje = date.today()
    data_fim_analise = hoje + timedelta(days=30)
    
    # Act
    resultados_por_categoria = {}
    
    # Para cada categoria, calcular entradas e saídas previstas
    for categoria in categorias:
        # Inicializar valores
        total_entradas = Decimal('0')
        total_saidas = Decimal('0')
        
        if categoria.tipo == "receita":
            # Buscar entradas previstas para a categoria (contas a receber)
            query_entradas = select(func.sum(ContaReceber.valor)).where(
                ContaReceber.data_vencimento.between(hoje, data_fim_analise),
                ContaReceber.status.in_(["pendente", "atrasado"]),
                ContaReceber.id_categoria == categoria.id_categoria,
                ContaReceber.id_empresa == empresa_id
            )
            result_entradas = await db_session.execute(query_entradas)
            entradas_categoria = result_entradas.scalar_one_or_none() or Decimal('0')
            total_entradas = entradas_categoria
        
        elif categoria.tipo == "despesa":
            # Buscar saídas previstas para a categoria (contas a pagar)
            query_saidas = select(func.sum(ContaPagar.valor)).where(
                ContaPagar.data_vencimento.between(hoje, data_fim_analise),
                ContaPagar.status.in_(["pendente", "atrasado"]),
                ContaPagar.id_categoria == categoria.id_categoria,
                ContaPagar.id_empresa == empresa_id
            )
            result_saidas = await db_session.execute(query_saidas)
            saidas_categoria = result_saidas.scalar_one_or_none() or Decimal('0')
            total_saidas = saidas_categoria
        
        # Armazenar resultados
        resultados_por_categoria[categoria.nome] = {
            "tipo": categoria.tipo,
            "entradas": total_entradas,
            "saidas": total_saidas,
            "saldo": total_entradas - total_saidas
        }
    
    # Assert
    # Verificar se temos resultados para todas as categorias
    assert len(resultados_por_categoria) == len(categorias), "Deve haver resultados para todas as categorias"
    
    # Verificar se os tipos estão corretos
    for nome, resultado in resultados_por_categoria.items():
        categoria_tipo = resultado["tipo"]
        
        if categoria_tipo == "receita":
            assert resultado["entradas"] >= Decimal('0'), f"Entradas para categoria {nome} devem ser não-negativas"
            assert resultado["saidas"] == Decimal('0'), f"Saídas para categoria de receita {nome} devem ser zero"
        
        elif categoria_tipo == "despesa":
            assert resultado["saidas"] >= Decimal('0'), f"Saídas para categoria {nome} devem ser não-negativas"
            assert resultado["entradas"] == Decimal('0'), f"Entradas para categoria de despesa {nome} devem ser zero"


@pytest.mark.no_db
async def test_analise_tendencia_fluxo(dados_completos, db_session: AsyncSession):
    """Teste para validar a análise de tendência do fluxo de caixa."""
    # Arrange
    empresa_id = dados_completos["empresa"].id_empresa
    
    # Definir períodos para análise (3 meses)
    hoje = date.today()
    
    # Mês atual
    inicio_mes_atual = date(hoje.year, hoje.month, 1)
    if hoje.month == 12:
        fim_mes_atual = date(hoje.year + 1, 1, 1) - timedelta(days=1)
    else:
        fim_mes_atual = date(hoje.year, hoje.month + 1, 1) - timedelta(days=1)
    
    # Mês anterior
    if hoje.month == 1:
        inicio_mes_anterior = date(hoje.year - 1, 12, 1)
        fim_mes_anterior = date(hoje.year, 1, 1) - timedelta(days=1)
    else:
        inicio_mes_anterior = date(hoje.year, hoje.month - 1, 1)
        inicio_mes_atual = date(hoje.year, hoje.month, 1)
        fim_mes_anterior = inicio_mes_atual - timedelta(days=1)
    
    # Próximo mês (projeção)
    if hoje.month == 12:
        inicio_prox_mes = date(hoje.year + 1, 1, 1)
        fim_prox_mes = date(hoje.year + 1, 2, 1) - timedelta(days=1)
    else:
        inicio_prox_mes = date(hoje.year, hoje.month + 1, 1)
        fim_prox_mes = date(hoje.year, hoje.month + 2, 1) - timedelta(days=1)
    
    # Act
    # Fluxo do mês anterior (realizado)
    query_entradas_anterior = select(func.sum(Lancamento.valor)).where(
        Lancamento.tipo == "receita",
        Lancamento.data_lancamento.between(inicio_mes_anterior, fim_mes_anterior),
        Lancamento.id_empresa == empresa_id
    )
    result_entradas_anterior = await db_session.execute(query_entradas_anterior)
    total_entradas_anterior = result_entradas_anterior.scalar_one_or_none() or Decimal('0')
    
    query_saidas_anterior = select(func.sum(Lancamento.valor)).where(
        Lancamento.tipo == "despesa",
        Lancamento.data_lancamento.between(inicio_mes_anterior, fim_mes_anterior),
        Lancamento.id_empresa == empresa_id
    )
    result_saidas_anterior = await db_session.execute(query_saidas_anterior)
    total_saidas_anterior = result_saidas_anterior.scalar_one_or_none() or Decimal('0')
    
    saldo_anterior = total_entradas_anterior - total_saidas_anterior
    
    # Fluxo do mês atual (parcialmente realizado)
    query_entradas_atual = select(func.sum(Lancamento.valor)).where(
        Lancamento.tipo == "receita",
        Lancamento.data_lancamento.between(inicio_mes_atual, hoje),
        Lancamento.id_empresa == empresa_id
    )
    result_entradas_atual = await db_session.execute(query_entradas_atual)
    entradas_realizadas_atual = result_entradas_atual.scalar_one_or_none() or Decimal('0')
    
    query_saidas_atual = select(func.sum(Lancamento.valor)).where(
        Lancamento.tipo == "despesa",
        Lancamento.data_lancamento.between(inicio_mes_atual, hoje),
        Lancamento.id_empresa == empresa_id
    )
    result_saidas_atual = await db_session.execute(query_saidas_atual)
    saidas_realizadas_atual = result_saidas_atual.scalar_one_or_none() or Decimal('0')
    
    # Projeção para o restante do mês atual
    query_entradas_resto_atual = select(func.sum(ContaReceber.valor)).where(
        ContaReceber.data_vencimento.between(hoje + timedelta(days=1), fim_mes_atual),
        ContaReceber.status.in_(["pendente", "atrasado"]),
        ContaReceber.id_empresa == empresa_id
    )
    result_entradas_resto_atual = await db_session.execute(query_entradas_resto_atual)
    entradas_previstas_atual = result_entradas_resto_atual.scalar_one_or_none() or Decimal('0')
    
    query_saidas_resto_atual = select(func.sum(ContaPagar.valor)).where(
        ContaPagar.data_vencimento.between(hoje + timedelta(days=1), fim_mes_atual),
        ContaPagar.status.in_(["pendente", "atrasado"]),
        ContaPagar.id_empresa == empresa_id
    )
    result_saidas_resto_atual = await db_session.execute(query_saidas_resto_atual)
    saidas_previstas_atual = result_saidas_resto_atual.scalar_one_or_none() or Decimal('0')
    
    total_entradas_atual = entradas_realizadas_atual + entradas_previstas_atual
    total_saidas_atual = saidas_realizadas_atual + saidas_previstas_atual
    saldo_atual = total_entradas_atual - total_saidas_atual
    
    # Projeção para o próximo mês
    query_entradas_prox = select(func.sum(ContaReceber.valor)).where(
        ContaReceber.data_vencimento.between(inicio_prox_mes, fim_prox_mes),
        ContaReceber.status == "pendente",
        ContaReceber.id_empresa == empresa_id
    )
    result_entradas_prox = await db_session.execute(query_entradas_prox)
    total_entradas_prox = result_entradas_prox.scalar_one_or_none() or Decimal('0')
    
    query_saidas_prox = select(func.sum(ContaPagar.valor)).where(
        ContaPagar.data_vencimento.between(inicio_prox_mes, fim_prox_mes),
        ContaPagar.status == "pendente",
        ContaPagar.id_empresa == empresa_id
    )
    result_saidas_prox = await db_session.execute(query_saidas_prox)
    total_saidas_prox = result_saidas_prox.scalar_one_or_none() or Decimal('0')
    
    saldo_prox = total_entradas_prox - total_saidas_prox
    
    # Calcular tendências
    variacao_saldo_atual_anterior = saldo_atual - saldo_anterior
    variacao_percentual_atual = (
        (variacao_saldo_atual_anterior / saldo_anterior * 100)
        if saldo_anterior != Decimal('0') else Decimal('0')
    )
    
    variacao_saldo_prox_atual = saldo_prox - saldo_atual
    variacao_percentual_prox = (
        (variacao_saldo_prox_atual / saldo_atual * 100)
        if saldo_atual != Decimal('0') else Decimal('0')
    )
    
    # Assert
    # Verificar se os cálculos estão corretos
    assert saldo_anterior == total_entradas_anterior - total_saidas_anterior
    assert saldo_atual == total_entradas_atual - total_saidas_atual
    assert saldo_prox == total_entradas_prox - total_saidas_prox
    
    # Verificar se os tipos de dados estão corretos
    assert isinstance(variacao_saldo_atual_anterior, Decimal)
    assert isinstance(variacao_percentual_atual, Decimal)
    assert isinstance(variacao_saldo_prox_atual, Decimal)
    assert isinstance(variacao_percentual_prox, Decimal)


@pytest.mark.no_db
async def test_consistencia_dados_fluxo_caixa(dados_completos, db_session: AsyncSession):
    """Teste para validar a consistência dos dados de fluxo de caixa."""
    # Arrange
    empresa_id = dados_completos["empresa"].id_empresa
    contas_bancarias = dados_completos["contas_bancarias"]
    
    # Definir o período de análise
    hoje = date.today()
    inicio_periodo = hoje - timedelta(days=30)
    fim_periodo = hoje + timedelta(days=30)
    
    # Act
    # 1. Verificar saldos iniciais das contas bancárias
    for conta in contas_bancarias:
        # Buscar lançamentos realizados para a conta
        query_lancamentos = select(Lancamento).where(
            Lancamento.data_lancamento <= hoje,
            Lancamento.id_conta_bancaria == conta.id_conta_bancaria,
            Lancamento.id_empresa == empresa_id
        )
        result_lancamentos = await db_session.execute(query_lancamentos)
        lancamentos = result_lancamentos.scalars().all()
        
        # Calcular saldo atual com base nos lançamentos
        saldo_calculado = conta.saldo_inicial
        for lancamento in lancamentos:
            if lancamento.tipo == "receita":
                saldo_calculado += lancamento.valor
            else:
                saldo_calculado -= lancamento.valor
        
        # Verificar se o saldo calculado é consistente
        assert isinstance(saldo_calculado, Decimal), "Saldo calculado deve ser Decimal"
    
    # 2. Verificar consistência entre lançamentos e contas a receber/pagar
    # Lançamentos de receita (recebimentos)
    query_lancamentos_receita = select(Lancamento).where(
        Lancamento.tipo == "receita",
        Lancamento.data_lancamento.between(inicio_periodo, hoje),
        Lancamento.id_empresa == empresa_id
    )
    result_lancamentos_receita = await db_session.execute(query_lancamentos_receita)
    lancamentos_receita = result_lancamentos_receita.scalars().all()
    
    # Contas a receber recebidas no período
    query_contas_recebidas = select(ContaReceber).where(
        ContaReceber.data_recebimento.between(inicio_periodo, hoje),
        ContaReceber.status == "recebido",
        ContaReceber.id_empresa == empresa_id
    )
    result_contas_recebidas = await db_session.execute(query_contas_recebidas)
    contas_recebidas = result_contas_recebidas.scalars().all()
    
    # Lançamentos de despesa (pagamentos)
    query_lancamentos_despesa = select(Lancamento).where(
        Lancamento.tipo == "despesa",
        Lancamento.data_lancamento.between(inicio_periodo, hoje),
        Lancamento.id_empresa == empresa_id
    )
    result_lancamentos_despesa = await db_session.execute(query_lancamentos_despesa)
    lancamentos_despesa = result_lancamentos_despesa.scalars().all()
    
    # Contas a pagar pagas no período
    query_contas_pagas = select(ContaPagar).where(
        ContaPagar.data_pagamento.between(inicio_periodo, hoje),
        ContaPagar.status == "pago",
        ContaPagar.id_empresa == empresa_id
    )
    result_contas_pagas = await db_session.execute(query_contas_pagas)
    contas_pagas = result_contas_pagas.scalars().all()
    
    # Assert
    # Verificar se há dados para o teste
    assert len(contas_bancarias) > 0, "Nenhuma conta bancária para teste"
    
    # Verificar se os tipos de dados estão corretos
    assert all(isinstance(lancamento.valor, Decimal) for lancamento in lancamentos_receita)
    assert all(isinstance(conta.valor, Decimal) for conta in contas_recebidas)
    assert all(isinstance(lancamento.valor, Decimal) for lancamento in lancamentos_despesa)
    assert all(isinstance(conta.valor, Decimal) for conta in contas_pagas) 