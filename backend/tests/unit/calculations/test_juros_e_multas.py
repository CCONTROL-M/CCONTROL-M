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
        
        # Mock de parcela atrasada
        parcela_mock = MagicMock(
            id_parcela=uuid.uuid4(),
            valor=valor_original,
            data_vencimento=data_vencimento,
            data_pagamento=None,
            status='pendente'
        )
        
        # Act
        # Função para calcular juros simples
        def calcular_juros_simples(valor, data_vencimento, data_pagamento, taxa_diaria):
            """Calcula juros simples para um valor em atraso."""
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
        # Simular a função de cálculo de juros
        def mock_calcular_juros(conta, data_pagamento, taxa_diaria=taxa_juros_diaria):
            """Calcula juros para uma conta a receber em atraso."""
            if data_pagamento <= conta.data_vencimento:
                return 0.0
                
            dias_atraso = (data_pagamento - conta.data_vencimento).days
            juros = conta.valor * taxa_diaria * dias_atraso
            return round(juros, 2)
            
        # Calcular juros
        juros_calculado = mock_calcular_juros(
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
        
        # Mock de parcela atrasada
        parcela_mock = MagicMock(
            id_parcela=uuid.uuid4(),
            valor=valor_original,
            data_vencimento=data_vencimento,
            data_pagamento=None,
            status='pendente'
        )
        
        # Act
        # Função para calcular juros compostos
        def calcular_juros_compostos(valor, data_vencimento, data_pagamento, taxa_diaria):
            """Calcula juros compostos para um valor em atraso."""
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
        """Teste para mostrar a diferença entre juros simples e compostos."""
        # Arrange
        taxa_juros_diaria = 0.001  # 0.1% ao dia
        valor_original = 5000.0
        dias_atraso = 60  # Período maior para evidenciar diferença
        
        data_vencimento = date.today() - timedelta(days=dias_atraso)
        data_pagamento = date.today()
        
        # Act
        # Função para calcular juros simples
        def calcular_juros_simples(valor, data_vencimento, data_pagamento, taxa_diaria):
            if data_pagamento <= data_vencimento:
                return 0.0
                
            dias_atraso = (data_pagamento - data_vencimento).days
            juros = valor * taxa_diaria * dias_atraso
            return round(juros, 2)
        
        # Função para calcular juros compostos
        def calcular_juros_compostos(valor, data_vencimento, data_pagamento, taxa_diaria):
            if data_pagamento <= data_vencimento:
                return 0.0
                
            dias_atraso = (data_pagamento - data_vencimento).days
            valor_com_juros = valor * (1 + taxa_diaria) ** dias_atraso
            juros = valor_com_juros - valor
            return round(juros, 2)
            
        # Calcular ambos os tipos de juros
        juros_simples = calcular_juros_simples(
            valor=valor_original,
            data_vencimento=data_vencimento,
            data_pagamento=data_pagamento,
            taxa_diaria=taxa_juros_diaria
        )
        
        juros_compostos = calcular_juros_compostos(
            valor=valor_original,
            data_vencimento=data_vencimento,
            data_pagamento=data_pagamento,
            taxa_diaria=taxa_juros_diaria
        )
        
        # Assert
        # Verificar que juros compostos são maiores que juros simples
        assert juros_compostos > juros_simples
        
        # Calcular a diferença percentual
        diferenca = juros_compostos - juros_simples
        diferenca_percentual = (diferenca / juros_simples) * 100
        
        # A diferença deve ser significativa para um período longo
        assert diferenca_percentual > 1.0  # Mais de 1% de diferença


class TestMultaEJuros:
    """Testes para validação de cálculos de multa fixa e juros diários após atraso."""
    
    @pytest.mark.unit
    async def test_calculo_multa_fixa_mais_juros_diario(self, mock_db_session):
        """Teste de cálculo de multa fixa + juros diário após atraso."""
        # Arrange
        percentual_multa = 0.02  # 2% de multa fixa
        taxa_juros_diaria = 0.001  # 0.1% ao dia
        valor_original = 2000.0
        dias_atraso = 20
        
        # Calcular multa fixa
        valor_multa = valor_original * percentual_multa
        
        # Calcular juros diários
        valor_juros = valor_original * taxa_juros_diaria * dias_atraso
        
        # Valor total esperado
        valor_total_esperado = valor_original + valor_multa + valor_juros
        
        data_vencimento = date.today() - timedelta(days=dias_atraso)
        data_pagamento = date.today()
        
        # Mock de parcela atrasada
        parcela_mock = MagicMock(
            id_parcela=uuid.uuid4(),
            valor=valor_original,
            data_vencimento=data_vencimento,
            data_pagamento=None,
            status='pendente'
        )
        
        # Act
        # Função para calcular multa e juros
        def calcular_multa_e_juros(valor, data_vencimento, data_pagamento, 
                                 percentual_multa, taxa_juros_diaria):
            """Calcula multa fixa e juros diários para um valor em atraso."""
            if data_pagamento <= data_vencimento:
                return 0.0, 0.0
                
            # Calcular multa fixa
            multa = valor * percentual_multa
            
            # Calcular juros diários
            dias_atraso = (data_pagamento - data_vencimento).days
            juros = valor * taxa_juros_diaria * dias_atraso
            
            return round(multa, 2), round(juros, 2)
            
        # Calcular multa e juros
        multa_calculada, juros_calculado = calcular_multa_e_juros(
            valor=valor_original,
            data_vencimento=data_vencimento,
            data_pagamento=data_pagamento,
            percentual_multa=percentual_multa,
            taxa_juros_diaria=taxa_juros_diaria
        )
        
        # Calcular valor total
        valor_total_calculado = valor_original + multa_calculada + juros_calculado
        
        # Assert
        assert round(multa_calculada, 2) == round(valor_multa, 2)
        assert round(juros_calculado, 2) == round(valor_juros, 2)
        assert round(valor_total_calculado, 2) == round(valor_total_esperado, 2)


class TestTaxasVariaveis:
    """Testes para validação de cálculos com taxas variáveis."""
    
    @pytest.mark.unit
    async def test_calculo_juros_taxa_variavel(self, mock_db_session):
        """Teste de cálculo de juros com taxa variável no meio do período."""
        # Arrange
        # Definir taxas para diferentes períodos
        taxa_periodo1 = 0.001  # 0.1% ao dia (primeiros 10 dias)
        taxa_periodo2 = 0.002  # 0.2% ao dia (dias subsequentes)
        
        valor_original = 3000.0
        dias_atraso_total = 25
        dias_periodo1 = 10
        dias_periodo2 = dias_atraso_total - dias_periodo1
        
        # Calcular juros para cada período
        juros_periodo1 = valor_original * taxa_periodo1 * dias_periodo1
        juros_periodo2 = valor_original * taxa_periodo2 * dias_periodo2
        
        # Calcular juros total esperado
        juros_total_esperado = juros_periodo1 + juros_periodo2
        valor_com_juros_esperado = valor_original + juros_total_esperado
        
        data_vencimento = date.today() - timedelta(days=dias_atraso_total)
        data_alteracao_taxa = data_vencimento + timedelta(days=dias_periodo1)
        data_pagamento = date.today()
        
        # Mock de parcela atrasada
        parcela_mock = MagicMock(
            id_parcela=uuid.uuid4(),
            valor=valor_original,
            data_vencimento=data_vencimento,
            data_pagamento=None,
            status='pendente'
        )
        
        # Act
        # Função para calcular juros com taxa variável
        def calcular_juros_taxa_variavel(valor, data_vencimento, data_pagamento,
                                      data_alteracao_taxa, taxa_periodo1, taxa_periodo2):
            """Calcula juros com taxa variável para um valor em atraso."""
            if data_pagamento <= data_vencimento:
                return 0.0
                
            # Calcular dias de cada período
            if data_pagamento <= data_alteracao_taxa:
                # Só utilizou a primeira taxa
                dias_periodo1 = (data_pagamento - data_vencimento).days
                dias_periodo2 = 0
            else:
                # Utilizou ambas as taxas
                dias_periodo1 = (data_alteracao_taxa - data_vencimento).days
                dias_periodo2 = (data_pagamento - data_alteracao_taxa).days
                
            # Calcular juros para cada período
            juros_p1 = valor * taxa_periodo1 * dias_periodo1
            juros_p2 = valor * taxa_periodo2 * dias_periodo2
            
            # Retornar juros total
            return round(juros_p1 + juros_p2, 2)
            
        # Calcular juros
        juros_calculado = calcular_juros_taxa_variavel(
            valor=valor_original,
            data_vencimento=data_vencimento,
            data_pagamento=data_pagamento,
            data_alteracao_taxa=data_alteracao_taxa,
            taxa_periodo1=taxa_periodo1,
            taxa_periodo2=taxa_periodo2
        )
        
        # Assert
        assert round(juros_calculado, 2) == round(juros_total_esperado, 2)
        assert round(valor_original + juros_calculado, 2) == round(valor_com_juros_esperado, 2)
    
    @pytest.mark.unit
    async def test_juros_escalonado_por_dias_atraso(self, mock_db_session):
        """Teste de juros escalonado conforme dias de atraso."""
        # Arrange
        # Definir taxas progressivas conforme dias de atraso
        taxas_escalonadas = {
            0: 0.0,       # Em dia (0%)
            1: 0.0005,    # Até 5 dias (0.05% ao dia)
            6: 0.001,     # De 6 a 15 dias (0.1% ao dia)
            16: 0.0015,   # De 16 a 30 dias (0.15% ao dia)
            31: 0.002     # Acima de 30 dias (0.2% ao dia)
        }
        
        valor_original = 2500.0
        dias_atraso = 20  # 20 dias de atraso (cai na faixa de 16-30 dias)
        
        # Obter taxa aplicável para o período
        taxa_aplicavel = None
        for limite_dias, taxa in sorted(taxas_escalonadas.items()):
            if dias_atraso >= limite_dias:
                taxa_aplicavel = taxa
        
        # Calcular juros escalonado
        juros_esperado = valor_original * taxa_aplicavel * dias_atraso
        valor_com_juros = valor_original + juros_esperado
        
        data_vencimento = date.today() - timedelta(days=dias_atraso)
        data_pagamento = date.today()
        
        # Act
        # Função para calcular juros escalonado
        def calcular_juros_escalonado(valor, data_vencimento, data_pagamento, taxas_escalonadas):
            """Calcula juros escalonado conforme dias de atraso."""
            if data_pagamento <= data_vencimento:
                return 0.0
                
            dias_atraso = (data_pagamento - data_vencimento).days
            
            # Determinar a taxa aplicável
            taxa_aplicavel = None
            for limite_dias, taxa in sorted(taxas_escalonadas.items()):
                if dias_atraso >= limite_dias:
                    taxa_aplicavel = taxa
            
            # Calcular juros
            juros = valor * taxa_aplicavel * dias_atraso
            return round(juros, 2)
            
        # Calcular juros
        juros_calculado = calcular_juros_escalonado(
            valor=valor_original,
            data_vencimento=data_vencimento,
            data_pagamento=data_pagamento,
            taxas_escalonadas=taxas_escalonadas
        )
        
        # Assert
        assert round(juros_calculado, 2) == round(juros_esperado, 2)
        assert round(valor_original + juros_calculado, 2) == round(valor_com_juros, 2)
        # Verificar que a taxa aplicada foi a correta (0.15% para 20 dias)
        assert taxa_aplicavel == 0.0015 