"""
Teste básico para verificar se o pytest está funcionando.
"""
import pytest
import sys
import traceback


def test_true_is_true():
    """Teste simples para verificar se True é True."""
    assert True is True


def test_sum():
    """Teste simples para verificar se a adição funciona."""
    assert 1 + 1 == 2


@pytest.mark.asyncio
async def test_async_function():
    """Teste simples para verificar se funções assíncronas funcionam."""
    assert await async_function()


async def async_function():
    """Função assíncrona simples para teste."""
    return True


def test_app_imports():
    """Teste de importação do aplicativo principal."""
    try:
        # Importar app.main
        from app.main import app
        assert app is not None, "Aplicação não foi inicializada corretamente"
        
        # Verificar os routers registrados
        from app.routers import api_router
        assert len(api_router.routes) > 0, "Nenhum router foi registrado"
        
        return True
    except Exception as e:
        pytest.fail(f"Erro durante importação do app: {str(e)}")
        return False


def test_basic_imports():
    """Teste de importação de módulos básicos da aplicação."""
    try:
        # Importar módulos básicos
        from app.database import get_async_session, db_async_session
        from app.dependencies import get_current_user
        
        assert get_async_session is not None, "Sessão async não foi importada corretamente"
        assert get_current_user is not None, "Dependência get_current_user não foi importada corretamente"
        
        return True
    except Exception as e:
        pytest.fail(f"Erro durante importações básicas: {str(e)}")
        return False


def test_router_imports():
    """Teste de importação dos routers da aplicação."""
    try:
        # Importar routers principais
        from app.routers.contas_receber import router as contas_receber_router
        from app.routers.contas_pagar import router as contas_pagar_router
        from app.routers.clientes import router as clientes_router
        
        assert contas_receber_router is not None, "Router de contas a receber não foi importado corretamente"
        assert contas_pagar_router is not None, "Router de contas a pagar não foi importado corretamente"
        assert clientes_router is not None, "Router de clientes não foi importado corretamente"
        
        return True
    except Exception as e:
        pytest.fail(f"Erro durante importação de routers: {str(e)}")
        return False 