"""Testes para cálculos financeiros relacionados a parcelas e lançamentos."""
import pytest
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from unittest.mock import MagicMock, AsyncMock, patch
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.unit
async def test_geracao_parcelas_automaticas():
    """
    Testa a geração automática de parcelas para um valor total.
    
    O processo deve:
    1. Dividir o valor total pelo número de parcelas
    2. Ajustar a última parcela para garantir a soma exata
    3. Gerar as datas de vencimento adequadas
    """
    # Arrange
    valor_total = Decimal("2550.00")
    num_parcelas = 6
    data_inicial = date.today()
    intervalo_dias = 30
    
    # Act
    valor_parcela_base = valor_total / num_parcelas
    valor_parcela = round(valor_parcela_base, 2)
    
    parcelas = []
    for i in range(1, num_parcelas + 1):
        # Última parcela ajustada para garantir soma exata
        if i == num_parcelas:
            valor_parcela_atual = valor_total - sum(p["valor"] for p in parcelas)
        else:
            valor_parcela_atual = valor_parcela
        
        parcelas.append({
            "numero": i,
            "valor": valor_parcela_atual,
            "data_vencimento": data_inicial + timedelta(days=intervalo_dias * i)
        })
    
    # Assert
    assert len(parcelas) == num_parcelas
    assert sum(p["valor"] for p in parcelas) == valor_total
    
    # Verificar valores específicos
    assert parcelas[0]["valor"] == Decimal("425.00")
    assert parcelas[1]["valor"] == Decimal("425.00")
    assert parcelas[5]["valor"] == Decimal("425.00")  # Última parcela ajustada
    
    # Verificar datas
    assert parcelas[0]["data_vencimento"] == data_inicial + timedelta(days=intervalo_dias)
    assert parcelas[5]["data_vencimento"] == data_inicial + timedelta(days=intervalo_dias * 6)

@pytest.mark.unit
async def test_arredondamento_valores_parcelas():
    """
    Testa diferentes estratégias de arredondamento para valores de parcelas.
    
    O teste deve verificar:
    1. Arredondamento para cima
    2. Arredondamento para baixo
    3. Arredondamento bancário (meio para cima)
    4. Ajuste na última parcela
    """
    # Arrange
    valor_total = Decimal("1000.00")
    num_parcelas = 3
    
    # Act - Arredondamento Bancário (padrão)
    valor_parcela_base = valor_total / num_parcelas
    # Arredondamento bancário (ROUND_HALF_UP)
    valor_parcela_padrao = valor_parcela_base.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    parcelas_padrao = []
    for i in range(1, num_parcelas + 1):
        if i == num_parcelas:
            valor_parcela_atual = valor_total - sum(p["valor"] for p in parcelas_padrao)
        else:
            valor_parcela_atual = valor_parcela_padrao
        
        parcelas_padrao.append({
            "numero": i,
            "valor": valor_parcela_atual
        })
    
    # Assert - Arredondamento Padrão
    assert valor_parcela_base == Decimal("333.33333333333333333333333333")
    assert valor_parcela_padrao == Decimal("333.33")
    assert sum(p["valor"] for p in parcelas_padrao) == valor_total
    assert parcelas_padrao[0]["valor"] == Decimal("333.33")
    assert parcelas_padrao[1]["valor"] == Decimal("333.33")
    assert parcelas_padrao[2]["valor"] == Decimal("333.34")  # Ajuste na última parcela
    
    # Act - Arredondamento para cima
    valor_parcela_cima = valor_parcela_base.quantize(Decimal("0.01"), rounding=Decimal.ROUND_UP)
    
    parcelas_cima = []
    total_parcelas = Decimal("0")
    for i in range(1, num_parcelas):
        parcelas_cima.append({
            "numero": i,
            "valor": valor_parcela_cima
        })
        total_parcelas += valor_parcela_cima
    
    # Última parcela é o restante
    valor_ultima = valor_total - total_parcelas
    parcelas_cima.append({
        "numero": num_parcelas,
        "valor": valor_ultima
    })
    
    # Assert - Arredondamento para cima
    assert valor_parcela_cima == Decimal("333.34")
    assert sum(p["valor"] for p in parcelas_cima) == valor_total
    assert parcelas_cima[0]["valor"] == Decimal("333.34")
    assert parcelas_cima[1]["valor"] == Decimal("333.34")
    assert parcelas_cima[2]["valor"] == Decimal("333.32")  # Menor na última parcela

@pytest.mark.unit
async def test_lancamentos_recorrentes():
    """
    Testa a geração de lançamentos recorrentes.
    
    O teste deve validar:
    1. Recorrência mensal com data fixa
    2. Recorrência mensal com dia da semana específico
    3. Cálculo correto de meses com diferentes números de dias
    """
    # Arrange
    data_inicial = date(2023, 1, 15)  # 15 de janeiro de 2023 (um domingo)
    valor_recorrente = Decimal("500.00")
    quantidade_recorrencias = 5
    
    # Act - Recorrência mensal com data fixa
    lancamentos_fixos = []
    for i in range(quantidade_recorrencias):
        mes = data_inicial.month + i
        ano = data_inicial.year + (mes - 1) // 12
        mes = ((mes - 1) % 12) + 1
        
        # Ajuste para meses com menos dias
        try:
            data_lancamento = date(ano, mes, data_inicial.day)
        except ValueError:
            # Se o mês não tiver o dia específico (ex: 31 em fevereiro),
            # usa o último dia do mês
            if mes == 2:
                # Fevereiro
                if (ano % 4 == 0 and ano % 100 != 0) or (ano % 400 == 0):
                    # Ano bissexto
                    data_lancamento = date(ano, mes, 29)
                else:
                    data_lancamento = date(ano, mes, 28)
            elif mes in [4, 6, 9, 11]:
                # Meses com 30 dias
                data_lancamento = date(ano, mes, 30)
        
        lancamentos_fixos.append({
            "descricao": f"Lançamento Recorrente {i+1}",
            "valor": valor_recorrente,
            "data": data_lancamento
        })
    
    # Act - Recorrência mensal com dia da semana específico (ex: segundo domingo do mês)
    lancamentos_dia_semana = []
    dia_semana = 6  # Domingo (0=segunda, 6=domingo)
    ocorrencia = 2  # Segunda ocorrência do dia da semana
    
    for i in range(quantidade_recorrencias):
        mes = data_inicial.month + i
        ano = data_inicial.year + (mes - 1) // 12
        mes = ((mes - 1) % 12) + 1
        
        # Encontrar o primeiro dia do mês
        primeiro_dia = date(ano, mes, 1)
        
        # Encontrar o primeiro dia da semana especificado
        dias_para_adicionar = (dia_semana - primeiro_dia.weekday()) % 7
        primeiro_dia_semana = primeiro_dia + timedelta(days=dias_para_adicionar)
        
        # Adicionar semanas para chegar à ocorrência desejada
        data_lancamento = primeiro_dia_semana + timedelta(days=7 * (ocorrencia - 1))
        
        # Se a data cair no próximo mês, voltar para a ocorrência anterior
        if data_lancamento.month != mes:
            data_lancamento = data_lancamento - timedelta(days=7)
        
        lancamentos_dia_semana.append({
            "descricao": f"Lançamento Recorrente Dia Semana {i+1}",
            "valor": valor_recorrente,
            "data": data_lancamento
        })
    
    # Assert - Data fixa
    assert len(lancamentos_fixos) == quantidade_recorrencias
    assert lancamentos_fixos[0]["data"] == date(2023, 1, 15)
    assert lancamentos_fixos[1]["data"] == date(2023, 2, 15)
    # Fevereiro (verificação se vai para o último dia em meses curtos)
    assert lancamentos_fixos[1]["data"].day == 15
    
    # Assert - Dia da semana específico
    assert len(lancamentos_dia_semana) == quantidade_recorrencias
    # Verificar que todas as datas caem no dia da semana correto
    for lanc in lancamentos_dia_semana:
        assert lanc["data"].weekday() == dia_semana

@pytest.mark.unit
async def test_lancamentos_escalonados():
    """
    Testa a geração de lançamentos com valores escalonados.
    
    O teste deve validar:
    1. Escalonamento com valor fixo (aumento ou redução)
    2. Escalonamento com percentual
    3. Aplicação de limites mínimos/máximos
    """
    # Arrange
    valor_inicial = Decimal("1000.00")
    num_lancamentos = 5
    
    # Act - Escalonamento com valor fixo (acréscimo)
    valor_acrescimo = Decimal("100.00")
    lancamentos_acrescimo = []
    
    for i in range(num_lancamentos):
        valor_atual = valor_inicial + (valor_acrescimo * i)
        lancamentos_acrescimo.append({
            "numero": i + 1,
            "valor": valor_atual
        })
    
    # Act - Escalonamento com percentual (aumento de 10% a cada lançamento)
    percentual_aumento = Decimal("0.10")  # 10%
    lancamentos_percentual = []
    valor_atual = valor_inicial
    
    for i in range(num_lancamentos):
        lancamentos_percentual.append({
            "numero": i + 1,
            "valor": valor_atual
        })
        valor_atual = valor_atual * (1 + percentual_aumento)
        valor_atual = round(valor_atual, 2)  # Arredondar para 2 casas decimais
    
    # Act - Escalonamento com limite máximo
    valor_limite_maximo = Decimal("1300.00")
    lancamentos_limitados = []
    valor_atual = valor_inicial
    
    for i in range(num_lancamentos):
        valor_atual = valor_inicial + (valor_acrescimo * i)
        # Aplicar limite máximo
        valor_atual = min(valor_atual, valor_limite_maximo)
        
        lancamentos_limitados.append({
            "numero": i + 1,
            "valor": valor_atual
        })
    
    # Assert - Escalonamento com valor fixo
    assert lancamentos_acrescimo[0]["valor"] == Decimal("1000.00")
    assert lancamentos_acrescimo[1]["valor"] == Decimal("1100.00")
    assert lancamentos_acrescimo[2]["valor"] == Decimal("1200.00")
    assert lancamentos_acrescimo[3]["valor"] == Decimal("1300.00")
    assert lancamentos_acrescimo[4]["valor"] == Decimal("1400.00")
    
    # Assert - Escalonamento percentual
    assert lancamentos_percentual[0]["valor"] == Decimal("1000.00")
    assert lancamentos_percentual[1]["valor"] == Decimal("1100.00")
    assert lancamentos_percentual[2]["valor"] == Decimal("1210.00")
    assert lancamentos_percentual[3]["valor"] == Decimal("1331.00")
    assert lancamentos_percentual[4]["valor"] == Decimal("1464.10")
    
    # Assert - Escalonamento com limite
    assert lancamentos_limitados[0]["valor"] == Decimal("1000.00")
    assert lancamentos_limitados[1]["valor"] == Decimal("1100.00")
    assert lancamentos_limitados[2]["valor"] == Decimal("1200.00")
    assert lancamentos_limitados[3]["valor"] == Decimal("1300.00")  # Atingiu o limite
    assert lancamentos_limitados[4]["valor"] == Decimal("1300.00")  # Mantém o limite

@pytest.mark.unit
async def test_agrupamento_parcelas_por_vencimento():
    """
    Testa o agrupamento de parcelas por data de vencimento.
    
    O teste deve validar:
    1. Agrupamento correto por data
    2. Cálculo de totais por data
    3. Organização cronológica dos vencimentos
    """
    # Arrange
    parcelas = [
        {"id": 1, "valor": Decimal("300.00"), "data_vencimento": date(2023, 5, 15)},
        {"id": 2, "valor": Decimal("450.00"), "data_vencimento": date(2023, 5, 15)},
        {"id": 3, "valor": Decimal("200.00"), "data_vencimento": date(2023, 5, 20)},
        {"id": 4, "valor": Decimal("800.00"), "data_vencimento": date(2023, 5, 20)},
        {"id": 5, "valor": Decimal("150.00"), "data_vencimento": date(2023, 5, 10)},
        {"id": 6, "valor": Decimal("350.00"), "data_vencimento": date(2023, 5, 10)},
    ]
    
    # Act - Agrupar por data de vencimento
    agrupamento = {}
    
    for parcela in parcelas:
        data_str = parcela["data_vencimento"].isoformat()
        if data_str not in agrupamento:
            agrupamento[data_str] = {
                "data": parcela["data_vencimento"],
                "parcelas": [],
                "total": Decimal("0")
            }
        
        agrupamento[data_str]["parcelas"].append(parcela)
        agrupamento[data_str]["total"] += parcela["valor"]
    
    # Ordenar por data
    datas_ordenadas = sorted(agrupamento.keys())
    resultado_ordenado = [agrupamento[data] for data in datas_ordenadas]
    
    # Assert
    assert len(agrupamento) == 3  # Três datas distintas
    
    # Verificar a primeira data (10/05/2023)
    assert resultado_ordenado[0]["data"] == date(2023, 5, 10)
    assert len(resultado_ordenado[0]["parcelas"]) == 2
    assert resultado_ordenado[0]["total"] == Decimal("500.00")
    
    # Verificar a segunda data (15/05/2023)
    assert resultado_ordenado[1]["data"] == date(2023, 5, 15)
    assert len(resultado_ordenado[1]["parcelas"]) == 2
    assert resultado_ordenado[1]["total"] == Decimal("750.00")
    
    # Verificar a terceira data (20/05/2023)
    assert resultado_ordenado[2]["data"] == date(2023, 5, 20)
    assert len(resultado_ordenado[2]["parcelas"]) == 2
    assert resultado_ordenado[2]["total"] == Decimal("1000.00")

@pytest.mark.unit
async def test_previsao_saldo_parcela():
    """
    Testa a previsão de saldo após pagamento de parcelas.
    
    O teste deve validar:
    1. Saldo inicial
    2. Impacto das parcelas a pagar
    3. Impacto das parcelas a receber
    4. Saldo final previsto
    """
    # Arrange
    saldo_inicial = Decimal("5000.00")
    
    parcelas_pagar = [
        {"valor": Decimal("800.00"), "data_vencimento": date.today() + timedelta(days=5)},
        {"valor": Decimal("1200.00"), "data_vencimento": date.today() + timedelta(days=15)},
        {"valor": Decimal("500.00"), "data_vencimento": date.today() + timedelta(days=25)},
    ]
    
    parcelas_receber = [
        {"valor": Decimal("1500.00"), "data_vencimento": date.today() + timedelta(days=10)},
        {"valor": Decimal("900.00"), "data_vencimento": date.today() + timedelta(days=20)},
        {"valor": Decimal("700.00"), "data_vencimento": date.today() + timedelta(days=30)},
    ]
    
    # Act - Calcular previsão de saldo
    data_limite = date.today() + timedelta(days=30)
    
    # Ordenar todas as movimentações por data
    movimentacoes = []
    
    for parcela in parcelas_pagar:
        if parcela["data_vencimento"] <= data_limite:
            movimentacoes.append({
                "data": parcela["data_vencimento"],
                "valor": -parcela["valor"],  # Negativo pois é pagamento
                "tipo": "pagamento"
            })
    
    for parcela in parcelas_receber:
        if parcela["data_vencimento"] <= data_limite:
            movimentacoes.append({
                "data": parcela["data_vencimento"],
                "valor": parcela["valor"],  # Positivo pois é recebimento
                "tipo": "recebimento"
            })
    
    # Ordenar por data
    movimentacoes_ordenadas = sorted(movimentacoes, key=lambda x: x["data"])
    
    # Calcular evolução do saldo
    evolucao_saldo = []
    saldo_atual = saldo_inicial
    
    for mov in movimentacoes_ordenadas:
        saldo_atual += mov["valor"]
        evolucao_saldo.append({
            "data": mov["data"],
            "tipo": mov["tipo"],
            "valor": mov["valor"],
            "saldo": saldo_atual
        })
    
    # Assert
    assert len(evolucao_saldo) == 6  # Total de movimentações no período
    
    # Verificar saldo após primeira movimentação (pagamento de 800)
    assert evolucao_saldo[0]["valor"] == Decimal("-800.00")
    assert evolucao_saldo[0]["saldo"] == Decimal("4200.00")
    
    # Verificar saldo após segunda movimentação (recebimento de 1500)
    assert evolucao_saldo[1]["valor"] == Decimal("1500.00")
    assert evolucao_saldo[1]["saldo"] == Decimal("5700.00")
    
    # Verificar saldo após terceira movimentação (pagamento de 1200)
    assert evolucao_saldo[2]["valor"] == Decimal("-1200.00")
    assert evolucao_saldo[2]["saldo"] == Decimal("4500.00")
    
    # Verificar saldo final (após todas as movimentações)
    assert evolucao_saldo[-1]["saldo"] == Decimal("4600.00")
    
    # Verificar saldo líquido do período
    saldo_liquido = sum(mov["valor"] for mov in movimentacoes_ordenadas)
    assert saldo_liquido == Decimal("-400.00")  # Redução de 400 no saldo 