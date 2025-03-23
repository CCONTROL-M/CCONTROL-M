"""Testes para cálculos financeiros relacionados a vendas."""
import pytest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, AsyncMock, patch
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.no_db
async def test_calculo_venda_a_vista():
    """
    Testa o cálculo de uma venda à vista.
    
    Uma venda à vista deve calcular corretamente:
    1. O valor total (soma dos itens)
    2. Aplicação de desconto
    3. Valor líquido final
    """
    # Arrange
    itens = [
        {"descricao": "Produto 1", "quantidade": 2, "valor_unitario": Decimal("150.00")},
        {"descricao": "Produto 2", "quantidade": 1, "valor_unitario": Decimal("200.00")}
    ]
    desconto = Decimal("50.00")
    
    # Act
    valor_total = sum(Decimal(str(item["quantidade"])) * Decimal(str(item["valor_unitario"])) for item in itens)
    valor_liquido = valor_total - desconto
    
    # Assert
    assert valor_total == Decimal("500.00")
    assert valor_liquido == Decimal("450.00")

@pytest.mark.no_db
async def test_calculo_venda_parcelada():
    """
    Testa o cálculo de uma venda parcelada.
    
    Uma venda parcelada deve:
    1. Dividir o valor total em N parcelas
    2. Ajustar a última parcela para garantir que a soma seja exata
    3. Gerar as datas de vencimento corretamente
    """
    # Arrange
    valor_total = Decimal("1000.00")
    num_parcelas = 3
    data_venda = date.today()
    
    # Act
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
            "valor": valor_parcela_atual,
            "data_vencimento": data_venda + timedelta(days=30 * i)
        })
    
    # Assert
    assert len(parcelas) == num_parcelas
    assert parcelas[0]["valor"] == Decimal("333.33")
    assert parcelas[1]["valor"] == Decimal("333.33")
    assert parcelas[2]["valor"] == Decimal("333.34")
    assert sum(p["valor"] for p in parcelas) == valor_total
    
    # Verificar datas
    assert parcelas[0]["data_vencimento"] == data_venda + timedelta(days=30)
    assert parcelas[1]["data_vencimento"] == data_venda + timedelta(days=60)
    assert parcelas[2]["data_vencimento"] == data_venda + timedelta(days=90)

@pytest.mark.no_db
async def test_calculo_juros_atraso_venda():
    """
    Testa o cálculo de juros por atraso em parcelas de venda.
    
    Quando uma parcela é paga com atraso:
    1. Deve calcular corretamente o valor dos juros
    2. Deve adicionar o juros ao valor da parcela
    """
    # Arrange
    valor_parcela = Decimal("300.00")
    taxa_juros_diaria = Decimal("0.001")  # 0.1% ao dia
    data_vencimento = date.today() - timedelta(days=10)  # Vencida há 10 dias
    data_pagamento = date.today()
    
    # Act
    dias_atraso = (data_pagamento - data_vencimento).days
    valor_juros = valor_parcela * taxa_juros_diaria * dias_atraso
    valor_total_com_juros = valor_parcela + valor_juros
    
    # Assert
    assert dias_atraso == 10
    assert valor_juros == Decimal("3.00")
    assert valor_total_com_juros == Decimal("303.00")

@pytest.mark.no_db
async def test_calculo_desconto_antecipado_venda():
    """
    Testa o cálculo de desconto por pagamento antecipado.
    
    Quando uma parcela é paga antecipadamente:
    1. Deve aplicar um desconto proporcional aos dias de antecipação
    2. Deve subtrair o desconto do valor da parcela
    """
    # Arrange
    valor_parcela = Decimal("500.00")
    taxa_desconto_diaria = Decimal("0.0005")  # 0.05% ao dia
    data_vencimento = date.today() + timedelta(days=15)  # Vence em 15 dias
    data_pagamento = date.today()
    
    # Act
    dias_antecipacao = (data_vencimento - data_pagamento).days
    valor_desconto = valor_parcela * taxa_desconto_diaria * dias_antecipacao
    valor_com_desconto = valor_parcela - valor_desconto
    
    # Assert
    assert dias_antecipacao == 15
    assert valor_desconto == Decimal("3.75")
    assert valor_com_desconto == Decimal("496.25")

@pytest.mark.no_db
async def test_calculo_comissao_vendedor():
    """
    Testa o cálculo de comissão de vendedor.
    
    A comissão deve ser calculada como um percentual sobre o valor líquido da venda.
    """
    # Arrange
    valor_venda = Decimal("1000.00")
    percentual_comissao = Decimal("0.05")  # 5%
    
    # Act
    valor_comissao = valor_venda * percentual_comissao
    
    # Assert
    assert valor_comissao == Decimal("50.00")

@pytest.mark.unit
async def test_calculo_impostos_venda():
    """
    Testa o cálculo de impostos sobre uma venda.
    
    Os impostos devem ser calculados corretamente sobre o valor total.
    """
    # Arrange
    valor_venda = Decimal("1000.00")
    taxa_imposto = Decimal("0.18")  # 18% (exemplo soma de ICMS, PIS, COFINS)
    
    # Act
    valor_imposto = valor_venda * taxa_imposto
    valor_liquido = valor_venda - valor_imposto
    
    # Assert
    assert valor_imposto == Decimal("180.00")
    assert valor_liquido == Decimal("820.00")

@pytest.mark.unit
async def test_venda_com_multiplos_pagamentos():
    """
    Testa o cálculo de uma venda com múltiplos métodos de pagamento.
    
    Uma venda pode ser paga com diferentes métodos, cada um com seu valor.
    """
    # Arrange
    valor_total = Decimal("800.00")
    pagamentos = [
        {"metodo": "dinheiro", "valor": Decimal("300.00")},
        {"metodo": "cartao_credito", "valor": Decimal("500.00")}
    ]
    
    # Act
    soma_pagamentos = sum(p["valor"] for p in pagamentos)
    
    # Assert
    assert soma_pagamentos == valor_total
    assert len(pagamentos) == 2
    assert pagamentos[0]["valor"] + pagamentos[1]["valor"] == valor_total 