"""Testes para o serviço de relatórios."""
import pytest
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.services.relatorio_service import RelatorioService
from app.services.auditoria_service import AuditoriaService

from .fixtures.venda import venda, vendas_lista
from .fixtures.conta_pagar import conta_pagar, contas_pagar_lista
from .fixtures.conta_receber import conta_receber, contas_receber_lista
from .fixtures.usuario import usuario


@pytest.mark.asyncio
async def test_gerar_relatorio_vendas_periodo(
    session: AsyncSession,
    vendas_lista: list[Venda]
):
    """Testa a geração de relatório de vendas por período."""
    service = RelatorioService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    data_inicial = date.today() - timedelta(days=30)
    data_final = date.today()
    
    relatorio = await service.gerar_relatorio_vendas(
        data_inicial=data_inicial,
        data_final=data_final
    )
    
    assert relatorio is not None
    assert "total_vendas" in relatorio
    assert "quantidade_vendas" in relatorio
    assert "ticket_medio" in relatorio
    assert isinstance(relatorio["total_vendas"], Decimal)
    assert isinstance(relatorio["quantidade_vendas"], int)
    assert isinstance(relatorio["ticket_medio"], Decimal)
    assert relatorio["quantidade_vendas"] >= len(vendas_lista)


@pytest.mark.asyncio
async def test_gerar_relatorio_contas_pagar_periodo(
    session: AsyncSession,
    contas_pagar_lista: list[ContaPagar]
):
    """Testa a geração de relatório de contas a pagar por período."""
    service = RelatorioService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    data_inicial = date.today()
    data_final = date.today() + timedelta(days=30)
    
    relatorio = await service.gerar_relatorio_contas_pagar(
        data_inicial=data_inicial,
        data_final=data_final
    )
    
    assert relatorio is not None
    assert "total_contas" in relatorio
    assert "quantidade_contas" in relatorio
    assert "total_pago" in relatorio
    assert "total_pendente" in relatorio
    assert isinstance(relatorio["total_contas"], Decimal)
    assert isinstance(relatorio["quantidade_contas"], int)
    assert isinstance(relatorio["total_pago"], Decimal)
    assert isinstance(relatorio["total_pendente"], Decimal)
    assert relatorio["quantidade_contas"] >= len(contas_pagar_lista)


@pytest.mark.asyncio
async def test_gerar_relatorio_contas_receber_periodo(
    session: AsyncSession,
    contas_receber_lista: list[ContaReceber]
):
    """Testa a geração de relatório de contas a receber por período."""
    service = RelatorioService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    data_inicial = date.today()
    data_final = date.today() + timedelta(days=30)
    
    relatorio = await service.gerar_relatorio_contas_receber(
        data_inicial=data_inicial,
        data_final=data_final
    )
    
    assert relatorio is not None
    assert "total_contas" in relatorio
    assert "quantidade_contas" in relatorio
    assert "total_recebido" in relatorio
    assert "total_pendente" in relatorio
    assert isinstance(relatorio["total_contas"], Decimal)
    assert isinstance(relatorio["quantidade_contas"], int)
    assert isinstance(relatorio["total_recebido"], Decimal)
    assert isinstance(relatorio["total_pendente"], Decimal)
    assert relatorio["quantidade_contas"] >= len(contas_receber_lista)


@pytest.mark.asyncio
async def test_gerar_relatorio_fluxo_caixa(
    session: AsyncSession,
    vendas_lista: list[Venda],
    contas_pagar_lista: list[ContaPagar],
    contas_receber_lista: list[ContaReceber]
):
    """Testa a geração de relatório de fluxo de caixa."""
    service = RelatorioService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    data_inicial = date.today()
    data_final = date.today() + timedelta(days=30)
    
    relatorio = await service.gerar_relatorio_fluxo_caixa(
        data_inicial=data_inicial,
        data_final=data_final
    )
    
    assert relatorio is not None
    assert "saldo_inicial" in relatorio
    assert "entradas" in relatorio
    assert "saidas" in relatorio
    assert "saldo_final" in relatorio
    assert isinstance(relatorio["saldo_inicial"], Decimal)
    assert isinstance(relatorio["entradas"], Decimal)
    assert isinstance(relatorio["saidas"], Decimal)
    assert isinstance(relatorio["saldo_final"], Decimal)
    assert relatorio["saldo_final"] == relatorio["saldo_inicial"] + relatorio["entradas"] - relatorio["saidas"]


@pytest.mark.asyncio
async def test_gerar_relatorio_produtos_mais_vendidos(
    session: AsyncSession,
    vendas_lista: list[Venda]
):
    """Testa a geração de relatório de produtos mais vendidos."""
    service = RelatorioService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    data_inicial = date.today() - timedelta(days=30)
    data_final = date.today()
    limite = 5
    
    relatorio = await service.gerar_relatorio_produtos_mais_vendidos(
        data_inicial=data_inicial,
        data_final=data_final,
        limite=limite
    )
    
    assert relatorio is not None
    assert isinstance(relatorio, list)
    assert len(relatorio) <= limite
    for item in relatorio:
        assert "id_produto" in item
        assert "nome" in item
        assert "quantidade_vendida" in item
        assert "valor_total" in item
        assert isinstance(item["quantidade_vendida"], int)
        assert isinstance(item["valor_total"], Decimal)


@pytest.mark.asyncio
async def test_gerar_relatorio_clientes_mais_compraram(
    session: AsyncSession,
    vendas_lista: list[Venda]
):
    """Testa a geração de relatório de clientes que mais compraram."""
    service = RelatorioService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    data_inicial = date.today() - timedelta(days=30)
    data_final = date.today()
    limite = 5
    
    relatorio = await service.gerar_relatorio_clientes_mais_compraram(
        data_inicial=data_inicial,
        data_final=data_final,
        limite=limite
    )
    
    assert relatorio is not None
    assert isinstance(relatorio, list)
    assert len(relatorio) <= limite
    for item in relatorio:
        assert "id_cliente" in item
        assert "nome" in item
        assert "quantidade_compras" in item
        assert "valor_total" in item
        assert isinstance(item["quantidade_compras"], int)
        assert isinstance(item["valor_total"], Decimal)


@pytest.mark.asyncio
async def test_erro_data_final_menor_que_inicial(session: AsyncSession):
    """Testa o erro ao gerar relatório com data final menor que inicial."""
    service = RelatorioService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    data_inicial = date.today()
    data_final = date.today() - timedelta(days=1)
    
    with pytest.raises(HTTPException) as exc_info:
        await service.gerar_relatorio_vendas(
            data_inicial=data_inicial,
            data_final=data_final
        )
    
    assert exc_info.value.status_code == 400
    assert "Data final não pode ser menor que a data inicial" in str(exc_info.value.detail) 