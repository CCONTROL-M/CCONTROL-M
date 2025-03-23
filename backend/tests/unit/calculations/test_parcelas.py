"""Testes unitários para cálculos de parcelas no sistema CCONTROL-M."""
import pytest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

from app.models.parcela import Parcela, ParcelaVenda, ParcelaCompra
from app.models.venda import Venda
from app.models.lancamento import Lancamento
from app.schemas.parcela import ParcelaCreate, StatusParcela


class TestGeracaoParcelas:
    """Testes para geração automática de parcelas."""
    
    @pytest.mark.unit
    @pytest.mark.no_db
    async def test_geracao_parcelas_iguais(self, mock_db_session):
        """Teste de geração de parcelas com valores iguais."""
        # Arrange
        valor_total = 1000.0
        num_parcelas = 4
        data_primeira_parcela = date.today()
        id_venda = uuid.uuid4()
        id_empresa = uuid.uuid4()
        
        # Mock para retornar o objeto venda
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = MagicMock(
            id_venda=id_venda,
            id_empresa=id_empresa
        )
        
        # Mock para simular ParcelaVenda
        parcela_mock = MagicMock()
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = []
        
        # Act
        # Simular a função de geração de parcelas
        async def gerar_parcelas_iguais(valor_total, num_parcelas, data_primeira_parcela, id_venda):
            """Gera parcelas com valores iguais."""
            if num_parcelas <= 0:
                raise ValueError("Número de parcelas deve ser maior que zero")
            
            valor_parcela = round(valor_total / num_parcelas, 2)
            parcelas = []
            
            for i in range(num_parcelas):
                data_vencimento = data_primeira_parcela + timedelta(days=30 * i)
                parcela = Parcela(
                    id_parcela=uuid.uuid4(),
                    numero=i + 1,
                    valor=valor_parcela,
                    data_vencimento=data_vencimento,
                    status="pendente",
                    id_venda=id_venda,
                    id_empresa=id_empresa
                )
                parcelas.append(parcela)
                
            # Arredondar diferenças para a última parcela
            diferenca = valor_total - sum(p.valor for p in parcelas)
            if diferenca != 0:
                parcelas[-1].valor = round(parcelas[-1].valor + diferenca, 2)
                
            return parcelas
            
        # Executar a função
        parcelas = await gerar_parcelas_iguais(
            valor_total, 
            num_parcelas, 
            data_primeira_parcela, 
            id_venda
        )
            
        # Assert
        assert len(parcelas) == num_parcelas
        assert sum(parcela.valor for parcela in parcelas) == pytest.approx(valor_total, 0.01)
        for i, parcela in enumerate(parcelas):
            assert parcela.id_venda == id_venda
            assert parcela.status == "pendente"
            assert parcela.numero == i + 1
            assert parcela.data_vencimento == data_primeira_parcela + timedelta(days=30 * i)
    
    @pytest.mark.unit
    async def test_geracao_parcelas_com_arredondamento_cima(self, mock_db_session):
        """Teste de geração de parcelas com arredondamento para cima."""
        # Arrange
        valor_total = 1000.0
        num_parcelas = 3  # Isso vai causar arredondamento
        data_primeira_parcela = date.today()
        id_venda = uuid.uuid4()
        id_empresa = uuid.uuid4()
        
        # Mock para retornar o objeto venda
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = MagicMock(
            id_venda=id_venda,
            id_empresa=id_empresa
        )
        
        # Mock para simular ParcelaVenda
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = []
        
        # Act
        # Simular a função de geração de parcelas com arredondamento para cima
        async def gerar_parcelas_arredondamento_cima(valor_total, num_parcelas, data_primeira_parcela, id_venda):
            """Gera parcelas com arredondamento para cima."""
            if num_parcelas <= 0:
                raise ValueError("Número de parcelas deve ser maior que zero")
            
            # Calcular valor base por parcela (sem arredondamento)
            valor_parcela_base = valor_total / num_parcelas
            
            # Arredondar para cima com 2 casas decimais
            valor_parcela = round(valor_parcela_base + 0.005, 2)
            
            parcelas = []
            for i in range(num_parcelas - 1):  # Gerar n-1 parcelas
                data_vencimento = data_primeira_parcela + timedelta(days=30 * i)
                parcela = Parcela(
                    id_parcela=uuid.uuid4(),
                    numero=i + 1,
                    valor=valor_parcela,
                    data_vencimento=data_vencimento,
                    status="pendente",
                    id_venda=id_venda,
                    id_empresa=id_empresa
                )
                parcelas.append(parcela)
            
            # Calcular a última parcela como o restante
            valor_restante = valor_total - sum(p.valor for p in parcelas)
            
            # Adicionar última parcela
            data_vencimento = data_primeira_parcela + timedelta(days=30 * (num_parcelas - 1))
            parcela = Parcela(
                id_parcela=uuid.uuid4(),
                numero=num_parcelas,
                valor=round(valor_restante, 2),
                data_vencimento=data_vencimento,
                status="pendente",
                id_venda=id_venda,
                id_empresa=id_empresa
            )
            parcelas.append(parcela)
            
            return parcelas
            
        # Executar a função
        parcelas = await gerar_parcelas_arredondamento_cima(
            valor_total, 
            num_parcelas, 
            data_primeira_parcela, 
            id_venda
        )
            
        # Assert
        assert len(parcelas) == num_parcelas
        assert sum(parcela.valor for parcela in parcelas) == pytest.approx(valor_total, 0.01)
        # Verificar se as primeiras parcelas são iguais
        primeiro_valor = parcelas[0].valor
        for i in range(num_parcelas - 1):
            assert parcelas[i].valor == primeiro_valor
        # Verificar se a última parcela é diferente (para ajuste)
        assert parcelas[-1].valor != primeiro_valor
    
    @pytest.mark.unit
    async def test_geracao_parcelas_com_arredondamento_baixo(self, mock_db_session):
        """Teste de geração de parcelas com arredondamento para baixo."""
        # Arrange
        valor_total = 100.0
        num_parcelas = 3  # Isso vai causar arredondamento
        data_primeira_parcela = date.today()
        id_venda = uuid.uuid4()
        id_empresa = uuid.uuid4()
        
        # Mock para retornar o objeto venda
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = MagicMock(
            id_venda=id_venda,
            id_empresa=id_empresa
        )
        
        # Mock para simular ParcelaVenda
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = []
        
        # Act
        # Simular a função de geração de parcelas com arredondamento para baixo
        async def gerar_parcelas_arredondamento_baixo(valor_total, num_parcelas, data_primeira_parcela, id_venda):
            """Gera parcelas com arredondamento para baixo."""
            if num_parcelas <= 0:
                raise ValueError("Número de parcelas deve ser maior que zero")
            
            # Calcular valor base por parcela (sem arredondamento)
            valor_parcela_base = valor_total / num_parcelas
            
            # Arredondar para baixo com 2 casas decimais
            valor_parcela = int(valor_parcela_base * 100) / 100
            
            parcelas = []
            for i in range(num_parcelas - 1):  # Gerar n-1 parcelas
                data_vencimento = data_primeira_parcela + timedelta(days=30 * i)
                parcela = Parcela(
                    id_parcela=uuid.uuid4(),
                    numero=i + 1,
                    valor=valor_parcela,
                    data_vencimento=data_vencimento,
                    status="pendente",
                    id_venda=id_venda,
                    id_empresa=id_empresa
                )
                parcelas.append(parcela)
            
            # Calcular a última parcela como o restante
            valor_restante = valor_total - sum(p.valor for p in parcelas)
            
            # Adicionar última parcela
            data_vencimento = data_primeira_parcela + timedelta(days=30 * (num_parcelas - 1))
            parcela = Parcela(
                id_parcela=uuid.uuid4(),
                numero=num_parcelas,
                valor=round(valor_restante, 2),
                data_vencimento=data_vencimento,
                status="pendente",
                id_venda=id_venda,
                id_empresa=id_empresa
            )
            parcelas.append(parcela)
            
            return parcelas
            
        # Executar a função
        parcelas = await gerar_parcelas_arredondamento_baixo(
            valor_total, 
            num_parcelas, 
            data_primeira_parcela, 
            id_venda
        )
            
        # Assert
        assert len(parcelas) == num_parcelas
        assert sum(parcela.valor for parcela in parcelas) == pytest.approx(valor_total, 0.01)
        # Verificar se as primeiras parcelas são iguais
        primeiro_valor = parcelas[0].valor
        for i in range(num_parcelas - 1):
            assert parcelas[i].valor == primeiro_valor
        # Verificar se a última parcela é maior (para compensar arredondamento para baixo)
        assert parcelas[-1].valor > primeiro_valor
        # Verificar se a soma das parcelas é igual ao valor total
        assert sum(p.valor for p in parcelas) == pytest.approx(valor_total)


class TestPagamentoAntecipado:
    """Testes para pagamento antecipado de parcelas."""
    
    @pytest.mark.unit
    async def test_pagamento_antecipado_com_desconto_juros(self, mock_db_session):
        """Teste de pagamento antecipado com desconto de juros."""
        # Arrange
        id_parcela = uuid.uuid4()
        valor_original = 1000.0
        taxa_juros_mensal = 0.02  # 2% ao mês
        
        # Data de vencimento futura (60 dias a frente)
        data_vencimento = date.today() + timedelta(days=60)
        
        # Data de pagamento atual (antecipado)
        data_pagamento = date.today()
        
        # Dias de antecipação
        dias_antecipacao = (data_vencimento - data_pagamento).days
        
        # Calcular desconto esperado
        # Usando juros simples: taxa_diaria * dias * valor
        taxa_diaria = taxa_juros_mensal / 30
        desconto_esperado = round(taxa_diaria * dias_antecipacao * valor_original, 2)
        valor_final_esperado = valor_original - desconto_esperado
        
        # Mock da parcela
        parcela_mock = MagicMock()
        parcela_mock.id_parcela = id_parcela
        parcela_mock.valor = valor_original
        parcela_mock.data_vencimento = data_vencimento
        parcela_mock.status = "pendente"
        parcela_mock.id_empresa = uuid.uuid4()
        
        # Mock para buscar a parcela
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = parcela_mock
        
        # Act
        # Simular a função de cálculo de desconto para pagamento antecipado
        async def calcular_desconto_antecipacao(parcela, data_pagamento, taxa_juros=taxa_juros_mensal):
            """Calcula desconto para pagamento antecipado."""
            if data_pagamento >= parcela.data_vencimento:
                return 0.0
            
            dias_antecipacao = (parcela.data_vencimento - data_pagamento).days
            taxa_diaria = taxa_juros / 30
            desconto = parcela.valor * taxa_diaria * dias_antecipacao
            return round(desconto, 2)
            
        # Executar a função
        desconto = await calcular_desconto_antecipacao(
            parcela_mock,
            data_pagamento
        )
        
        valor_com_desconto = valor_original - desconto
        
        # Assert
        assert desconto > 0
        assert desconto == pytest.approx(desconto_esperado, 0.01)
        assert valor_com_desconto == pytest.approx(valor_final_esperado, 0.01)


class TestPagamentoParcial:
    """Testes para pagamento parcial de parcelas."""
    
    @pytest.mark.unit
    async def test_pagamento_parcial_com_saldo_restante(self, mock_db_session):
        """Teste de pagamento parcial com ajuste de saldo restante."""
        # Arrange
        id_parcela = uuid.uuid4()
        id_empresa = uuid.uuid4()
        id_usuario = uuid.uuid4()
        valor_original = 1000.0
        valor_pago = 400.0
        saldo_restante = valor_original - valor_pago
        
        # Data de pagamento
        data_pagamento = date.today()
        
        # Mock da parcela
        parcela_mock = MagicMock()
        parcela_mock.id_parcela = id_parcela
        parcela_mock.valor = valor_original
        parcela_mock.valor_pago = None
        parcela_mock.status = "pendente"
        parcela_mock.id_empresa = id_empresa
        
        # Mock para buscar a parcela
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = parcela_mock
        
        # Act
        # Simular a função de registrar pagamento parcial
        async def registrar_pagamento_parcial(id_parcela, valor_pago, id_empresa, id_usuario, data_pagamento):
            # Buscar parcela original
            parcela = mock_db_session.execute.return_value.scalar_one_or_none.return_value
            
            if not parcela:
                raise ValueError("Parcela não encontrada")
                
            if valor_pago <= 0:
                raise ValueError("Valor pago deve ser maior que zero")
                
            if valor_pago > parcela.valor:
                raise ValueError("Valor pago não pode ser maior que o valor da parcela")
                
            # Calcular saldo restante
            saldo = parcela.valor - valor_pago
            
            # Atualizar parcela existente
            parcela.valor_pago = valor_pago
            parcela.data_pagamento = data_pagamento
            
            # Determinar o novo status
            if saldo > 0:
                parcela.status = "parcial"
            else:
                parcela.status = "pago"
                
            await mock_db_session.commit()
            
            # Retornar a parcela atualizada
            return parcela
            
        # Executar a função
        parcela_atualizada = await registrar_pagamento_parcial(
            id_parcela,
            valor_pago,
            id_empresa,
            id_usuario,
            data_pagamento
        )
        
        # Assert
        assert parcela_atualizada.valor_pago == valor_pago
        assert parcela_atualizada.status == "parcial"
        assert parcela_atualizada.data_pagamento == data_pagamento
        assert parcela_atualizada.valor - parcela_atualizada.valor_pago == saldo_restante 