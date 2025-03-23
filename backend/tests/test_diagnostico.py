"""Arquivo de diagnóstico para testes."""
import pytest
from decimal import Decimal


@pytest.mark.active
@pytest.mark.unit
def test_simples_sync():
    """Teste simples síncrono para diagnóstico."""
    assert 1 + 1 == 2
    assert Decimal('1.1') + Decimal('2.2') == Decimal('3.3')
    print("Teste síncrono executado com sucesso!")


@pytest.mark.active
@pytest.mark.unit
@pytest.mark.asyncio
async def test_simples_async():
    """Teste simples assíncrono para diagnóstico."""
    assert 1 + 1 == 2
    assert await coro_simples()
    print("Teste assíncrono executado com sucesso!")


async def coro_simples():
    """Corrotina simples para teste assíncrono."""
    return True 