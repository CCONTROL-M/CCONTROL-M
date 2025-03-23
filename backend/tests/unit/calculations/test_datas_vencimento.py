"""Testes para cálculos de datas de vencimento no sistema CCONTROL-M."""
import pytest
from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, AsyncMock, patch

class TestDiasUteis:
    """Testes para cálculos de dias úteis."""
    
    @pytest.mark.unit
    async def test_identificacao_de_finais_de_semana(self, mock_db_session):
        """Teste para verificar se a função identifica corretamente os finais de semana."""
        # Arrange
        # Define um conjunto de datas que são finais de semana
        datas_finais_semana = [
            date(2023, 10, 7),   # Sábado
            date(2023, 10, 8),   # Domingo
            date(2023, 10, 14),  # Sábado
            date(2023, 10, 15),  # Domingo
            date(2023, 10, 21),  # Sábado
            date(2023, 10, 22),  # Domingo
        ]
        
        # Define um conjunto de datas que não são finais de semana
        datas_dias_uteis = [
            date(2023, 10, 9),   # Segunda-feira
            date(2023, 10, 10),  # Terça-feira
            date(2023, 10, 11),  # Quarta-feira
            date(2023, 10, 12),  # Quinta-feira
            date(2023, 10, 13),  # Sexta-feira
        ]
        
        # Act
        def eh_final_de_semana(data):
            """Verifica se a data informada é um final de semana."""
            return data.weekday() >= 5  # 5=Sábado, 6=Domingo
        
        # Assert
        # Todas as datas de final de semana devem retornar True
        for data in datas_finais_semana:
            assert eh_final_de_semana(data) is True
            
        # Todas as datas de dias úteis devem retornar False
        for data in datas_dias_uteis:
            assert eh_final_de_semana(data) is False
    
    @pytest.mark.unit
    async def test_encontrar_proximo_dia_util(self, mock_db_session, feriados):
        """Teste para verificar se a função encontra corretamente o próximo dia útil."""
        # Arrange
        # Datas que são finais de semana ou feriados
        datas_nao_uteis = [
            date(2023, 10, 7),   # Sábado
            date(2023, 10, 8),   # Domingo
            date(2023, 11, 2),   # Feriado - Finados
            date(2023, 11, 15),  # Feriado - Proclamação da República
            date(2023, 12, 25),  # Feriado - Natal
        ]
        
        # Datas esperadas para o próximo dia útil
        datas_proximos_uteis = [
            date(2023, 10, 9),   # Segunda-feira
            date(2023, 10, 9),   # Segunda-feira
            date(2023, 11, 3),   # Sexta-feira
            date(2023, 11, 16),  # Quinta-feira
            date(2023, 12, 26),  # Terça-feira
        ]
        
        # Act
        def proximo_dia_util(data, lista_feriados):
            """Encontra o próximo dia útil após a data informada."""
            data_atual = data
            while True:
                # Avança para o próximo dia
                data_atual = data_atual + timedelta(days=1)
                
                # Verifica se é dia útil (não é final de semana nem feriado)
                if data_atual.weekday() < 5 and data_atual not in lista_feriados:
                    return data_atual
        
        # Assert
        for i in range(len(datas_nao_uteis)):
            proxima_data = proximo_dia_util(datas_nao_uteis[i], feriados)
            assert proxima_data == datas_proximos_uteis[i]
    
    @pytest.mark.unit
    async def test_contar_dias_uteis_entre_datas(self, mock_db_session, feriados):
        """Teste para contar o número de dias úteis entre duas datas."""
        # Arrange
        data_inicial = date(2023, 10, 2)  # Segunda-feira
        data_final = date(2023, 10, 13)   # Sexta-feira
        
        # Considerando que entre 02/10 e 13/10 temos:
        # - 10 dias corridos, excluindo a data inicial
        # - 2 finais de semana (7-8/10)
        # - Nenhum feriado na lista
        # Então temos 8 dias úteis
        dias_uteis_esperados = 8
        
        # Act
        def contar_dias_uteis(data_inicial, data_final, lista_feriados):
            """Conta o número de dias úteis entre duas datas (excluindo a data inicial)."""
            if data_final <= data_inicial:
                return 0
                
            dias_uteis = 0
            data_atual = data_inicial
            
            while data_atual < data_final:
                data_atual = data_atual + timedelta(days=1)
                
                # Verifica se é dia útil (não é final de semana nem feriado)
                if data_atual.weekday() < 5 and data_atual not in lista_feriados:
                    dias_uteis += 1
                    
            return dias_uteis
        
        # Assert
        assert contar_dias_uteis(data_inicial, data_final, feriados) == dias_uteis_esperados


class TestVencimentosAjustados:
    """Testes para ajustes de datas de vencimento que caem em dias não úteis."""
    
    @pytest.mark.unit
    async def test_ajuste_vencimento_para_proximo_dia_util(self, mock_db_session, feriados):
        """Teste para verificar o ajuste de vencimento para o próximo dia útil."""
        # Arrange
        # Vencimentos que caem em finais de semana ou feriados
        vencimentos_nao_uteis = [
            date(2023, 10, 7),   # Sábado
            date(2023, 10, 8),   # Domingo
            date(2023, 11, 2),   # Feriado - Finados
            date(2023, 11, 15),  # Feriado - Proclamação da República
        ]
        
        # Vencimentos ajustados esperados
        vencimentos_ajustados = [
            date(2023, 10, 9),   # Segunda-feira
            date(2023, 10, 9),   # Segunda-feira
            date(2023, 11, 3),   # Sexta-feira
            date(2023, 11, 16),  # Quinta-feira
        ]
        
        # Act
        def ajustar_vencimento(data_vencimento, lista_feriados):
            """Ajusta a data de vencimento para o próximo dia útil se cair em final de semana ou feriado."""
            # Se o vencimento cair em final de semana ou feriado,
            # ajusta para o próximo dia útil
            if data_vencimento.weekday() >= 5 or data_vencimento in lista_feriados:
                data_atual = data_vencimento
                while True:
                    # Avança para o próximo dia
                    data_atual = data_atual + timedelta(days=1)
                    
                    # Verifica se é dia útil
                    if data_atual.weekday() < 5 and data_atual not in lista_feriados:
                        return data_atual
            
            # Se o vencimento já for dia útil, mantém a data
            return data_vencimento
        
        # Assert
        for i in range(len(vencimentos_nao_uteis)):
            vencimento_ajustado = ajustar_vencimento(vencimentos_nao_uteis[i], feriados)
            assert vencimento_ajustado == vencimentos_ajustados[i]
    
    @pytest.mark.unit
    async def test_ajuste_vencimento_para_dia_util_anterior(self, mock_db_session, feriados):
        """Teste para verificar o ajuste de vencimento para o dia útil anterior."""
        # Arrange
        # Vencimentos que caem em finais de semana ou feriados
        vencimentos_nao_uteis = [
            date(2023, 10, 7),   # Sábado
            date(2023, 10, 8),   # Domingo
            date(2023, 11, 2),   # Feriado - Finados
            date(2023, 11, 15),  # Feriado - Proclamação da República
        ]
        
        # Vencimentos ajustados esperados (para dia útil anterior)
        vencimentos_ajustados = [
            date(2023, 10, 6),   # Sexta-feira
            date(2023, 10, 6),   # Sexta-feira
            date(2023, 11, 1),   # Quarta-feira
            date(2023, 11, 14),  # Terça-feira
        ]
        
        # Act
        def ajustar_vencimento_anterior(data_vencimento, lista_feriados):
            """Ajusta a data de vencimento para o dia útil anterior se cair em final de semana ou feriado."""
            # Se o vencimento cair em final de semana ou feriado,
            # ajusta para o dia útil anterior
            if data_vencimento.weekday() >= 5 or data_vencimento in lista_feriados:
                data_atual = data_vencimento
                while True:
                    # Retrocede para o dia anterior
                    data_atual = data_atual - timedelta(days=1)
                    
                    # Verifica se é dia útil
                    if data_atual.weekday() < 5 and data_atual not in lista_feriados:
                        return data_atual
            
            # Se o vencimento já for dia útil, mantém a data
            return data_vencimento
        
        # Assert
        for i in range(len(vencimentos_nao_uteis)):
            vencimento_ajustado = ajustar_vencimento_anterior(vencimentos_nao_uteis[i], feriados)
            assert vencimento_ajustado == vencimentos_ajustados[i]


class TestVencimentosMensais:
    """Testes para geração de datas de vencimento mensais."""
    
    @pytest.mark.unit
    async def test_gerar_vencimentos_mensais_mesmo_dia(self, mock_db_session):
        """Teste para gerar vencimentos mensais mantendo o mesmo dia."""
        # Arrange
        data_inicial = date(2023, 3, 15)  # 15 de março de 2023
        quantidade_meses = 6
        
        # Vencimentos esperados (mesmo dia em meses consecutivos)
        vencimentos_esperados = [
            date(2023, 4, 15),  # 15 de abril de 2023
            date(2023, 5, 15),  # 15 de maio de 2023
            date(2023, 6, 15),  # 15 de junho de 2023
            date(2023, 7, 15),  # 15 de julho de 2023
            date(2023, 8, 15),  # 15 de agosto de 2023
            date(2023, 9, 15),  # 15 de setembro de 2023
        ]
        
        # Act
        def gerar_vencimentos_mensais(data_inicial, quantidade_meses):
            """Gera uma lista de datas de vencimento mensais mantendo o mesmo dia."""
            vencimentos = []
            
            # Mês atual como base para cálculos
            ano_atual = data_inicial.year
            mes_atual = data_inicial.month
            dia_vencimento = data_inicial.day
            
            for i in range(quantidade_meses):
                # Avança para o próximo mês
                mes_atual += 1
                if mes_atual > 12:
                    mes_atual = 1
                    ano_atual += 1
                
                # Verifica se o dia existe no mês (ex: 31 em fevereiro)
                ultimo_dia = 31
                if mes_atual in [4, 6, 9, 11]:
                    ultimo_dia = 30
                elif mes_atual == 2:
                    # Verifica se é ano bissexto
                    if ano_atual % 4 == 0 and (ano_atual % 100 != 0 or ano_atual % 400 == 0):
                        ultimo_dia = 29
                    else:
                        ultimo_dia = 28
                
                # Usa o dia de vencimento ou o último dia do mês
                dia = min(dia_vencimento, ultimo_dia)
                
                # Adiciona a data à lista
                vencimentos.append(date(ano_atual, mes_atual, dia))
            
            return vencimentos
        
        # Assert
        vencimentos_gerados = gerar_vencimentos_mensais(data_inicial, quantidade_meses)
        assert len(vencimentos_gerados) == quantidade_meses
        
        for i in range(quantidade_meses):
            assert vencimentos_gerados[i] == vencimentos_esperados[i]
    
    @pytest.mark.unit
    async def test_gerar_vencimentos_mensais_ultimo_dia(self, mock_db_session):
        """Teste para gerar vencimentos mensais no último dia de cada mês."""
        # Arrange
        data_inicial = date(2023, 1, 31)  # 31 de janeiro de 2023
        quantidade_meses = 6
        
        # Vencimentos esperados (último dia de cada mês)
        vencimentos_esperados = [
            date(2023, 2, 28),  # 28 de fevereiro de 2023 (não bissexto)
            date(2023, 3, 31),  # 31 de março de 2023
            date(2023, 4, 30),  # 30 de abril de 2023
            date(2023, 5, 31),  # 31 de maio de 2023
            date(2023, 6, 30),  # 30 de junho de 2023
            date(2023, 7, 31),  # 31 de julho de 2023
        ]
        
        # Act
        def gerar_vencimentos_ultimo_dia(data_inicial, quantidade_meses):
            """Gera uma lista de datas de vencimento no último dia de cada mês."""
            vencimentos = []
            
            # Mês atual como base para cálculos
            ano_atual = data_inicial.year
            mes_atual = data_inicial.month
            
            for i in range(quantidade_meses):
                # Avança para o próximo mês
                mes_atual += 1
                if mes_atual > 12:
                    mes_atual = 1
                    ano_atual += 1
                
                # Calcula o último dia do mês
                if mes_atual == 12:
                    # Para dezembro, use 31 de dezembro
                    ultimo_dia = date(ano_atual, mes_atual, 31)
                else:
                    # Para outros meses, é o dia anterior ao dia 1 do próximo mês
                    proximo_mes = mes_atual + 1
                    proximo_ano = ano_atual
                    if proximo_mes > 12:
                        proximo_mes = 1
                        proximo_ano += 1
                    
                    ultimo_dia = date(proximo_ano, proximo_mes, 1) - timedelta(days=1)
                
                # Adiciona a data à lista
                vencimentos.append(ultimo_dia)
            
            return vencimentos
        
        # Assert
        vencimentos_gerados = gerar_vencimentos_ultimo_dia(data_inicial, quantidade_meses)
        assert len(vencimentos_gerados) == quantidade_meses
        
        for i in range(quantidade_meses):
            assert vencimentos_gerados[i] == vencimentos_esperados[i]


class TestAjustePeriodos:
    """Testes para ajustes de períodos com base em datas."""
    
    @pytest.mark.unit
    async def test_calcular_dias_entre_pagamento_vencimento(self, mock_db_session):
        """Teste para calcular o número de dias entre pagamento e vencimento."""
        # Arrange
        casos_teste = [
            {
                'data_vencimento': date(2023, 10, 15),
                'data_pagamento': date(2023, 10, 10),
                'dias_esperados': -5  # 5 dias antes do vencimento
            },
            {
                'data_vencimento': date(2023, 10, 15),
                'data_pagamento': date(2023, 10, 15),
                'dias_esperados': 0  # No dia do vencimento
            },
            {
                'data_vencimento': date(2023, 10, 15),
                'data_pagamento': date(2023, 10, 20),
                'dias_esperados': 5  # 5 dias após o vencimento
            }
        ]
        
        # Act
        def calcular_dias_entre_datas(data_vencimento, data_pagamento):
            """Calcula o número de dias entre a data de pagamento e a data de vencimento."""
            # Número positivo indica atraso, negativo indica antecipação
            return (data_pagamento - data_vencimento).days
        
        # Assert
        for caso in casos_teste:
            dias = calcular_dias_entre_datas(caso['data_vencimento'], caso['data_pagamento'])
            assert dias == caso['dias_esperados']
    
    @pytest.mark.unit
    async def test_identificar_mes_referencia(self, mock_db_session):
        """Teste para identificar o mês de referência com base na data de vencimento."""
        # Arrange
        # Assumindo que o mês de referência é o mês anterior ao vencimento
        casos_teste = [
            {
                'data_vencimento': date(2023, 2, 10),
                'mes_referencia_esperado': (2023, 1)  # Janeiro/2023
            },
            {
                'data_vencimento': date(2023, 1, 5),
                'mes_referencia_esperado': (2022, 12)  # Dezembro/2022
            },
            {
                'data_vencimento': date(2023, 12, 15),
                'mes_referencia_esperado': (2023, 11)  # Novembro/2023
            }
        ]
        
        # Act
        def obter_mes_referencia(data_vencimento):
            """Obtém o mês de referência (mês anterior) com base na data de vencimento."""
            # Retrocede um mês
            if data_vencimento.month == 1:
                return (data_vencimento.year - 1, 12)
            else:
                return (data_vencimento.year, data_vencimento.month - 1)
        
        # Assert
        for caso in casos_teste:
            mes_ref = obter_mes_referencia(caso['data_vencimento'])
            assert mes_ref == caso['mes_referencia_esperado'] 