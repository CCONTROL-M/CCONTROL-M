"""Testes para cálculos financeiros relacionados a fluxo de caixa e categorias."""
import pytest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, AsyncMock, patch
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.unit
async def test_previsao_saldo_periodo():
    """
    Testa a previsão de saldo para um período futuro.
    
    O teste deve validar:
    1. Saldo inicial
    2. Projeção considerando receitas e despesas previstas
    3. Cálculo de saldo final previsto para cada período
    """
    # Arrange
    saldo_inicial = Decimal("10000.00")
    periodo_inicial = date.today()
    periodo_final = date.today() + timedelta(days=90)
    
    movimentacoes = [
        {"tipo": "receita", "valor": Decimal("5000.00"), "data": date.today() + timedelta(days=15)},
        {"tipo": "despesa", "valor": Decimal("3000.00"), "data": date.today() + timedelta(days=20)},
        {"tipo": "receita", "valor": Decimal("2000.00"), "data": date.today() + timedelta(days=30)},
        {"tipo": "despesa", "valor": Decimal("1500.00"), "data": date.today() + timedelta(days=45)},
        {"tipo": "receita", "valor": Decimal("3500.00"), "data": date.today() + timedelta(days=60)},
        {"tipo": "despesa", "valor": Decimal("4000.00"), "data": date.today() + timedelta(days=75)},
        {"tipo": "receita", "valor": Decimal("1000.00"), "data": date.today() + timedelta(days=85)},
    ]
    
    # Act
    # Agrupar por mês para análise mensal
    meses = {}
    saldo_acumulado = saldo_inicial
    
    for mov in sorted(movimentacoes, key=lambda x: x["data"]):
        valor = mov["valor"] if mov["tipo"] == "receita" else -mov["valor"]
        mes_ano = (mov["data"].year, mov["data"].month)
        
        if mes_ano not in meses:
            meses[mes_ano] = {
                "receitas": Decimal("0"),
                "despesas": Decimal("0"),
                "saldo_inicial": saldo_acumulado,
                "saldo_final": saldo_acumulado,
                "mes": mov["data"].month,
                "ano": mov["data"].year
            }
        
        if mov["tipo"] == "receita":
            meses[mes_ano]["receitas"] += mov["valor"]
        else:
            meses[mes_ano]["despesas"] += mov["valor"]
        
        meses[mes_ano]["saldo_final"] += valor
        saldo_acumulado += valor
    
    # Ordenar meses cronologicamente
    meses_ordenados = [meses[mes_ano] for mes_ano in sorted(meses.keys())]
    
    # Calcular saldo final de cada período ajustando o acumulado
    for i in range(1, len(meses_ordenados)):
        meses_ordenados[i]["saldo_inicial"] = meses_ordenados[i-1]["saldo_final"]
    
    # Assert
    assert len(meses_ordenados) > 0
    
    # Verificar saldo final previsto para o último mês
    ultimo_mes = meses_ordenados[-1]
    saldo_final_previsto = ultimo_mes["saldo_final"]
    
    # Cálculo manual para verificação
    total_receitas = sum(mov["valor"] for mov in movimentacoes if mov["tipo"] == "receita")
    total_despesas = sum(mov["valor"] for mov in movimentacoes if mov["tipo"] == "despesa")
    saldo_calculado = saldo_inicial + total_receitas - total_despesas
    
    assert saldo_final_previsto == saldo_calculado
    assert saldo_final_previsto == Decimal("13000.00")  # 10000 + 5000 + 2000 + 3500 + 1000 - 3000 - 1500 - 4000
    
    # Verificar primeiro mês
    if len(meses_ordenados) >= 1:
        assert meses_ordenados[0]["saldo_inicial"] == saldo_inicial
        assert meses_ordenados[0]["receitas"] > Decimal("0")
        assert meses_ordenados[0]["despesas"] > Decimal("0")

@pytest.mark.unit
async def test_conciliacao_valor_diferente():
    """
    Testa a conciliação de lançamentos quando o valor difere do esperado.
    
    O teste deve validar:
    1. Identificação de divergência entre valor previsto e efetivo
    2. Ajuste da diferença
    3. Registro de receita/despesa adicional para equalizar
    """
    # Arrange
    lancamento = {
        "id": 1,
        "tipo": "receita",
        "descricao": "Recebimento Cliente X",
        "valor_previsto": Decimal("1200.00"),
        "valor_efetivo": Decimal("1150.00"),
        "data_prevista": date.today() - timedelta(days=5),
        "data_efetiva": date.today(),
        "conciliado": False
    }
    
    # Act
    diferenca = lancamento["valor_efetivo"] - lancamento["valor_previsto"]
    precisa_ajuste = diferenca != 0
    
    tipo_ajuste = "despesa" if diferenca < 0 else "receita"
    valor_ajuste = abs(diferenca)
    motivo_ajuste = "Valor menor que o previsto" if diferenca < 0 else "Valor maior que o previsto"
    
    # Simular conciliação
    lancamento_conciliado = {**lancamento, "conciliado": True}
    
    ajuste = {
        "id_lancamento_origem": lancamento["id"],
        "tipo": tipo_ajuste,
        "descricao": f"Ajuste de conciliação: {motivo_ajuste}",
        "valor": valor_ajuste,
        "data": date.today()
    }
    
    # Assert
    assert precisa_ajuste is True
    assert diferenca == Decimal("-50.00")
    assert tipo_ajuste == "despesa"
    assert valor_ajuste == Decimal("50.00")
    assert lancamento_conciliado["conciliado"] is True
    assert ajuste["valor"] == Decimal("50.00")
    assert ajuste["tipo"] == "despesa"

@pytest.mark.unit
async def test_agrupamento_por_categoria():
    """
    Testa o agrupamento de lançamentos por categoria.
    
    O teste deve validar:
    1. Soma correta de valores por categoria
    2. Cálculo percentual de cada categoria em relação ao total
    3. Ordenação por valor (do maior para o menor)
    """
    # Arrange
    lancamentos = [
        {"id": 1, "valor": Decimal("500.00"), "categoria": "Salários", "tipo": "despesa"},
        {"id": 2, "valor": Decimal("200.00"), "categoria": "Alimentação", "tipo": "despesa"},
        {"id": 3, "valor": Decimal("300.00"), "categoria": "Transporte", "tipo": "despesa"},
        {"id": 4, "valor": Decimal("150.00"), "categoria": "Alimentação", "tipo": "despesa"},
        {"id": 5, "valor": Decimal("450.00"), "categoria": "Salários", "tipo": "despesa"},
        {"id": 6, "valor": Decimal("100.00"), "categoria": "Material de Escritório", "tipo": "despesa"},
        {"id": 7, "valor": Decimal("250.00"), "categoria": "Transporte", "tipo": "despesa"},
    ]
    
    # Act
    agrupamento = {}
    valor_total = Decimal("0")
    
    for lanc in lancamentos:
        categoria = lanc["categoria"]
        valor = lanc["valor"]
        
        if categoria not in agrupamento:
            agrupamento[categoria] = {
                "categoria": categoria,
                "valor": Decimal("0"),
                "quantidade": 0
            }
        
        agrupamento[categoria]["valor"] += valor
        agrupamento[categoria]["quantidade"] += 1
        valor_total += valor
    
    # Calcular percentuais
    for cat in agrupamento.values():
        cat["percentual"] = (cat["valor"] / valor_total) * 100 if valor_total > 0 else Decimal("0")
    
    # Ordenar por valor (maior para menor)
    categorias_ordenadas = sorted(
        agrupamento.values(),
        key=lambda x: x["valor"],
        reverse=True
    )
    
    # Assert
    assert len(agrupamento) == 4  # Quatro categorias distintas
    assert valor_total == Decimal("1950.00")
    
    # Verificar categoria com maior valor (Salários)
    assert categorias_ordenadas[0]["categoria"] == "Salários"
    assert categorias_ordenadas[0]["valor"] == Decimal("950.00")
    assert categorias_ordenadas[0]["quantidade"] == 2
    assert categorias_ordenadas[0]["percentual"] == Decimal("950.00") / Decimal("1950.00") * 100
    
    # Verificar categoria com menor valor (Material de Escritório)
    assert categorias_ordenadas[3]["categoria"] == "Material de Escritório"
    assert categorias_ordenadas[3]["valor"] == Decimal("100.00")
    assert categorias_ordenadas[3]["quantidade"] == 1
    assert categorias_ordenadas[3]["percentual"] == Decimal("100.00") / Decimal("1950.00") * 100
    
    # Verificar soma dos percentuais
    soma_percentuais = sum(cat["percentual"] for cat in agrupamento.values())
    assert round(soma_percentuais, 2) == Decimal("100.00")

@pytest.mark.unit
async def test_agrupamento_centro_custo():
    """
    Testa o agrupamento de lançamentos por centro de custo.
    
    O teste deve validar:
    1. Totais corretos por centro de custo
    2. Divisão entre receitas e despesas
    3. Cálculo do resultado (receitas - despesas)
    """
    # Arrange
    lancamentos = [
        {"id": 1, "valor": Decimal("2000.00"), "centro_custo": "Administrativo", "tipo": "receita"},
        {"id": 2, "valor": Decimal("1500.00"), "centro_custo": "Administrativo", "tipo": "despesa"},
        {"id": 3, "valor": Decimal("3000.00"), "centro_custo": "Comercial", "tipo": "receita"},
        {"id": 4, "valor": Decimal("1800.00"), "centro_custo": "Comercial", "tipo": "despesa"},
        {"id": 5, "valor": Decimal("1000.00"), "centro_custo": "Produção", "tipo": "receita"},
        {"id": 6, "valor": Decimal("1200.00"), "centro_custo": "Produção", "tipo": "despesa"},
        {"id": 7, "valor": Decimal("500.00"), "centro_custo": "Administrativo", "tipo": "receita"},
    ]
    
    # Act
    agrupamento = {}
    
    for lanc in lancamentos:
        centro = lanc["centro_custo"]
        valor = lanc["valor"]
        tipo = lanc["tipo"]
        
        if centro not in agrupamento:
            agrupamento[centro] = {
                "centro_custo": centro,
                "receitas": Decimal("0"),
                "despesas": Decimal("0"),
                "resultado": Decimal("0")
            }
        
        if tipo == "receita":
            agrupamento[centro]["receitas"] += valor
        else:
            agrupamento[centro]["despesas"] += valor
        
        # Recalcular resultado
        agrupamento[centro]["resultado"] = agrupamento[centro]["receitas"] - agrupamento[centro]["despesas"]
    
    # Ordenar por resultado (maior para menor)
    centros_ordenados = sorted(
        agrupamento.values(),
        key=lambda x: x["resultado"],
        reverse=True
    )
    
    # Calcular totais
    total_receitas = sum(centro["receitas"] for centro in agrupamento.values())
    total_despesas = sum(centro["despesas"] for centro in agrupamento.values())
    resultado_geral = total_receitas - total_despesas
    
    # Assert
    assert len(agrupamento) == 3  # Três centros de custo distintos
    
    # Verificar centro de custo com melhor resultado (Comercial)
    assert centros_ordenados[0]["centro_custo"] == "Comercial"
    assert centros_ordenados[0]["receitas"] == Decimal("3000.00")
    assert centros_ordenados[0]["despesas"] == Decimal("1800.00")
    assert centros_ordenados[0]["resultado"] == Decimal("1200.00")
    
    # Verificar centro de custo com pior resultado (Produção)
    assert centros_ordenados[2]["centro_custo"] == "Produção"
    assert centros_ordenados[2]["receitas"] == Decimal("1000.00")
    assert centros_ordenados[2]["despesas"] == Decimal("1200.00")
    assert centros_ordenados[2]["resultado"] == Decimal("-200.00")
    
    # Verificar totais
    assert total_receitas == Decimal("6500.00")
    assert total_despesas == Decimal("4500.00")
    assert resultado_geral == Decimal("2000.00")

@pytest.mark.unit
async def test_agrupamento_conta_bancaria():
    """
    Testa o agrupamento de lançamentos por conta bancária.
    
    O teste deve validar:
    1. Saldo inicial e final por conta
    2. Movimentação (entradas e saídas)
    3. Consistência entre saldo inicial + movimentação = saldo final
    """
    # Arrange
    contas = [
        {"id": 1, "descricao": "Conta Principal", "saldo_inicial": Decimal("5000.00")},
        {"id": 2, "descricao": "Conta Reserva", "saldo_inicial": Decimal("10000.00")},
        {"id": 3, "descricao": "Conta Investimentos", "saldo_inicial": Decimal("15000.00")},
    ]
    
    lancamentos = [
        {"id": 101, "valor": Decimal("2000.00"), "tipo": "receita", "conta_id": 1},
        {"id": 102, "valor": Decimal("1500.00"), "tipo": "despesa", "conta_id": 1},
        {"id": 103, "valor": Decimal("3000.00"), "tipo": "receita", "conta_id": 2},
        {"id": 104, "valor": Decimal("800.00"), "tipo": "despesa", "conta_id": 2},
        {"id": 105, "valor": Decimal("5000.00"), "tipo": "receita", "conta_id": 3},
        {"id": 106, "valor": Decimal("1200.00"), "tipo": "despesa", "conta_id": 3},
        {"id": 107, "valor": Decimal("1000.00"), "tipo": "receita", "conta_id": 1},
        {"id": 108, "valor": Decimal("700.00"), "tipo": "despesa", "conta_id": 1},
    ]
    
    # Act
    # Preparar dicionário de contas com saldo inicial
    dict_contas = {conta["id"]: {
        "id": conta["id"],
        "descricao": conta["descricao"],
        "saldo_inicial": conta["saldo_inicial"],
        "entradas": Decimal("0"),
        "saidas": Decimal("0"),
        "saldo_final": conta["saldo_inicial"]
    } for conta in contas}
    
    # Processar lançamentos
    for lanc in lancamentos:
        conta_id = lanc["conta_id"]
        valor = lanc["valor"]
        tipo = lanc["tipo"]
        
        if tipo == "receita":
            dict_contas[conta_id]["entradas"] += valor
            dict_contas[conta_id]["saldo_final"] += valor
        else:
            dict_contas[conta_id]["saidas"] += valor
            dict_contas[conta_id]["saldo_final"] -= valor
    
    # Ordenar por saldo final (maior para menor)
    contas_ordenadas = sorted(
        dict_contas.values(),
        key=lambda x: x["saldo_final"],
        reverse=True
    )
    
    # Calcular totais
    total_saldo_inicial = sum(conta["saldo_inicial"] for conta in dict_contas.values())
    total_entradas = sum(conta["entradas"] for conta in dict_contas.values())
    total_saidas = sum(conta["saidas"] for conta in dict_contas.values())
    total_saldo_final = sum(conta["saldo_final"] for conta in dict_contas.values())
    
    # Assert
    assert len(dict_contas) == 3  # Três contas bancárias
    
    # Verificar conta com maior saldo final (Conta Investimentos)
    assert contas_ordenadas[0]["descricao"] == "Conta Investimentos"
    assert contas_ordenadas[0]["saldo_inicial"] == Decimal("15000.00")
    assert contas_ordenadas[0]["entradas"] == Decimal("5000.00")
    assert contas_ordenadas[0]["saidas"] == Decimal("1200.00")
    assert contas_ordenadas[0]["saldo_final"] == Decimal("18800.00")  # 15000 + 5000 - 1200
    
    # Verificar totais
    assert total_saldo_inicial == Decimal("30000.00")
    assert total_entradas == Decimal("11000.00")
    assert total_saidas == Decimal("4200.00")
    assert total_saldo_final == Decimal("36800.00")  # 30000 + 11000 - 4200
    
    # Verificar consistência
    for conta in dict_contas.values():
        assert conta["saldo_final"] == conta["saldo_inicial"] + conta["entradas"] - conta["saidas"]

@pytest.mark.unit
async def test_transferencia_entre_contas():
    """
    Testa a transferência de valores entre contas bancárias.
    
    O teste deve validar:
    1. Redução do saldo na conta de origem
    2. Aumento do saldo na conta de destino
    3. Consistência entre os saldos antes e depois
    """
    # Arrange
    conta_origem = {
        "id": 1,
        "descricao": "Conta Corrente",
        "saldo": Decimal("5000.00")
    }
    
    conta_destino = {
        "id": 2,
        "descricao": "Conta Investimento",
        "saldo": Decimal("10000.00")
    }
    
    valor_transferencia = Decimal("2000.00")
    data_transferencia = date.today()
    
    # Act
    # Registrar saída na conta de origem
    lancamento_saida = {
        "id": 101,
        "conta_id": conta_origem["id"],
        "tipo": "transferencia_saida",
        "valor": valor_transferencia,
        "data": data_transferencia,
        "descricao": f"Transferência para {conta_destino['descricao']}"
    }
    
    # Registrar entrada na conta de destino
    lancamento_entrada = {
        "id": 102,
        "conta_id": conta_destino["id"],
        "tipo": "transferencia_entrada",
        "valor": valor_transferencia,
        "data": data_transferencia,
        "descricao": f"Transferência de {conta_origem['descricao']}"
    }
    
    # Atualizar saldos
    saldo_origem_antes = conta_origem["saldo"]
    saldo_destino_antes = conta_destino["saldo"]
    
    conta_origem["saldo"] -= valor_transferencia
    conta_destino["saldo"] += valor_transferencia
    
    saldo_origem_depois = conta_origem["saldo"]
    saldo_destino_depois = conta_destino["saldo"]
    
    # Assert
    assert saldo_origem_antes == Decimal("5000.00")
    assert saldo_destino_antes == Decimal("10000.00")
    
    assert saldo_origem_depois == Decimal("3000.00")
    assert saldo_destino_depois == Decimal("12000.00")
    
    assert lancamento_saida["valor"] == valor_transferencia
    assert lancamento_entrada["valor"] == valor_transferencia
    
    # Verificar que a soma dos saldos permanece inalterada
    assert saldo_origem_antes + saldo_destino_antes == saldo_origem_depois + saldo_destino_depois 