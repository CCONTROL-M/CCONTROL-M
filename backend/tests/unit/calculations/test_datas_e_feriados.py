"""Testes para cálculos relacionados a datas e feriados."""
import pytest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, AsyncMock, patch
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

@pytest.fixture
def feriados():
    """Lista de feriados para testes."""
    ano_atual = date.today().year
    return [
        date(ano_atual, 1, 1),    # Ano Novo
        date(ano_atual, 4, 21),   # Tiradentes
        date(ano_atual, 5, 1),    # Dia do Trabalho
        date(ano_atual, 9, 7),    # Independência
        date(ano_atual, 10, 12),  # Nossa Senhora Aparecida
        date(ano_atual, 11, 2),   # Finados
        date(ano_atual, 11, 15),  # Proclamação da República
        date(ano_atual, 12, 25),  # Natal
    ]

@pytest.mark.unit
async def test_ajuste_dia_util_proximo(feriados):
    """
    Testa o ajuste de data para o próximo dia útil.
    
    O teste deve validar:
    1. Se a data cai em um final de semana, ajustar para segunda-feira
    2. Se a data cai em um feriado, ajustar para o próximo dia útil
    3. Se o próximo dia útil é também um feriado, continuar ajustando
    """
    # Arrange
    data_sabado = date(2023, 5, 6)        # Sábado
    data_domingo = date(2023, 5, 7)       # Domingo
    data_feriado = feriados[2]            # Dia do Trabalho (1/maio)
    data_feriado_sexta = date(2023, 4, 21)  # Tiradentes (sexta-feira em 2023)
    data_util = date(2023, 5, 2)          # Terça-feira normal
    
    # Act - Função que ajusta para o próximo dia útil
    def ajustar_para_proximo_dia_util(data_verificar, lista_feriados):
        data_ajustada = data_verificar
        
        # Ajustar para o próximo dia útil (não final de semana e não feriado)
        while (data_ajustada.weekday() >= 5) or (data_ajustada in lista_feriados):
            data_ajustada = data_ajustada + timedelta(days=1)
            
        return data_ajustada
    
    data_sabado_ajustada = ajustar_para_proximo_dia_util(data_sabado, feriados)
    data_domingo_ajustada = ajustar_para_proximo_dia_util(data_domingo, feriados)
    data_feriado_ajustada = ajustar_para_proximo_dia_util(data_feriado, feriados)
    data_feriado_sexta_ajustada = ajustar_para_proximo_dia_util(data_feriado_sexta, feriados)
    data_util_ajustada = ajustar_para_proximo_dia_util(data_util, feriados)
    
    # Assert
    assert data_sabado.weekday() == 5  # Confirmar que é sábado
    assert data_sabado_ajustada.weekday() == 0  # Deve ser ajustada para segunda (dia 8/5)
    assert data_sabado_ajustada == date(2023, 5, 8)
    
    assert data_domingo.weekday() == 6  # Confirmar que é domingo
    assert data_domingo_ajustada.weekday() == 0  # Deve ser ajustada para segunda (dia 8/5)
    assert data_domingo_ajustada == date(2023, 5, 8)
    
    assert data_feriado in feriados  # Confirmar que é feriado
    assert data_feriado_ajustada not in feriados  # Não deve ser feriado
    assert data_feriado_ajustada.weekday() < 5  # Não deve ser final de semana
    assert data_feriado_ajustada == date(2023, 5, 2)  # Deve ser ajustada para o dia seguinte (2/5)
    
    assert data_feriado_sexta in feriados  # Confirmar que é feriado
    assert data_feriado_sexta_ajustada not in feriados  # Não deve ser feriado
    assert data_feriado_sexta_ajustada.weekday() < 5  # Não deve ser final de semana
    assert data_feriado_sexta_ajustada == date(2023, 4, 24)  # Deve ser ajustada para segunda (24/4)
    
    assert data_util_ajustada == data_util  # Não deve haver alteração para dia útil normal

@pytest.mark.unit
async def test_ajuste_dia_util_anterior(feriados):
    """
    Testa o ajuste de data para o dia útil anterior.
    
    O teste deve validar:
    1. Se a data cai em um final de semana, ajustar para sexta-feira
    2. Se a data cai em um feriado, ajustar para o dia útil anterior
    3. Se o dia útil anterior é também um feriado, continuar ajustando
    """
    # Arrange
    data_sabado = date(2023, 5, 6)        # Sábado
    data_domingo = date(2023, 5, 7)       # Domingo
    data_feriado = feriados[2]            # Dia do Trabalho (1/maio)
    data_feriado_segunda = date(2023, 1, 1)  # Ano Novo (cai em uma segunda em 2024)
    data_util = date(2023, 5, 2)          # Terça-feira normal
    
    # Act - Função que ajusta para o dia útil anterior
    def ajustar_para_dia_util_anterior(data_verificar, lista_feriados):
        data_ajustada = data_verificar
        
        # Ajustar para o dia útil anterior (não final de semana e não feriado)
        while (data_ajustada.weekday() >= 5) or (data_ajustada in lista_feriados):
            data_ajustada = data_ajustada - timedelta(days=1)
            
        return data_ajustada
    
    data_sabado_ajustada = ajustar_para_dia_util_anterior(data_sabado, feriados)
    data_domingo_ajustada = ajustar_para_dia_util_anterior(data_domingo, feriados)
    data_feriado_ajustada = ajustar_para_dia_util_anterior(data_feriado, feriados)
    data_feriado_segunda_ajustada = ajustar_para_dia_util_anterior(data_feriado_segunda, feriados)
    data_util_ajustada = ajustar_para_dia_util_anterior(data_util, feriados)
    
    # Assert
    assert data_sabado.weekday() == 5  # Confirmar que é sábado
    assert data_sabado_ajustada.weekday() == 4  # Deve ser ajustada para sexta (dia 5/5)
    assert data_sabado_ajustada == date(2023, 5, 5)
    
    assert data_domingo.weekday() == 6  # Confirmar que é domingo
    assert data_domingo_ajustada.weekday() == 4  # Deve ser ajustada para sexta (dia 5/5)
    assert data_domingo_ajustada == date(2023, 5, 5)
    
    assert data_feriado in feriados  # Confirmar que é feriado
    assert data_feriado_ajustada not in feriados  # Não deve ser feriado
    assert data_feriado_ajustada.weekday() < 5  # Não deve ser final de semana
    assert data_feriado_ajustada == date(2023, 4, 28)  # Deve ser ajustada para sexta (28/4)
    
    # Verifica que se o feriado cai em uma segunda, devemos voltar para sexta
    assert data_feriado_segunda_ajustada.weekday() == 4  # Deve ser sexta-feira
    
    assert data_util_ajustada == data_util  # Não deve haver alteração para dia útil normal

@pytest.mark.unit
async def test_dias_uteis_entre_datas(feriados):
    """
    Testa o cálculo de dias úteis entre duas datas.
    
    O teste deve validar:
    1. Exclusão de finais de semana
    2. Exclusão de feriados
    3. Inclusão apenas de dias úteis
    """
    # Arrange
    data_inicio = date(2023, 5, 1)  # Segunda-feira, feriado (Dia do Trabalho)
    data_fim = date(2023, 5, 12)    # Sexta-feira normal
    
    # Act - Função que calcula dias úteis entre datas
    def calcular_dias_uteis(data_inicio, data_fim, lista_feriados):
        dias_uteis = 0
        data_atual = data_inicio
        
        while data_atual <= data_fim:
            # Verificar se não é final de semana (0-4 são segunda a sexta)
            # E se não é feriado
            if data_atual.weekday() < 5 and data_atual not in lista_feriados:
                dias_uteis += 1
            
            data_atual += timedelta(days=1)
            
        return dias_uteis
    
    # Calcular dias úteis entre 01/05 e 12/05/2023
    dias_uteis = calcular_dias_uteis(data_inicio, data_fim, feriados)
    
    # Calcular dias corridos entre as mesmas datas
    dias_corridos = (data_fim - data_inicio).days + 1
    
    # Assert
    assert dias_corridos == 12  # 12 dias corridos no total
    assert dias_uteis == 9  # 9 dias úteis (excluindo finais de semana e feriados)
    
    # Verificação manual: de 01/05 a 12/05 temos:
    # 01/05 (feriado): não conta
    # 02/05 a 05/05 (dias úteis): 4 dias
    # 06/05 e 07/05 (sáb e dom): não contam
    # 08/05 a 12/05 (dias úteis): 5 dias
    # Total: 9 dias úteis

@pytest.mark.unit
async def test_calculo_vencimento_em_dia_util(feriados):
    """
    Testa o cálculo de data de vencimento ajustada para dia útil.
    
    O teste deve validar:
    1. Se a data de vencimento cai em dia não útil, deve ser ajustada
    2. A regra de ajuste pode variar (anterior ou próximo dia útil)
    3. Diferentes combinações de dias da semana e feriados
    """
    # Arrange
    vencimento_sabado = date(2023, 5, 6)    # Sábado
    vencimento_feriado = feriados[2]        # Dia do Trabalho (1/maio)
    regra_proximo = "proximo"
    regra_anterior = "anterior"
    
    # Act - Função que ajusta vencimento conforme regra
    def ajustar_vencimento(data_vencimento, lista_feriados, regra):
        data_ajustada = data_vencimento
        
        # Verificar se cai em fim de semana ou feriado
        if data_ajustada.weekday() >= 5 or data_ajustada in lista_feriados:
            if regra == "proximo":
                # Ajustar para o próximo dia útil
                while (data_ajustada.weekday() >= 5) or (data_ajustada in lista_feriados):
                    data_ajustada += timedelta(days=1)
            elif regra == "anterior":
                # Ajustar para o dia útil anterior
                while (data_ajustada.weekday() >= 5) or (data_ajustada in lista_feriados):
                    data_ajustada -= timedelta(days=1)
        
        return data_ajustada
    
    vencimento_sabado_proximo = ajustar_vencimento(vencimento_sabado, feriados, regra_proximo)
    vencimento_sabado_anterior = ajustar_vencimento(vencimento_sabado, feriados, regra_anterior)
    vencimento_feriado_proximo = ajustar_vencimento(vencimento_feriado, feriados, regra_proximo)
    vencimento_feriado_anterior = ajustar_vencimento(vencimento_feriado, feriados, regra_anterior)
    
    # Assert
    assert vencimento_sabado_proximo == date(2023, 5, 8)  # Segunda-feira
    assert vencimento_sabado_anterior == date(2023, 5, 5)  # Sexta-feira
    assert vencimento_feriado_proximo == date(2023, 5, 2)  # Terça-feira
    assert vencimento_feriado_anterior == date(2023, 4, 28)  # Sexta-feira

@pytest.mark.unit
async def test_tolerancia_antes_multa():
    """
    Testa o cálculo de período de tolerância antes da aplicação de multa.
    
    O teste deve validar:
    1. Se está dentro do período de tolerância, não aplicar multa
    2. Se passou do período de tolerância, aplicar multa
    3. Calcular o valor da multa corretamente
    """
    # Arrange
    valor_titulo = Decimal("1000.00")
    data_vencimento = date.today() - timedelta(days=5)  # Vencida há 5 dias
    dias_tolerancia = 3  # 3 dias de tolerância
    taxa_multa = Decimal("0.02")  # 2% de multa
    taxa_juros_diaria = Decimal("0.001")  # 0.1% de juros ao dia
    
    # Act - Verificar se está no período de tolerância
    dias_atraso = (date.today() - data_vencimento).days
    esta_no_periodo_tolerancia = dias_atraso <= dias_tolerancia
    
    # Calcular valor de multa e juros
    valor_multa = Decimal("0")
    valor_juros = Decimal("0")
    
    if not esta_no_periodo_tolerancia:
        # Aplicar multa fixa
        valor_multa = valor_titulo * taxa_multa
        
        # Calcular juros sobre os dias excedentes ao período de tolerância
        dias_para_juros = dias_atraso - dias_tolerancia
        valor_juros = valor_titulo * taxa_juros_diaria * dias_para_juros
    
    valor_total = valor_titulo + valor_multa + valor_juros
    
    # Assert
    assert dias_atraso == 5
    assert not esta_no_periodo_tolerancia  # Passou do período de tolerância
    assert valor_multa == Decimal("20.00")  # 2% de multa sobre 1000
    assert dias_atraso - dias_tolerancia == 2  # 2 dias para calcular juros
    assert valor_juros == Decimal("2.00")  # 0.1% ao dia por 2 dias
    assert valor_total == Decimal("1022.00")  # 1000 + 20 + 2
    
    # Testar dentro do período de tolerância
    data_vencimento_2 = date.today() - timedelta(days=2)  # Vencida há 2 dias
    dias_atraso_2 = (date.today() - data_vencimento_2).days
    esta_no_periodo_tolerancia_2 = dias_atraso_2 <= dias_tolerancia
    
    valor_multa_2 = Decimal("0")
    valor_juros_2 = Decimal("0")
    
    if not esta_no_periodo_tolerancia_2:
        valor_multa_2 = valor_titulo * taxa_multa
        dias_para_juros_2 = dias_atraso_2 - dias_tolerancia
        valor_juros_2 = valor_titulo * taxa_juros_diaria * dias_para_juros_2
    
    valor_total_2 = valor_titulo + valor_multa_2 + valor_juros_2
    
    assert dias_atraso_2 == 2
    assert esta_no_periodo_tolerancia_2  # Dentro do período de tolerância
    assert valor_multa_2 == Decimal("0")  # Sem multa
    assert valor_juros_2 == Decimal("0")  # Sem juros
    assert valor_total_2 == valor_titulo  # Valor original

@pytest.mark.unit
async def test_feriados_moveis():
    """
    Testa o cálculo de feriados móveis com base na Páscoa.
    
    O teste deve validar:
    1. Cálculo correto da data da Páscoa
    2. Cálculo de feriados derivados da Páscoa (Carnaval, Corpus Christi, etc.)
    3. Lista completa de feriados para um determinado ano
    """
    # Arrange
    ano = 2023
    
    # Act - Função que calcula a data da Páscoa usando o algoritmo de Butcher-Meeus
    def calcular_data_pascoa(ano):
        a = ano % 19
        b = ano // 100
        c = ano % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l) // 451
        mes = (h + l - 7 * m + 114) // 31
        dia = ((h + l - 7 * m + 114) % 31) + 1
        
        return date(ano, mes, dia)
    
    data_pascoa = calcular_data_pascoa(ano)
    
    # Calcular feriados baseados na Páscoa
    sexta_santa = data_pascoa - timedelta(days=2)
    carnaval = data_pascoa - timedelta(days=47)  # Terça-feira de carnaval
    corpus_christi = data_pascoa + timedelta(days=60)
    
    # Adicionar feriados fixos
    feriados_fixos = [
        date(ano, 1, 1),   # Ano Novo
        date(ano, 4, 21),  # Tiradentes
        date(ano, 5, 1),   # Dia do Trabalho
        date(ano, 9, 7),   # Independência
        date(ano, 10, 12), # Nossa Senhora Aparecida
        date(ano, 11, 2),  # Finados
        date(ano, 11, 15), # Proclamação da República
        date(ano, 12, 25)  # Natal
    ]
    
    # Combinar feriados fixos e móveis
    feriados_ano = feriados_fixos + [sexta_santa, carnaval, corpus_christi]
    
    # Assert
    # Verificar data da Páscoa em 2023
    assert data_pascoa == date(2023, 4, 9)
    
    # Verificar feriados derivados
    assert sexta_santa == date(2023, 4, 7)
    assert carnaval == date(2023, 2, 21)
    assert corpus_christi == date(2023, 6, 8)
    
    # Verificar total de feriados
    assert len(feriados_ano) == 11  # 8 fixos + 3 móveis

@pytest.mark.unit
async def test_atraso_com_feriados(feriados):
    """
    Testa o cálculo de dias de atraso considerando apenas dias úteis.
    
    O teste deve validar:
    1. Contagem de dias úteis entre vencimento e pagamento
    2. Exclusão de finais de semana e feriados da contagem
    3. Cálculo correto de juros com base nos dias úteis de atraso
    """
    # Arrange
    valor_titulo = Decimal("1500.00")
    data_vencimento = date(2023, 4, 28)  # Sexta-feira
    data_pagamento = date(2023, 5, 5)    # Sexta-feira seguinte
    taxa_juros_diaria_util = Decimal("0.003")  # 0.3% por dia útil
    
    # Act - Função que calcula dias úteis entre datas
    def calcular_dias_uteis(data_inicio, data_fim, lista_feriados):
        dias_uteis = 0
        data_atual = data_inicio
        
        while data_atual <= data_fim:
            # Verificar se não é final de semana (0-4 são segunda a sexta)
            # E se não é feriado
            if data_atual.weekday() < 5 and data_atual not in lista_feriados:
                dias_uteis += 1
            
            data_atual += timedelta(days=1)
            
        return dias_uteis
    
    # Calcular dias úteis de atraso (excluindo data de vencimento)
    data_inicio_atraso = data_vencimento + timedelta(days=1)
    dias_uteis_atraso = calcular_dias_uteis(data_inicio_atraso, data_pagamento, feriados)
    
    # Calcular juros sobre dias úteis
    valor_juros = valor_titulo * taxa_juros_diaria_util * dias_uteis_atraso
    valor_total = valor_titulo + valor_juros
    
    # Assert
    # Verificação manual para o período de 29/04 a 05/05/2023:
    # 29-30/04: finais de semana (não contam)
    # 01/05: feriado (não conta)
    # 02-05/05: dias úteis (contam 4 dias)
    assert dias_uteis_atraso == 4
    assert valor_juros == Decimal("18.00")  # 1500 * 0.003 * 4
    assert valor_total == Decimal("1518.00")  # 1500 + 18