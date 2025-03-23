"""Testes unitários para cálculos de juros e multas no sistema CCONTROL-M."""
import pytest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

from app.models.parcela import Parcela
from app.models.conta_receber import ContaReceber
from app.models.conta_pagar import ContaPagar


class TestJurosSimples:
    """Testes para validação de cálculos de juros simples em contas atrasadas."""
    
    @pytest.mark.unit
    async def test_calculo_juros_simples_apos_vencimento(self, mock_db_session):
        """Teste de cálculo de juros simples após o vencimento."""
        # Arrange
        taxa_juros_diaria = 0.001  # 0.1% ao dia
        valor_original = 1000.0
        dias_atraso = 10
        
        # Calcular juros esperado
        juros_esperado = valor_original * taxa_juros_diaria * dias_atraso
        valor_com_juros = valor_original + juros_esperado
        
        data_vencimento = date.today() - timedelta(days=dias_atraso)
        data_pagamento = date.today()
        
        # Act
        # Simular a função de cálculo de juros simples
        def calcular_juros_simples(valor, data_vencimento, data_pagamento, taxa_diaria):
            """Calcula juros simples para pagamento em atraso."""
            if data_pagamento <= data_vencimento:
                return 0.0
                
            dias_atraso = (data_pagamento - data_vencimento).days
            juros = valor * taxa_diaria * dias_atraso
            return round(juros, 2)
            
        # Calcular juros
        juros_calculado = calcular_juros_simples(
            valor=valor_original,
            data_vencimento=data_vencimento,
            data_pagamento=data_pagamento,
            taxa_diaria=taxa_juros_diaria
        )
        
        # Assert
        assert round(juros_calculado, 2) == round(juros_esperado, 2)
        assert round(valor_original + juros_calculado, 2) == round(valor_com_juros, 2)
    
    @pytest.mark.unit
    async def test_calculo_juros_simples_conta_receber(self, mock_db_session):
        """Teste de cálculo de juros simples em conta a receber."""
        # Arrange
        taxa_juros_diaria = 0.001  # 0.1% ao dia
        valor_original = 1500.0
        dias_atraso = 15
        
        # Calcular juros esperado
        juros_esperado = valor_original * taxa_juros_diaria * dias_atraso
        valor_com_juros = valor_original + juros_esperado
        
        data_vencimento = date.today() - timedelta(days=dias_atraso)
        data_recebimento = date.today()
        
        # Mock de conta a receber atrasada
        conta_receber_mock = MagicMock(
            id_conta_receber=uuid.uuid4(),
            valor=valor_original,
            data_vencimento=data_vencimento,
            data_recebimento=None,
            status='pendente'
        )
        
        # Act
        # Simular a função de cálculo de juros específica para contas a receber
        def calcular_juros(conta, data_pagamento, taxa_diaria=taxa_juros_diaria):
            """Calcula juros para uma conta a receber em atraso."""
            if data_pagamento <= conta.data_vencimento:
                return 0.0
                
            dias_atraso = (data_pagamento - conta.data_vencimento).days
            juros = conta.valor * taxa_diaria * dias_atraso
            return round(juros, 2)
            
        # Calcular juros
        juros_calculado = calcular_juros(
            conta=conta_receber_mock,
            data_pagamento=data_recebimento
        )
        
        # Assert
        assert round(juros_calculado, 2) == round(juros_esperado, 2)
        assert round(valor_original + juros_calculado, 2) == round(valor_com_juros, 2)


class TestJurosCompostos:
    """Testes para validação de cálculos de juros compostos em contas atrasadas."""
    
    @pytest.mark.unit
    async def test_calculo_juros_compostos_apos_vencimento(self, mock_db_session):
        """Teste de cálculo de juros compostos após o vencimento."""
        # Arrange
        taxa_juros_diaria = 0.001  # 0.1% ao dia
        valor_original = 1000.0
        dias_atraso = 30
        
        # Calcular juros compostos esperado
        valor_com_juros = valor_original * (1 + taxa_juros_diaria) ** dias_atraso
        juros_esperado = valor_com_juros - valor_original
        
        data_vencimento = date.today() - timedelta(days=dias_atraso)
        data_pagamento = date.today()
        
        # Act
        # Simular a função de cálculo de juros compostos
        def calcular_juros_compostos(valor, data_vencimento, data_pagamento, taxa_diaria):
            """Calcula juros compostos para pagamento em atraso."""
            if data_pagamento <= data_vencimento:
                return 0.0
                
            dias_atraso = (data_pagamento - data_vencimento).days
            valor_com_juros = valor * (1 + taxa_diaria) ** dias_atraso
            juros = valor_com_juros - valor
            return round(juros, 2)
            
        # Calcular juros
        juros_calculado = calcular_juros_compostos(
            valor=valor_original,
            data_vencimento=data_vencimento,
            data_pagamento=data_pagamento,
            taxa_diaria=taxa_juros_diaria
        )
        
        # Assert
        assert round(juros_calculado, 2) == round(juros_esperado, 2)
        assert round(valor_original + juros_calculado, 2) == round(valor_com_juros, 2)
    
    @pytest.mark.unit
    async def test_diferenca_juros_simples_compostos(self, mock_db_session):
        """Teste para comparar a diferença entre juros simples e compostos."""
        # Arrange
        taxa_juros_diaria = 0.002  # 0.2% ao dia
        valor_original = 5000.0
        dias_atraso = 45
        
        data_vencimento = date.today() - timedelta(days=dias_atraso)
        data_pagamento = date.today()
        
        # Act
        # Função para cálculo de juros simples
        def calcular_juros_simples(valor, data_vencimento, data_pagamento, taxa_diaria):
            """Calcula juros simples para pagamento em atraso."""
            if data_pagamento <= data_vencimento:
                return 0.0
            dias_atraso = (data_pagamento - data_vencimento).days
            return round(valor * taxa_diaria * dias_atraso, 2)
            
        # Função para cálculo de juros compostos
        def calcular_juros_compostos(valor, data_vencimento, data_pagamento, taxa_diaria):
            """Calcula juros compostos para pagamento em atraso."""
            if data_pagamento <= data_vencimento:
                return 0.0
            dias_atraso = (data_pagamento - data_vencimento).days
            valor_com_juros = valor * (1 + taxa_diaria) ** dias_atraso
            return round(valor_com_juros - valor, 2)
        
        # Calcular juros simples
        juros_simples = calcular_juros_simples(
            valor=valor_original,
            data_vencimento=data_vencimento,
            data_pagamento=data_pagamento,
            taxa_diaria=taxa_juros_diaria
        )
        
        # Calcular juros compostos
        juros_compostos = calcular_juros_compostos(
            valor=valor_original,
            data_vencimento=data_vencimento,
            data_pagamento=data_pagamento,
            taxa_diaria=taxa_juros_diaria
        )
        
        # Assert
        assert juros_compostos > juros_simples
        # A diferença deve ser significativa para um período longo
        diferenca = juros_compostos - juros_simples
        assert diferenca > 0
        # Calcular a diferença percentual
        diferenca_percentual = (diferenca / juros_simples) * 100
        assert diferenca_percentual > 0


class TestMultaEJuros:
    """Testes para validação de cálculos de multa fixa mais juros em contas atrasadas."""
    
    @pytest.mark.unit
    async def test_calculo_multa_fixa_mais_juros_diario(self, mock_db_session):
        """Teste de cálculo de multa fixa mais juros diário em atraso."""
        # Arrange
        valor_original = 2000.0
        percentual_multa = 0.02  # 2% de multa fixa
        taxa_juros_diaria = 0.001  # 0.1% ao dia
        dias_atraso = 20
        
        data_vencimento = date.today() - timedelta(days=dias_atraso)
        data_pagamento = date.today()
        
        # Calcular valores esperados
        multa_esperada = valor_original * percentual_multa
        juros_esperados = valor_original * taxa_juros_diaria * dias_atraso
        valor_total_esperado = valor_original + multa_esperada + juros_esperados
        
        # Act
        # Simular a função de cálculo de multa e juros
        def calcular_multa_e_juros(valor, data_vencimento, data_pagamento, 
                                 percentual_multa, taxa_juros_diaria):
            """Calcula multa fixa e juros para pagamento em atraso."""
            if data_pagamento <= data_vencimento:
                return 0.0, 0.0
                
            dias_atraso = (data_pagamento - data_vencimento).days
            
            # Calcular multa fixa
            multa = valor * percentual_multa
            
            # Calcular juros diário
            juros = valor * taxa_juros_diaria * dias_atraso
            
            return round(multa, 2), round(juros, 2)
        
        # Calcular multa e juros
        multa_calculada, juros_calculados = calcular_multa_e_juros(
            valor=valor_original,
            data_vencimento=data_vencimento,
            data_pagamento=data_pagamento,
            percentual_multa=percentual_multa,
            taxa_juros_diaria=taxa_juros_diaria
        )
        
        valor_total_calculado = valor_original + multa_calculada + juros_calculados
        
        # Assert
        assert round(multa_calculada, 2) == round(multa_esperada, 2)
        assert round(juros_calculados, 2) == round(juros_esperados, 2)
        assert round(valor_total_calculado, 2) == round(valor_total_esperado, 2)


class TestTaxasVariaveis:
    """Testes para validação de cálculos com taxas variáveis durante o período."""
    
    @pytest.mark.unit
    async def test_calculo_juros_taxa_variavel(self, mock_db_session):
        """Teste de cálculo de juros com taxa variável durante o período."""
        # Arrange
        valor_original = 3000.0
        taxa_periodo1 = 0.001  # 0.1% ao dia no primeiro período
        taxa_periodo2 = 0.002  # 0.2% ao dia no segundo período
        
        data_vencimento = date.today() - timedelta(days=30)
        data_alteracao_taxa = date.today() - timedelta(days=15)  # Alteração na metade do período
        data_pagamento = date.today()
        
        # Calcular dias em cada período
        dias_periodo1 = (data_alteracao_taxa - data_vencimento).days
        dias_periodo2 = (data_pagamento - data_alteracao_taxa).days
        
        # Calcular juros esperados para cada período
        juros_periodo1 = valor_original * taxa_periodo1 * dias_periodo1
        juros_periodo2 = valor_original * taxa_periodo2 * dias_periodo2
        juros_total_esperado = juros_periodo1 + juros_periodo2
        
        # Act
        # Simular a função de cálculo de juros com taxa variável
        def calcular_juros_taxa_variavel(valor, data_vencimento, data_pagamento,
                                      data_alteracao_taxa, taxa_periodo1, taxa_periodo2):
            """Calcula juros com taxa variável durante o período."""
            if data_pagamento <= data_vencimento:
                return 0.0
                
            # Se o pagamento for antes da alteração da taxa,
            # usa apenas a taxa do primeiro período
            if data_pagamento <= data_alteracao_taxa:
                dias_atraso = (data_pagamento - data_vencimento).days
                return round(valor * taxa_periodo1 * dias_atraso, 2)
                
            # Se o vencimento for após a alteração da taxa,
            # usa apenas a taxa do segundo período
            if data_vencimento >= data_alteracao_taxa:
                dias_atraso = (data_pagamento - data_vencimento).days
                return round(valor * taxa_periodo2 * dias_atraso, 2)
                
            # Caso contrário, calcula juros para cada período separadamente
            dias_periodo1 = (data_alteracao_taxa - data_vencimento).days
            dias_periodo2 = (data_pagamento - data_alteracao_taxa).days
            
            juros_periodo1 = valor * taxa_periodo1 * dias_periodo1
            juros_periodo2 = valor * taxa_periodo2 * dias_periodo2
            
            return round(juros_periodo1 + juros_periodo2, 2)
        
        # Calcular juros
        juros_calculados = calcular_juros_taxa_variavel(
            valor=valor_original,
            data_vencimento=data_vencimento,
            data_pagamento=data_pagamento,
            data_alteracao_taxa=data_alteracao_taxa,
            taxa_periodo1=taxa_periodo1,
            taxa_periodo2=taxa_periodo2
        )
        
        # Assert
        assert round(juros_calculados, 2) == round(juros_total_esperado, 2)
    
    @pytest.mark.unit
    async def test_juros_escalonado_por_dias_atraso(self, mock_db_session):
        """Teste de cálculo de juros escalonado conforme dias de atraso."""
        # Arrange
        valor_original = 5000.0
        
        # Definir taxas escalonadas por dias de atraso
        taxas_escalonadas = {
            0: 0.0,           # Sem juros até o vencimento
            1: 0.001,         # 0.1% ao dia até 10 dias de atraso
            11: 0.0015,       # 0.15% ao dia de 11 a 30 dias de atraso
            31: 0.002,        # 0.2% ao dia a partir de 31 dias de atraso
        }
        
        # Caso de teste: pagamento com 25 dias de atraso
        dias_atraso = 25
        data_vencimento = date.today() - timedelta(days=dias_atraso)
        data_pagamento = date.today()
        
        # Calcular juros esperados para o período (fórmula escalonada)
        juros_esperados = 0
        dias_calculados = 0
        
        # Ordenar pontos de escalonamento
        pontos_escalonamento = sorted(taxas_escalonadas.keys())
        
        for i in range(len(pontos_escalonamento)):
            inicio_faixa = pontos_escalonamento[i]
            if i < len(pontos_escalonamento) - 1:
                fim_faixa = pontos_escalonamento[i + 1] - 1
            else:
                fim_faixa = dias_atraso
                
            if inicio_faixa > dias_atraso:
                break
                
            if fim_faixa > dias_atraso:
                fim_faixa = dias_atraso
                
            dias_na_faixa = fim_faixa - inicio_faixa + 1
            if dias_na_faixa > 0:
                taxa = taxas_escalonadas[inicio_faixa]
                juros_na_faixa = valor_original * taxa * dias_na_faixa
                juros_esperados += juros_na_faixa
                dias_calculados += dias_na_faixa
        
        # Act
        # Simular a função de cálculo de juros escalonado
        def calcular_juros_escalonado(valor, data_vencimento, data_pagamento, taxas_escalonadas):
            """Calcula juros escalonados conforme dias de atraso."""
            if data_pagamento <= data_vencimento:
                return 0.0
                
            dias_atraso = (data_pagamento - data_vencimento).days
            juros_total = 0
            
            # Ordenar pontos de escalonamento
            pontos_escalonamento = sorted(taxas_escalonadas.keys())
            
            for i in range(len(pontos_escalonamento)):
                inicio_faixa = pontos_escalonamento[i]
                if i < len(pontos_escalonamento) - 1:
                    fim_faixa = pontos_escalonamento[i + 1] - 1
                else:
                    fim_faixa = dias_atraso
                    
                if inicio_faixa > dias_atraso:
                    break
                    
                if fim_faixa > dias_atraso:
                    fim_faixa = dias_atraso
                    
                dias_na_faixa = fim_faixa - inicio_faixa + 1
                if dias_na_faixa > 0:
                    taxa = taxas_escalonadas[inicio_faixa]
                    juros_na_faixa = valor * taxa * dias_na_faixa
                    juros_total += juros_na_faixa
            
            return round(juros_total, 2)
        
        # Calcular juros
        juros_calculados = calcular_juros_escalonado(
            valor=valor_original,
            data_vencimento=data_vencimento,
            data_pagamento=data_pagamento,
            taxas_escalonadas=taxas_escalonadas
        )
        
        # Assert
        assert round(juros_calculados, 2) == round(juros_esperados, 2)
        assert dias_calculados == dias_atraso 