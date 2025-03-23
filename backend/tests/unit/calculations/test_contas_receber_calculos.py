"""Testes para cálculos financeiros relacionados a contas a receber."""
import pytest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, AsyncMock, patch
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.unit
async def test_antecipacao_recebivel():
    """
    Testa o cálculo de antecipação de recebíveis.
    
    A antecipação deve:
    1. Aplicar uma taxa de desconto sobre o valor do título
    2. Calcular o valor líquido a receber
    3. Considerar o prazo entre a antecipação e o vencimento
    """
    # Arrange
    valor_titulo = Decimal("5000.00")
    taxa_desconto_mensal = Decimal("0.025")  # 2.5% ao mês
    data_vencimento = date.today() + timedelta(days=60)
    data_antecipacao = date.today()
    
    # Act
    dias_antecipacao = (data_vencimento - data_antecipacao).days
    meses_antecipacao = dias_antecipacao / 30  # Aproximação de meses
    
    taxa_proporcional = taxa_desconto_mensal * Decimal(str(meses_antecipacao))
    valor_desconto = valor_titulo * taxa_proporcional
    valor_liquido = valor_titulo - valor_desconto
    
    # Assert
    assert dias_antecipacao == 60
    assert meses_antecipacao == 2
    assert taxa_proporcional == Decimal("0.05")  # 5% para 2 meses
    assert valor_desconto == Decimal("250.00")
    assert valor_liquido == Decimal("4750.00")

@pytest.mark.unit
async def test_recebimento_parcial():
    """
    Testa o recebimento parcial de uma conta.
    
    O recebimento parcial deve:
    1. Registrar o valor parcial recebido
    2. Calcular o saldo a receber
    3. Possivelmente gerar uma nova conta para o saldo restante
    """
    # Arrange
    valor_original = Decimal("3000.00")
    valor_recebido = Decimal("1800.00")
    data_recebimento_parcial = date.today()
    data_vencimento_original = date.today() + timedelta(days=15)
    
    # Act
    valor_restante = valor_original - valor_recebido
    
    # Simula a baixa parcial da conta e criação de uma nova para o saldo
    conta_original = {
        "valor": valor_original,
        "valor_recebido": valor_recebido,
        "data_recebimento_parcial": data_recebimento_parcial,
        "status": "parcialmente_recebido"
    }
    
    nova_conta = {
        "valor": valor_restante,
        "data_vencimento": data_vencimento_original,  # Mantém a data de vencimento original
        "referencia_conta_original": "id_original",
        "status": "pendente"
    }
    
    # Assert
    assert valor_restante == Decimal("1200.00")
    assert conta_original["status"] == "parcialmente_recebido"
    assert conta_original["valor_recebido"] == valor_recebido
    assert nova_conta["valor"] == valor_restante
    assert nova_conta["data_vencimento"] == data_vencimento_original

@pytest.mark.unit
async def test_recebimento_valor_diferente():
    """
    Testa o recebimento com valor diferente do esperado.
    
    O recebimento pode ser:
    1. Com valor inferior - registro de recebimento parcial
    2. Com valor superior - registro de valor adicional (taxa, multa, etc.)
    """
    # Arrange - Cenário 1: Valor inferior
    valor_titulo_1 = Decimal("2000.00")
    valor_recebido_1 = Decimal("1800.00")
    
    # Arrange - Cenário 2: Valor superior
    valor_titulo_2 = Decimal("2000.00")
    valor_recebido_2 = Decimal("2150.00")
    
    # Act - Cenário 1: Valor inferior
    diferenca_1 = valor_recebido_1 - valor_titulo_1
    tipo_recebimento_1 = "parcial" if diferenca_1 < 0 else "integral"
    saldo_restante_1 = abs(diferenca_1) if diferenca_1 < 0 else Decimal("0")
    
    # Act - Cenário 2: Valor superior
    diferenca_2 = valor_recebido_2 - valor_titulo_2
    tipo_recebimento_2 = "integral_com_adicional" if diferenca_2 > 0 else "integral"
    valor_adicional_2 = diferenca_2 if diferenca_2 > 0 else Decimal("0")
    
    # Assert - Cenário 1: Valor inferior
    assert diferenca_1 == Decimal("-200.00")
    assert tipo_recebimento_1 == "parcial"
    assert saldo_restante_1 == Decimal("200.00")
    
    # Assert - Cenário 2: Valor superior
    assert diferenca_2 == Decimal("150.00")
    assert tipo_recebimento_2 == "integral_com_adicional"
    assert valor_adicional_2 == Decimal("150.00")

@pytest.mark.unit
async def test_desconto_pagamento_antecipado():
    """
    Testa o desconto por pagamento antecipado de uma conta a receber.
    
    O desconto deve:
    1. Ser calculado proporcionalmente aos dias de antecipação
    2. Reduzir o valor a receber
    """
    # Arrange
    valor_titulo = Decimal("4000.00")
    taxa_desconto_diaria = Decimal("0.0005")  # 0.05% ao dia
    data_vencimento = date.today() + timedelta(days=20)
    data_recebimento = date.today()
    
    # Act
    dias_antecipacao = (data_vencimento - data_recebimento).days
    valor_desconto = valor_titulo * taxa_desconto_diaria * dias_antecipacao
    valor_liquido = valor_titulo - valor_desconto
    
    # Assert
    assert dias_antecipacao == 20
    assert valor_desconto == Decimal("40.00")
    assert valor_liquido == Decimal("3960.00")

@pytest.mark.unit
async def test_cobranca_juros_atraso():
    """
    Testa a cobrança de juros por atraso em uma conta a receber.
    
    A cobrança deve:
    1. Calcular os dias de atraso
    2. Aplicar taxa de juros e multa conforme configurado
    3. Aumentar o valor a receber
    """
    # Arrange
    valor_titulo = Decimal("3500.00")
    taxa_juros_diaria = Decimal("0.001")  # 0.1% ao dia
    taxa_multa = Decimal("0.02")  # 2% (multa fixa)
    data_vencimento = date.today() - timedelta(days=12)  # Vencida há 12 dias
    data_recebimento = date.today()
    
    # Act
    dias_atraso = (data_recebimento - data_vencimento).days
    
    valor_multa = valor_titulo * taxa_multa if dias_atraso > 0 else Decimal("0")
    valor_juros = valor_titulo * taxa_juros_diaria * dias_atraso if dias_atraso > 0 else Decimal("0")
    valor_total = valor_titulo + valor_multa + valor_juros
    
    # Assert
    assert dias_atraso == 12
    assert valor_multa == Decimal("70.00")
    assert valor_juros == Decimal("42.00")
    assert valor_total == Decimal("3612.00")

@pytest.mark.unit
async def test_renegociacao_conta_receber():
    """
    Testa a renegociação de uma conta a receber.
    
    A renegociação deve:
    1. Eventualmente aplicar desconto sobre juros/multa
    2. Gerar novo parcelamento
    3. Atualizar datas de vencimento
    """
    # Arrange
    valor_original = Decimal("5000.00")
    valor_juros_multa = Decimal("600.00")
    percentual_desconto = Decimal("0.30")  # 30% de desconto nos juros e multa
    novo_num_parcelas = 4
    data_base = date.today()
    
    # Act
    valor_desconto = valor_juros_multa * percentual_desconto
    valor_juros_multa_final = valor_juros_multa - valor_desconto
    valor_total_renegociado = valor_original + valor_juros_multa_final
    
    # Calcular novas parcelas
    valor_parcela_base = valor_total_renegociado / novo_num_parcelas
    valor_parcela = round(valor_parcela_base, 2)
    
    parcelas = []
    for i in range(1, novo_num_parcelas + 1):
        # Última parcela ajustada para garantir soma exata
        if i == novo_num_parcelas:
            valor_parcela_atual = valor_total_renegociado - sum(p["valor"] for p in parcelas)
        else:
            valor_parcela_atual = valor_parcela
        
        parcelas.append({
            "numero": i,
            "valor": valor_parcela_atual,
            "data_vencimento": data_base + timedelta(days=30 * i)
        })
    
    # Assert
    assert valor_desconto == Decimal("180.00")
    assert valor_juros_multa_final == Decimal("420.00")
    assert valor_total_renegociado == Decimal("5420.00")
    assert len(parcelas) == novo_num_parcelas
    assert sum(p["valor"] for p in parcelas) == valor_total_renegociado
    
    # Verificar que as parcelas têm o valor correto
    assert parcelas[0]["valor"] == Decimal("1355.00") 
    assert parcelas[1]["valor"] == Decimal("1355.00")
    assert parcelas[2]["valor"] == Decimal("1355.00")
    assert parcelas[3]["valor"] == Decimal("1355.00")

@pytest.mark.unit
async def test_calculo_taxa_inadimplencia():
    """
    Testa o cálculo da taxa de inadimplência de contas a receber.
    
    O cálculo deve:
    1. Identificar contas vencidas
    2. Calcular percentual de inadimplência em relação ao total
    3. Agrupar por período (30, 60, 90 dias, etc)
    """
    # Arrange
    contas = [
        {"id": 1, "valor": Decimal("1000.00"), "data_vencimento": date.today() - timedelta(days=10), "status": "vencida"},
        {"id": 2, "valor": Decimal("2000.00"), "data_vencimento": date.today() - timedelta(days=45), "status": "vencida"},
        {"id": 3, "valor": Decimal("1500.00"), "data_vencimento": date.today() - timedelta(days=95), "status": "vencida"},
        {"id": 4, "valor": Decimal("3000.00"), "data_vencimento": date.today() + timedelta(days=15), "status": "pendente"},
        {"id": 5, "valor": Decimal("2500.00"), "data_vencimento": date.today() - timedelta(days=5), "status": "recebida"}
    ]
    
    data_referencia = date.today()
    
    # Act
    total_contas = sum(c["valor"] for c in contas if c["status"] in ["vencida", "pendente", "recebida"])
    total_vencidas = sum(c["valor"] for c in contas if c["status"] == "vencida")
    
    # Agrupar por período de vencimento
    ate_30_dias = sum(c["valor"] for c in contas 
                     if c["status"] == "vencida" 
                     and 0 < (data_referencia - c["data_vencimento"]).days <= 30)
    
    de_31_a_60_dias = sum(c["valor"] for c in contas 
                         if c["status"] == "vencida" 
                         and 30 < (data_referencia - c["data_vencimento"]).days <= 60)
    
    de_61_a_90_dias = sum(c["valor"] for c in contas 
                         if c["status"] == "vencida" 
                         and 60 < (data_referencia - c["data_vencimento"]).days <= 90)
    
    acima_90_dias = sum(c["valor"] for c in contas 
                       if c["status"] == "vencida" 
                       and (data_referencia - c["data_vencimento"]).days > 90)
    
    taxa_inadimplencia = total_vencidas / total_contas if total_contas > 0 else Decimal("0")
    
    # Assert
    assert total_contas == Decimal("10000.00")
    assert total_vencidas == Decimal("4500.00")
    assert taxa_inadimplencia == Decimal("0.45")  # 45% de inadimplência
    
    assert ate_30_dias == Decimal("1000.00")
    assert de_31_a_60_dias == Decimal("2000.00")
    assert de_61_a_90_dias == Decimal("0")
    assert acima_90_dias == Decimal("1500.00")

@pytest.mark.unit
async def test_calculo_media_dias_recebimento():
    """
    Testa o cálculo da média de dias para recebimento.
    
    O cálculo deve:
    1. Considerar o prazo entre emissão/venda e recebimento efetivo
    2. Calcular a média ponderada pelo valor
    """
    # Arrange
    recebimentos = [
        {"valor": Decimal("1000.00"), "dias_para_receber": 15},
        {"valor": Decimal("2000.00"), "dias_para_receber": 30},
        {"valor": Decimal("1500.00"), "dias_para_receber": 45},
        {"valor": Decimal("3000.00"), "dias_para_receber": 60}
    ]
    
    # Act
    total_valor = sum(r["valor"] for r in recebimentos)
    soma_ponderada = sum(r["valor"] * Decimal(str(r["dias_para_receber"])) for r in recebimentos)
    
    prazo_medio = soma_ponderada / total_valor if total_valor > 0 else Decimal("0")
    
    # Assert
    assert total_valor == Decimal("7500.00")
    # (1000*15 + 2000*30 + 1500*45 + 3000*60) / 7500 = 42
    assert prazo_medio == Decimal("42") 