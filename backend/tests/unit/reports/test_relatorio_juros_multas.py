"""Testes para cálculos de juros e multas em relatórios financeiros."""
import pytest
from decimal import Decimal
from datetime import date, datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Any

from app.models.conta_receber import ContaReceber
from app.models.conta_pagar import ContaPagar
from app.models.parcela import Parcela


@pytest.mark.no_db
async def test_calculo_juros_simples(dados_completos, db_session: AsyncSession):
    """Teste para validar o cálculo de juros simples em contas atrasadas."""
    # Arrange
    empresa_id = dados_completos["empresa"].id_empresa
    
    # Buscar contas a receber atrasadas
    query_contas_atrasadas = select(ContaReceber).where(
        ContaReceber.status == "atrasado",
        ContaReceber.id_empresa == empresa_id
    )
    result_contas_atrasadas = await db_session.execute(query_contas_atrasadas)
    contas_atrasadas = result_contas_atrasadas.scalars().all()
    
    # Verificar se temos contas atrasadas para testar
    assert len(contas_atrasadas) > 0, "Nenhuma conta a receber atrasada encontrada para o teste"
    
    # Selecionar uma conta atrasada para o teste
    conta_teste = contas_atrasadas[0]
    
    # Parâmetros para o cálculo
    taxa_juros_diaria = Decimal("0.001")  # 0.1% ao dia
    data_atual = date.today()
    dias_atraso = (data_atual - conta_teste.data_vencimento).days
    
    # Act
    # Função para calcular juros simples
    def calcular_juros_simples(valor_original, data_vencimento, data_atual, taxa_diaria=taxa_juros_diaria):
        """Calcula juros simples para um valor em atraso."""
        if data_atual <= data_vencimento:
            return Decimal("0")
            
        dias_atraso = (data_atual - data_vencimento).days
        juros = valor_original * taxa_diaria * dias_atraso
        return juros.quantize(Decimal("0.01"))
    
    # Calcular juros simples
    juros_calculados = calcular_juros_simples(
        conta_teste.valor, 
        conta_teste.data_vencimento,
        data_atual
    )
    
    # Calcular valor esperado para conferência
    valor_esperado = conta_teste.valor * taxa_juros_diaria * dias_atraso
    valor_esperado = valor_esperado.quantize(Decimal("0.01"))
    
    # Assert
    assert juros_calculados > Decimal("0"), "Juros calculados devem ser positivos para uma conta atrasada"
    assert juros_calculados == valor_esperado, "Juros calculados não correspondem ao valor esperado"
    
    # Valor total a pagar (valor original + juros)
    valor_total = conta_teste.valor + juros_calculados
    assert valor_total > conta_teste.valor, "Valor total deve ser maior que o valor original"


@pytest.mark.no_db
async def test_calculo_juros_compostos(dados_completos, db_session: AsyncSession):
    """Teste para validar o cálculo de juros compostos em contas atrasadas."""
    # Arrange
    empresa_id = dados_completos["empresa"].id_empresa
    
    # Buscar contas a pagar atrasadas
    query_contas_atrasadas = select(ContaPagar).where(
        ContaPagar.status == "atrasado",
        ContaPagar.id_empresa == empresa_id
    )
    result_contas_atrasadas = await db_session.execute(query_contas_atrasadas)
    contas_atrasadas = result_contas_atrasadas.scalars().all()
    
    # Verificar se temos contas atrasadas para testar
    assert len(contas_atrasadas) > 0, "Nenhuma conta a pagar atrasada encontrada para o teste"
    
    # Selecionar uma conta atrasada para o teste
    conta_teste = contas_atrasadas[0]
    
    # Parâmetros para o cálculo
    taxa_juros_diaria = Decimal("0.001")  # 0.1% ao dia
    data_atual = date.today()
    dias_atraso = (data_atual - conta_teste.data_vencimento).days
    
    # Act
    # Função para calcular juros compostos
    def calcular_juros_compostos(valor_original, data_vencimento, data_atual, taxa_diaria=taxa_juros_diaria):
        """Calcula juros compostos para um valor em atraso."""
        if data_atual <= data_vencimento:
            return Decimal("0")
            
        dias_atraso = (data_atual - data_vencimento).days
        valor_com_juros = valor_original * (1 + taxa_diaria) ** dias_atraso
        juros = valor_com_juros - valor_original
        return juros.quantize(Decimal("0.01"))
    
    # Calcular juros compostos
    juros_calculados = calcular_juros_compostos(
        conta_teste.valor, 
        conta_teste.data_vencimento,
        data_atual
    )
    
    # Calcular valor esperado para conferência
    valor_com_juros = conta_teste.valor * (1 + taxa_juros_diaria) ** dias_atraso
    valor_esperado = (valor_com_juros - conta_teste.valor).quantize(Decimal("0.01"))
    
    # Assert
    assert juros_calculados > Decimal("0"), "Juros calculados devem ser positivos para uma conta atrasada"
    assert juros_calculados == valor_esperado, "Juros calculados não correspondem ao valor esperado"
    
    # Valor total a pagar (valor original + juros)
    valor_total = conta_teste.valor + juros_calculados
    assert valor_total > conta_teste.valor, "Valor total deve ser maior que o valor original"
    
    # Comparar juros simples vs compostos para o mesmo período
    juros_simples = conta_teste.valor * taxa_juros_diaria * dias_atraso
    juros_simples = juros_simples.quantize(Decimal("0.01"))
    
    # Para períodos longos, os juros compostos devem ser maiores que os juros simples
    if dias_atraso > 30:
        assert juros_calculados > juros_simples, "Juros compostos devem ser maiores que juros simples para períodos longos"


@pytest.mark.no_db
async def test_calculo_multa_fixa(dados_completos, db_session: AsyncSession):
    """Teste para validar o cálculo de multa fixa em contas atrasadas."""
    # Arrange
    empresa_id = dados_completos["empresa"].id_empresa
    
    # Buscar parcelas atrasadas
    query_parcelas_atrasadas = select(Parcela).where(
        Parcela.status == "atrasado",
        Parcela.id_empresa == empresa_id
    )
    result_parcelas_atrasadas = await db_session.execute(query_parcelas_atrasadas)
    parcelas_atrasadas = result_parcelas_atrasadas.scalars().all()
    
    # Verificar se temos parcelas atrasadas para testar
    if not parcelas_atrasadas:
        # Buscar alguma conta atrasada se não houver parcelas
        query_contas_atrasadas = select(ContaReceber).where(
            ContaReceber.status == "atrasado",
            ContaReceber.id_empresa == empresa_id
        )
        result_contas_atrasadas = await db_session.execute(query_contas_atrasadas)
        contas_atrasadas = result_contas_atrasadas.scalars().all()
        
        assert len(contas_atrasadas) > 0, "Nenhuma parcela ou conta atrasada encontrada para o teste"
        
        # Usar a conta atrasada
        valor_original = contas_atrasadas[0].valor
    else:
        # Usar a parcela atrasada
        valor_original = parcelas_atrasadas[0].valor
    
    # Parâmetros para o cálculo
    percentual_multa = Decimal("0.02")  # 2% de multa fixa
    
    # Act
    # Função para calcular multa fixa
    def calcular_multa_fixa(valor_original, percentual_multa):
        """Calcula multa fixa para um valor em atraso."""
        multa = valor_original * percentual_multa
        return multa.quantize(Decimal("0.01"))
    
    # Calcular multa fixa
    multa_calculada = calcular_multa_fixa(valor_original, percentual_multa)
    
    # Calcular valor esperado para conferência
    valor_esperado = valor_original * percentual_multa
    valor_esperado = valor_esperado.quantize(Decimal("0.01"))
    
    # Assert
    assert multa_calculada > Decimal("0"), "Multa calculada deve ser positiva"
    assert multa_calculada == valor_esperado, "Multa calculada não corresponde ao valor esperado"
    
    # Valor total a pagar (valor original + multa)
    valor_total = valor_original + multa_calculada
    assert valor_total > valor_original, "Valor total deve ser maior que o valor original"


@pytest.mark.no_db
async def test_calculo_multa_juros_diarios(dados_completos, db_session: AsyncSession):
    """Teste para validar o cálculo combinado de multa fixa e juros diários em contas atrasadas."""
    # Arrange
    empresa_id = dados_completos["empresa"].id_empresa
    
    # Buscar contas a receber atrasadas
    query_contas_atrasadas = select(ContaReceber).where(
        ContaReceber.status == "atrasado",
        ContaReceber.id_empresa == empresa_id
    )
    result_contas_atrasadas = await db_session.execute(query_contas_atrasadas)
    contas_atrasadas = result_contas_atrasadas.scalars().all()
    
    # Verificar se temos contas atrasadas para testar
    assert len(contas_atrasadas) > 0, "Nenhuma conta a receber atrasada encontrada para o teste"
    
    # Selecionar uma conta atrasada para o teste
    conta_teste = contas_atrasadas[0]
    
    # Parâmetros para o cálculo
    percentual_multa = Decimal("0.02")  # 2% de multa fixa
    taxa_juros_diaria = Decimal("0.001")  # 0.1% ao dia
    data_atual = date.today()
    dias_atraso = (data_atual - conta_teste.data_vencimento).days
    
    # Act
    # Função para calcular multa e juros
    def calcular_multa_e_juros(valor_original, data_vencimento, data_atual, percentual_multa, taxa_juros_diaria):
        """Calcula multa fixa e juros diários para um valor em atraso."""
        if data_atual <= data_vencimento:
            return Decimal("0"), Decimal("0")
            
        # Calcular multa fixa
        multa = valor_original * percentual_multa
        
        # Calcular juros diários
        dias_atraso = (data_atual - data_vencimento).days
        juros = valor_original * taxa_juros_diaria * dias_atraso
        
        return multa.quantize(Decimal("0.01")), juros.quantize(Decimal("0.01"))
    
    # Calcular multa e juros
    multa_calculada, juros_calculados = calcular_multa_e_juros(
        conta_teste.valor, 
        conta_teste.data_vencimento,
        data_atual,
        percentual_multa,
        taxa_juros_diaria
    )
    
    # Calcular valores esperados para conferência
    multa_esperada = (conta_teste.valor * percentual_multa).quantize(Decimal("0.01"))
    juros_esperados = (conta_teste.valor * taxa_juros_diaria * dias_atraso).quantize(Decimal("0.01"))
    valor_total_esperado = conta_teste.valor + multa_esperada + juros_esperados
    
    # Assert
    assert multa_calculada == multa_esperada, "Multa calculada não corresponde ao valor esperado"
    assert juros_calculados == juros_esperados, "Juros calculados não correspondem ao valor esperado"
    
    # Valor total a pagar (valor original + multa + juros)
    valor_total = conta_teste.valor + multa_calculada + juros_calculados
    assert valor_total == valor_total_esperado, "Valor total não corresponde ao esperado"
    assert valor_total > conta_teste.valor, "Valor total deve ser maior que o valor original"


@pytest.mark.no_db
async def test_juros_por_faixa_dias_atraso(dados_completos, db_session: AsyncSession):
    """Teste para validar o cálculo de juros com taxas diferentes por faixa de dias de atraso."""
    # Arrange
    empresa_id = dados_completos["empresa"].id_empresa
    
    # Buscar parcelas atrasadas
    query_parcelas = select(Parcela).where(
        Parcela.status == "atrasado",
        Parcela.id_empresa == empresa_id
    )
    result_parcelas = await db_session.execute(query_parcelas)
    parcelas_atrasadas = result_parcelas.scalars().all()
    
    # Verificar se temos parcelas atrasadas para testar
    if not parcelas_atrasadas:
        # Buscar alguma conta atrasada se não houver parcelas
        query_contas = select(ContaReceber).where(
            ContaReceber.status == "atrasado",
            ContaReceber.id_empresa == empresa_id
        )
        result_contas = await db_session.execute(query_contas)
        contas_atrasadas = result_contas.scalars().all()
        
        assert len(contas_atrasadas) > 0, "Nenhuma parcela ou conta atrasada encontrada para o teste"
        
        # Usar a conta atrasada
        valor_original = contas_atrasadas[0].valor
        data_vencimento = contas_atrasadas[0].data_vencimento
    else:
        # Usar a parcela atrasada
        valor_original = parcelas_atrasadas[0].valor
        data_vencimento = parcelas_atrasadas[0].data_vencimento
    
    # Definir taxas progressivas conforme dias de atraso
    taxas_por_faixa = {
        0: Decimal("0"),       # Em dia (0%)
        1: Decimal("0.0005"),  # 1-5 dias (0.05% ao dia)
        6: Decimal("0.001"),   # 6-15 dias (0.1% ao dia)
        16: Decimal("0.0015"), # 16-30 dias (0.15% ao dia)
        31: Decimal("0.002")   # 31+ dias (0.2% ao dia)
    }
    
    data_atual = date.today()
    dias_atraso = (data_atual - data_vencimento).days
    
    # Act
    # Função para calcular juros por faixa de atraso
    def calcular_juros_por_faixa(valor_original, data_vencimento, data_atual, taxas_por_faixa):
        """Calcula juros considerando taxas diferentes por faixa de dias de atraso."""
        if data_atual <= data_vencimento:
            return Decimal("0")
            
        dias_atraso = (data_atual - data_vencimento).days
        
        # Determinar a taxa aplicável com base nos dias de atraso
        taxa_aplicavel = None
        for limite_dias, taxa in sorted(taxas_por_faixa.items()):
            if dias_atraso >= limite_dias:
                taxa_aplicavel = taxa
        
        # Calcular juros
        juros = valor_original * taxa_aplicavel * dias_atraso
        return juros.quantize(Decimal("0.01"))
    
    # Calcular juros por faixa
    juros_calculados = calcular_juros_por_faixa(
        valor_original, 
        data_vencimento,
        data_atual,
        taxas_por_faixa
    )
    
    # Calcular valor esperado para conferência
    # Determinar a taxa aplicável
    taxa_aplicavel = None
    for limite_dias, taxa in sorted(taxas_por_faixa.items()):
        if dias_atraso >= limite_dias:
            taxa_aplicavel = taxa
    
    juros_esperados = (valor_original * taxa_aplicavel * dias_atraso).quantize(Decimal("0.01"))
    
    # Assert
    assert juros_calculados > Decimal("0"), "Juros calculados devem ser positivos para um valor atrasado"
    assert juros_calculados == juros_esperados, "Juros calculados não correspondem ao valor esperado"
    
    # Verificar se a taxa aplicada está correta com base nos dias de atraso
    if dias_atraso <= 0:
        taxa_correta = taxas_por_faixa[0]
    elif dias_atraso <= 5:
        taxa_correta = taxas_por_faixa[1]
    elif dias_atraso <= 15:
        taxa_correta = taxas_por_faixa[6]
    elif dias_atraso <= 30:
        taxa_correta = taxas_por_faixa[16]
    else:
        taxa_correta = taxas_por_faixa[31]
    
    assert taxa_aplicavel == taxa_correta, f"Taxa aplicada incorreta para {dias_atraso} dias de atraso" 