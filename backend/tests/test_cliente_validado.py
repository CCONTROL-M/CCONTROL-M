"""
Testes para os modelos de validação de Cliente.

Verifica que todas as validações são aplicadas corretamente nos esquemas Pydantic.
"""
import pytest
import json
from datetime import date, datetime
from decimal import Decimal
from pydantic import ValidationError

from app.schemas.cliente_validado import (
    SituacaoCliente, TipoCliente, Endereco, Contato,
    ClienteCreate, ClienteUpdate, ClienteResponse
)


class TestEndereco:
    """Testes para o modelo de endereço."""

    def test_endereco_valido(self):
        """Teste com dados válidos de endereço."""
        endereco_data = {
            "logradouro": "Rua de Teste",
            "numero": "123",
            "bairro": "Centro",
            "cidade": "São Paulo",
            "uf": "SP",
            "cep": "01234567",
            "principal": True
        }
        
        endereco = Endereco(**endereco_data)
        assert endereco.logradouro == "Rua de Teste"
        assert endereco.cep == "01234-567"  # Testando a formatação
        assert endereco.uf == "SP"
        assert endereco.principal is True

    def test_cep_invalido(self):
        """Teste com CEP inválido."""
        endereco_data = {
            "logradouro": "Rua de Teste",
            "numero": "123",
            "bairro": "Centro",
            "cidade": "São Paulo",
            "uf": "SP",
            "cep": "123",  # CEP inválido
            "principal": True
        }
        
        with pytest.raises(ValidationError) as exc_info:
            Endereco(**endereco_data)
        
        assert "CEP deve conter 8 dígitos" in str(exc_info.value)

    def test_uf_invalida(self):
        """Teste com UF inválida."""
        endereco_data = {
            "logradouro": "Rua de Teste",
            "numero": "123",
            "bairro": "Centro",
            "cidade": "São Paulo",
            "uf": "XX",  # UF inválida
            "cep": "01234567",
            "principal": True
        }
        
        with pytest.raises(ValidationError) as exc_info:
            Endereco(**endereco_data)
        
        assert "UF inválida" in str(exc_info.value)

    def test_sanitizacao_campos(self):
        """Testa sanitização de campos de texto."""
        endereco_data = {
            "logradouro": "Rua <script>alert('teste')</script>",
            "numero": "123",
            "bairro": "Centro",
            "cidade": "São Paulo",
            "uf": "SP",
            "cep": "01234567",
            "principal": True
        }
        
        with pytest.raises(ValidationError) as exc_info:
            Endereco(**endereco_data)
        
        assert "Campo contém padrões de ataque" in str(exc_info.value)


class TestContato:
    """Testes para o modelo de contato."""

    def test_contato_valido(self):
        """Teste com dados válidos de contato."""
        contato_data = {
            "tipo": "celular",
            "valor": "(11) 98765-4321",
            "principal": True
        }
        
        contato = Contato(**contato_data)
        assert contato.tipo == "celular"
        assert contato.valor == "(11) 98765-4321"
        assert contato.principal is True

    def test_tipo_invalido(self):
        """Teste com tipo de contato inválido."""
        contato_data = {
            "tipo": "invalidtype",
            "valor": "(11) 98765-4321",
            "principal": True
        }
        
        with pytest.raises(ValidationError) as exc_info:
            Contato(**contato_data)
        
        assert "Tipo de contato inválido" in str(exc_info.value)

    def test_celular_invalido(self):
        """Teste com número de celular inválido."""
        contato_data = {
            "tipo": "celular",
            "valor": "123",  # Celular inválido
            "principal": True
        }
        
        with pytest.raises(ValidationError) as exc_info:
            Contato(**contato_data)
        
        assert "Número de telefone inválido" in str(exc_info.value)

    def test_email_invalido(self):
        """Teste com e-mail inválido."""
        contato_data = {
            "tipo": "email",
            "valor": "email_invalido",  # Email inválido
            "principal": True
        }
        
        with pytest.raises(ValidationError) as exc_info:
            Contato(**contato_data)
        
        assert "Endereço de e-mail inválido" in str(exc_info.value)


class TestClienteCreate:
    """Testes para o modelo de criação de cliente."""

    def test_cliente_pessoa_fisica_valido(self):
        """Teste com dados válidos de cliente pessoa física."""
        cliente_data = {
            "tipo": "pessoa_fisica",
            "nome": "João da Silva",
            "documento": "123.456.789-00",
            "data_nascimento": "1990-01-01",
            "limite_credito": 1000.0,
            "situacao": "ativo",
            "enderecos": [
                {
                    "logradouro": "Rua de Teste",
                    "numero": "123",
                    "bairro": "Centro",
                    "cidade": "São Paulo",
                    "uf": "SP",
                    "cep": "01234567",
                    "principal": True
                }
            ],
            "contatos": [
                {
                    "tipo": "celular",
                    "valor": "(11) 98765-4321",
                    "principal": True
                },
                {
                    "tipo": "email",
                    "valor": "joao@exemplo.com",
                    "principal": False
                }
            ]
        }
        
        cliente = ClienteCreate(**cliente_data)
        assert cliente.tipo == TipoCliente.PESSOA_FISICA
        assert cliente.nome == "João da Silva"
        assert cliente.documento == "123.456.789-00"
        assert cliente.data_nascimento == date(1990, 1, 1)
        assert cliente.limite_credito == Decimal("1000.0")
        assert cliente.situacao == SituacaoCliente.ATIVO
        assert len(cliente.enderecos) == 1
        assert len(cliente.contatos) == 2
        assert cliente.enderecos[0].principal is True
        assert cliente.contatos[0].principal is True

    def test_cliente_pessoa_juridica_valido(self):
        """Teste com dados válidos de cliente pessoa jurídica."""
        cliente_data = {
            "tipo": "pessoa_juridica",
            "nome": "Empresa XYZ Ltda",
            "nome_fantasia": "XYZ",
            "documento": "12.345.678/0001-90",
            "inscricao_estadual": "123456789",
            "limite_credito": 10000.0,
            "situacao": "ativo",
            "enderecos": [
                {
                    "logradouro": "Avenida Comercial",
                    "numero": "1000",
                    "bairro": "Centro",
                    "cidade": "São Paulo",
                    "uf": "SP",
                    "cep": "01234567",
                    "principal": True
                }
            ],
            "contatos": [
                {
                    "tipo": "telefone",
                    "valor": "(11) 3333-4444",
                    "principal": True
                },
                {
                    "tipo": "email",
                    "valor": "contato@xyz.com.br",
                    "principal": False
                }
            ]
        }
        
        cliente = ClienteCreate(**cliente_data)
        assert cliente.tipo == TipoCliente.PESSOA_JURIDICA
        assert cliente.nome == "Empresa XYZ Ltda"
        assert cliente.nome_fantasia == "XYZ"
        assert cliente.documento == "12.345.678/0001-90"
        assert cliente.inscricao_estadual == "123456789"
        assert cliente.situacao == SituacaoCliente.ATIVO
        assert len(cliente.enderecos) == 1
        assert len(cliente.contatos) == 2

    def test_cpf_para_pessoa_juridica(self):
        """Teste com CPF para pessoa jurídica (deve falhar)."""
        cliente_data = {
            "tipo": "pessoa_juridica",
            "nome": "Empresa XYZ Ltda",
            "documento": "123.456.789-00",  # CPF para pessoa jurídica
            "enderecos": [
                {
                    "logradouro": "Avenida Comercial",
                    "numero": "1000",
                    "bairro": "Centro",
                    "cidade": "São Paulo",
                    "uf": "SP",
                    "cep": "01234567",
                    "principal": True
                }
            ],
            "contatos": [
                {
                    "tipo": "telefone",
                    "valor": "(11) 3333-4444",
                    "principal": True
                }
            ]
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ClienteCreate(**cliente_data)
        
        assert "Para Pessoa Jurídica, o documento deve ser um CNPJ válido" in str(exc_info.value)

    def test_cnpj_para_pessoa_fisica(self):
        """Teste com CNPJ para pessoa física (deve falhar)."""
        cliente_data = {
            "tipo": "pessoa_fisica",
            "nome": "João da Silva",
            "documento": "12.345.678/0001-90",  # CNPJ para pessoa física
            "enderecos": [
                {
                    "logradouro": "Rua de Teste",
                    "numero": "123",
                    "bairro": "Centro",
                    "cidade": "São Paulo",
                    "uf": "SP",
                    "cep": "01234567",
                    "principal": True
                }
            ],
            "contatos": [
                {
                    "tipo": "celular",
                    "valor": "(11) 98765-4321",
                    "principal": True
                }
            ]
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ClienteCreate(**cliente_data)
        
        assert "Para Pessoa Física, o documento deve ser um CPF válido" in str(exc_info.value)

    def test_definir_contato_principal_automatico(self):
        """Testa definição automática de contato principal."""
        cliente_data = {
            "tipo": "pessoa_fisica",
            "nome": "João da Silva",
            "documento": "123.456.789-00",
            "enderecos": [
                {
                    "logradouro": "Rua de Teste",
                    "numero": "123",
                    "bairro": "Centro",
                    "cidade": "São Paulo",
                    "uf": "SP",
                    "cep": "01234567",
                    "principal": True
                }
            ],
            "contatos": [
                {
                    "tipo": "celular",
                    "valor": "(11) 98765-4321",
                    "principal": False  # Nenhum contato marcado como principal
                },
                {
                    "tipo": "email",
                    "valor": "joao@exemplo.com",
                    "principal": False
                }
            ]
        }
        
        cliente = ClienteCreate(**cliente_data)
        assert cliente.contatos[0].principal is True  # Primeiro contato deveria ser marcado como principal


class TestClienteUpdate:
    """Testes para o modelo de atualização de cliente."""

    def test_atualizacao_parcial(self):
        """Teste de atualização parcial de cliente."""
        update_data = {
            "nome": "João da Silva Atualizado",
            "situacao": "inadimplente"
        }
        
        update = ClienteUpdate(**update_data)
        assert update.nome == "João da Silva Atualizado"
        assert update.situacao == SituacaoCliente.INADIMPLENTE
        assert update.nome_fantasia is None
        assert update.inscricao_estadual is None
        assert update.data_nascimento is None
        assert update.limite_credito is None
        assert update.observacoes is None

    def test_sanitizacao_nome(self):
        """Testa sanitização do campo nome."""
        update_data = {
            "nome": "Nome<script>alert('teste')</script>"
        }
        
        update = ClienteUpdate(**update_data)
        assert update.nome == "Nomescriptalerttestescript"  # Conteúdo sanitizado


class TestClienteResponse:
    """Testes para o modelo de resposta de cliente."""

    def test_response_completo(self):
        """Teste com dados completos de resposta."""
        response_data = {
            "id": 1,
            "tipo": "pessoa_fisica",
            "nome": "João da Silva",
            "nome_fantasia": None,
            "documento": "123.456.789-00",
            "inscricao_estadual": None,
            "data_nascimento": "1990-01-01",
            "limite_credito": 1000.0,
            "situacao": "ativo",
            "observacoes": None,
            "enderecos": [
                {
                    "logradouro": "Rua de Teste",
                    "numero": "123",
                    "complemento": None,
                    "bairro": "Centro",
                    "cidade": "São Paulo",
                    "uf": "SP",
                    "cep": "01234-567",
                    "principal": True
                }
            ],
            "contatos": [
                {
                    "tipo": "celular",
                    "valor": "(11) 98765-4321",
                    "principal": True,
                    "observacao": None
                }
            ],
            "created_at": "2023-01-01",
            "updated_at": "2023-01-02"
        }
        
        response = ClienteResponse(**response_data)
        assert response.id == 1
        assert response.tipo == TipoCliente.PESSOA_FISICA
        assert response.nome == "João da Silva"
        assert response.documento == "123.456.789-00"
        assert response.data_nascimento == date(1990, 1, 1)
        assert response.limite_credito == Decimal("1000.0")
        assert response.situacao == SituacaoCliente.ATIVO
        assert len(response.enderecos) == 1
        assert len(response.contatos) == 1
        assert response.created_at == date(2023, 1, 1)
        assert response.updated_at == date(2023, 1, 2) 