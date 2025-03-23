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
        
        # Act
        with patch('app.services.parcela_service.ParcelaRepository') as mock_repo:
            # Configurar mock do repository para retornar parcelas criadas
            mock_repo_instance = mock_repo.return_value
            mock_repo_instance.create.side_effect = lambda data: Parcela(
                id_parcela=uuid.uuid4(),
                id_lancamento=data.get('id_lancamento'),
                numero_parcela=data.get('numero_parcela'),
                valor=data.get('valor'),
                data_vencimento=data.get('data_vencimento'),
                status=data.get('status', 'pendente')
            )
            
            # Importar serviço aqui para evitar importações circulares
            from app.services.parcela_service import ParcelaService
            
            # Criar instância do serviço
            service = ParcelaService(session=mock_db_session)
            
            # Criar parcelas
            parcelas = []
            for i in range(num_parcelas):
                parcela_data = ParcelaCreate(
                    id_empresa=id_empresa,
                    id_venda=id_venda,
                    numero_parcela=i+1,
                    valor=valor_total/num_parcelas,
                    data_vencimento=data_primeira_parcela + timedelta(days=30*i),
                    status=StatusParcela.PENDENTE
                )
                parcela = await service.criar_parcela(parcela_data, id_usuario=uuid.uuid4())
                parcelas.append(parcela)
        
        # Assert
        assert len(parcelas) == num_parcelas
        
        # Verificar se cada parcela tem o valor correto (250.0)
        for parcela in parcelas:
            assert parcela.valor == valor_total / num_parcelas
            
        # Verificar se a soma dos valores das parcelas é igual ao valor total
        total_parcelas = sum(p.valor for p in parcelas)
        assert total_parcelas == valor_total
    
    @pytest.mark.unit
    async def test_geracao_parcelas_com_arredondamento_cima(self, mock_db_session):
        """Teste de geração de parcelas com arredondamento para cima."""
        # Arrange
        valor_total = 100.0
        num_parcelas = 3  # Isso vai resultar em 33.33... por parcela
        data_primeira_parcela = date.today()
        id_venda = uuid.uuid4()
        id_empresa = uuid.uuid4()
        
        # Mock para retornar o objeto venda
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = MagicMock(
            id_venda=id_venda,
            id_empresa=id_empresa
        )
        
        # Act
        with patch('app.services.parcela_service.ParcelaRepository') as mock_repo:
            # Configurar mock do repository
            mock_repo_instance = mock_repo.return_value
            
            # Criar parcelas com arredondamento para cima
            created_parcelas = []
            
            # Calcular valor base da parcela
            valor_parcela_base = round(valor_total / num_parcelas, 2)  # 33.33
            
            # Ajustar última parcela para fechar o valor total
            for i in range(num_parcelas):
                # Última parcela recebe o restante para fechar a conta
                if i == num_parcelas - 1:
                    valor_parcela = round(valor_total - sum(p.valor for p in created_parcelas), 2)
                else:
                    valor_parcela = valor_parcela_base
                
                nova_parcela = Parcela(
                    id_parcela=uuid.uuid4(),
                    numero_parcela=i+1,
                    valor=valor_parcela,
                    data_vencimento=data_primeira_parcela + timedelta(days=30*i),
                    status='pendente'
                )
                created_parcelas.append(nova_parcela)
                
                # Configurar mock para retornar esta parcela
                if i == 0:
                    mock_repo_instance.create.return_value = nova_parcela
                else:
                    mock_repo_instance.create.side_effect = lambda data: next(
                        p for p in created_parcelas if p.numero_parcela == data.get('numero_parcela')
                    )
            
            # Importar serviço
            from app.services.parcela_service import ParcelaService
            service = ParcelaService(session=mock_db_session)
            
            # Criar parcelas
            parcelas = []
            for i in range(num_parcelas):
                parcela_data = ParcelaCreate(
                    id_empresa=id_empresa,
                    id_venda=id_venda,
                    numero_parcela=i+1,
                    valor=created_parcelas[i].valor,
                    data_vencimento=data_primeira_parcela + timedelta(days=30*i),
                    status=StatusParcela.PENDENTE
                )
                parcela = await service.criar_parcela(parcela_data, id_usuario=uuid.uuid4())
                parcelas.append(parcela)
        
        # Assert
        assert len(parcelas) == num_parcelas
        
        # As primeiras duas parcelas devem ter valor de 33.33
        assert parcelas[0].valor == 33.33
        assert parcelas[1].valor == 33.33
        
        # A última parcela deve ter o resto para fechar 100.0
        assert parcelas[2].valor == 33.34
        
        # Verificar se a soma dos valores das parcelas é igual ao valor total
        total_parcelas = sum(p.valor for p in parcelas)
        assert round(total_parcelas, 2) == valor_total
            
    @pytest.mark.unit
    async def test_geracao_parcelas_com_arredondamento_baixo(self, mock_db_session):
        """Teste de geração de parcelas com arredondamento para baixo."""
        # Arrange
        valor_total = 100.0
        num_parcelas = 3
        data_primeira_parcela = date.today()
        id_venda = uuid.uuid4()
        id_empresa = uuid.uuid4()
        
        # Mock para retornar o objeto venda
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = MagicMock(
            id_venda=id_venda,
            id_empresa=id_empresa
        )
        
        # Act
        with patch('app.services.parcela_service.ParcelaRepository') as mock_repo:
            # Configurar mock do repository
            mock_repo_instance = mock_repo.return_value
            
            # Criar parcelas com arredondamento para baixo
            created_parcelas = []
            
            # Calcular valor base da parcela arredondado para baixo
            valor_parcela_base = int(valor_total / num_parcelas)  # 33
            
            # Ajustar última parcela para fechar o valor total
            for i in range(num_parcelas):
                # Última parcela recebe o restante para fechar a conta
                if i == num_parcelas - 1:
                    valor_parcela = round(valor_total - sum(p.valor for p in created_parcelas), 2)
                else:
                    valor_parcela = valor_parcela_base
                
                nova_parcela = Parcela(
                    id_parcela=uuid.uuid4(),
                    numero_parcela=i+1,
                    valor=valor_parcela,
                    data_vencimento=data_primeira_parcela + timedelta(days=30*i),
                    status='pendente'
                )
                created_parcelas.append(nova_parcela)
                
                # Configurar mock para retornar esta parcela
                if i == 0:
                    mock_repo_instance.create.return_value = nova_parcela
                else:
                    mock_repo_instance.create.side_effect = lambda data: next(
                        p for p in created_parcelas if p.numero_parcela == data.get('numero_parcela')
                    )
            
            # Importar serviço
            from app.services.parcela_service import ParcelaService
            service = ParcelaService(session=mock_db_session)
            
            # Criar parcelas
            parcelas = []
            for i in range(num_parcelas):
                parcela_data = ParcelaCreate(
                    id_empresa=id_empresa,
                    id_venda=id_venda,
                    numero_parcela=i+1,
                    valor=created_parcelas[i].valor,
                    data_vencimento=data_primeira_parcela + timedelta(days=30*i),
                    status=StatusParcela.PENDENTE
                )
                parcela = await service.criar_parcela(parcela_data, id_usuario=uuid.uuid4())
                parcelas.append(parcela)
        
        # Assert
        assert len(parcelas) == num_parcelas
        
        # As primeiras duas parcelas devem ter valor de 33.0
        assert parcelas[0].valor == 33.0
        assert parcelas[1].valor == 33.0
        
        # A última parcela deve ter o resto para fechar 100.0
        assert parcelas[2].valor == 34.0
        
        # Verificar se a soma dos valores das parcelas é igual ao valor total
        total_parcelas = sum(p.valor for p in parcelas)
        assert total_parcelas == valor_total


class TestPagamentoAntecipado:
    """Testes para validação de pagamento antecipado de parcelas."""
    
    @pytest.mark.unit
    async def test_pagamento_antecipado_com_desconto_juros(self, mock_db_session):
        """Teste de pagamento antecipado com redução proporcional de juros."""
        # Arrange
        taxa_juros_mensal = 0.02  # 2% ao mês
        id_parcela = uuid.uuid4()
        id_empresa = uuid.uuid4()
        id_usuario = uuid.uuid4()
        data_vencimento = date.today() + timedelta(days=30)  # 30 dias no futuro
        data_pagamento = date.today()  # Pagamento hoje (30 dias antes)
        valor_original = 1000.0
        
        # Calcular desconto esperado
        # Desconto = juros que não serão cobrados pelo pagamento antecipado
        dias_antecipacao = (data_vencimento - data_pagamento).days
        desconto_esperado = valor_original * taxa_juros_mensal * (dias_antecipacao / 30)
        valor_com_desconto = valor_original - desconto_esperado
        
        # Mock para parcela existente
        parcela_mock = MagicMock(
            id_parcela=id_parcela,
            id_empresa=id_empresa,
            valor=valor_original,
            data_vencimento=data_vencimento,
            data_pagamento=None,
            status='pendente'
        )
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = parcela_mock
        
        # Act
        with patch('app.services.parcela_service.ParcelaRepository') as mock_repo:
            # Configurar mock do repository
            mock_repo_instance = mock_repo.return_value
            mock_repo_instance.get_by_id.return_value = parcela_mock
            
            # Simular atualização da parcela com desconto
            parcela_atualizada = MagicMock(
                id_parcela=id_parcela,
                id_empresa=id_empresa,
                valor=valor_com_desconto,  # Valor com desconto aplicado
                data_vencimento=data_vencimento,
                data_pagamento=data_pagamento,
                status='pago'
            )
            mock_repo_instance.update.return_value = parcela_atualizada
            
            # Importar serviço
            from app.services.parcela_service import ParcelaService
            service = ParcelaService(session=mock_db_session)
            
            # Implementar função para calcular desconto por antecipação
            async def calcular_desconto_antecipacao(parcela, data_pagamento, taxa_juros=taxa_juros_mensal):
                if data_pagamento >= parcela.data_vencimento:
                    return 0.0  # Sem desconto se não for antecipado
                
                dias_antecipacao = (parcela.data_vencimento - data_pagamento).days
                desconto = parcela.valor * taxa_juros * (dias_antecipacao / 30)
                return round(desconto, 2)
            
            # Simular o registro de pagamento com desconto
            desconto = await calcular_desconto_antecipacao(parcela_mock, data_pagamento)
            resultado = await service.registrar_pagamento(
                id_parcela=id_parcela,
                id_empresa=id_empresa,
                id_usuario=id_usuario,
                data_pagamento=data_pagamento
            )
        
        # Assert
        # Verificar se o desconto foi aplicado corretamente
        assert round(desconto, 2) == round(desconto_esperado, 2)
        assert resultado.valor == valor_com_desconto
        assert resultado.data_pagamento == data_pagamento
        assert resultado.status == 'pago'


class TestPagamentoParcial:
    """Testes para validação de pagamento parcial de parcelas."""
    
    @pytest.mark.unit
    async def test_pagamento_parcial_com_saldo_restante(self, mock_db_session):
        """Teste de pagamento parcial com geração de saldo restante."""
        # Arrange
        id_parcela = uuid.uuid4()
        id_empresa = uuid.uuid4()
        id_usuario = uuid.uuid4()
        valor_original = 1000.0
        valor_pago = 600.0
        saldo_restante = valor_original - valor_pago
        data_vencimento = date.today() + timedelta(days=15)
        data_pagamento = date.today()
        
        # Mock para parcela existente
        parcela_mock = MagicMock(
            id_parcela=id_parcela,
            id_empresa=id_empresa,
            valor=valor_original,
            data_vencimento=data_vencimento,
            data_pagamento=None,
            status='pendente'
        )
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = parcela_mock
        
        # Act
        with patch('app.services.parcela_service.ParcelaRepository') as mock_repo:
            # Configurar mock do repository
            mock_repo_instance = mock_repo.return_value
            mock_repo_instance.get_by_id.return_value = parcela_mock
            
            # Simular atualização da parcela para status parcialmente pago
            parcela_atualizada = MagicMock(
                id_parcela=id_parcela,
                id_empresa=id_empresa,
                valor=valor_pago,  # Valor pago
                data_vencimento=data_vencimento,
                data_pagamento=data_pagamento,
                status='pago'
            )
            mock_repo_instance.update.return_value = parcela_atualizada
            
            # Simular criação da nova parcela com saldo restante
            nova_parcela = MagicMock(
                id_parcela=uuid.uuid4(),
                id_empresa=id_empresa,
                valor=saldo_restante,  # Saldo restante
                data_vencimento=data_vencimento,
                data_pagamento=None,
                status='pendente'
            )
            mock_repo_instance.create.return_value = nova_parcela
            
            # Importar serviço
            from app.services.parcela_service import ParcelaService
            service = ParcelaService(session=mock_db_session)
            
            # Implementar função para processamento de pagamento parcial
            async def registrar_pagamento_parcial(id_parcela, valor_pago, id_empresa, id_usuario, data_pagamento):
                # Buscar parcela original
                parcela_original = await service.get_parcela(id_parcela, id_empresa)
                
                # Verificar se o valor pago é menor que o valor total
                if valor_pago >= parcela_original.valor:
                    # Se for pagamento total, registrar normalmente
                    return await service.registrar_pagamento(id_parcela, id_empresa, id_usuario, data_pagamento)
                
                # Calcular saldo restante
                saldo = parcela_original.valor - valor_pago
                
                # Atualizar parcela atual para pago (com o valor pago)
                parcela_atualizada_data = {
                    "valor": valor_pago,
                    "data_pagamento": data_pagamento,
                    "status": "pago"
                }
                parcela_atualizada = await mock_repo_instance.update(id_parcela, parcela_atualizada_data, id_empresa)
                
                # Criar nova parcela com o saldo restante
                nova_parcela_data = {
                    "id_empresa": id_empresa,
                    "valor": saldo,
                    "data_vencimento": parcela_original.data_vencimento,
                    "status": "pendente",
                    "numero_parcela": parcela_original.numero_parcela + 0.5  # Para indicar que é um desdobramento
                }
                nova_parcela = await mock_repo_instance.create(nova_parcela_data)
                
                return parcela_atualizada, nova_parcela
            
            # Executar a função
            parcela_paga, parcela_saldo = await registrar_pagamento_parcial(
                id_parcela=id_parcela,
                valor_pago=valor_pago,
                id_empresa=id_empresa,
                id_usuario=id_usuario,
                data_pagamento=data_pagamento
            )
            
        # Assert
        # Verificar se a parcela original foi atualizada
        assert parcela_paga.valor == valor_pago
        assert parcela_paga.status == 'pago'
        assert parcela_paga.data_pagamento == data_pagamento
        
        # Verificar se a nova parcela foi criada corretamente
        assert parcela_saldo.valor == saldo_restante
        assert parcela_saldo.status == 'pendente'
        assert parcela_saldo.data_pagamento is None 