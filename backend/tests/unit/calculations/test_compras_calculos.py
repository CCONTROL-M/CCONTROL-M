"""Testes para cálculos financeiros relacionados a compras."""
import pytest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, AsyncMock, patch
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.unit
async def test_calculo_compra_a_prazo():
    """
    Testa o cálculo de uma compra a prazo.
    
    Uma compra a prazo deve:
    1. Calcular corretamente o valor total dos itens
    2. Dividir em parcelas adequadamente
    3. Ajustar a última parcela para garantir que a soma seja exata
    """
    # Arrange
    itens = [
        {"descricao": "Item 1", "quantidade": 5, "valor_unitario": Decimal("120.00")},
        {"descricao": "Item 2", "quantidade": 3, "valor_unitario": Decimal("80.00")}
    ]
    num_parcelas = 4
    
    # Act
    valor_total = sum(Decimal(str(item["quantidade"])) * Decimal(str(item["valor_unitario"])) for item in itens)
    valor_parcela_base = valor_total / num_parcelas
    valor_parcela = round(valor_parcela_base, 2)
    
    parcelas = []
    for i in range(1, num_parcelas + 1):
        # Última parcela ajustada para garantir soma exata
        if i == num_parcelas:
            valor_parcela_atual = valor_total - sum(p["valor"] for p in parcelas)
        else:
            valor_parcela_atual = valor_parcela
        
        parcelas.append({
            "numero": i,
            "valor": valor_parcela_atual
        })
    
    # Assert
    assert valor_total == Decimal("840.00")
    assert len(parcelas) == num_parcelas
    assert sum(p["valor"] for p in parcelas) == valor_total
    assert parcelas[0]["valor"] == Decimal("210.00")
    assert parcelas[1]["valor"] == Decimal("210.00")
    assert parcelas[2]["valor"] == Decimal("210.00")
    assert parcelas[3]["valor"] == Decimal("210.00")

@pytest.mark.unit
async def test_calculo_prazo_medio_ponderado():
    """
    Testa o cálculo do prazo médio ponderado de pagamento de uma compra.
    
    O prazo médio deve considerar:
    1. O valor de cada parcela
    2. O prazo (em dias) de cada parcela
    3. Calcular a média ponderada pelo valor
    """
    # Arrange
    parcelas = [
        {"valor": Decimal("200.00"), "prazo_dias": 30},
        {"valor": Decimal("300.00"), "prazo_dias": 60},
        {"valor": Decimal("500.00"), "prazo_dias": 90}
    ]
    valor_total = sum(p["valor"] for p in parcelas)
    
    # Act
    prazo_medio = sum(p["valor"] * Decimal(str(p["prazo_dias"])) for p in parcelas) / valor_total
    
    # Assert
    assert valor_total == Decimal("1000.00")
    # (200 * 30 + 300 * 60 + 500 * 90) / 1000 = 69
    assert prazo_medio == Decimal("69")

@pytest.mark.unit
async def test_calculo_variacao_cambial_compra():
    """
    Testa o cálculo de variação cambial em uma compra internacional.
    
    Uma compra em moeda estrangeira deve:
    1. Registrar o valor na moeda original e na moeda local
    2. Calcular a variação cambial na data de pagamento
    3. Ajustar o valor final com base na variação
    """
    # Arrange
    valor_compra_usd = Decimal("1000.00")
    taxa_cambio_compra = Decimal("5.20")  # R$ por USD no momento da compra
    taxa_cambio_pagamento = Decimal("5.35")  # R$ por USD no momento do pagamento
    
    # Act
    valor_compra_brl = valor_compra_usd * taxa_cambio_compra
    valor_pagamento_brl = valor_compra_usd * taxa_cambio_pagamento
    variacao_cambial = valor_pagamento_brl - valor_compra_brl
    
    # Assert
    assert valor_compra_brl == Decimal("5200.00")
    assert valor_pagamento_brl == Decimal("5350.00")
    assert variacao_cambial == Decimal("150.00")

@pytest.mark.unit
async def test_ajuste_valor_data_pagamento():
    """
    Testa o ajuste de valor de uma compra conforme a data de pagamento efetivo.
    
    O valor deve ser ajustado se o pagamento for feito:
    1. Com atraso: aplicar juros e multa
    2. Antecipado: aplicar desconto por pagamento antecipado
    """
    # Arrange
    valor_parcela = Decimal("800.00")
    data_vencimento = date.today() - timedelta(days=5)  # Vencida há 5 dias
    data_pagamento = date.today()
    taxa_juros_diaria = Decimal("0.001")  # 0.1% ao dia
    multa_atraso = Decimal("0.02")  # 2% de multa fixa
    
    # Act - Cálculo para pagamento em atraso
    dias_atraso = (data_pagamento - data_vencimento).days
    valor_multa = valor_parcela * multa_atraso if dias_atraso > 0 else Decimal("0")
    valor_juros = valor_parcela * taxa_juros_diaria * dias_atraso if dias_atraso > 0 else Decimal("0")
    valor_total_com_ajuste = valor_parcela + valor_multa + valor_juros
    
    # Assert - Pagamento em atraso
    assert dias_atraso == 5
    assert valor_multa == Decimal("16.00")
    assert valor_juros == Decimal("4.00")
    assert valor_total_com_ajuste == Decimal("820.00")
    
    # Arrange - Para pagamento antecipado
    valor_parcela_2 = Decimal("1200.00")
    data_vencimento_2 = date.today() + timedelta(days=10)  # Vence em 10 dias
    data_pagamento_2 = date.today()
    taxa_desconto_diaria = Decimal("0.0005")  # 0.05% ao dia
    
    # Act - Cálculo para pagamento antecipado
    dias_antecipacao = (data_vencimento_2 - data_pagamento_2).days
    valor_desconto = valor_parcela_2 * taxa_desconto_diaria * dias_antecipacao
    valor_com_desconto = valor_parcela_2 - valor_desconto
    
    # Assert - Pagamento antecipado
    assert dias_antecipacao == 10
    assert valor_desconto == Decimal("6.00")
    assert valor_com_desconto == Decimal("1194.00")

@pytest.mark.unit
async def test_calculo_impostos_recuperaveis_compra():
    """
    Testa o cálculo de impostos recuperáveis em uma compra.
    
    Uma compra pode ter impostos que são recuperáveis:
    1. ICMS, PIS, COFINS recuperáveis devem ser calculados corretamente
    2. O valor líquido da compra deve descontar os impostos recuperáveis
    """
    # Arrange
    valor_compra = Decimal("10000.00")
    aliquota_icms = Decimal("0.18")  # 18%
    aliquota_pis = Decimal("0.0165")  # 1.65%
    aliquota_cofins = Decimal("0.076")  # 7.6%
    
    # Act
    valor_icms = valor_compra * aliquota_icms
    valor_pis = valor_compra * aliquota_pis
    valor_cofins = valor_compra * aliquota_cofins
    
    total_impostos_recuperaveis = valor_icms + valor_pis + valor_cofins
    valor_liquido = valor_compra - total_impostos_recuperaveis
    
    # Assert
    assert valor_icms == Decimal("1800.00")
    assert valor_pis == Decimal("165.00")
    assert valor_cofins == Decimal("760.00")
    assert total_impostos_recuperaveis == Decimal("2725.00")
    assert valor_liquido == Decimal("7275.00")

@pytest.mark.unit
async def test_calculo_custo_medio_ponderado():
    """
    Testa o cálculo do custo médio ponderado após uma nova compra.
    
    O custo médio deve ser atualizado:
    1. Considerar o estoque existente e seu custo atual
    2. Adicionar a nova compra
    3. Calcular o novo custo médio ponderado
    """
    # Arrange
    quantidade_estoque = 50
    custo_medio_atual = Decimal("25.00")
    
    quantidade_compra = 30
    custo_unitario_compra = Decimal("30.00")
    
    # Act
    valor_estoque_atual = quantidade_estoque * custo_medio_atual
    valor_compra = quantidade_compra * custo_unitario_compra
    
    nova_quantidade = quantidade_estoque + quantidade_compra
    novo_valor_total = valor_estoque_atual + valor_compra
    novo_custo_medio = novo_valor_total / nova_quantidade
    
    # Assert
    assert valor_estoque_atual == Decimal("1250.00")
    assert valor_compra == Decimal("900.00")
    assert nova_quantidade == 80
    assert novo_valor_total == Decimal("2150.00")
    assert novo_custo_medio == Decimal("26.875")

@pytest.mark.unit
async def test_calculo_frete_e_seguro_compra():
    """
    Testa o cálculo de frete e seguro em uma compra.
    
    O valor do frete e seguro deve:
    1. Ser adicionado ao valor da compra para formação do custo total
    2. Ser rateado proporcionalmente entre os itens, se necessário
    """
    # Arrange
    itens = [
        {"descricao": "Item 1", "quantidade": 10, "valor_unitario": Decimal("50.00")},
        {"descricao": "Item 2", "quantidade": 5, "valor_unitario": Decimal("100.00")}
    ]
    valor_frete = Decimal("200.00")
    valor_seguro = Decimal("100.00")
    
    # Act
    valor_itens = sum(Decimal(str(item["quantidade"])) * Decimal(str(item["valor_unitario"])) for item in itens)
    valor_total_compra = valor_itens + valor_frete + valor_seguro
    
    # Rateio proporcional do frete e seguro
    itens_com_rateio = []
    for item in itens:
        valor_item = Decimal(str(item["quantidade"])) * Decimal(str(item["valor_unitario"]))
        proporcao = valor_item / valor_itens
        
        frete_rateado = valor_frete * proporcao
        seguro_rateado = valor_seguro * proporcao
        
        custo_total = valor_item + frete_rateado + seguro_rateado
        custo_unitario = custo_total / Decimal(str(item["quantidade"]))
        
        itens_com_rateio.append({
            "descricao": item["descricao"],
            "quantidade": item["quantidade"],
            "valor_unitario_original": Decimal(str(item["valor_unitario"])),
            "valor_item": valor_item,
            "frete_rateado": frete_rateado,
            "seguro_rateado": seguro_rateado,
            "custo_total": custo_total,
            "custo_unitario": custo_unitario
        })
    
    # Assert
    assert valor_itens == Decimal("1000.00")
    assert valor_total_compra == Decimal("1300.00")
    
    # Verificar rateio para o Item 1
    assert itens_com_rateio[0]["valor_item"] == Decimal("500.00")
    assert itens_com_rateio[0]["frete_rateado"] == Decimal("100.00")
    assert itens_com_rateio[0]["seguro_rateado"] == Decimal("50.00")
    assert itens_com_rateio[0]["custo_total"] == Decimal("650.00")
    assert itens_com_rateio[0]["custo_unitario"] == Decimal("65.00")
    
    # Verificar rateio para o Item 2
    assert itens_com_rateio[1]["valor_item"] == Decimal("500.00")
    assert itens_com_rateio[1]["frete_rateado"] == Decimal("100.00")
    assert itens_com_rateio[1]["seguro_rateado"] == Decimal("50.00")
    assert itens_com_rateio[1]["custo_total"] == Decimal("650.00")
    assert itens_com_rateio[1]["custo_unitario"] == Decimal("130.00") 