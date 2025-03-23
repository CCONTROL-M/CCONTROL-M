"""Teste de exemplo que deve funcionar sem problemas."""
import pytest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock


@pytest.mark.no_db
async def test_calculo_simples():
    """Teste simples de cálculo que deve funcionar."""
    # Arrange
    valor1 = Decimal('100.50')
    valor2 = Decimal('200.75')
    
    # Act
    resultado = valor1 + valor2
    
    # Assert
    assert resultado == Decimal('301.25')
    assert isinstance(resultado, Decimal)


@pytest.mark.no_db
async def test_calculo_desconto():
    """Teste de cálculo de desconto percentual."""
    # Arrange
    valor_original = Decimal('500.00')
    percentual_desconto = Decimal('0.10')  # 10%
    
    # Act
    valor_desconto = valor_original * percentual_desconto
    valor_final = valor_original - valor_desconto
    
    # Assert
    assert valor_desconto == Decimal('50.00')
    assert valor_final == Decimal('450.00')


@pytest.mark.no_db
async def test_calculo_parcelas():
    """Teste de cálculo de parcelas dividindo um valor total."""
    # Arrange
    valor_total = Decimal('1000.00')
    num_parcelas = 3
    
    # Act
    valor_parcela = valor_total / num_parcelas
    # Arredondar para 2 casas decimais
    valor_parcela_arredondado = round(valor_parcela, 2)
    
    # Calcular o valor da última parcela para compensar arredondamentos
    valor_ultima_parcela = valor_total - (valor_parcela_arredondado * (num_parcelas - 1))
    
    # Assert
    assert valor_parcela_arredondado == Decimal('333.33')
    assert valor_ultima_parcela == Decimal('333.34')
    assert (valor_parcela_arredondado * (num_parcelas - 1) + valor_ultima_parcela) == valor_total


@pytest.mark.no_db
async def test_calculo_juros_simples():
    """Teste de cálculo de juros simples."""
    # Arrange
    valor_principal = Decimal('1000.00')
    taxa_juros = Decimal('0.02')  # 2% ao mês
    periodo_meses = 3
    
    # Act
    juros = valor_principal * taxa_juros * periodo_meses
    montante = valor_principal + juros
    
    # Assert
    assert juros == Decimal('60.00')
    assert montante == Decimal('1060.00')


@pytest.mark.no_db
async def test_calculo_juros_compostos():
    """Teste de cálculo de juros compostos."""
    # Arrange
    valor_principal = Decimal('1000.00')
    taxa_juros = Decimal('0.02')  # 2% ao mês
    periodo_meses = 3
    
    # Act
    montante = valor_principal * (1 + taxa_juros) ** periodo_meses
    montante_arredondado = round(montante, 2)
    
    # Assert
    assert montante_arredondado == Decimal('1061.21')
    
    # Calcular juros a partir do montante
    juros = montante - valor_principal
    juros_arredondado = round(juros, 2)
    assert juros_arredondado == Decimal('61.21') 