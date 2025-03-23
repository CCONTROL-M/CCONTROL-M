"""Testes para cálculos financeiros relacionados a contas a pagar."""
import pytest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, AsyncMock, patch
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.unit
async def test_calculo_juros_simples_atraso():
    """
    Testa o cálculo de juros simples por atraso em uma conta a pagar.
    
    O cálculo deve:
    1. Identificar os dias de atraso
    2. Aplicar a taxa de juros diária
    3. Adicionar ao valor original
    """
    # Arrange
    valor_original = Decimal("1500.00")
    taxa_juros_diaria = Decimal("0.001")  # 0.1% ao dia
    data_vencimento = date.today() - timedelta(days=15)  # Vencida há 15 dias
    data_pagamento = date.today()
    
    # Act
    dias_atraso = (data_pagamento - data_vencimento).days
    valor_juros = valor_original * taxa_juros_diaria * dias_atraso
    valor_total = valor_original + valor_juros
    
    # Assert
    assert dias_atraso == 15
    assert valor_juros == Decimal("22.50")
    assert valor_total == Decimal("1522.50")

@pytest.mark.unit
async def test_calculo_multa_atraso():
    """
    Testa o cálculo de multa por atraso em uma conta a pagar.
    
    O cálculo deve:
    1. Verificar se há atraso
    2. Aplicar a taxa de multa fixa sobre o valor original
    3. Adicionar ao valor com juros
    """
    # Arrange
    valor_original = Decimal("1200.00")
    taxa_multa = Decimal("0.02")  # 2% de multa
    taxa_juros_diaria = Decimal("0.001")  # 0.1% ao dia
    data_vencimento = date.today() - timedelta(days=10)  # Vencida há 10 dias
    data_pagamento = date.today()
    
    # Act
    dias_atraso = (data_pagamento - data_vencimento).days
    
    valor_multa = Decimal("0")
    valor_juros = Decimal("0")
    
    if dias_atraso > 0:
        valor_multa = valor_original * taxa_multa
        valor_juros = valor_original * taxa_juros_diaria * dias_atraso
    
    valor_total = valor_original + valor_multa + valor_juros
    
    # Assert
    assert dias_atraso == 10
    assert valor_multa == Decimal("24.00")
    assert valor_juros == Decimal("12.00")
    assert valor_total == Decimal("1236.00")

@pytest.mark.unit
async def test_negociacao_divida():
    """
    Testa a negociação de uma dívida em atraso.
    
    A negociação pode incluir:
    1. Desconto no valor de multa e juros
    2. Novo parcelamento do valor
    3. Recálculo das datas de vencimento
    """
    # Arrange
    valor_original = Decimal("3000.00")
    valor_juros_multa = Decimal("500.00")
    percentual_desconto = Decimal("0.40")  # 40% de desconto nos juros e multa
    novo_num_parcelas = 3
    data_base = date.today()
    
    # Act
    valor_desconto = valor_juros_multa * percentual_desconto
    valor_juros_multa_final = valor_juros_multa - valor_desconto
    valor_total_negociado = valor_original + valor_juros_multa_final
    
    # Calcular novas parcelas
    valor_parcela_base = valor_total_negociado / novo_num_parcelas
    valor_parcela = round(valor_parcela_base, 2)
    
    parcelas = []
    for i in range(1, novo_num_parcelas + 1):
        # Última parcela ajustada para garantir soma exata
        if i == novo_num_parcelas:
            valor_parcela_atual = valor_total_negociado - sum(p["valor"] for p in parcelas)
        else:
            valor_parcela_atual = valor_parcela
        
        parcelas.append({
            "numero": i,
            "valor": valor_parcela_atual,
            "data_vencimento": data_base + timedelta(days=30 * i)
        })
    
    # Assert
    assert valor_desconto == Decimal("200.00")
    assert valor_juros_multa_final == Decimal("300.00")
    assert valor_total_negociado == Decimal("3300.00")
    assert len(parcelas) == novo_num_parcelas
    assert sum(p["valor"] for p in parcelas) == valor_total_negociado
    
    # Verificar parcelas específicas
    assert parcelas[0]["valor"] == Decimal("1100.00")
    assert parcelas[1]["valor"] == Decimal("1100.00")
    assert parcelas[2]["valor"] == Decimal("1100.00")

@pytest.mark.unit
async def test_pagamento_parcial():
    """
    Testa o pagamento parcial de uma conta a pagar.
    
    O pagamento parcial deve:
    1. Registrar o valor pago
    2. Calcular o saldo devedor
    3. Possivelmente gerar uma nova conta para o saldo restante
    """
    # Arrange
    valor_original = Decimal("2500.00")
    valor_pagamento = Decimal("1000.00")
    data_pagamento_parcial = date.today()
    data_vencimento_original = date.today() - timedelta(days=5)
    nova_data_vencimento = date.today() + timedelta(days=30)
    
    # Act
    valor_restante = valor_original - valor_pagamento
    
    # Simula a quitação da conta original e criação de uma nova para o saldo
    conta_original = {
        "valor": valor_original,
        "valor_pago": valor_pagamento,
        "data_pagamento_parcial": data_pagamento_parcial,
        "status": "parcialmente_pago"
    }
    
    nova_conta = {
        "valor": valor_restante,
        "data_vencimento": nova_data_vencimento,
        "referencia_conta_original": "id_original",
        "status": "pendente"
    }
    
    # Assert
    assert valor_restante == Decimal("1500.00")
    assert conta_original["status"] == "parcialmente_pago"
    assert conta_original["valor_pago"] == valor_pagamento
    assert nova_conta["valor"] == valor_restante
    assert nova_conta["data_vencimento"] == nova_data_vencimento

@pytest.mark.unit
async def test_reagendamento_parcelas():
    """
    Testa o reagendamento de parcelas de uma conta a pagar.
    
    O reagendamento deve:
    1. Atualizar as datas de vencimento
    2. Possivelmente aplicar juros ou taxas de reagendamento
    3. Manter as demais condições da dívida
    """
    # Arrange
    parcelas_originais = [
        {"numero": 1, "valor": Decimal("500.00"), "data_vencimento": date.today() - timedelta(days=15), "status": "vencida"},
        {"numero": 2, "valor": Decimal("500.00"), "data_vencimento": date.today() + timedelta(days=15), "status": "pendente"},
        {"numero": 3, "valor": Decimal("500.00"), "data_vencimento": date.today() + timedelta(days=45), "status": "pendente"},
    ]
    
    taxa_reagendamento = Decimal("0.01")  # 1% de taxa por reagendamento
    dias_adicionar = 30  # Adicionar 30 dias a cada vencimento
    
    # Act
    parcelas_reagendadas = []
    
    for parcela in parcelas_originais:
        valor_reagendamento = parcela["valor"] * taxa_reagendamento
        nova_data = parcela["data_vencimento"] + timedelta(days=dias_adicionar)
        
        parcelas_reagendadas.append({
            "numero": parcela["numero"],
            "valor_original": parcela["valor"],
            "valor_taxa": valor_reagendamento,
            "valor_total": parcela["valor"] + valor_reagendamento,
            "data_vencimento_original": parcela["data_vencimento"],
            "data_vencimento_nova": nova_data,
            "status": "reagendada"
        })
    
    # Assert
    assert len(parcelas_reagendadas) == len(parcelas_originais)
    
    # Verificar primeira parcela
    assert parcelas_reagendadas[0]["valor_taxa"] == Decimal("5.00")
    assert parcelas_reagendadas[0]["valor_total"] == Decimal("505.00")
    assert (parcelas_reagendadas[0]["data_vencimento_nova"] - parcelas_reagendadas[0]["data_vencimento_original"]).days == 30
    
    # Verificar que todas as parcelas foram reagendadas
    for p in parcelas_reagendadas:
        assert p["status"] == "reagendada"
        assert p["valor_total"] > p["valor_original"]

@pytest.mark.unit
async def test_calculo_imposto_retido():
    """
    Testa o cálculo de impostos retidos em uma conta a pagar.
    
    O cálculo deve:
    1. Aplicar as alíquotas corretas (IRRF, ISS, etc.)
    2. Calcular o valor líquido a pagar após retenções
    3. Registrar os impostos retidos separadamente
    """
    # Arrange
    valor_bruto = Decimal("5000.00")
    aliquota_irrf = Decimal("0.015")  # 1.5% IRRF
    aliquota_iss = Decimal("0.05")  # 5% ISS
    aliquota_inss = Decimal("0.11")  # 11% INSS
    
    # Act
    valor_irrf = valor_bruto * aliquota_irrf
    valor_iss = valor_bruto * aliquota_iss
    valor_inss = valor_bruto * aliquota_inss
    
    total_retencoes = valor_irrf + valor_iss + valor_inss
    valor_liquido = valor_bruto - total_retencoes
    
    retencoes = {
        "irrf": valor_irrf,
        "iss": valor_iss,
        "inss": valor_inss,
        "total": total_retencoes
    }
    
    # Assert
    assert valor_irrf == Decimal("75.00")
    assert valor_iss == Decimal("250.00")
    assert valor_inss == Decimal("550.00")
    assert total_retencoes == Decimal("875.00")
    assert valor_liquido == Decimal("4125.00")
    assert retencoes["total"] == total_retencoes

@pytest.mark.unit
async def test_calculo_priorizacao_pagamentos():
    """
    Testa a priorização de pagamentos quando há recursos limitados.
    
    A priorização deve:
    1. Ordenar as contas por critérios (vencimento, valor, importância)
    2. Alocar os recursos disponíveis conforme a prioridade
    3. Identificar contas que não podem ser pagas
    """
    # Arrange
    saldo_disponivel = Decimal("3000.00")
    
    contas = [
        {"id": 1, "valor": Decimal("1000.00"), "data_vencimento": date.today() - timedelta(days=5), "prioridade": "alta"},
        {"id": 2, "valor": Decimal("1500.00"), "data_vencimento": date.today(), "prioridade": "media"},
        {"id": 3, "valor": Decimal("800.00"), "data_vencimento": date.today() + timedelta(days=2), "prioridade": "media"},
        {"id": 4, "valor": Decimal("2000.00"), "data_vencimento": date.today() + timedelta(days=7), "prioridade": "baixa"},
    ]
    
    # Act
    # Ordenar por: 1º prioridade, 2º data de vencimento (mais antigas primeiro), 3º valor (menores primeiro)
    contas_ordenadas = sorted(contas, key=lambda x: (
        0 if x["prioridade"] == "alta" else (1 if x["prioridade"] == "media" else 2),
        x["data_vencimento"],
        x["valor"]
    ))
    
    contas_a_pagar = []
    valor_total_a_pagar = Decimal("0")
    
    for conta in contas_ordenadas:
        if valor_total_a_pagar + conta["valor"] <= saldo_disponivel:
            contas_a_pagar.append(conta)
            valor_total_a_pagar += conta["valor"]
    
    contas_nao_pagas = [conta for conta in contas if conta not in contas_a_pagar]
    
    # Assert
    assert len(contas_a_pagar) == 3
    assert valor_total_a_pagar == Decimal("3300.00")  # Não é possível pagar todas
    assert len(contas_nao_pagas) == 1
    
    # Verificar que a conta de prioridade baixa ficou de fora
    assert contas_nao_pagas[0]["prioridade"] == "baixa"
    assert contas_nao_pagas[0]["id"] == 4 