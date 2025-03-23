"""Testes para o serviço de logs do sistema."""
import pytest
from uuid import uuid4
from typing import Callable, AsyncGenerator
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.log_sistema import LogSistema
from app.schemas.log_sistema import LogSistemaCreate, TipoLog
from app.services.log_sistema_service import LogSistemaService

# Fixtures - definição de dados para testes
@pytest.fixture
async def log(session: AsyncSession) -> LogSistema:
    """Cria um log do sistema para testes."""
    # Criar um log diretamente no banco
    log = LogSistema(
        id=uuid4(),
        empresa_id=uuid4(),
        usuario_id=uuid4(),
        tipo=TipoLog.info,
        mensagem="Log de teste",
        dados={"contexto": "Teste unitário"},
        ip="127.0.0.1",
        user_agent="Test Browser",
        created_at=datetime.now()
    )
    
    session.add(log)
    await session.commit()
    await session.refresh(log)
    
    return log

@pytest.fixture
async def log_factory(session: AsyncSession) -> Callable[..., AsyncGenerator[LogSistema, None]]:
    """Factory para criar logs com parâmetros customizados."""
    async def _create_log(**kwargs) -> LogSistema:
        default_empresa_id = uuid4()  # Geramos um UUID para empresa
        default_usuario_id = uuid4()  # Geramos um UUID para usuário
        
        # Valores padrão para testes
        defaults = {
            "id": uuid4(),
            "empresa_id": default_empresa_id,
            "usuario_id": default_usuario_id,
            "tipo": TipoLog.info,
            "mensagem": f"Log {uuid4().hex[:8]}",
            "dados": {"contexto": "Teste unitário"},
            "ip": "127.0.0.1",
            "user_agent": "Test Browser",
            "created_at": datetime.now()
        }
        
        # Sobrescrever valores padrão com valores fornecidos
        defaults.update(kwargs)
        
        log = LogSistema(**defaults)
        session.add(log)
        await session.commit()
        await session.refresh(log)
        
        return log
    
    return _create_log

@pytest.fixture
async def logs_lista(session: AsyncSession) -> list[LogSistema]:
    """Cria uma lista de logs para testes."""
    
    # IDs comuns para todos os logs
    empresa_id = uuid4()
    usuario_id = uuid4()
    
    # Criar diversos tipos de logs
    logs = []
    
    # Log de info
    log_info = LogSistema(
        id=uuid4(),
        empresa_id=empresa_id,
        usuario_id=usuario_id,
        tipo=TipoLog.info,
        mensagem="Log de informação",
        dados={"ação": "login"},
        ip="127.0.0.1",
        user_agent="Test Browser",
        created_at=datetime.now()
    )
    session.add(log_info)
    logs.append(log_info)
    
    # Log de warning
    log_warning = LogSistema(
        id=uuid4(),
        empresa_id=empresa_id,
        usuario_id=usuario_id,
        tipo=TipoLog.warning,
        mensagem="Log de aviso",
        dados={"ação": "validação"},
        ip="127.0.0.1",
        user_agent="Test Browser",
        created_at=datetime.now()
    )
    session.add(log_warning)
    logs.append(log_warning)
    
    # Log de erro
    log_error = LogSistema(
        id=uuid4(),
        empresa_id=empresa_id,
        usuario_id=usuario_id,
        tipo=TipoLog.error,
        mensagem="Log de erro",
        dados={"ação": "processamento", "erro": "Falha na operação"},
        ip="127.0.0.1",
        user_agent="Test Browser",
        created_at=datetime.now()
    )
    session.add(log_error)
    logs.append(log_error)
    
    # Log de segurança
    log_security = LogSistema(
        id=uuid4(),
        empresa_id=empresa_id,
        usuario_id=usuario_id,
        tipo=TipoLog.security,
        mensagem="Log de segurança",
        dados={"ação": "acesso negado"},
        ip="192.168.1.1",
        user_agent="Test Browser",
        created_at=datetime.now()
    )
    session.add(log_security)
    logs.append(log_security)
    
    # Log de auditoria
    log_audit = LogSistema(
        id=uuid4(),
        empresa_id=empresa_id,
        usuario_id=usuario_id,
        tipo=TipoLog.audit,
        mensagem="Log de auditoria",
        dados={"ação": "edição", "entidade": "cliente", "id_entidade": str(uuid4())},
        ip="127.0.0.1",
        user_agent="Test Browser",
        created_at=datetime.now()
    )
    session.add(log_audit)
    logs.append(log_audit)
    
    await session.commit()
    for log in logs:
        await session.refresh(log)
    
    return logs


# Testes do serviço de logs
@pytest.mark.asyncio
async def test_criar_log(session: AsyncSession):
    """Teste de criação de log do sistema."""
    # Arrange
    service = LogSistemaService(session)
    empresa_id = uuid4()
    usuario_id = uuid4()
    
    dados_log = {
        "empresa_id": empresa_id,
        "usuario_id": usuario_id,
        "tipo": TipoLog.info,
        "mensagem": "Novo log para teste",
        "dados": {"ação": "teste unitário"},
        "ip": "127.0.0.1",
        "user_agent": "Test Browser"
    }
    
    log_create = LogSistemaCreate(**dados_log)
    
    # Act
    log = await service.create(log_create)
    
    # Assert
    assert log is not None
    assert log.id is not None
    assert log.empresa_id == empresa_id
    assert log.usuario_id == usuario_id
    assert log.tipo == TipoLog.info
    assert log.mensagem == "Novo log para teste"
    assert log.dados == {"ação": "teste unitário"}
    assert log.ip == "127.0.0.1"
    assert log.user_agent == "Test Browser"


@pytest.mark.asyncio
async def test_criar_log_erro(session: AsyncSession):
    """Teste de criação de log de erro."""
    # Arrange
    service = LogSistemaService(session)
    empresa_id = uuid4()
    usuario_id = uuid4()
    
    dados_log = {
        "empresa_id": empresa_id,
        "usuario_id": usuario_id,
        "tipo": TipoLog.error,
        "mensagem": "Erro durante operação",
        "dados": {"ação": "teste unitário", "erro": "Falha simulada"},
        "ip": "127.0.0.1",
        "user_agent": "Test Browser"
    }
    
    log_create = LogSistemaCreate(**dados_log)
    
    # Act
    log = await service.create(log_create)
    
    # Assert
    assert log is not None
    assert log.id is not None
    assert log.tipo == TipoLog.error
    assert log.mensagem == "Erro durante operação"
    assert log.dados["erro"] == "Falha simulada"


@pytest.mark.asyncio
async def test_buscar_log(session: AsyncSession, log: LogSistema):
    """Teste de busca de log pelo ID."""
    # Arrange
    service = LogSistemaService(session)
    
    # Act
    result = await service.get(log.id)
    
    # Assert
    assert result is not None
    assert result.id == log.id
    assert result.mensagem == log.mensagem
    assert result.tipo == log.tipo


@pytest.mark.asyncio
async def test_listar_logs(session: AsyncSession, logs_lista: list[LogSistema]):
    """Teste de listagem de logs."""
    # Arrange
    service = LogSistemaService(session)
    empresa_id = logs_lista[0].empresa_id
    
    # Act
    result, total = await service.list(
        empresa_id=empresa_id,
        skip=0,
        limit=10
    )
    
    # Assert
    assert len(result) == 5
    assert total == 5
    assert all(l.empresa_id == empresa_id for l in result)


@pytest.mark.asyncio
async def test_listar_logs_por_tipo(session: AsyncSession, logs_lista: list[LogSistema]):
    """Teste de listagem de logs por tipo."""
    # Arrange
    service = LogSistemaService(session)
    empresa_id = logs_lista[0].empresa_id
    
    # Act
    result, total = await service.list(
        empresa_id=empresa_id,
        tipo=TipoLog.error,
        skip=0,
        limit=10
    )
    
    # Assert
    assert len(result) == 1
    assert total == 1
    assert result[0].tipo == TipoLog.error


@pytest.mark.asyncio
async def test_listar_logs_por_usuario(session: AsyncSession, logs_lista: list[LogSistema]):
    """Teste de listagem de logs por usuário."""
    # Arrange
    service = LogSistemaService(session)
    empresa_id = logs_lista[0].empresa_id
    usuario_id = logs_lista[0].usuario_id
    
    # Act
    result, total = await service.list(
        empresa_id=empresa_id,
        usuario_id=usuario_id,
        skip=0,
        limit=10
    )
    
    # Assert
    assert len(result) == 5
    assert total == 5
    assert all(l.usuario_id == usuario_id for l in result)


@pytest.mark.asyncio
async def test_listar_logs_por_ip(session: AsyncSession, logs_lista: list[LogSistema]):
    """Teste de listagem de logs por IP."""
    # Arrange
    service = LogSistemaService(session)
    empresa_id = logs_lista[0].empresa_id
    
    # Act
    result, total = await service.list(
        empresa_id=empresa_id,
        ip="192.168.1.1",
        skip=0,
        limit=10
    )
    
    # Assert
    assert len(result) == 1
    assert total == 1
    assert result[0].ip == "192.168.1.1"


@pytest.mark.asyncio
async def test_buscar_logs_por_termo(session: AsyncSession, logs_lista: list[LogSistema]):
    """Teste de busca de logs por termo na mensagem."""
    # Arrange
    service = LogSistemaService(session)
    empresa_id = logs_lista[0].empresa_id
    
    # Act
    result, total = await service.search(
        empresa_id=empresa_id,
        termo="segurança",
        skip=0,
        limit=10
    )
    
    # Assert
    assert len(result) == 1
    assert total == 1
    assert "segurança" in result[0].mensagem.lower()


@pytest.mark.asyncio
async def test_registrar_log_info(session: AsyncSession):
    """Teste de método utilitário para registrar log de informação."""
    # Arrange
    service = LogSistemaService(session)
    empresa_id = uuid4()
    usuario_id = uuid4()
    
    # Act
    log = await service.registrar_info(
        empresa_id=empresa_id,
        usuario_id=usuario_id,
        mensagem="Log de informação via método utilitário",
        dados={"método": "registrar_info"},
        ip="127.0.0.1",
        user_agent="Test Browser"
    )
    
    # Assert
    assert log is not None
    assert log.id is not None
    assert log.tipo == TipoLog.info
    assert log.mensagem == "Log de informação via método utilitário"


@pytest.mark.asyncio
async def test_registrar_log_erro(session: AsyncSession):
    """Teste de método utilitário para registrar log de erro."""
    # Arrange
    service = LogSistemaService(session)
    empresa_id = uuid4()
    usuario_id = uuid4()
    
    # Act
    log = await service.registrar_erro(
        empresa_id=empresa_id,
        usuario_id=usuario_id,
        mensagem="Log de erro via método utilitário",
        dados={"método": "registrar_erro", "exceção": "ValueError"},
        ip="127.0.0.1",
        user_agent="Test Browser"
    )
    
    # Assert
    assert log is not None
    assert log.id is not None
    assert log.tipo == TipoLog.error
    assert log.mensagem == "Log de erro via método utilitário"
    assert log.dados["exceção"] == "ValueError"


@pytest.mark.asyncio
async def test_registrar_log_seguranca(session: AsyncSession):
    """Teste de método utilitário para registrar log de segurança."""
    # Arrange
    service = LogSistemaService(session)
    empresa_id = uuid4()
    usuario_id = uuid4()
    
    # Act
    log = await service.registrar_seguranca(
        empresa_id=empresa_id,
        usuario_id=usuario_id,
        mensagem="Tentativa de acesso não autorizado",
        dados={"recurso": "/api/v1/admin", "método": "GET"},
        ip="192.168.1.100",
        user_agent="Test Browser"
    )
    
    # Assert
    assert log is not None
    assert log.id is not None
    assert log.tipo == TipoLog.security
    assert log.mensagem == "Tentativa de acesso não autorizado"
    assert log.dados["recurso"] == "/api/v1/admin" 