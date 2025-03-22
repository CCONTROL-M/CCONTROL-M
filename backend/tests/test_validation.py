"""
Testes para o módulo de validação.

Verifica todas as funções do módulo de validação e seus comportamentos
esperados com diferentes tipos de entrada.
"""
import pytest
from app.utils.validation import (
    is_valid_email, is_valid_cpf, is_valid_cnpj, is_valid_phone,
    is_valid_date, is_valid_decimal, is_valid_uuid, sanitize_string,
    detect_attack_patterns, validate_json_structure, has_attack_input,
    validate_url_params
)


class TestEmailValidation:
    """Testes para a função is_valid_email"""

    def test_valid_emails(self):
        """Testa emails válidos"""
        valid_emails = [
            "usuario@exemplo.com.br",
            "usuario.nome@empresa.com",
            "user123@test.co",
            "user-name@domain.org",
            "user+tag@example.com"
        ]
        for email in valid_emails:
            assert is_valid_email(email) is True

    def test_invalid_emails(self):
        """Testa emails inválidos"""
        invalid_emails = [
            "usuario@",
            "@exemplo.com",
            "usuario@.com",
            "usuario@exemplo.",
            "usuário@exemplo.com",  # caractere especial
            "usuario@exemplo..com",
            "usuario@exemplo com",
            "usuario@exemplo,com",
            "",
            None,
            123
        ]
        for email in invalid_emails:
            assert is_valid_email(email) is False


class TestCpfValidation:
    """Testes para a função is_valid_cpf"""

    def test_valid_cpfs(self):
        """Testa CPFs válidos com e sem formatação"""
        valid_cpfs = [
            "529.982.247-25",
            "52998224725",
            "111.444.777-35",
            "11144477735"
        ]
        for cpf in valid_cpfs:
            assert is_valid_cpf(cpf) is True

    def test_invalid_cpfs(self):
        """Testa CPFs inválidos"""
        invalid_cpfs = [
            "111.111.111-11",  # dígitos repetidos
            "123.456.789-10",  # inválido pelo algoritmo
            "529.982.247-24",  # dígito verificador errado
            "123456",  # curto demais
            "123456789012",  # longo demais
            "",
            None,
            12345678901
        ]
        for cpf in invalid_cpfs:
            assert is_valid_cpf(cpf) is False


class TestCnpjValidation:
    """Testes para a função is_valid_cnpj"""

    def test_valid_cnpjs(self):
        """Testa CNPJs válidos com e sem formatação"""
        valid_cnpjs = [
            "13.347.016/0001-17",
            "13347016000117",
            "69.103.604/0001-60",
            "69103604000160"
        ]
        for cnpj in valid_cnpjs:
            assert is_valid_cnpj(cnpj) is True

    def test_invalid_cnpjs(self):
        """Testa CNPJs inválidos"""
        invalid_cnpjs = [
            "11.111.111/1111-11",  # dígitos repetidos
            "12.345.678/0001-90",  # inválido pelo algoritmo
            "13.347.016/0001-18",  # dígito verificador errado
            "123456789",  # curto demais
            "123456789012345",  # longo demais
            "",
            None,
            13347016000117
        ]
        for cnpj in invalid_cnpjs:
            assert is_valid_cnpj(cnpj) is False


class TestPhoneValidation:
    """Testes para a função is_valid_phone"""

    def test_valid_phones(self):
        """Testa números de telefone válidos"""
        valid_phones = [
            "(11) 98765-4321",
            "11987654321",
            "(21)3333-4444",
            "2133334444",
            "11 987654321"
        ]
        for phone in valid_phones:
            assert is_valid_phone(phone) is True

    def test_invalid_phones(self):
        """Testa números de telefone inválidos"""
        invalid_phones = [
            "(00) 98765-4321",  # DDD inválido
            "123",  # curto demais
            "123456789012345",  # longo demais
            "(11) abcd-efgh",  # contém letras
            "",
            None,
            1234567890
        ]
        for phone in invalid_phones:
            assert is_valid_phone(phone) is False


class TestDateValidation:
    """Testes para a função is_valid_date"""

    def test_valid_dates(self):
        """Testa datas válidas em diferentes formatos"""
        valid_dates = [
            "2023-01-01",
            "01/01/2023",
            "2023-12-31",
            "31/12/2023"
        ]
        for date in valid_dates:
            assert is_valid_date(date) is True

    def test_invalid_dates(self):
        """Testa datas inválidas"""
        invalid_dates = [
            "2023-13-01",  # mês inválido
            "2023-01-32",  # dia inválido
            "32/01/2023",  # dia inválido
            "01/13/2023",  # mês inválido
            "01-01-2023",  # formato não suportado por padrão
            "2023/01/01",  # formato não suportado por padrão
            "01-01-23",    # ano com 2 dígitos
            "",
            None,
            20230101
        ]
        for date in invalid_dates:
            assert is_valid_date(date) is False

    def test_custom_format(self):
        """Testa datas com formatos personalizados"""
        assert is_valid_date("01-01-2023", formats=["%d-%m-%Y"]) is True
        assert is_valid_date("2023/01/01", formats=["%Y/%m/%d"]) is True


class TestDecimalValidation:
    """Testes para a função is_valid_decimal"""

    def test_valid_decimals(self):
        """Testa valores decimais válidos"""
        valid_decimals = [
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
        for decimal in valid_decimals:
            assert is_valid_decimal(decimal) is True

    def test_invalid_decimals(self):
        """Testa valores decimais inválidos"""
        invalid_decimals = [
            "abc",
            "123.45.67",
            "123,45,67",
            "123a45",
            "",
            None
        ]
        for decimal in invalid_decimals:
            assert is_valid_decimal(decimal) is False


class TestUuidValidation:
    """Testes para a função is_valid_uuid"""

    def test_valid_uuids(self):
        """Testa UUIDs válidos"""
        valid_uuids = [
            "123e4567-e89b-12d3-a456-426614174000",
            "c73bcdcc-2669-4bf6-81d3-e4ae73fb11fd",
            "C73BCDCC-2669-4BF6-81D3-E4AE73FB11FD"  # maiúsculas também são válidas
        ]
        for uuid in valid_uuids:
            assert is_valid_uuid(uuid) is True

    def test_invalid_uuids(self):
        """Testa UUIDs inválidos"""
        invalid_uuids = [
            "123e4567-e89b-12d3-a456-4266141740",  # curto demais
            "123e4567-e89b-12d3-a456-42661417400g",  # caractere inválido
            "123e4567e89b12d3a4564266141740",  # sem hífens
            "",
            None,
            123
        ]
        for uuid in invalid_uuids:
            assert is_valid_uuid(uuid) is False


class TestStringSanitization:
    """Testes para a função sanitize_string"""

    def test_basic_sanitization(self):
        """Testa sanitização básica de strings"""
        assert sanitize_string("<script>alert('XSS')</script>") == "scriptalertXSSscript"
        assert sanitize_string("Nome com (parênteses) é permitido") == "Nome com (parênteses) é permitido"
        assert sanitize_string("Email: user@example.com") == "Email: user@example.com"
        assert sanitize_string("Caracteres especiais: !@#$%^&*()") == "Caracteres especiais: @()[]/"

    def test_max_length_limitation(self):
        """Testa limitação de tamanho máximo"""
        long_string = "a" * 100
        assert len(sanitize_string(long_string, max_length=50)) == 50
        assert sanitize_string(long_string, max_length=50) == "a" * 50

    def test_invalid_inputs(self):
        """Testa entradas inválidas"""
        assert sanitize_string(None) == ""
        assert sanitize_string(123) == ""
        assert sanitize_string("") == ""


class TestAttackDetection:
    """Testes para a função detect_attack_patterns"""

    def test_sql_injection_detection(self):
        """Testa detecção de SQL Injection"""
        sql_injections = [
            "SELECT * FROM users",
            "1' OR '1'='1",
            "1'; DROP TABLE users; --",
            "' OR 1=1 --",
            "admin' --"
        ]
        for injection in sql_injections:
            result = detect_attack_patterns(injection)
            assert "sql_injection" in result

    def test_xss_detection(self):
        """Testa detecção de XSS"""
        xss_attacks = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "<iframe src=javascript:alert('XSS')>",
            "eval('alert(1)')"
        ]
        for attack in xss_attacks:
            result = detect_attack_patterns(attack)
            assert "xss" in result

    def test_path_traversal_detection(self):
        """Testa detecção de Path Traversal"""
        path_traversal = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "/etc/passwd",
            "file:///etc/passwd"
        ]
        for attack in path_traversal:
            result = detect_attack_patterns(attack)
            assert "path_traversal" in result

    def test_command_injection_detection(self):
        """Testa detecção de Command Injection"""
        command_injections = [
            "ls; cat /etc/passwd",
            "ping 127.0.0.1 | cat /etc/passwd",
            "`cat /etc/passwd`",
            "$(cat /etc/passwd)"
        ]
        for attack in command_injections:
            result = detect_attack_patterns(attack)
            assert "command_injection" in result

    def test_safe_inputs(self):
        """Testa entradas seguras (sem ataques)"""
        safe_inputs = [
            "Nome do usuário",
            "email@exemplo.com",
            "123-456",
            "Texto normal sem ataques"
        ]
        for safe in safe_inputs:
            result = detect_attack_patterns(safe)
            assert not result


class TestJsonStructureValidation:
    """Testes para a função validate_json_structure"""

    def test_valid_structure(self):
        """Testa estrutura JSON válida"""
        schema = {
            "nome": {"type": "string", "required": True},
            "email": {"type": "string", "required": True, "validators": [is_valid_email]},
            "idade": {"type": "number", "required": False, "min_value": 18, "max_value": 100},
            "ativo": {"type": "boolean", "required": False}
        }
        
        valid_data = {
            "nome": "João Silva",
            "email": "joao@exemplo.com",
            "idade": 30,
            "ativo": True
        }
        
        errors = validate_json_structure(valid_data, schema)
        assert not errors

    def test_missing_required_field(self):
        """Testa campo obrigatório ausente"""
        schema = {
            "nome": {"type": "string", "required": True},
            "email": {"type": "string", "required": True}
        }
        
        invalid_data = {
            "nome": "João Silva"
        }
        
        errors = validate_json_structure(invalid_data, schema)
        assert "email" in errors
        assert "Campo obrigatório" in errors["email"][0]

    def test_invalid_field_type(self):
        """Testa tipo de campo inválido"""
        schema = {
            "nome": {"type": "string", "required": True},
            "idade": {"type": "number", "required": True}
        }
        
        invalid_data = {
            "nome": "João Silva",
            "idade": "trinta"
        }
        
        errors = validate_json_structure(invalid_data, schema)
        assert "idade" in errors
        assert "Tipo inválido" in errors["idade"][0]

    def test_validator_failure(self):
        """Testa falha no validador personalizado"""
        schema = {
            "email": {"type": "string", "required": True, "validators": [is_valid_email]}
        }
        
        invalid_data = {
            "email": "email_invalido"
        }
        
        errors = validate_json_structure(invalid_data, schema)
        assert "email" in errors
        assert "Email inválido" in errors["email"][0]

    def test_min_max_value_validation(self):
        """Testa validação de valor mínimo e máximo"""
        schema = {
            "idade": {"type": "number", "required": True, "min_value": 18, "max_value": 100}
        }
        
        # Teste valor muito baixo
        invalid_data_low = {
            "idade": 17
        }
        errors_low = validate_json_structure(invalid_data_low, schema)
        assert "idade" in errors_low
        assert "Valor mínimo permitido: 18" in errors_low["idade"][0]
        
        # Teste valor muito alto
        invalid_data_high = {
            "idade": 101
        }
        errors_high = validate_json_structure(invalid_data_high, schema)
        assert "idade" in errors_high
        assert "Valor máximo permitido: 100" in errors_high["idade"][0]


class TestAttackInputDetection:
    """Testes para a função has_attack_input"""

    def test_attack_in_json(self):
        """Testa detecção de ataques em JSON"""
        attack_json = {
            "nome": "Usuário normal",
            "comentario": "<script>alert('XSS')</script>",
            "info": {
                "website": "https://example.com',DROP TABLE users;--"
            }
        }
        assert has_attack_input(attack_json) is True

    def test_attack_in_nested_json(self):
        """Testa detecção de ataques em JSON aninhado"""
        attack_json = {
            "usuario": {
                "nome": "Usuário normal",
                "perfil": {
                    "descricao": "SELECT * FROM users WHERE id = 1"
                }
            },
            "itens": [
                {"nome": "Item 1", "descricao": "Normal"},
                {"nome": "Item 2", "descricao": "`rm -rf /`"}
            ]
        }
        assert has_attack_input(attack_json) is True

    def test_clean_json(self):
        """Testa JSON sem ataques"""
        clean_json = {
            "nome": "Usuário normal",
            "email": "usuario@exemplo.com",
            "idade": 30,
            "items": [
                {"id": 1, "nome": "Item 1"},
                {"id": 2, "nome": "Item 2"}
            ],
            "endereco": {
                "rua": "Avenida Brasil",
                "numero": 123,
                "cidade": "São Paulo"
            }
        }
        assert has_attack_input(clean_json) is False

    def test_invalid_inputs(self):
        """Testa entradas inválidas"""
        assert has_attack_input(None) is False
        assert has_attack_input("string") is False
        assert has_attack_input(123) is False


class TestUrlParamsValidation:
    """Testes para a função validate_url_params"""

    def test_valid_params(self):
        """Testa parâmetros válidos"""
        allowed = ["page", "size", "sort", "filter"]
        
        valid_params = {
            "page": "1",
            "size": "10",
            "sort": "name"
        }
        assert validate_url_params(valid_params, allowed) is True

    def test_invalid_params(self):
        """Testa parâmetros inválidos"""
        allowed = ["page", "size", "sort", "filter"]
        
        invalid_params = {
            "page": "1",
            "size": "10",
            "unknown": "value",
            "hackerman": "1' OR '1'='1"
        }
        assert validate_url_params(invalid_params, allowed) is False

    def test_empty_params(self):
        """Testa parâmetros vazios"""
        allowed = ["page", "size", "sort", "filter"]
        assert validate_url_params({}, allowed) is True 