"""Testes unitários para o serviço de auditoria.

Estes testes validam o funcionamento do AuditoriaService sem depender 
de uma conexão real com o banco de dados (PostgreSQL ou Supabase).

Para mais informações sobre a estratégia de testes, consulte o README.md.
"""
import uuid
import json
import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, AsyncMock
from uuid import uuid4
from typing import Dict, Any, List, Tuple

# Marcar todos os testes neste arquivo como unitários (sem banco de dados)
pytestmark = pytest.mark.unit

# Configurar mock para o AsyncSession antes de importar outros módulos
class MockAsyncSession:
    """Mock da sessão assíncrona do SQLAlchemy."""
    
    async def __aenter__(self):
        """Simula a entrada no contexto assíncrono."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Simula a saída do contexto assíncrono."""
        pass

    async def commit(self):
        """Simula o commit da transação."""
        pass

    async def rollback(self):
        """Simula o rollback da transação."""
        pass

    async def execute(self, query):
        """Simula a execução de uma query."""
        mock_result = MagicMock()
        
        # Configure o mock para retornar resultados específicos baseados na query
        if hasattr(query, 'whereclause') and getattr(query, 'whereclause', None) is not None:
            # Simula busca por um log específico pelo ID
            mock_result.scalar_one_or_none.return_value = mock_log_sistema(id_log=uuid4())
        
        # Simula busca múltipla    
        mock_result.scalars.return_value.all.return_value = [
            mock_log_sistema(id_log=uuid4()),
            mock_log_sistema(id_log=uuid4())
        ]
        
        return mock_result

    async def refresh(self, obj):
        """Simula a atualização de um objeto após operação."""
        pass
    
    def add(self, obj):
        """Simula a adição de um objeto à sessão."""
        pass
    
    def delete(self, obj):
        """Simula a remoção de um objeto da sessão."""
        pass


def mock_log_sistema(id_log=None, id_usuario=None, acao="TESTE", dados=None):
    """Cria um mock de objeto LogSistema para testes."""
    log = MagicMock()
    log.id_log = id_log or uuid4()
    log.id_usuario = id_usuario or uuid4()
    log.acao = acao
    log.dados = dados or {}
    log.created_at = datetime.now()
    return log


# Mock para o módulo database inteiro
with patch('app.database.get_async_session') as mock_get_session:
    mock_get_session.return_value = MockAsyncSession()
    
    # Agora podemos importar com segurança
    from app.services.auditoria_service import AuditoriaService
    from app.models.log_sistema import LogSistema
    from app.schemas.log_sistema import LogSistema as LogSistemaSchema


class MockRepository:
    """Mock do repositório de logs do sistema."""
    
    async def criar_log(self, **kwargs):
        """Simula a criação de um log."""
        return mock_log_sistema(**kwargs)
    
    async def get_by_id(self, id_log):
        """Simula a busca de um log pelo ID."""
        return mock_log_sistema(id_log=id_log)
    
    async def get_multi(self, **kwargs):
        """Simula a busca por múltiplos logs."""
        logs = [mock_log_sistema() for _ in range(3)]
        return logs, len(logs)
    
    async def limpar_logs_antigos(self, dias, id_empresa=None):
        """Simula a limpeza de logs antigos."""
        return 5  # Número de logs removidos


@pytest.fixture
def auditoria_service():
    """Cria um serviço de auditoria com repositório mockado."""
    service = AuditoriaService()
    # Substituir o repositório por um mock
    service.repository = AsyncMock()
    service.repository.criar_log = AsyncMock(return_value=mock_log_sistema())
    service.repository.get_by_id = AsyncMock(return_value=mock_log_sistema())
    service.repository.get_multi = AsyncMock(return_value=([mock_log_sistema() for _ in range(3)], 3))
    service.repository.limpar_logs_antigos = AsyncMock(return_value=5)
    return service


def test_mascarar_dados_sensiveis(auditoria_service):
    """Testa o mascaramento de dados sensíveis em vários formatos."""
    # Dados de teste com diferentes níveis e tipos de dados sensíveis
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
    assert resultado["cpf"] == "**************"  # Corrigido para 14 asteriscos
    assert resultado["cartao"] == "****************"
    assert resultado["detalhes"]["token"] == "******"
    assert resultado["detalhes"]["info"] == "pública"
    assert resultado["detalhes"]["nested"]["secret"] == "******"
    assert resultado["detalhes"]["nested"]["public"] == "ok"
    assert resultado["lista"][0]["senha"] == "***"
    assert resultado["lista"][0]["nome"] == "teste"
    assert resultado["lista"][1]["token"] == "***"
    assert resultado["lista"][1]["email"] == "teste@teste.com"


def test_mascarar_dados_sensiveis_tipos_especiais(auditoria_service):
    """Testa o comportamento do mascaramento com tipos especiais de dados."""
    # Teste com tipos não padrão e valores vazios
    dados = {
        "senha": None,
        "valor_nulo": None,
        "lista_vazia": [],
        "dic_vazio": {},
        "lista_complexa": [
            {"senha": 123456, "nome": "teste"},  # número em vez de string
            None,  # item nulo na lista
            "string simples"  # string sem chave
        ],
        "numero": 12345,
        "booleano": True
    }
    
    resultado = auditoria_service._mascarar_dados_sensiveis(dados)
    
    # Verificações
    assert resultado["senha"] is None  # Valores nulos devem permanecer nulos
    assert resultado["valor_nulo"] is None
    assert resultado["lista_vazia"] == []
    assert resultado["dic_vazio"] == {}
    assert len(resultado["lista_complexa"]) == 3
    assert resultado["lista_complexa"][0]["senha"] == 123456  # Apenas strings são mascaradas
    assert resultado["lista_complexa"][1] is None
    assert resultado["lista_complexa"][2] == "string simples"
    assert resultado["numero"] == 12345
    assert resultado["booleano"] is True


@pytest.mark.asyncio
async def test_registrar_acao(auditoria_service):
    """Testa o registro de ação de auditoria com todos os parâmetros."""
    # Arrange
    usuario_id = uuid4()
    empresa_id = uuid4()
    acao = "TESTE_ACAO"
    detalhes = {"campo1": "valor1", "campo2": 123}
    request_id = "test-req-123"
    
    # Act
    with patch('app.services.auditoria_service.get_request_id', return_value=request_id):
        await auditoria_service.registrar_acao(
            usuario_id=usuario_id,
            acao=acao,
            detalhes=detalhes,
            empresa_id=empresa_id,
            request_id=request_id
        )
    
    # Assert
    auditoria_service.repository.criar_log.assert_called_once()
    call_args = auditoria_service.repository.criar_log.call_args[1]
    assert call_args["acao"] == acao
    assert call_args["id_usuario"] == usuario_id
    assert call_args["id_empresa"] == empresa_id
    assert call_args["descricao"] == f"[{request_id}] {acao}"
    assert call_args["dados"]["request_id"] == request_id
    assert call_args["dados"]["detalhes"] == detalhes


@pytest.mark.asyncio
async def test_registrar_acao_parametros_minimos(auditoria_service):
    """Testa o registro de ação com apenas os parâmetros obrigatórios."""
    # Arrange
    usuario_id = uuid4()
    acao = "TESTE_MINIMO"
    
    # Act - apenas com parâmetros obrigatórios
    with patch('app.services.auditoria_service.get_request_id', return_value="auto-req-id"):
        await auditoria_service.registrar_acao(
            usuario_id=usuario_id,
            acao=acao
        )
    
    # Assert
    auditoria_service.repository.criar_log.assert_called_once()
    call_args = auditoria_service.repository.criar_log.call_args[1]
    assert call_args["acao"] == acao
    assert call_args["id_usuario"] == usuario_id
    assert call_args["id_empresa"] is None  # Deve ser None quando não fornecido
    assert call_args["dados"]["detalhes"] is None


@pytest.mark.asyncio
async def test_registrar_acao_com_erro(auditoria_service):
    """Testa o comportamento quando ocorre um erro no registro."""
    # Simular erro no repositório
    auditoria_service.repository.criar_log.side_effect = Exception("Erro de teste")
    
    # Arrange
    usuario_id = uuid4()
    acao = "TESTE_ERRO"
    
    # Act & Assert - não deve propagar o erro
    try:
        await auditoria_service.registrar_acao(usuario_id=usuario_id, acao=acao)
        # Se não lançar exceção, o teste passa
    except Exception:
        pytest.fail("O método registrar_acao não deveria propagar exceções")
    
    # Verificar que o log foi tentado mesmo com erro
    auditoria_service.repository.criar_log.assert_called_once()


@pytest.mark.asyncio
async def test_registrar_acao_com_dados_sensiveis(auditoria_service):
    """Testa mascaramento automático de dados sensíveis ao registrar ação."""
    # Arrange
    usuario_id = uuid4()
    acao = "TESTE_DADOS_SENSIVEIS"
    detalhes = {
        "usuario": "teste",
        "senha": "secreta",
        "token": "abc123",
        "info_publica": "OK"
    }
    
    # Act
    with patch('app.services.auditoria_service.get_request_id', return_value="test-id"):
        await auditoria_service.registrar_acao(
            usuario_id=usuario_id,
            acao=acao,
            detalhes=detalhes
        )
    
    # Assert - verificar que dados sensíveis foram mascarados
    call_args = auditoria_service.repository.criar_log.call_args[1]
    dados_registrados = call_args["dados"]["detalhes"]
    
    assert dados_registrados["senha"] == "******"
    assert dados_registrados["token"] == "******"
    assert dados_registrados["usuario"] == "teste"
    assert dados_registrados["info_publica"] == "OK"


@pytest.mark.asyncio
async def test_listar_acoes(auditoria_service):
    """Testa a listagem de ações com filtros."""
    # Arrange
    filtros = {
        "id_usuario": uuid4(),
        "data_inicio": datetime.now() - timedelta(days=7),
        "data_fim": datetime.now(),
        "acao": "LOGIN"
    }
    
    # Mock já está configurado para retornar 3 logs
    
    # Act
    logs, total = await auditoria_service.listar_acoes(**filtros)
    
    # Assert
    assert len(logs) == 3
    assert total == 3
    # Verificar que os parâmetros foram repassados ao repository
    auditoria_service.repository.get_multi.assert_called_once()
    for key, value in filtros.items():
        assert auditoria_service.repository.get_multi.call_args[1][key] == value


@pytest.mark.asyncio
async def test_obter_acao(auditoria_service):
    """Testa a obtenção de uma ação específica pelo ID."""
    # Arrange
    id_log = uuid4()
    
    # Act
    log = await auditoria_service.obter_acao(id_log)
    
    # Assert
    assert log is not None
    auditoria_service.repository.get_by_id.assert_called_once_with(id_log)


@pytest.mark.asyncio
async def test_obter_acao_inexistente(auditoria_service):
    """Testa o comportamento quando um log não existe."""
    # Arrange - configurar mock para retornar None
    auditoria_service.repository.get_by_id.return_value = None
    id_log = uuid4()
    
    # Act
    log = await auditoria_service.obter_acao(id_log)
    
    # Assert
    assert log is None
    auditoria_service.repository.get_by_id.assert_called_once_with(id_log)


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 