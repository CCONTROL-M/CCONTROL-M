"""Testes para validar exceções financeiras e casos especiais."""
import pytest
from datetime import date, timedelta, datetime
from decimal import Decimal, InvalidOperation
from unittest.mock import MagicMock, AsyncMock, patch
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

class ValorNegativoError(Exception):
    """Exceção para valor negativo."""
    pass

class DataInvalidaError(Exception):
    """Exceção para data inválida."""
    pass

class DuplicacaoError(Exception):
    """Exceção para duplicação de registros."""
    pass

@pytest.mark.unit
async def test_rejeicao_valor_negativo():
    """
    Testa a rejeição de valores negativos em cálculos financeiros.
    
    O teste deve validar:
    1. Detecção correta de valores negativos
    2. Lançamento de exceção apropriada
    3. Mensagem de erro coerente
    """
    # Arrange
    valor_negativo = Decimal("-100.00")
    valor_zero = Decimal("0.00")
    valor_positivo = Decimal("100.00")
    
    # Act/Assert - Validar função que rejeita valores negativos
    def validar_valor_positivo(valor):
        if valor < 0:
            raise ValorNegativoError(f"Valor não pode ser negativo: {valor}")
        return True
    
    # Testar valor negativo
    with pytest.raises(ValorNegativoError) as excinfo:
        validar_valor_positivo(valor_negativo)
    assert "Valor não pode ser negativo" in str(excinfo.value)
    
    # Testar valores não negativos
    assert validar_valor_positivo(valor_zero) is True
    assert validar_valor_positivo(valor_positivo) is True

@pytest.mark.unit
async def test_rejeicao_valor_zero_divisao():
    """
    Testa a rejeição de divisão por zero em cálculos financeiros.
    
    O teste deve validar:
    1. Detecção de tentativa de divisão por zero
    2. Tratamento adequado para o caso
    3. Prevenção de erros de execução
    """
    # Arrange
    valor_total = Decimal("1000.00")
    numero_parcelas_zero = 0
    numero_parcelas_valido = 3
    
    # Act/Assert - Calcular valor da parcela com proteção contra divisão por zero
    def calcular_valor_parcela(total, num_parcelas):
        if num_parcelas <= 0:
            raise ValueError("Número de parcelas deve ser maior que zero")
        return total / num_parcelas
    
    # Testar divisão por zero
    with pytest.raises(ValueError) as excinfo:
        calcular_valor_parcela(valor_total, numero_parcelas_zero)
    assert "deve ser maior que zero" in str(excinfo.value)
    
    # Testar divisão válida
    valor_parcela = calcular_valor_parcela(valor_total, numero_parcelas_valido)
    assert valor_parcela == Decimal("333.33333333333333333333333333")

@pytest.mark.unit
async def test_validacao_data_vencimento():
    """
    Testa a validação de datas de vencimento.
    
    O teste deve validar:
    1. Rejeição de datas no passado
    2. Rejeição de datas muito distantes no futuro
    3. Aceitação de datas válidas
    """
    # Arrange
    data_passada = date.today() - timedelta(days=1)
    data_muito_futura = date.today() + timedelta(days=365 * 10)  # 10 anos no futuro
    data_valida = date.today() + timedelta(days=30)
    
    limite_dias_futuro = 365 * 5  # 5 anos
    
    # Act/Assert - Função que valida datas de vencimento
    def validar_data_vencimento(data_venc):
        if data_venc < date.today():
            raise DataInvalidaError("Data de vencimento não pode ser no passado")
        
        dias_futuro = (data_venc - date.today()).days
        if dias_futuro > limite_dias_futuro:
            raise DataInvalidaError(f"Data de vencimento não pode ser mais de {limite_dias_futuro} dias no futuro")
        
        return True
    
    # Testar data no passado
    with pytest.raises(DataInvalidaError) as excinfo:
        validar_data_vencimento(data_passada)
    assert "não pode ser no passado" in str(excinfo.value)
    
    # Testar data muito no futuro
    with pytest.raises(DataInvalidaError) as excinfo:
        validar_data_vencimento(data_muito_futura)
    assert "não pode ser mais de" in str(excinfo.value)
    
    # Testar data válida
    assert validar_data_vencimento(data_valida) is True

@pytest.mark.unit
async def test_validacao_duplicidade_parcelas():
    """
    Testa a validação de duplicidade de parcelas.
    
    O teste deve validar:
    1. Detecção de parcelas duplicadas
    2. Lançamento de exceção apropriada
    3. Mensagem de erro coerente
    """
    # Arrange
    parcelas = [
        {"id": 1, "numero": 1, "valor": Decimal("100.00")},
        {"id": 2, "numero": 2, "valor": Decimal("100.00")},
        {"id": 3, "numero": 3, "valor": Decimal("100.00")}
    ]
    
    nova_parcela_valida = {"numero": 4, "valor": Decimal("100.00")}
    nova_parcela_duplicada = {"numero": 2, "valor": Decimal("150.00")}  # Mesmo número da parcela 2
    
    # Act/Assert - Função que verifica duplicidade
    def verificar_duplicidade(lista_parcelas, nova_parcela):
        for p in lista_parcelas:
            if p["numero"] == nova_parcela["numero"]:
                raise DuplicacaoError(f"Já existe uma parcela com o número {nova_parcela['numero']}")
        return True
    
    # Testar parcela duplicada
    with pytest.raises(DuplicacaoError) as excinfo:
        verificar_duplicidade(parcelas, nova_parcela_duplicada)
    assert "Já existe uma parcela" in str(excinfo.value)
    
    # Testar parcela válida
    assert verificar_duplicidade(parcelas, nova_parcela_valida) is True

@pytest.mark.unit
async def test_validacao_integridade_lancamento():
    """
    Testa a validação de integridade de um lançamento financeiro.
    
    O teste deve validar:
    1. Verificação de campos obrigatórios
    2. Validação de tipos de dados
    3. Rejeição de valores inválidos
    """
    # Arrange
    lancamento_valido = {
        "descricao": "Pagamento de serviço",
        "valor": Decimal("500.00"),
        "data": date.today(),
        "tipo": "despesa"
    }
    
    lancamento_sem_descricao = {
        "valor": Decimal("500.00"),
        "data": date.today(),
        "tipo": "despesa"
    }
    
    lancamento_valor_invalido = {
        "descricao": "Pagamento de serviço",
        "valor": "quinhentos reais",  # Tipo inválido
        "data": date.today(),
        "tipo": "despesa"
    }
    
    lancamento_tipo_invalido = {
        "descricao": "Pagamento de serviço",
        "valor": Decimal("500.00"),
        "data": date.today(),
        "tipo": "outro"  # Tipo não aceito
    }
    
    # Act/Assert - Função que valida lançamento
    def validar_lancamento(lanc):
        # Verificar campos obrigatórios
        campos_obrigatorios = ["descricao", "valor", "data", "tipo"]
        for campo in campos_obrigatorios:
            if campo not in lanc:
                raise ValueError(f"Campo obrigatório ausente: {campo}")
        
        # Validar tipo de dados
        if not isinstance(lanc["valor"], Decimal):
            raise TypeError("Valor deve ser do tipo Decimal")
        
        if not isinstance(lanc["data"], date):
            raise TypeError("Data deve ser do tipo date")
        
        # Validar valores
        if lanc["tipo"] not in ["receita", "despesa", "transferencia"]:
            raise ValueError(f"Tipo inválido: {lanc['tipo']}. Deve ser 'receita', 'despesa' ou 'transferencia'")
        
        return True
    
    # Testar lançamento válido
    assert validar_lancamento(lancamento_valido) is True
    
    # Testar lançamento sem descrição
    with pytest.raises(ValueError) as excinfo:
        validar_lancamento(lancamento_sem_descricao)
    assert "Campo obrigatório ausente" in str(excinfo.value)
    
    # Testar lançamento com valor de tipo inválido
    with pytest.raises(TypeError) as excinfo:
        validar_lancamento(lancamento_valor_invalido)
    assert "Valor deve ser do tipo Decimal" in str(excinfo.value)
    
    # Testar lançamento com tipo inválido
    with pytest.raises(ValueError) as excinfo:
        validar_lancamento(lancamento_tipo_invalido)
    assert "Tipo inválido" in str(excinfo.value)

@pytest.mark.unit
async def test_conversao_segura_decimal():
    """
    Testa a conversão segura de valores para Decimal.
    
    O teste deve validar:
    1. Conversão de string válida para Decimal
    2. Conversão de número para Decimal
    3. Tratamento de erros para valores não conversíveis
    """
    # Arrange
    valor_str_valido = "123.45"
    valor_str_invalido = "123,45"  # Usa vírgula em vez de ponto
    valor_str_texto = "não é um número"
    valor_float = 123.45
    valor_int = 123
    
    # Act/Assert - Função de conversão segura
    def converter_para_decimal(valor):
        try:
            if isinstance(valor, (int, float)):
                return Decimal(str(valor))
            return Decimal(valor)
        except (InvalidOperation, TypeError, ValueError):
            raise ValueError(f"Valor não pode ser convertido para Decimal: {valor}")
    
    # Testar conversões válidas
    assert converter_para_decimal(valor_str_valido) == Decimal("123.45")
    assert converter_para_decimal(valor_float) == Decimal("123.45")
    assert converter_para_decimal(valor_int) == Decimal("123")
    
    # Testar conversões inválidas
    with pytest.raises(ValueError) as excinfo:
        converter_para_decimal(valor_str_invalido)
    assert "não pode ser convertido" in str(excinfo.value)
    
    with pytest.raises(ValueError) as excinfo:
        converter_para_decimal(valor_str_texto)
    assert "não pode ser convertido" in str(excinfo.value)

@pytest.mark.unit
async def test_validacao_data_retroativa():
    """
    Testa a validação de operações com data retroativa.
    
    O teste deve validar:
    1. Operações retroativas são permitidas somente com autorização
    2. Operações com data futura são rejeitadas em certos contextos
    3. Verificações de data conforme regras de negócio
    """
    # Arrange
    hoje = date.today()
    ontem = hoje - timedelta(days=1)
    mes_passado = hoje.replace(month=hoje.month-1 if hoje.month > 1 else 12, year=hoje.year if hoje.month > 1 else hoje.year-1)
    amanha = hoje + timedelta(days=1)
    
    limite_retroativo_dias = 30
    limite_retroativo_data = hoje - timedelta(days=limite_retroativo_dias)
    
    # Act/Assert - Função para validar operação retroativa
    def validar_data_operacao(data_operacao, permite_retroativo=False, permite_futuro=False, exige_autorizacao=False):
        # Verificar operação no futuro
        if data_operacao > hoje and not permite_futuro:
            raise DataInvalidaError("Operações com data futura não são permitidas")
        
        # Verificar operação retroativa
        if data_operacao < hoje:
            # Verificar limite de retroatividade
            if data_operacao < limite_retroativo_data:
                raise DataInvalidaError(f"Operações com mais de {limite_retroativo_dias} dias no passado não são permitidas")
            
            # Verificar se operação retroativa é permitida
            if not permite_retroativo:
                raise DataInvalidaError("Operações retroativas não são permitidas")
            
            # Verificar se exige autorização
            if exige_autorizacao:
                return {"valido": True, "exige_autorizacao": True, "mensagem": "Operação retroativa requer autorização"}
        
        return {"valido": True, "exige_autorizacao": False}
    
    # Testar operação com data de hoje
    resultado_hoje = validar_data_operacao(hoje)
    assert resultado_hoje["valido"] is True
    assert resultado_hoje["exige_autorizacao"] is False
    
    # Testar operação com data futura (não permitida)
    with pytest.raises(DataInvalidaError) as excinfo:
        validar_data_operacao(amanha)
    assert "data futura não são permitidas" in str(excinfo.value)
    
    # Testar operação com data futura (permitida)
    resultado_amanha = validar_data_operacao(amanha, permite_futuro=True)
    assert resultado_amanha["valido"] is True
    
    # Testar operação retroativa (não permitida)
    with pytest.raises(DataInvalidaError) as excinfo:
        validar_data_operacao(ontem)
    assert "retroativas não são permitidas" in str(excinfo.value)
    
    # Testar operação retroativa (permitida, sem autorização)
    resultado_ontem = validar_data_operacao(ontem, permite_retroativo=True)
    assert resultado_ontem["valido"] is True
    assert resultado_ontem["exige_autorizacao"] is False
    
    # Testar operação retroativa (permitida, com autorização)
    resultado_ontem_auth = validar_data_operacao(ontem, permite_retroativo=True, exige_autorizacao=True)
    assert resultado_ontem_auth["valido"] is True
    assert resultado_ontem_auth["exige_autorizacao"] is True
    
    # Testar operação retroativa fora do limite
    with pytest.raises(DataInvalidaError) as excinfo:
        validar_data_operacao(mes_passado, permite_retroativo=True)
    assert f"mais de {limite_retroativo_dias} dias no passado" in str(excinfo.value)

@pytest.mark.unit
async def test_validacao_rateio_valores():
    """
    Testa a validação de rateio de valores.
    
    O teste deve validar:
    1. A soma das partes deve ser igual ao total
    2. Não são permitidos valores negativos nas partes
    3. Ajuste automático para compensar arredondamentos
    """
    # Arrange
    valor_total = Decimal("1000.00")
    
    rateio_valido = [
        {"descricao": "Parte 1", "percentual": Decimal("0.3"), "valor": Decimal("300.00")},
        {"descricao": "Parte 2", "percentual": Decimal("0.5"), "valor": Decimal("500.00")},
        {"descricao": "Parte 3", "percentual": Decimal("0.2"), "valor": Decimal("200.00")}
    ]
    
    rateio_invalido_soma = [
        {"descricao": "Parte 1", "percentual": Decimal("0.3"), "valor": Decimal("300.00")},
        {"descricao": "Parte 2", "percentual": Decimal("0.4"), "valor": Decimal("400.00")},
        {"descricao": "Parte 3", "percentual": Decimal("0.2"), "valor": Decimal("200.00")}
    ]  # Soma = 90%
    
    rateio_com_negativo = [
        {"descricao": "Parte 1", "percentual": Decimal("0.3"), "valor": Decimal("300.00")},
        {"descricao": "Parte 2", "percentual": Decimal("-0.1"), "valor": Decimal("-100.00")},
        {"descricao": "Parte 3", "percentual": Decimal("0.8"), "valor": Decimal("800.00")}
    ]
    
    # Act/Assert - Função que valida rateio
    def validar_rateio(total, partes):
        # Verificar valores negativos
        for parte in partes:
            if parte["valor"] < 0 or parte["percentual"] < 0:
                raise ValorNegativoError(f"Rateio não pode conter valores negativos: {parte['descricao']}")
        
        # Verificar soma dos percentuais
        soma_percentuais = sum(parte["percentual"] for parte in partes)
        if soma_percentuais != Decimal("1"):
            raise ValueError(f"Soma dos percentuais deve ser 100%, encontrado: {soma_percentuais*100}%")
        
        # Verificar soma dos valores
        soma_valores = sum(parte["valor"] for parte in partes)
        if soma_valores != total:
            raise ValueError(f"Soma dos valores ({soma_valores}) difere do total ({total})")
        
        return True
    
    # Testar rateio válido
    assert validar_rateio(valor_total, rateio_valido) is True
    
    # Testar rateio com soma incorreta de percentuais
    with pytest.raises(ValueError) as excinfo:
        validar_rateio(valor_total, rateio_invalido_soma)
    assert "Soma dos percentuais deve ser 100%" in str(excinfo.value)
    
    # Testar rateio com valor negativo
    with pytest.raises(ValorNegativoError) as excinfo:
        validar_rateio(valor_total, rateio_com_negativo)
    assert "não pode conter valores negativos" in str(excinfo.value)

@pytest.mark.unit
async def test_validacao_conciliacao_bancaria():
    """
    Testa a validação de conciliação bancária.
    
    O teste deve validar:
    1. Validação de saldo bancário informado contra saldo calculado
    2. Identificação de divergências
    3. Tratamento de ajustes de conciliação
    """
    # Arrange
    lancamentos = [
        {"tipo": "receita", "valor": Decimal("1000.00"), "conciliado": True},
        {"tipo": "despesa", "valor": Decimal("500.00"), "conciliado": True},
        {"tipo": "receita", "valor": Decimal("300.00"), "conciliado": False},
        {"tipo": "despesa", "valor": Decimal("200.00"), "conciliado": False}
    ]
    
    saldo_inicial = Decimal("500.00")
    saldo_extrato = Decimal("1000.00")  # Saldo conforme extrato bancário
    
    # Act - Calcular saldo conforme lançamentos conciliados
    saldo_calculado = saldo_inicial
    
    for lanc in lancamentos:
        if lanc["conciliado"]:
            valor = lanc["valor"] if lanc["tipo"] == "receita" else -lanc["valor"]
            saldo_calculado += valor
    
    # Verificar divergência
    divergencia = saldo_extrato - saldo_calculado
    
    # Gerar ajuste de conciliação se houver divergência
    ajuste_conciliacao = None
    if divergencia != 0:
        tipo_ajuste = "receita" if divergencia > 0 else "despesa"
        valor_ajuste = abs(divergencia)
        
        ajuste_conciliacao = {
            "tipo": tipo_ajuste,
            "valor": valor_ajuste,
            "descricao": "Ajuste de conciliação bancária",
            "conciliado": True,
            "data": date.today()
        }
    
    # Assert
    assert saldo_calculado == Decimal("1000.00")  # 500 (inicial) + 1000 (receita) - 500 (despesa)
    assert divergencia == Decimal("0.00")  # Sem divergência neste caso
    assert ajuste_conciliacao is None  # Não deve gerar ajuste
    
    # Testar com divergência
    saldo_extrato_divergente = Decimal("950.00")
    divergencia_2 = saldo_extrato_divergente - saldo_calculado
    
    ajuste_conciliacao_2 = None
    if divergencia_2 != 0:
        tipo_ajuste = "receita" if divergencia_2 > 0 else "despesa"
        valor_ajuste = abs(divergencia_2)
        
        ajuste_conciliacao_2 = {
            "tipo": tipo_ajuste,
            "valor": valor_ajuste,
            "descricao": "Ajuste de conciliação bancária",
            "conciliado": True,
            "data": date.today()
        }
    
    assert divergencia_2 == Decimal("-50.00")  # Divergência negativa
    assert ajuste_conciliacao_2 is not None
    assert ajuste_conciliacao_2["tipo"] == "despesa"
    assert ajuste_conciliacao_2["valor"] == Decimal("50.00") 