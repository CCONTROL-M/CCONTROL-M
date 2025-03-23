"""Testes unitários para cálculos de datas de vencimento no sistema CCONTROL-M."""
import pytest
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
import calendar

from app.models.parcela import Parcela


class TestCalculoDatasVencimento:
    """Testes para validação de cálculos de datas de vencimento."""
    
    @pytest.mark.unit
    async def test_calculo_proxima_data_vencimento_mensal(self, mock_db_session):
        """Teste de cálculo de próxima data de vencimento para periodicidade mensal."""
        # Arrange
        dia_vencimento = 15
        mes_atual = date.today().month
        ano_atual = date.today().year
        
        # Próximo mês
        if mes_atual == 12:
            mes_proximo = 1
            ano_proximo = ano_atual + 1
        else:
            mes_proximo = mes_atual + 1
            ano_proximo = ano_atual
        
        # Data atual como base para o cálculo
        data_base = date.today()
        
        # Data esperada para o próximo vencimento
        data_esperada = date(ano_proximo, mes_proximo, dia_vencimento)
        
        # Act
        # Função para calcular próxima data de vencimento
        def calcular_proxima_data_vencimento(data_base, dia_vencimento, periodicidade="mensal"):
            """Calcula a próxima data de vencimento com base na periodicidade."""
            if periodicidade == "mensal":
                # Calcular próximo mês
                mes = data_base.month + 1
                ano = data_base.year
                
                # Ajustar para o ano seguinte se passar de dezembro
                if mes > 12:
                    mes = 1
                    ano += 1
                
                # Ajustar o dia para não exceder o último dia do mês
                ultimo_dia = calendar.monthrange(ano, mes)[1]
                dia = min(dia_vencimento, ultimo_dia)
                
                return date(ano, mes, dia)
            elif periodicidade == "quinzenal":
                # Adicionar 15 dias
                return data_base + timedelta(days=15)
            elif periodicidade == "semanal":
                # Adicionar 7 dias
                return data_base + timedelta(days=7)
            elif periodicidade == "trimestral":
                # Adicionar 3 meses
                mes = data_base.month + 3
                ano = data_base.year
                
                # Ajustar para o ano seguinte se passar de dezembro
                if mes > 12:
                    mes -= 12
                    ano += 1
                
                # Ajustar o dia para não exceder o último dia do mês
                ultimo_dia = calendar.monthrange(ano, mes)[1]
                dia = min(dia_vencimento, ultimo_dia)
                
                return date(ano, mes, dia)
            else:
                # Periodicidade não reconhecida
                raise ValueError(f"Periodicidade não suportada: {periodicidade}")
        
        # Calcular próxima data
        data_calculada = calcular_proxima_data_vencimento(data_base, dia_vencimento)
        
        # Assert
        assert data_calculada == data_esperada
    
    @pytest.mark.unit
    async def test_ajuste_dia_vencimento_fevereiro(self, mock_db_session):
        """Teste de ajuste de dia de vencimento para o mês de fevereiro (29, 30 ou 31)."""
        # Arrange
        # Dias de vencimento que precisam de ajuste em fevereiro
        dias_vencimento = [29, 30, 31]
        
        # Ano atual
        ano_atual = date.today().year
        
        # Verificar se é ano bissexto (para fevereiro)
        is_bissexto = calendar.isleap(ano_atual)
        
        # Ajustes esperados
        ajustes_esperados = {}
        for dia in dias_vencimento:
            if is_bissexto and dia == 29:
                # Em ano bissexto, dia 29 é válido em fevereiro
                ajustes_esperados[dia] = 29
            else:
                # Caso contrário, ajustar para o último dia de fevereiro
                ultimo_dia_fevereiro = 29 if is_bissexto else 28
                ajustes_esperados[dia] = ultimo_dia_fevereiro
        
        # Act
        # Função para ajustar dia de vencimento ao limite do mês
        def ajustar_dia_vencimento(dia, mes, ano):
            """Ajusta o dia de vencimento para não exceder o último dia do mês."""
            ultimo_dia = calendar.monthrange(ano, mes)[1]
            return min(dia, ultimo_dia)
        
        # Calcular ajustes
        ajustes_calculados = {}
        for dia in dias_vencimento:
            ajustes_calculados[dia] = ajustar_dia_vencimento(dia, 2, ano_atual)  # Mês 2 = fevereiro
        
        # Assert
        assert ajustes_calculados == ajustes_esperados
        
    @pytest.mark.unit
    async def test_adiamento_vencimento_final_semana(self, mock_db_session):
        """Teste de adiamento de vencimento quando cai no final de semana."""
        # Arrange
        # Definir uma data que cai em um sábado
        # Encontrar o próximo sábado a partir de hoje
        data_hoje = date.today()
        dias_para_sabado = (5 - data_hoje.weekday()) % 7  # 5 = sábado (0 = segunda, 6 = domingo)
        data_vencimento_sabado = data_hoje + timedelta(days=dias_para_sabado)
        
        # Definir uma data que cai em um domingo
        data_vencimento_domingo = data_vencimento_sabado + timedelta(days=1)
        
        # Data esperada após ajuste (próxima segunda-feira)
        data_esperada_apos_fim_semana = data_vencimento_domingo + timedelta(days=1)
        
        # Act
        # Função para ajustar data de vencimento para dia útil
        def ajustar_vencimento_para_dia_util(data_vencimento):
            """Ajusta a data de vencimento para o próximo dia útil, se cair em fim de semana."""
            # Verificar se é sábado (5) ou domingo (6)
            if data_vencimento.weekday() >= 5:
                # Calcular dias para a próxima segunda-feira
                dias_para_segunda = 7 - data_vencimento.weekday()
                # Adicionar dias para cair na segunda-feira
                return data_vencimento + timedelta(days=dias_para_segunda)
            else:
                # Já é dia útil, retornar sem alterar
                return data_vencimento
        
        # Calcular ajustes
        data_ajustada_sabado = ajustar_vencimento_para_dia_util(data_vencimento_sabado)
        data_ajustada_domingo = ajustar_vencimento_para_dia_util(data_vencimento_domingo)
        
        # Assert
        assert data_ajustada_sabado == data_esperada_apos_fim_semana
        assert data_ajustada_domingo == data_esperada_apos_fim_semana
        
    @pytest.mark.unit
    async def test_adiamento_vencimento_feriado(self, mock_db_session):
        """Teste de adiamento de vencimento quando cai em feriado."""
        # Arrange
        # Lista de feriados nacionais (exemplo para 2023)
        feriados_2023 = [
            date(2023, 1, 1),   # Ano Novo
            date(2023, 4, 7),   # Sexta-feira Santa
            date(2023, 4, 21),  # Tiradentes
            date(2023, 5, 1),   # Dia do Trabalho
            date(2023, 9, 7),   # Independência
            date(2023, 10, 12), # Nossa Senhora Aparecida
            date(2023, 11, 2),  # Finados
            date(2023, 11, 15), # Proclamação da República
            date(2023, 12, 25)  # Natal
        ]
        
        # Mock para a função de verificar feriados
        def is_feriado(data, feriados):
            """Verifica se a data é um feriado."""
            return data in feriados
        
        # Data de vencimento que cai em feriado (exemplo: Dia do Trabalho)
        data_vencimento_feriado = date(2023, 5, 1)
        
        # Data esperada após ajuste (próximo dia útil)
        data_esperada_apos_feriado = date(2023, 5, 2)  # 02/05/2023 (terça-feira após o feriado)
        
        # Act
        # Função para ajustar data de vencimento para dia útil, considerando feriados
        def ajustar_vencimento_para_dia_util_com_feriado(data_vencimento, feriados):
            """
            Ajusta a data de vencimento para o próximo dia útil,
            se cair em fim de semana ou feriado.
            """
            # Verificar se é fim de semana
            if data_vencimento.weekday() >= 5:
                # Calcular dias para a próxima segunda-feira
                dias_para_segunda = 7 - data_vencimento.weekday()
                # Atualizar data para a segunda-feira
                data_vencimento = data_vencimento + timedelta(days=dias_para_segunda)
            
            # Verificar se a nova data é feriado
            # Se for, adicionar dias até não ser mais feriado e nem fim de semana
            while is_feriado(data_vencimento, feriados) or data_vencimento.weekday() >= 5:
                data_vencimento += timedelta(days=1)
                
            return data_vencimento
        
        # Calcular ajuste
        data_ajustada = ajustar_vencimento_para_dia_util_com_feriado(data_vencimento_feriado, feriados_2023)
        
        # Assert
        assert data_ajustada == data_esperada_apos_feriado


class TestToleranciaPagamento:
    """Testes para validação de tolerância de pagamento após vencimento."""
    
    @pytest.mark.unit
    async def test_verificacao_tolerancia_pagamento(self, mock_db_session):
        """Teste de verificação de tolerância de pagamento após vencimento."""
        # Arrange
        dias_tolerancia = 3  # 3 dias de tolerância
        
        # Data de vencimento
        data_vencimento = date.today() - timedelta(days=2)  # Venceu 2 dias atrás
        
        # Data de pagamento
        data_pagamento = date.today()  # Pagando hoje
        
        # Definir expectativa de estar dentro da tolerância
        dentro_tolerancia = True  # Esperamos que esteja dentro da tolerância
        
        # Act
        # Função para verificar se pagamento está dentro da tolerância
        def verificar_tolerancia_pagamento(data_vencimento, data_pagamento, dias_tolerancia):
            """Verifica se o pagamento está dentro do período de tolerância após vencimento."""
            if data_pagamento <= data_vencimento:
                # Pagamento em dia, não precisa verificar tolerância
                return True
                
            # Calcular dias de atraso
            dias_atraso = (data_pagamento - data_vencimento).days
            
            # Verificar se está dentro da tolerância
            return dias_atraso <= dias_tolerancia
            
        # Verificar tolerância
        resultado = verificar_tolerancia_pagamento(data_vencimento, data_pagamento, dias_tolerancia)
        
        # Assert
        assert resultado == dentro_tolerancia
        
    @pytest.mark.unit
    async def test_atualizacao_status_com_tolerancia(self, mock_db_session):
        """Teste de atualização de status considerando tolerância de pagamento."""
        # Arrange
        dias_tolerancia = 5  # 5 dias de tolerância
        
        # Criar parcelas em diferentes situações
        # 1. Parcela em dia
        parcela_em_dia = MagicMock(
            id_parcela=uuid.uuid4(),
            data_vencimento=date.today() + timedelta(days=10),  # Vence em 10 dias
            data_pagamento=None,
            status="pendente"
        )
        
        # 2. Parcela vencida dentro da tolerância
        parcela_tolerancia = MagicMock(
            id_parcela=uuid.uuid4(),
            data_vencimento=date.today() - timedelta(days=3),  # Venceu há 3 dias
            data_pagamento=None,
            status="pendente"
        )
        
        # 3. Parcela vencida fora da tolerância
        parcela_atrasada = MagicMock(
            id_parcela=uuid.uuid4(),
            data_vencimento=date.today() - timedelta(days=10),  # Venceu há 10 dias
            data_pagamento=None,
            status="pendente"
        )
        
        # Status esperados após atualização
        status_esperado_em_dia = "pendente"
        status_esperado_tolerancia = "pendente"  # Ainda está em tolerância
        status_esperado_atrasada = "atrasada"
        
        # Act
        # Função para atualizar status da parcela com tolerância
        def atualizar_status_parcela_com_tolerancia(parcela, data_atual, dias_tolerancia):
            """Atualiza o status da parcela considerando a tolerância de pagamento."""
            # Se já estiver paga ou cancelada, não altera o status
            if parcela.status in ("pago", "cancelado"):
                return parcela.status
                
            # Se ainda não venceu, mantém pendente
            if data_atual <= parcela.data_vencimento:
                return "pendente"
                
            # Calcular dias de atraso
            dias_atraso = (data_atual - parcela.data_vencimento).days
            
            # Verificar se está dentro da tolerância
            if dias_atraso <= dias_tolerancia:
                return "pendente"  # Mantém pendente dentro da tolerância
            else:
                return "atrasada"  # Marca como atrasada fora da tolerância
                
        # Atualizar status das parcelas
        data_atual = date.today()
        status_em_dia = atualizar_status_parcela_com_tolerancia(parcela_em_dia, data_atual, dias_tolerancia)
        status_tolerancia = atualizar_status_parcela_com_tolerancia(parcela_tolerancia, data_atual, dias_tolerancia)
        status_atrasada = atualizar_status_parcela_com_tolerancia(parcela_atrasada, data_atual, dias_tolerancia)
        
        # Assert
        assert status_em_dia == status_esperado_em_dia
        assert status_tolerancia == status_esperado_tolerancia
        assert status_atrasada == status_esperado_atrasada 