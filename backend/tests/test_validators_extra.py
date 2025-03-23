"""
Testes para as funções de validação extras.

Este módulo testa todas as funções de validação centralizadas no módulo validators_extra.
"""
import pytest
from decimal import Decimal
from app.utils.validators_extra import (
    validar_cep, validar_uf, validar_telefone, validar_data,
    validar_decimal, validar_email, validar_tipo_contato,
    validar_valor_contato
)


class TestValidarCep:
    """Testes para a função validar_cep."""

    def test_ceps_validos(self):
        """Testa CEPs válidos com e sem formatação."""
        ceps_validos = [
            "12345-678",
            "12345678",
            "01234-567",
            "01234567"
        ]
        for cep in ceps_validos:
            assert validar_cep(cep) == f"{cep[:5]}-{cep[5:]}".replace("-", "")[:5] + "-" + cep.replace("-", "")[5:]

    def test_ceps_invalidos(self):
        """Testa CEPs inválidos."""
        ceps_invalidos = [
            "1234-567",  # curto demais
            "123456789",  # longo demais
            "abcde-fgh",  # contém letras
            "",
            None
        ]
        for cep in ceps_invalidos:
            with pytest.raises(ValueError):
                validar_cep(cep)


class TestValidarUf:
    """Testes para a função validar_uf."""

    def test_ufs_validas(self):
        """Testa UFs válidas em diferentes formatos."""
        ufs_validas = [
            "SP", "sp", "RJ", "rj", "MG", "mg"
        ]
        for uf in ufs_validas:
            assert validar_uf(uf) == uf.upper()

    def test_ufs_invalidas(self):
        """Testa UFs inválidas."""
        ufs_invalidas = [
            "XX",  # não existe
            "ZZ",  # não existe
            "ABC",  # formato inválido
            "1",   # número
            "",
            None
        ]
        for uf in ufs_invalidas:
            with pytest.raises(ValueError):
                validar_uf(uf)


class TestValidarTelefone:
    """Testes para a função validar_telefone."""

    def test_telefones_validos(self):
        """Testa números de telefone válidos."""
        telefones_validos = [
            "(11) 98765-4321",
            "11987654321",
            "(21)3333-4444",
            "2133334444",
            "11 987654321"
        ]
        for telefone in telefones_validos:
            resultado = validar_telefone(telefone)
            assert len(resultado) in [14, 15]  # (11) 3333-4444 ou (11) 98765-4321
            assert resultado[0] == "("
            assert resultado[3] == ")"
            assert resultado[-5] == "-"

    def test_telefones_invalidos(self):
        """Testa números de telefone inválidos."""
        telefones_invalidos = [
            "(00) 98765-4321",  # DDD inválido
            "123",  # curto demais
            "123456789012345",  # longo demais
            "(11) abcd-efgh",  # contém letras
            "",
            None
        ]
        for telefone in telefones_invalidos:
            with pytest.raises(ValueError):
                validar_telefone(telefone)


class TestValidarData:
    """Testes para a função validar_data."""

    def test_datas_validas(self):
        """Testa datas válidas em diferentes formatos."""
        datas_validas = [
            "2023-01-01",
            "01/01/2023",
            "2023-12-31",
            "31/12/2023"
        ]
        for data in datas_validas:
            assert validar_data(data) == data

    def test_datas_invalidas(self):
        """Testa datas inválidas."""
        datas_invalidas = [
            "2023-13-01",  # mês inválido
            "2023-01-32",  # dia inválido
            "32/01/2023",  # dia inválido
            "01/13/2023",  # mês inválido
            "01-01-2023",  # formato não suportado por padrão
            "2023/01/01",  # formato não suportado por padrão
            "01-01-23",    # ano com 2 dígitos
            "",
            None
        ]
        for data in datas_invalidas:
            with pytest.raises(ValueError):
                validar_data(data)

    def test_formatos_personalizados(self):
        """Testa datas com formatos personalizados."""
        assert validar_data("01-01-2023", formatos=["%d-%m-%Y"]) == "01-01-2023"
        assert validar_data("2023/01/01", formatos=["%Y/%m/%d"]) == "2023/01/01"


class TestValidarDecimal:
    """Testes para a função validar_decimal."""

    def test_decimais_validos(self):
        """Testa valores decimais válidos."""
        decimais_validos = [
            "123.45",
            "123,45",
            "0.01",
            "0,01",
            "-123.45",
            "-123,45",
            123.45,
            0.01,
            -123.45,
            0,
            "0"
        ]
        for decimal in decimais_validos:
            resultado = validar_decimal(decimal)
            assert isinstance(resultado, Decimal)

    def test_decimais_invalidos(self):
        """Testa valores decimais inválidos."""
        decimais_invalidos = [
            "abc",
            "123.45.67",
            "123,45,67",
            "123a45",
            "",
            None
        ]
        for decimal in decimais_invalidos:
            with pytest.raises(ValueError):
                validar_decimal(decimal)


class TestValidarEmail:
    """Testes para a função validar_email."""

    def test_emails_validos(self):
        """Testa emails válidos."""
        emails_validos = [
            "usuario@exemplo.com.br",
            "usuario.nome@empresa.com",
            "user123@test.co",
            "user-name@domain.org",
            "user+tag@example.com"
        ]
        for email in emails_validos:
            assert validar_email(email) == email

    def test_emails_invalidos(self):
        """Testa emails inválidos."""
        emails_invalidos = [
            "usuario@",
            "@exemplo.com",
            "usuario@.com",
            "usuario@exemplo.",
            "usuário@exemplo.com",  # caractere especial
            "usuario@exemplo..com",
            "usuario@exemplo com",
            "usuario@exemplo,com",
            "",
            None
        ]
        for email in emails_invalidos:
            with pytest.raises(ValueError):
                validar_email(email)


class TestValidarTipoContato:
    """Testes para a função validar_tipo_contato."""

    def test_tipos_validos(self):
        """Testa tipos de contato válidos."""
        tipos_validos = [
            "celular",
            "CELULAR",
            "telefone",
            "email",
            "whatsapp",
            "instagram",
            "facebook",
            "outro"
        ]
        for tipo in tipos_validos:
            assert validar_tipo_contato(tipo) == tipo.lower()

    def test_tipos_invalidos(self):
        """Testa tipos de contato inválidos."""
        tipos_invalidos = [
            "telegram",  # não suportado
            "123",      # número
            "",
            None
        ]
        for tipo in tipos_invalidos:
            with pytest.raises(ValueError):
                validar_tipo_contato(tipo)


class TestValidarValorContato:
    """Testes para a função validar_valor_contato."""

    def test_valores_validos(self):
        """Testa valores válidos para diferentes tipos de contato."""
        casos_teste = [
            ("celular", "11987654321"),
            ("telefone", "1133334444"),
            ("whatsapp", "(11) 98765-4321"),
            ("email", "user@example.com"),
            ("instagram", "@usuario"),
            ("facebook", "fb.com/usuario"),
            ("outro", "qualquer valor")
        ]
        for tipo, valor in casos_teste:
            resultado = validar_valor_contato(tipo, valor)
            assert resultado  # não deve ser vazio

    def test_valores_invalidos(self):
        """Testa valores inválidos para diferentes tipos de contato."""
        casos_teste = [
            ("celular", "123"),  # muito curto
            ("telefone", "abcdefghij"),  # contém letras
            ("whatsapp", "00987654321"),  # DDD inválido
            ("email", "usuario@.com"),  # email inválido
        ]
        for tipo, valor in casos_teste:
            with pytest.raises(ValueError):
                validar_valor_contato(tipo, valor) 