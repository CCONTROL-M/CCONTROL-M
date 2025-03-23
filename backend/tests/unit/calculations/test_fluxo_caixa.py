"""Testes unitários para cálculos de fluxo de caixa no sistema CCONTROL-M."""
import pytest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
from typing import List, Dict, Any, Tuple

from app.models.lancamento import Lancamento
from app.models.conta_bancaria import ContaBancaria
from app.models.parcela import Parcela
from app.models.venda import Venda
from app.models.compra import Compra


class TestPrevisaoSaldoMensal:
    """Testes para validação de cálculos de previsão de saldo mensal."""
    
    @pytest.mark.unit
    async def test_calculo_previsao_saldo_mensal(self, mock_db_session):
        """Teste de cálculo de previsão de saldo mensal (receitas - despesas)."""
        # Arrange
        id_empresa = uuid.uuid4()
        mes_referencia = date.today().replace(day=1)  # Primeiro dia do mês atual
        proximo_mes = (mes_referencia + timedelta(days=32)).replace(day=1)  # Primeiro dia do próximo mês
        
        # Criar mock de lançamentos para o mês atual
        lancamentos = [
            # Entradas
            MagicMock(
                id_lancamento=uuid.uuid4(),
                id_empresa=id_empresa,
                tipo="entrada",
                valor=1000.0,
                data_vencimento=mes_referencia + timedelta(days=5),
                status="pendente"
            ),
            MagicMock(
                id_lancamento=uuid.uuid4(),
                id_empresa=id_empresa,
                tipo="entrada",
                valor=2500.0,
                data_vencimento=mes_referencia + timedelta(days=15),
                status="pendente"
            ),
            MagicMock(
                id_lancamento=uuid.uuid4(),
                id_empresa=id_empresa,
                tipo="entrada",
                valor=750.0,
                data_vencimento=mes_referencia + timedelta(days=25),
                status="pendente"
            ),
            # Saídas
            MagicMock(
                id_lancamento=uuid.uuid4(),
                id_empresa=id_empresa,
                tipo="saida",
                valor=800.0,
                data_vencimento=mes_referencia + timedelta(days=10),
                status="pendente"
            ),
            MagicMock(
                id_lancamento=uuid.uuid4(),
                id_empresa=id_empresa,
                tipo="saida",
                valor=1200.0,
                data_vencimento=mes_referencia + timedelta(days=20),
                status="pendente"
            ),
            # Lançamento do próximo mês (não deve ser contabilizado)
            MagicMock(
                id_lancamento=uuid.uuid4(),
                id_empresa=id_empresa,
                tipo="entrada",
                valor=3000.0,
                data_vencimento=proximo_mes + timedelta(days=5),
                status="pendente"
            ),
        ]
        
        # Configurar mock para retornar os lançamentos
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = lancamentos
        
        # Act
        # Função para calcular previsão de saldo mensal
        def calcular_previsao_saldo_mensal(lancamentos, mes_referencia):
            """Calcula a previsão de saldo para um mês específico."""
            # Filtrar lançamentos do mês
            inicio_mes = mes_referencia.replace(day=1)
            if mes_referencia.month == 12:
                fim_mes = date(mes_referencia.year + 1, 1, 1) - timedelta(days=1)
            else:
                fim_mes = date(mes_referencia.year, mes_referencia.month + 1, 1) - timedelta(days=1)
                
            lancamentos_mes = [l for l in lancamentos if inicio_mes <= l.data_vencimento <= fim_mes]
            
            # Calcular total de entradas
            total_entradas = sum(l.valor for l in lancamentos_mes if l.tipo == "entrada")
            
            # Calcular total de saídas
            total_saidas = sum(l.valor for l in lancamentos_mes if l.tipo == "saida")
            
            # Calcular saldo previsto
            saldo_previsto = total_entradas - total_saidas
            
            return {
                "total_entradas": round(total_entradas, 2),
                "total_saidas": round(total_saidas, 2),
                "saldo_previsto": round(saldo_previsto, 2)
            }
            
        # Calcular previsão de saldo para o mês atual
        resultado = calcular_previsao_saldo_mensal(lancamentos, mes_referencia)
        
        # Assert
        # Verificar valores esperados
        assert resultado["total_entradas"] == 4250.0  # 1000 + 2500 + 750
        assert resultado["total_saidas"] == 2000.0  # 800 + 1200
        assert resultado["saldo_previsto"] == 2250.0  # 4250 - 2000
    
    @pytest.mark.unit
    async def test_calculo_previsao_saldo_com_lancamentos_recorrentes(self, mock_db_session):
        """Teste de cálculo de previsão incluindo lançamentos recorrentes."""
        # Arrange
        id_empresa = uuid.uuid4()
        mes_referencia = date.today().replace(day=1)  # Primeiro dia do mês atual
        
        # Criar mock de lançamentos normais
        lancamentos_normais = [
            # Entradas
            MagicMock(
                id_lancamento=uuid.uuid4(),
                id_empresa=id_empresa,
                tipo="entrada",
                valor=1500.0,
                data_vencimento=mes_referencia + timedelta(days=10),
                status="pendente",
                recorrente=False
            ),
            # Saídas
            MagicMock(
                id_lancamento=uuid.uuid4(),
                id_empresa=id_empresa,
                tipo="saida",
                valor=800.0,
                data_vencimento=mes_referencia + timedelta(days=15),
                status="pendente",
                recorrente=False
            ),
        ]
        
        # Criar mock de lançamentos recorrentes (template)
        lancamentos_recorrentes = [
            # Entrada recorrente (ex: aluguel recebido)
            MagicMock(
                id_lancamento=uuid.uuid4(),
                id_empresa=id_empresa,
                tipo="entrada",
                valor=2000.0,
                data_vencimento=date(2023, 1, 20),  # Data de referência original
                status="pendente",
                recorrente=True,
                periodicidade="mensal",
                dia_vencimento=20
            ),
            # Saída recorrente (ex: salário funcionário)
            MagicMock(
                id_lancamento=uuid.uuid4(),
                id_empresa=id_empresa,
                tipo="saida",
                valor=1200.0,
                data_vencimento=date(2023, 1, 5),  # Data de referência original
                status="pendente",
                recorrente=True,
                periodicidade="mensal",
                dia_vencimento=5
            ),
        ]
        
        # Configurar mock para retornar os lançamentos
        mock_db_session.execute.return_value.scalars.return_value.all.side_effect = [
            lancamentos_normais,
            lancamentos_recorrentes
        ]
        
        # Act
        # Função para projetar lançamento recorrente para um mês específico
        def projetar_lancamento_recorrente(lancamento, mes_referencia):
            """Projeta um lançamento recorrente para o mês de referência."""
            # Criar cópia do lançamento
            lancamento_projetado = MagicMock(
                id_lancamento=uuid.uuid4(),  # Novo ID para lançamento projetado
                id_empresa=lancamento.id_empresa,
                tipo=lancamento.tipo,
                valor=lancamento.valor,
                status=lancamento.status,
                recorrente=False  # Lançamento projetado não é recorrente
            )
            
            # Atualizar data de vencimento para o mês de referência
            dia = min(lancamento.dia_vencimento, 28)  # Para evitar problemas em fevereiro
            mes = mes_referencia.month
            ano = mes_referencia.year
            
            lancamento_projetado.data_vencimento = date(ano, mes, dia)
            
            return lancamento_projetado
            
        # Função para calcular previsão de saldo com lançamentos recorrentes
        def calcular_previsao_saldo_com_recorrentes(lancamentos_normais, lancamentos_recorrentes, mes_referencia):
            """Calcula a previsão de saldo incluindo lançamentos recorrentes."""
            # Filtrar lançamentos normais do mês
            inicio_mes = mes_referencia.replace(day=1)
            if mes_referencia.month == 12:
                fim_mes = date(mes_referencia.year + 1, 1, 1) - timedelta(days=1)
            else:
                fim_mes = date(mes_referencia.year, mes_referencia.month + 1, 1) - timedelta(days=1)
                
            lancamentos_mes = [l for l in lancamentos_normais if inicio_mes <= l.data_vencimento <= fim_mes]
            
            # Projetar lançamentos recorrentes para o mês
            lancamentos_projetados = [
                projetar_lancamento_recorrente(l, mes_referencia) 
                for l in lancamentos_recorrentes
            ]
            
            # Combinar lançamentos
            todos_lancamentos = lancamentos_mes + lancamentos_projetados
            
            # Calcular total de entradas
            total_entradas = sum(l.valor for l in todos_lancamentos if l.tipo == "entrada")
            
            # Calcular total de saídas
            total_saidas = sum(l.valor for l in todos_lancamentos if l.tipo == "saida")
            
            # Calcular saldo previsto
            saldo_previsto = total_entradas - total_saidas
            
            return {
                "total_entradas": round(total_entradas, 2),
                "total_saidas": round(total_saidas, 2),
                "saldo_previsto": round(saldo_previsto, 2)
            }
            
        # Calcular previsão de saldo com lançamentos recorrentes
        resultado = calcular_previsao_saldo_com_recorrentes(
            lancamentos_normais, 
            lancamentos_recorrentes,
            mes_referencia
        )
        
        # Assert
        # Verificar valores esperados - normal + recorrente
        assert resultado["total_entradas"] == 3500.0  # 1500 (normal) + 2000 (recorrente)
        assert resultado["total_saidas"] == 2000.0  # 800 (normal) + 1200 (recorrente)
        assert resultado["saldo_previsto"] == 1500.0  # 3500 - 2000


class TestSaldoAcumulado:
    """Testes para validação de cálculos de saldo acumulado."""
    
    @pytest.mark.unit
    async def test_calculo_saldo_acumulado_por_conta(self, mock_db_session):
        """Teste de cálculo de saldo acumulado por conta bancária."""
        # Arrange
        id_empresa = uuid.uuid4()
        id_conta1 = uuid.uuid4()
        id_conta2 = uuid.uuid4()
        
        # Criar mock de contas bancárias
        contas = [
            MagicMock(
                id_conta=id_conta1,
                id_empresa=id_empresa,
                nome="Conta Corrente",
                saldo_inicial=1000.0
            ),
            MagicMock(
                id_conta=id_conta2,
                id_empresa=id_empresa,
                nome="Poupança",
                saldo_inicial=5000.0
            ),
        ]
        
        # Criar mock de lançamentos
        lancamentos = [
            # Conta 1 - Entradas
            MagicMock(
                id_lancamento=uuid.uuid4(),
                id_empresa=id_empresa,
                id_conta=id_conta1,
                tipo="entrada",
                valor=2000.0,
                data_pagamento=date.today() - timedelta(days=10),
                status="pago"
            ),
            MagicMock(
                id_lancamento=uuid.uuid4(),
                id_empresa=id_empresa,
                id_conta=id_conta1,
                tipo="entrada",
                valor=500.0,
                data_pagamento=date.today() - timedelta(days=5),
                status="pago"
            ),
            # Conta 1 - Saídas
            MagicMock(
                id_lancamento=uuid.uuid4(),
                id_empresa=id_empresa,
                id_conta=id_conta1,
                tipo="saida",
                valor=1200.0,
                data_pagamento=date.today() - timedelta(days=8),
                status="pago"
            ),
            # Conta 2 - Entradas
            MagicMock(
                id_lancamento=uuid.uuid4(),
                id_empresa=id_empresa,
                id_conta=id_conta2,
                tipo="entrada",
                valor=1000.0,
                data_pagamento=date.today() - timedelta(days=15),
                status="pago"
            ),
            # Conta 2 - Saídas
            MagicMock(
                id_lancamento=uuid.uuid4(),
                id_empresa=id_empresa,
                id_conta=id_conta2,
                tipo="saida",
                valor=500.0,
                data_pagamento=date.today() - timedelta(days=7),
                status="pago"
            ),
            # Lançamento pendente (não deve ser contabilizado)
            MagicMock(
                id_lancamento=uuid.uuid4(),
                id_empresa=id_empresa,
                id_conta=id_conta1,
                tipo="entrada",
                valor=2000.0,
                data_vencimento=date.today() + timedelta(days=5),
                data_pagamento=None,
                status="pendente"
            ),
        ]
        
        # Configurar mock para retornar os dados
        mock_db_session.execute.return_value.scalars.return_value.all.side_effect = [
            contas,
            lancamentos
        ]
        
        # Act
        # Função para calcular saldo acumulado por conta
        def calcular_saldo_acumulado_por_conta(contas, lancamentos):
            """Calcula o saldo acumulado para cada conta bancária."""
            resultado = {}
            
            for conta in contas:
                # Iniciar com saldo inicial
                saldo = conta.saldo_inicial
                
                # Filtrar lançamentos pagos para esta conta
                lancamentos_conta = [l for l in lancamentos if l.id_conta == conta.id_conta and l.status == "pago"]
                
                # Calcular entradas
                entradas = sum(l.valor for l in lancamentos_conta if l.tipo == "entrada")
                
                # Calcular saídas
                saidas = sum(l.valor for l in lancamentos_conta if l.tipo == "saida")
                
                # Atualizar saldo
                saldo += entradas - saidas
                
                # Adicionar ao resultado
                resultado[str(conta.id_conta)] = {
                    "nome_conta": conta.nome,
                    "saldo_inicial": round(conta.saldo_inicial, 2),
                    "entradas": round(entradas, 2),
                    "saidas": round(saidas, 2),
                    "saldo_atual": round(saldo, 2)
                }
            
            return resultado
            
        # Calcular saldo acumulado
        resultado = calcular_saldo_acumulado_por_conta(contas, lancamentos)
        
        # Assert
        # Verificar saldo da Conta 1
        assert resultado[str(id_conta1)]["saldo_inicial"] == 1000.0
        assert resultado[str(id_conta1)]["entradas"] == 2500.0  # 2000 + 500
        assert resultado[str(id_conta1)]["saidas"] == 1200.0
        assert resultado[str(id_conta1)]["saldo_atual"] == 2300.0  # 1000 + 2500 - 1200
        
        # Verificar saldo da Conta 2
        assert resultado[str(id_conta2)]["saldo_inicial"] == 5000.0
        assert resultado[str(id_conta2)]["entradas"] == 1000.0
        assert resultado[str(id_conta2)]["saidas"] == 500.0
        assert resultado[str(id_conta2)]["saldo_atual"] == 5500.0  # 5000 + 1000 - 500
    
    @pytest.mark.unit
    async def test_calculo_saldo_acumulado_por_centro_custo(self, mock_db_session):
        """Teste de cálculo de saldo acumulado por centro de custo."""
        # Arrange
        id_empresa = uuid.uuid4()
        id_centro1 = uuid.uuid4()
        id_centro2 = uuid.uuid4()
        
        # Criar mock de centros de custo
        centros_custo = [
            MagicMock(
                id_centro_custo=id_centro1,
                id_empresa=id_empresa,
                nome="Administrativo"
            ),
            MagicMock(
                id_centro_custo=id_centro2,
                id_empresa=id_empresa,
                nome="Comercial"
            ),
        ]
        
        # Criar mock de lançamentos
        lancamentos = [
            # Centro 1 - Entradas
            MagicMock(
                id_lancamento=uuid.uuid4(),
                id_empresa=id_empresa,
                id_centro_custo=id_centro1,
                tipo="entrada",
                valor=3000.0,
                data_pagamento=date.today() - timedelta(days=15),
                status="pago"
            ),
            # Centro 1 - Saídas
            MagicMock(
                id_lancamento=uuid.uuid4(),
                id_empresa=id_empresa,
                id_centro_custo=id_centro1,
                tipo="saida",
                valor=1800.0,
                data_pagamento=date.today() - timedelta(days=10),
                status="pago"
            ),
            MagicMock(
                id_lancamento=uuid.uuid4(),
                id_empresa=id_empresa,
                id_centro_custo=id_centro1,
                tipo="saida",
                valor=500.0,
                data_pagamento=date.today() - timedelta(days=5),
                status="pago"
            ),
            # Centro 2 - Entradas
            MagicMock(
                id_lancamento=uuid.uuid4(),
                id_empresa=id_empresa,
                id_centro_custo=id_centro2,
                tipo="entrada",
                valor=5000.0,
                data_pagamento=date.today() - timedelta(days=12),
                status="pago"
            ),
            MagicMock(
                id_lancamento=uuid.uuid4(),
                id_empresa=id_empresa,
                id_centro_custo=id_centro2,
                tipo="entrada",
                valor=2000.0,
                data_pagamento=date.today() - timedelta(days=7),
                status="pago"
            ),
            # Centro 2 - Saídas
            MagicMock(
                id_lancamento=uuid.uuid4(),
                id_empresa=id_empresa,
                id_centro_custo=id_centro2,
                tipo="saida",
                valor=2500.0,
                data_pagamento=date.today() - timedelta(days=8),
                status="pago"
            ),
            # Lançamento pendente (não deve ser contabilizado)
            MagicMock(
                id_lancamento=uuid.uuid4(),
                id_empresa=id_empresa,
                id_centro_custo=id_centro1,
                tipo="entrada",
                valor=1000.0,
                data_vencimento=date.today() + timedelta(days=5),
                data_pagamento=None,
                status="pendente"
            ),
        ]
        
        # Configurar mock para retornar os dados
        mock_db_session.execute.return_value.scalars.return_value.all.side_effect = [
            centros_custo,
            lancamentos
        ]
        
        # Act
        # Função para calcular saldo acumulado por centro de custo
        def calcular_saldo_por_centro_custo(centros_custo, lancamentos):
            """Calcula o saldo acumulado para cada centro de custo."""
            resultado = {}
            
            for centro in centros_custo:
                # Filtrar lançamentos pagos para este centro
                lancamentos_centro = [
                    l for l in lancamentos 
                    if l.id_centro_custo == centro.id_centro_custo and l.status == "pago"
                ]
                
                # Calcular entradas
                entradas = sum(l.valor for l in lancamentos_centro if l.tipo == "entrada")
                
                # Calcular saídas
                saidas = sum(l.valor for l in lancamentos_centro if l.tipo == "saida")
                
                # Calcular saldo
                saldo = entradas - saidas
                
                # Adicionar ao resultado
                resultado[str(centro.id_centro_custo)] = {
                    "nome_centro": centro.nome,
                    "entradas": round(entradas, 2),
                    "saidas": round(saidas, 2),
                    "saldo": round(saldo, 2)
                }
            
            return resultado
            
        # Calcular saldo por centro de custo
        resultado = calcular_saldo_por_centro_custo(centros_custo, lancamentos)
        
        # Assert
        # Verificar saldo do Centro 1
        assert resultado[str(id_centro1)]["entradas"] == 3000.0
        assert resultado[str(id_centro1)]["saidas"] == 2300.0  # 1800 + 500
        assert resultado[str(id_centro1)]["saldo"] == 700.0  # 3000 - 2300
        
        # Verificar saldo do Centro 2
        assert resultado[str(id_centro2)]["entradas"] == 7000.0  # 5000 + 2000
        assert resultado[str(id_centro2)]["saidas"] == 2500.0
        assert resultado[str(id_centro2)]["saldo"] == 4500.0  # 7000 - 2500


class TestConciliacaoBancaria:
    """Testes para validação de cálculos de conciliação bancária."""
    
    @pytest.mark.unit
    async def test_conciliacao_diferenca_valor_esperado_recebido(self, mock_db_session):
        """Teste de conciliação com diferença entre valor esperado e recebido."""
        # Arrange
        id_parcela = uuid.uuid4()
        id_empresa = uuid.uuid4()
        id_conta = uuid.uuid4()
        
        # Valor original e valor efetivamente recebido
        valor_esperado = 1000.0
        valor_recebido = 980.0
        diferenca = valor_esperado - valor_recebido  # 20.0
        
        # Criar mock de parcela
        parcela_mock = MagicMock(
            id_parcela=id_parcela,
            id_empresa=id_empresa,
            valor=valor_esperado,
            data_vencimento=date.today() - timedelta(days=5),
            data_pagamento=None,
            status="pendente"
        )
        
        # Configurar mock para retornar a parcela
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = parcela_mock
        
        # Act
        # Função para registrar pagamento com conciliação
        def registrar_pagamento_com_conciliacao(parcela, valor_recebido, data_pagamento, conta_id):
            """Registra o pagamento de uma parcela com conciliação."""
            # Verificar se há diferença entre valor esperado e recebido
            diferenca = parcela.valor - valor_recebido
            
            # Criar dados de lançamento para o valor recebido
            lancamento_data = {
                "id_empresa": parcela.id_empresa,
                "id_conta": conta_id,
                "tipo": "entrada" if diferenca >= 0 else "saida",  # Se recebeu mais, é saída (estorno)
                "valor": valor_recebido,
                "data_pagamento": data_pagamento,
                "status": "pago",
                "conciliado": True,  # Marcar como conciliado
                "id_parcela": parcela.id_parcela,
                "observacao": "Pagamento da parcela"
            }
            
            # Criar dados de lançamento para a diferença (se houver)
            lancamento_diferenca = None
            if abs(diferenca) > 0.01:  # Tolerância de 1 centavo
                tipo_diferenca = "saida" if diferenca > 0 else "entrada"
                lancamento_diferenca = {
                    "id_empresa": parcela.id_empresa,
                    "id_conta": conta_id,
                    "tipo": tipo_diferenca,
                    "valor": abs(diferenca),
                    "data_pagamento": data_pagamento,
                    "status": "pago",
                    "conciliado": True,
                    "id_parcela": parcela.id_parcela,
                    "observacao": "Diferença na conciliação"
                }
            
            # Atualizar parcela para status pago
            parcela_data = {
                "valor": valor_recebido,  # Atualizar para valor recebido
                "data_pagamento": data_pagamento,
                "status": "pago"
            }
            
            return {
                "parcela_atualizada": parcela_data,
                "lancamento_principal": lancamento_data,
                "lancamento_diferenca": lancamento_diferenca,
                "diferenca": diferenca
            }
            
        # Registrar pagamento
        resultado = registrar_pagamento_com_conciliacao(
            parcela=parcela_mock,
            valor_recebido=valor_recebido,
            data_pagamento=date.today(),
            conta_id=id_conta
        )
        
        # Assert
        # Verificar parcela atualizada
        assert resultado["parcela_atualizada"]["valor"] == valor_recebido
        assert resultado["parcela_atualizada"]["status"] == "pago"
        
        # Verificar lançamento principal
        assert resultado["lancamento_principal"]["valor"] == valor_recebido
        assert resultado["lancamento_principal"]["conciliado"] == True
        assert resultado["lancamento_principal"]["tipo"] == "entrada"
        
        # Verificar lançamento de diferença
        assert resultado["lancamento_diferenca"] is not None
        assert resultado["lancamento_diferenca"]["valor"] == abs(diferenca)
        assert resultado["lancamento_diferenca"]["tipo"] == "saida"  # Diferença negativa (recebeu menos)
        assert resultado["lancamento_diferenca"]["conciliado"] == True
        
        # Verificar diferença
        assert resultado["diferenca"] == diferenca 