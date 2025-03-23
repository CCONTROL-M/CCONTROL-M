"""Testes para o serviço de auditoria."""
import uuid
import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4
from typing import Dict, Any

# Mock para o AuditoriaService evitando conexão real
@pytest.fixture
def auditoria_service():
    """Cria um mock do serviço de auditoria para testes."""
    with patch('app.services.auditoria_service.LogSistemaRepository') as mock_repo_class:
        # Configurar o mock do repositório
        mock_repo = MagicMock()
        mock_repo.criar_log = MagicMock(return_value=None)
        mock_repo.get_multi = MagicMock(return_value=([], 0))
        mock_repo_class.return_value = mock_repo
        
        # Importar AuditoriaService após mock para evitar inicialização real
        from app.services.auditoria_service import AuditoriaService
        
        # Criar instância com dependência já mockada
        service = AuditoriaService()
        
        # Guardar referência ao mock repo para verificações
        service._mock_repo = mock_repo
        
        yield service


def test_mascarar_dados_sensiveis(auditoria_service):
    """Testa o mascaramento de dados sensíveis."""
    # Importar diretamente aqui para evitar importação no escopo global
    from app.services.auditoria_service import AuditoriaService
    
    # Dados de teste
    dados = {
        "usuario": "teste",
        "senha": "123456",
        "cpf": "123.456.789-00",
        "cartao": "4111111111111111",
        "detalhes": {
            "token": "abc123",
            "info": "pública",
            "nested": {
                "secret": "xyz789",
                "public": "ok"
            }
        },
        "lista": [
            {"senha": "123", "nome": "teste"},
            {"token": "456", "email": "teste@teste.com"}
        ]
    }
    
    # Mascarar dados
    resultado = auditoria_service._mascarar_dados_sensiveis(dados)
    
    # Verificar que dados sensíveis foram mascarados
    assert resultado["senha"] == "******"
    assert resultado["cpf"] == "***************"
    assert resultado["cartao"] == "****************"
    assert resultado["detalhes"]["token"] == "******"
    assert resultado["detalhes"]["info"] == "pública"
    assert resultado["detalhes"]["nested"]["secret"] == "******"
    assert resultado["detalhes"]["nested"]["public"] == "ok"
    assert resultado["lista"][0]["senha"] == "***"
    assert resultado["lista"][0]["nome"] == "teste"
    assert resultado["lista"][1]["token"] == "***"
    assert resultado["lista"][1]["email"] == "teste@teste.com"


@pytest.mark.asyncio
async def test_registrar_acao(auditoria_service):
    """Testar registro de ação de auditoria."""
    # Arrange
    usuario_id = uuid4()
    empresa_id = uuid4()
    acao = "TESTE_ACAO"
    detalhes = {"campo1": "valor1", "campo2": 123}
    
    # Act
    with patch('app.services.auditoria_service.get_request_id', return_value="test-123"):
        await auditoria_service.registrar_acao(
            usuario_id=usuario_id,
            acao=acao,
            detalhes=detalhes,
            empresa_id=empresa_id
        )
    
    # Assert
    auditoria_service._mock_repo.criar_log.assert_called_once()
    call_args = auditoria_service._mock_repo.criar_log.call_args[1]
    assert call_args["acao"] == acao
    assert call_args["id_usuario"] == usuario_id
    assert call_args["id_empresa"] == empresa_id
    assert "dados" in call_args
    assert call_args["dados"]["detalhes"] == detalhes


@pytest.mark.asyncio
async def test_registrar_acao_sem_detalhes(auditoria_service):
    """Testa o registro de uma ação sem detalhes adicionais."""
    # Mock do request_id
    request_id = "test-456"
    
    # Dados de teste
    usuario_id = uuid4()
    acao = "TESTE_SIMPLES"
    
    # Registrar ação
    with patch('app.services.auditoria_service.get_request_id', return_value=request_id):
        await auditoria_service.registrar_acao(
            usuario_id=usuario_id,
            acao=acao
        )
    
    # Verificar chamada ao repositório
    auditoria_service._mock_repo.criar_log.assert_called_once()
    call_args = auditoria_service._mock_repo.criar_log.call_args[1]
    
    # Verificar argumentos da chamada
    assert call_args["acao"] == acao
    assert call_args["descricao"] == f"[{request_id}] {acao}"
    assert call_args["id_usuario"] == usuario_id
    assert call_args["id_empresa"] is None
    
    # Verificar dados básicos
    dados = call_args["dados"]
    assert dados["request_id"] == request_id
    assert "timestamp" in dados
    assert dados["detalhes"] is None


@pytest.mark.asyncio
async def test_registrar_acao_com_request_id(auditoria_service):
    """Testa o registro de uma ação com request_id."""
    # Mock do request_id
    request_id = "test-request-id-456"
    
    # Dados de teste
    usuario_id = uuid4()
    acao = "TESTE_COM_REQUEST_ID"
    
    # Registrar ação
    with patch('app.services.auditoria_service.get_request_id', return_value=request_id):
        await auditoria_service.registrar_acao(
            usuario_id=usuario_id,
            acao=acao
        )
    
    # Verificar chamada ao repositório
    auditoria_service._mock_repo.criar_log.assert_called_once()
    call_args = auditoria_service._mock_repo.criar_log.call_args[1]
    
    # Verificar argumentos da chamada
    assert call_args["acao"] == acao
    assert f"[{request_id}]" in call_args["descricao"]
    assert call_args["id_usuario"] == usuario_id
    
    # Verificar dados básicos
    dados = call_args["dados"]
    assert dados["request_id"] == request_id
    assert "timestamp" in dados


@pytest.mark.asyncio
async def test_registrar_acao_com_request_id_fornecido(auditoria_service):
    """Testa o registro de uma ação com request_id fornecido externamente."""
    # Dados de teste
    usuario_id = uuid4()
    acao = "TESTE_REQUEST_ID_FORNECIDO"
    request_id = "custom-request-id-123"
    
    # Registrar ação com request_id fornecido
    await auditoria_service.registrar_acao(
        usuario_id=usuario_id,
        acao=acao,
        request_id=request_id
    )
    
    # Verificar chamada ao repositório
    auditoria_service._mock_repo.criar_log.assert_called_once()
    call_args = auditoria_service._mock_repo.criar_log.call_args[1]
    
    # Verificar que o request_id fornecido foi usado
    assert f"[{request_id}]" in call_args["descricao"]
    assert call_args["dados"]["request_id"] == request_id


@pytest.mark.asyncio
async def test_registrar_acao_com_erro(auditoria_service):
    """Testa o comportamento quando ocorre um erro no registro."""
    # Simular erro no repositório
    auditoria_service._mock_repo.criar_log.side_effect = Exception("Erro de teste")
    
    # Dados de teste
    usuario_id = uuid4()
    acao = "TESTE_ERRO"
    
    # Registrar ação (não deve lançar exceção)
    await auditoria_service.registrar_acao(
        usuario_id=usuario_id,
        acao=acao
    )
    
    # Verificar que o repositório foi chamado
    auditoria_service._mock_repo.criar_log.assert_called_once()


@pytest.mark.asyncio
async def test_registrar_acao_com_dados_sensiveis(auditoria_service):
    """Testa o mascaramento automático de dados sensíveis no registro."""
    # Dados de teste
    usuario_id = uuid4()
    acao = "TESTE_DADOS_SENSIVEIS"
    detalhes = {
        "usuario": "joao",
        "senha": "secreta123",
        "operacao": "pagamento",
        "dados_cartao": {
            "numero": "4111222233334444",
            "cvv": "123"
        }
    }
    
    # Registrar ação
    await auditoria_service.registrar_acao(
        usuario_id=usuario_id,
        acao=acao,
        detalhes=detalhes
    )
    
    # Verificar chamada ao repositório
    auditoria_service._mock_repo.criar_log.assert_called_once()
    call_args = auditoria_service._mock_repo.criar_log.call_args[1]
    
    # Verificar que os dados sensíveis foram mascarados
    dados_mascarados = call_args["dados"]
    assert dados_mascarados["detalhes"]["senha"] != "secreta123"
    assert dados_mascarados["detalhes"]["dados_cartao"]["numero"] != "4111222233334444"
    assert dados_mascarados["detalhes"]["dados_cartao"]["cvv"] != "123" 