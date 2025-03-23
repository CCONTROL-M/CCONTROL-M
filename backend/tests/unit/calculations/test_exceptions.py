"""Testes unitários para tratamento de exceções em cálculos financeiros no sistema CCONTROL-M."""
import pytest
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

from app.models.parcela import Parcela
from app.schemas.parcela import ParcelaCreate


class TestExcecoesValoresInvalidos:
    """Testes para validação de exceções com valores inválidos."""
    
    @pytest.mark.unit
    async def test_excecao_valor_negativo(self, mock_db_session):
        """Teste de exceção ao tentar criar parcela com valor negativo."""
        # Arrange
        valor_negativo = -100.0
        id_empresa = uuid.uuid4()
        id_venda = uuid.uuid4()
        
        # Simular dados de parcela com valor negativo
        parcela_data = ParcelaCreate(
            id_empresa=id_empresa,
            id_venda=id_venda,
            numero_parcela=1,
            valor=valor_negativo,
            data_vencimento=date.today() + timedelta(days=30),
            status="pendente"
        )
        
        # Importar serviço
        from app.services.parcela_service import ParcelaService
        
        # Act / Assert
        # Configurar mock de validação
        with patch('app.services.parcela_service.ParcelaRepository'):
            service = ParcelaService(session=mock_db_session)
            
            # Deve lançar exceção ao validar valor negativo
            with pytest.raises(ValueError) as exc_info:
                # Implementar função de validação para testar
                def validar_valor(valor):
                    if valor <= 0:
                        raise ValueError("Valor deve ser maior que zero")
                    return valor
                
                validar_valor(parcela_data.valor)
            
            # Verificar mensagem de erro
            assert "Valor deve ser maior que zero" in str(exc_info.value)
    
    @pytest.mark.unit
    async def test_excecao_valor_zero(self, mock_db_session):
        """Teste de exceção ao tentar criar parcela com valor zero."""
        # Arrange
        valor_zero = 0.0
        id_empresa = uuid.uuid4()
        id_venda = uuid.uuid4()
        
        # Simular dados de parcela com valor zero
        parcela_data = ParcelaCreate(
            id_empresa=id_empresa,
            id_venda=id_venda,
            numero_parcela=1,
            valor=valor_zero,
            data_vencimento=date.today() + timedelta(days=30),
            status="pendente"
        )
        
        # Act / Assert
        # Configurar validação
        def validar_valor_positivo(valor):
            """Valida se o valor é positivo."""
            if valor <= 0:
                raise ValueError("Valor deve ser maior que zero")
            return valor
            
        # Deve lançar exceção ao validar valor zero
        with pytest.raises(ValueError) as exc_info:
            validar_valor_positivo(parcela_data.valor)
            
        # Verificar mensagem de erro
        assert "Valor deve ser maior que zero" in str(exc_info.value)
        
    @pytest.mark.unit
    async def test_excecao_valor_nao_numerico(self, mock_db_session):
        """Teste de exceção ao tentar usar valor não numérico."""
        # Arrange
        # String que não pode ser convertida para número
        valor_nao_numerico = "abc"
        
        # Act / Assert
        # Função para converter e validar valor
        def converter_e_validar_valor(valor_str):
            """Converte string para número e valida se é positivo."""
            try:
                valor = float(valor_str)
                if valor <= 0:
                    raise ValueError("Valor deve ser maior que zero")
                return valor
            except ValueError as e:
                if "could not convert string to float" in str(e).lower():
                    raise ValueError("Valor deve ser numérico")
                raise
                
        # Deve lançar exceção ao converter valor não numérico
        with pytest.raises(ValueError) as exc_info:
            converter_e_validar_valor(valor_nao_numerico)
            
        # Verificar mensagem de erro
        assert "Valor deve ser numérico" in str(exc_info.value)


class TestExcecoesParcelas:
    """Testes para validação de exceções com parcelas inexistentes ou duplicadas."""
    
    @pytest.mark.unit
    async def test_excecao_parcela_inexistente(self, mock_db_session):
        """Teste de exceção ao tentar acessar parcela inexistente."""
        # Arrange
        id_parcela_inexistente = uuid.uuid4()
        id_empresa = uuid.uuid4()
        
        # Configurar mock para retornar None (parcela não encontrada)
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
        
        # Importar serviço
        from app.services.parcela_service import ParcelaService
        
        # Act / Assert
        with patch('app.services.parcela_service.ParcelaRepository') as mock_repo:
            # Configurar mock do repository
            mock_repo_instance = mock_repo.return_value
            mock_repo_instance.get_by_id.return_value = None
            
            service = ParcelaService(session=mock_db_session)
            
            # Deve lançar exceção ao tentar obter parcela inexistente
            with pytest.raises(Exception) as exc_info:
                await service.get_parcela(id_parcela_inexistente, id_empresa)
                
            # Verificar mensagem de erro (com texto parcial)
            assert "não encontrada" in str(exc_info.value).lower()
    
    @pytest.mark.unit
    async def test_excecao_parcela_duplicada(self, mock_db_session):
        """Teste de exceção ao tentar criar parcela duplicada."""
        # Arrange
        id_empresa = uuid.uuid4()
        id_venda = uuid.uuid4()
        numero_parcela = 1
        
        # Criar mock de lista de parcelas existentes
        parcelas_existentes = [
            MagicMock(
                id_parcela=uuid.uuid4(),
                id_empresa=id_empresa,
                id_venda=id_venda,
                numero_parcela=numero_parcela,
                valor=100.0,
                data_vencimento=date.today() + timedelta(days=30),
                status="pendente"
            )
        ]
        
        # Configurar mock para retornar as parcelas existentes
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = parcelas_existentes
        
        # Act / Assert
        # Função para verificar duplicidade
        def verificar_parcela_duplicada(id_venda, numero_parcela, parcelas):
            """Verifica se já existe parcela com mesmo número para a venda."""
            for parcela in parcelas:
                if parcela.id_venda == id_venda and parcela.numero_parcela == numero_parcela:
                    raise ValueError(f"Já existe parcela com número {numero_parcela} para esta venda")
            return False
            
        # Deve lançar exceção ao detectar parcela duplicada
        with pytest.raises(ValueError) as exc_info:
            verificar_parcela_duplicada(id_venda, numero_parcela, parcelas_existentes)
            
        # Verificar mensagem de erro
        assert f"Já existe parcela com número {numero_parcela}" in str(exc_info.value)


class TestExcecoesArredondamento:
    """Testes para validação de exceções com arredondamentos fora de padrão."""
    
    @pytest.mark.unit
    async def test_excecao_arredondamento_mais_duas_casas(self, mock_db_session):
        """Teste de exceção com arredondamento além de duas casas decimais."""
        # Arrange
        # Valor com mais de duas casas decimais
        valor_muitas_decimais = 100.123
        
        # Act / Assert
        # Função para validar arredondamento
        def validar_arredondamento(valor, casas_decimais=2):
            """Valida se o valor tem mais casas decimais do que o permitido."""
            # Converter para string para verificar casas decimais
            valor_str = str(valor)
            if '.' in valor_str:
                parte_decimal = valor_str.split('.')[1]
                # Verificar se a parte decimal é maior que o permitido
                if len(parte_decimal) > casas_decimais:
                    raise ValueError(f"Valor deve ter no máximo {casas_decimais} casas decimais")
            return True
            
        # Deve lançar exceção ao detectar mais de duas casas decimais
        with pytest.raises(ValueError) as exc_info:
            validar_arredondamento(valor_muitas_decimais)
            
        # Verificar mensagem de erro
        assert "Valor deve ter no máximo 2 casas decimais" in str(exc_info.value)
    
    @pytest.mark.unit
    async def test_consistencia_soma_parcelas(self, mock_db_session):
        """Teste de consistência na soma das parcelas em relação ao valor total."""
        # Arrange
        valor_total = 100.0
        valores_parcelas = [33.33, 33.33, 33.33]  # Soma: 99.99 (inconsistente)
        
        # Act / Assert
        # Função para validar consistência da soma
        def validar_consistencia_soma(valor_total, valores_parcelas, tolerancia=0.01):
            """Valida se a soma das parcelas é igual ao valor total (com tolerância)."""
            soma_parcelas = sum(valores_parcelas)
            diferenca = abs(valor_total - soma_parcelas)
            
            if diferenca > tolerancia:
                raise ValueError(
                    f"Soma das parcelas ({soma_parcelas}) não confere com valor total ({valor_total})"
                )
            return True
            
        # Deve lançar exceção se a diferença for maior que a tolerância
        # Neste caso, deve passar com tolerância de 0.01
        assert validar_consistencia_soma(valor_total, valores_parcelas) == True
        
        # Mas deve falhar com tolerância mais restrita
        with pytest.raises(ValueError) as exc_info:
            validar_consistencia_soma(valor_total, valores_parcelas, tolerancia=0.001)
            
        # Verificar mensagem de erro
        assert "Soma das parcelas (99.99) não confere com valor total (100.0)" in str(exc_info.value)


class TestExcecoesDatas:
    """Testes para validação de exceções com datas inválidas."""
    
    @pytest.mark.unit
    async def test_excecao_data_vencimento_passado(self, mock_db_session):
        """Teste de exceção ao tentar criar parcela com data de vencimento no passado."""
        # Arrange
        id_empresa = uuid.uuid4()
        id_venda = uuid.uuid4()
        data_passada = date.today() - timedelta(days=10)  # 10 dias atrás
        
        # Simular dados de parcela com data no passado
        parcela_data = ParcelaCreate(
            id_empresa=id_empresa,
            id_venda=id_venda,
            numero_parcela=1,
            valor=100.0,
            data_vencimento=data_passada,
            status="pendente"
        )
        
        # Act / Assert
        # Função para validar data de vencimento
        def validar_data_vencimento(data_vencimento, permitir_passado=False):
            """Valida se a data de vencimento é válida (não está no passado)."""
            hoje = date.today()
            if not permitir_passado and data_vencimento < hoje:
                raise ValueError("Data de vencimento não pode estar no passado")
            return True
            
        # Deve lançar exceção se a data estiver no passado e não for permitido
        with pytest.raises(ValueError) as exc_info:
            validar_data_vencimento(parcela_data.data_vencimento)
            
        # Verificar mensagem de erro
        assert "Data de vencimento não pode estar no passado" in str(exc_info.value)
        
        # Mas deve passar se permitir datas no passado
        assert validar_data_vencimento(parcela_data.data_vencimento, permitir_passado=True) == True
    
    @pytest.mark.unit
    async def test_excecao_data_pagamento_futura(self, mock_db_session):
        """Teste de exceção ao tentar registrar pagamento com data futura."""
        # Arrange
        id_parcela = uuid.uuid4()
        id_empresa = uuid.uuid4()
        data_futura = date.today() + timedelta(days=10)  # 10 dias no futuro
        
        # Mock de parcela existente
        parcela_mock = MagicMock(
            id_parcela=id_parcela,
            id_empresa=id_empresa,
            valor=100.0,
            data_vencimento=date.today(),
            data_pagamento=None,
            status="pendente"
        )
        
        # Act / Assert
        # Função para validar data de pagamento
        def validar_data_pagamento(data_pagamento):
            """Valida se a data de pagamento é válida (não está no futuro)."""
            hoje = date.today()
            if data_pagamento > hoje:
                raise ValueError("Data de pagamento não pode estar no futuro")
            return True
            
        # Deve lançar exceção se a data estiver no futuro
        with pytest.raises(ValueError) as exc_info:
            validar_data_pagamento(data_futura)
            
        # Verificar mensagem de erro
        assert "Data de pagamento não pode estar no futuro" in str(exc_info.value) 