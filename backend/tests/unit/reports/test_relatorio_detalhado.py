"""Testes para o relatório detalhado por entidade."""
import pytest
from decimal import Decimal
from datetime import date, timedelta
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Any

from app.models.venda import Venda
from app.models.compra import Compra
from app.models.conta_receber import ContaReceber
from app.models.conta_pagar import ContaPagar
from app.models.cliente import Cliente
from app.models.fornecedor import Fornecedor
from app.models.categoria import Categoria


@pytest.mark.no_db
async def test_listagem_vendas_valores_corretos(dados_completos, db_session: AsyncSession):
    """Teste para verificar se a listagem de vendas possui valores corretos."""
    # Arrange
    empresa_id = dados_completos["empresa"].id_empresa
    periodo = dados_completos["periodo"]
    
    # Act
    # Buscar todas as vendas no período
    query_vendas = select(Venda).where(
        Venda.data_venda.between(periodo["data_inicio"], periodo["data_fim"]),
        Venda.id_empresa == empresa_id
    )
    result_vendas = await db_session.execute(query_vendas)
    vendas = result_vendas.scalars().all()
    
    # Para cada venda, verificar se o valor total corresponde à soma das parcelas e/ou contas a receber
    resultados_verificacao = []
    for venda in vendas:
        # Buscar parcelas associadas à venda
        query_parcelas = select(Parcela).where(
            Parcela.id_venda == venda.id_venda
        )
        
        # Buscar contas a receber associadas à venda
        query_contas = select(ContaReceber).where(
            ContaReceber.id_venda == venda.id_venda
        )
        
        # Executar queries
        from app.models.parcela import Parcela
        
        result_parcelas = await db_session.execute(query_parcelas)
        parcelas = result_parcelas.scalars().all()
        
        result_contas = await db_session.execute(query_contas)
        contas = result_contas.scalars().all()
        
        # Calcular totais
        total_parcelas = sum(p.valor for p in parcelas) if parcelas else Decimal("0")
        total_contas = sum(c.valor for c in contas) if contas else Decimal("0")
        
        # Adicionar resultado da verificação
        resultados_verificacao.append({
            "venda_id": venda.id_venda,
            "venda_valor": venda.valor_total,
            "total_parcelas": total_parcelas,
            "total_contas": total_contas,
            "tem_parcelas": len(parcelas) > 0,
            "tem_contas": len(contas) > 0,
            # Uma venda pode ter parcelas OU contas a receber diretas
            "valor_consistente": (
                (total_parcelas > 0 and abs(total_parcelas - venda.valor_total) < Decimal("0.01")) or
                (total_contas > 0 and abs(total_contas - venda.valor_total) < Decimal("0.01")) or
                (total_parcelas == 0 and total_contas == 0)  # Venda sem parcelas/contas ainda
            )
        })
    
    # Assert
    # Verificamos se existem vendas para testar
    assert len(vendas) > 0, "Não foram encontradas vendas para o teste"
    
    # Para cada venda com parcelas ou contas, verificamos se os valores estão consistentes
    for resultado in resultados_verificacao:
        if resultado["tem_parcelas"] or resultado["tem_contas"]:
            assert resultado["valor_consistente"], (
                f"Venda {resultado['venda_id']} com valor inconsistente: "
                f"valor_total={resultado['venda_valor']}, "
                f"total_parcelas={resultado['total_parcelas']}, "
                f"total_contas={resultado['total_contas']}"
            )


@pytest.mark.no_db
async def test_listagem_compras_valores_corretos(dados_completos, db_session: AsyncSession):
    """Teste para verificar se a listagem de compras possui valores corretos."""
    # Arrange
    empresa_id = dados_completos["empresa"].id_empresa
    periodo = dados_completos["periodo"]
    
    # Act
    # Buscar todas as compras no período
    query_compras = select(Compra).where(
        Compra.data_compra.between(periodo["data_inicio"], periodo["data_fim"]),
        Compra.id_empresa == empresa_id
    )
    result_compras = await db_session.execute(query_compras)
    compras = result_compras.scalars().all()
    
    # Para cada compra, verificar se o valor total corresponde à soma das parcelas e/ou contas a pagar
    resultados_verificacao = []
    for compra in compras:
        # Buscar parcelas associadas à compra
        query_parcelas = select(Parcela).where(
            Parcela.id_compra == compra.id_compra
        )
        
        # Buscar contas a pagar associadas à compra
        query_contas = select(ContaPagar).where(
            ContaPagar.id_compra == compra.id_compra
        )
        
        # Executar queries
        from app.models.parcela import Parcela
        
        result_parcelas = await db_session.execute(query_parcelas)
        parcelas = result_parcelas.scalars().all()
        
        result_contas = await db_session.execute(query_contas)
        contas = result_contas.scalars().all()
        
        # Calcular totais
        total_parcelas = sum(p.valor for p in parcelas) if parcelas else Decimal("0")
        total_contas = sum(c.valor for c in contas) if contas else Decimal("0")
        
        # Adicionar resultado da verificação
        resultados_verificacao.append({
            "compra_id": compra.id_compra,
            "compra_valor": compra.valor_total,
            "total_parcelas": total_parcelas,
            "total_contas": total_contas,
            "tem_parcelas": len(parcelas) > 0,
            "tem_contas": len(contas) > 0,
            # Uma compra pode ter parcelas OU contas a pagar diretas
            "valor_consistente": (
                (total_parcelas > 0 and abs(total_parcelas - compra.valor_total) < Decimal("0.01")) or
                (total_contas > 0 and abs(total_contas - compra.valor_total) < Decimal("0.01")) or
                (total_parcelas == 0 and total_contas == 0)  # Compra sem parcelas/contas ainda
            )
        })
    
    # Assert
    # Verificamos se existem compras para testar
    assert len(compras) > 0, "Não foram encontradas compras para o teste"
    
    # Para cada compra com parcelas ou contas, verificamos se os valores estão consistentes
    for resultado in resultados_verificacao:
        if resultado["tem_parcelas"] or resultado["tem_contas"]:
            assert resultado["valor_consistente"], (
                f"Compra {resultado['compra_id']} com valor inconsistente: "
                f"valor_total={resultado['compra_valor']}, "
                f"total_parcelas={resultado['total_parcelas']}, "
                f"total_contas={resultado['total_contas']}"
            )


@pytest.mark.no_db
async def test_contas_receber_pagar_valores_corretos(dados_completos, db_session: AsyncSession):
    """Testa se as contas a receber e pagar têm valores corretos em relação às suas entidades associadas."""
    # Arrange
    empresa_id = dados_completos["empresa"].id_empresa
    periodo = dados_completos["periodo"]
    
    # Act - Contas a Receber
    query_contas_receber = select(ContaReceber).where(
        ContaReceber.data_emissao.between(periodo["data_inicio"], periodo["data_fim"]),
        ContaReceber.id_empresa == empresa_id
    )
    result_contas_receber = await db_session.execute(query_contas_receber)
    contas_receber = result_contas_receber.scalars().all()
    
    # Verificar contas a receber vinculadas a vendas
    for conta in contas_receber:
        if conta.id_venda:
            # Buscar a venda associada
            query_venda = select(Venda).where(Venda.id_venda == conta.id_venda)
            result_venda = await db_session.execute(query_venda)
            venda = result_venda.scalar_one_or_none()
            
            if venda:
                # Verificar se o valor da conta corresponde ao da venda
                assert abs(conta.valor - venda.valor_total) < Decimal("0.01"), (
                    f"Conta a receber {conta.id_conta_receber} com valor inconsistente: "
                    f"conta.valor={conta.valor}, venda.valor_total={venda.valor_total}"
                )
    
    # Act - Contas a Pagar
    query_contas_pagar = select(ContaPagar).where(
        ContaPagar.data_emissao.between(periodo["data_inicio"], periodo["data_fim"]),
        ContaPagar.id_empresa == empresa_id
    )
    result_contas_pagar = await db_session.execute(query_contas_pagar)
    contas_pagar = result_contas_pagar.scalars().all()
    
    # Verificar contas a pagar vinculadas a compras
    for conta in contas_pagar:
        if conta.id_compra:
            # Buscar a compra associada
            query_compra = select(Compra).where(Compra.id_compra == conta.id_compra)
            result_compra = await db_session.execute(query_compra)
            compra = result_compra.scalar_one_or_none()
            
            if compra:
                # Verificar se o valor da conta corresponde ao da compra
                assert abs(conta.valor - compra.valor_total) < Decimal("0.01"), (
                    f"Conta a pagar {conta.id_conta_pagar} com valor inconsistente: "
                    f"conta.valor={conta.valor}, compra.valor_total={compra.valor_total}"
                )


@pytest.mark.no_db
async def test_filtragem_por_data(dados_completos, db_session: AsyncSession):
    """Testa se a filtragem por data funciona corretamente."""
    # Arrange
    empresa_id = dados_completos["empresa"].id_empresa
    
    # Definir um período específico para teste (metade do período total)
    periodo_completo = dados_completos["periodo"]
    data_meio = periodo_completo["data_inicio"] + (periodo_completo["data_fim"] - periodo_completo["data_inicio"]) / 2
    
    periodo_teste = {
        "data_inicio": periodo_completo["data_inicio"],
        "data_fim": data_meio
    }
    
    # Act - Vendas
    # Todas as vendas no período completo
    query_vendas_completo = select(Venda).where(
        Venda.data_venda.between(periodo_completo["data_inicio"], periodo_completo["data_fim"]),
        Venda.id_empresa == empresa_id
    )
    result_vendas_completo = await db_session.execute(query_vendas_completo)
    vendas_completo = result_vendas_completo.scalars().all()
    
    # Vendas no período de teste
    query_vendas_teste = select(Venda).where(
        Venda.data_venda.between(periodo_teste["data_inicio"], periodo_teste["data_fim"]),
        Venda.id_empresa == empresa_id
    )
    result_vendas_teste = await db_session.execute(query_vendas_teste)
    vendas_teste = result_vendas_teste.scalars().all()
    
    # Act - Compras
    # Todas as compras no período completo
    query_compras_completo = select(Compra).where(
        Compra.data_compra.between(periodo_completo["data_inicio"], periodo_completo["data_fim"]),
        Compra.id_empresa == empresa_id
    )
    result_compras_completo = await db_session.execute(query_compras_completo)
    compras_completo = result_compras_completo.scalars().all()
    
    # Compras no período de teste
    query_compras_teste = select(Compra).where(
        Compra.data_compra.between(periodo_teste["data_inicio"], periodo_teste["data_fim"]),
        Compra.id_empresa == empresa_id
    )
    result_compras_teste = await db_session.execute(query_compras_teste)
    compras_teste = result_compras_teste.scalars().all()
    
    # Assert
    # O número de vendas e compras no período de teste deve ser menor ou igual ao período completo
    assert len(vendas_teste) <= len(vendas_completo), "Número inesperado de vendas no período de teste"
    assert len(compras_teste) <= len(compras_completo), "Número inesperado de compras no período de teste"
    
    # Todas as vendas do período de teste devem estar no período completo
    for venda in vendas_teste:
        assert venda in vendas_completo, f"Venda {venda.id_venda} encontrada no período de teste mas não no completo"
    
    # Todas as compras do período de teste devem estar no período completo
    for compra in compras_teste:
        assert compra in compras_completo, f"Compra {compra.id_compra} encontrada no período de teste mas não no completo"


@pytest.mark.no_db
async def test_filtragem_por_cliente(dados_completos, db_session: AsyncSession):
    """Testa se a filtragem por cliente funciona corretamente."""
    # Arrange
    empresa_id = dados_completos["empresa"].id_empresa
    periodo = dados_completos["periodo"]
    clientes = dados_completos["clientes"]
    
    # Escolher o primeiro cliente para filtrar
    cliente_filtro = clientes[0]
    
    # Act
    # Todas as vendas no período
    query_vendas_todas = select(Venda).where(
        Venda.data_venda.between(periodo["data_inicio"], periodo["data_fim"]),
        Venda.id_empresa == empresa_id
    )
    result_vendas_todas = await db_session.execute(query_vendas_todas)
    vendas_todas = result_vendas_todas.scalars().all()
    
    # Vendas filtradas por cliente
    query_vendas_cliente = select(Venda).where(
        Venda.data_venda.between(periodo["data_inicio"], periodo["data_fim"]),
        Venda.id_cliente == cliente_filtro.id_cliente,
        Venda.id_empresa == empresa_id
    )
    result_vendas_cliente = await db_session.execute(query_vendas_cliente)
    vendas_cliente = result_vendas_cliente.scalars().all()
    
    # Contas a receber do cliente
    query_contas_cliente = select(ContaReceber).where(
        ContaReceber.data_emissao.between(periodo["data_inicio"], periodo["data_fim"]),
        ContaReceber.id_cliente == cliente_filtro.id_cliente,
        ContaReceber.id_empresa == empresa_id
    )
    result_contas_cliente = await db_session.execute(query_contas_cliente)
    contas_cliente = result_contas_cliente.scalars().all()
    
    # Assert
    # Deve haver pelo menos uma venda para o cliente
    assert len(vendas_cliente) > 0, f"Nenhuma venda encontrada para o cliente {cliente_filtro.nome}"
    
    # O número de vendas do cliente deve ser menor ou igual ao total de vendas
    assert len(vendas_cliente) <= len(vendas_todas), "Número inesperado de vendas para o cliente"
    
    # Todas as vendas do cliente devem estar no conjunto total de vendas
    for venda in vendas_cliente:
        assert venda in vendas_todas, f"Venda {venda.id_venda} do cliente não encontrada no conjunto total"
        # O cliente da venda deve ser o cliente filtrado
        assert venda.id_cliente == cliente_filtro.id_cliente, f"Cliente incorreto na venda {venda.id_venda}"
    
    # Para cada conta a receber do cliente, se ela tiver uma venda associada, essa venda deve estar em vendas_cliente
    for conta in contas_cliente:
        if conta.id_venda:
            venda_encontrada = False
            for venda in vendas_cliente:
                if venda.id_venda == conta.id_venda:
                    venda_encontrada = True
                    break
            assert venda_encontrada, f"Conta a receber {conta.id_conta_receber} associada a uma venda que não está no conjunto filtrado"


@pytest.mark.no_db
async def test_filtragem_por_fornecedor(dados_completos, db_session: AsyncSession):
    """Testa se a filtragem por fornecedor funciona corretamente."""
    # Arrange
    empresa_id = dados_completos["empresa"].id_empresa
    periodo = dados_completos["periodo"]
    fornecedores = dados_completos["fornecedores"]
    
    # Escolher o primeiro fornecedor para filtrar
    fornecedor_filtro = fornecedores[0]
    
    # Act
    # Todas as compras no período
    query_compras_todas = select(Compra).where(
        Compra.data_compra.between(periodo["data_inicio"], periodo["data_fim"]),
        Compra.id_empresa == empresa_id
    )
    result_compras_todas = await db_session.execute(query_compras_todas)
    compras_todas = result_compras_todas.scalars().all()
    
    # Compras filtradas por fornecedor
    query_compras_fornecedor = select(Compra).where(
        Compra.data_compra.between(periodo["data_inicio"], periodo["data_fim"]),
        Compra.id_fornecedor == fornecedor_filtro.id_fornecedor,
        Compra.id_empresa == empresa_id
    )
    result_compras_fornecedor = await db_session.execute(query_compras_fornecedor)
    compras_fornecedor = result_compras_fornecedor.scalars().all()
    
    # Contas a pagar do fornecedor
    query_contas_fornecedor = select(ContaPagar).where(
        ContaPagar.data_emissao.between(periodo["data_inicio"], periodo["data_fim"]),
        ContaPagar.id_fornecedor == fornecedor_filtro.id_fornecedor,
        ContaPagar.id_empresa == empresa_id
    )
    result_contas_fornecedor = await db_session.execute(query_contas_fornecedor)
    contas_fornecedor = result_contas_fornecedor.scalars().all()
    
    # Assert
    # Deve haver pelo menos uma compra para o fornecedor
    assert len(compras_fornecedor) > 0, f"Nenhuma compra encontrada para o fornecedor {fornecedor_filtro.nome}"
    
    # O número de compras do fornecedor deve ser menor ou igual ao total de compras
    assert len(compras_fornecedor) <= len(compras_todas), "Número inesperado de compras para o fornecedor"
    
    # Todas as compras do fornecedor devem estar no conjunto total de compras
    for compra in compras_fornecedor:
        assert compra in compras_todas, f"Compra {compra.id_compra} do fornecedor não encontrada no conjunto total"
        # O fornecedor da compra deve ser o fornecedor filtrado
        assert compra.id_fornecedor == fornecedor_filtro.id_fornecedor, f"Fornecedor incorreto na compra {compra.id_compra}"
    
    # Para cada conta a pagar do fornecedor, se ela tiver uma compra associada, essa compra deve estar em compras_fornecedor
    for conta in contas_fornecedor:
        if conta.id_compra:
            compra_encontrada = False
            for compra in compras_fornecedor:
                if compra.id_compra == conta.id_compra:
                    compra_encontrada = True
                    break
            assert compra_encontrada, f"Conta a pagar {conta.id_conta_pagar} associada a uma compra que não está no conjunto filtrado"


@pytest.mark.no_db
async def test_filtragem_por_categoria(dados_completos, db_session: AsyncSession):
    """Testa se a filtragem por categoria funciona corretamente."""
    # Arrange
    empresa_id = dados_completos["empresa"].id_empresa
    periodo = dados_completos["periodo"]
    categorias = dados_completos["categorias"]
    
    # Escolher uma categoria de receita e uma de despesa para testar
    categoria_receita = next(cat for cat in categorias if cat.tipo == "receita")
    categoria_despesa = next(cat for cat in categorias if cat.tipo == "despesa")
    
    # Act - Receitas
    # Vendas da categoria de receita
    query_vendas_categoria = select(Venda).where(
        Venda.data_venda.between(periodo["data_inicio"], periodo["data_fim"]),
        Venda.id_categoria == categoria_receita.id_categoria,
        Venda.id_empresa == empresa_id
    )
    result_vendas_categoria = await db_session.execute(query_vendas_categoria)
    vendas_categoria = result_vendas_categoria.scalars().all()
    
    # Contas a receber com a categoria (ou associadas a vendas com a categoria)
    query_contas_receita = select(ContaReceber).where(
        ContaReceber.data_emissao.between(periodo["data_inicio"], periodo["data_fim"]),
        or_(
            ContaReceber.id_categoria == categoria_receita.id_categoria,
            ContaReceber.id_venda.in_([v.id_venda for v in vendas_categoria])
        ),
        ContaReceber.id_empresa == empresa_id
    )
    result_contas_receita = await db_session.execute(query_contas_receita)
    contas_receita = result_contas_receita.scalars().all()
    
    # Act - Despesas
    # Compras da categoria de despesa
    query_compras_categoria = select(Compra).where(
        Compra.data_compra.between(periodo["data_inicio"], periodo["data_fim"]),
        Compra.id_categoria == categoria_despesa.id_categoria,
        Compra.id_empresa == empresa_id
    )
    result_compras_categoria = await db_session.execute(query_compras_categoria)
    compras_categoria = result_compras_categoria.scalars().all()
    
    # Contas a pagar com a categoria (ou associadas a compras com a categoria)
    query_contas_despesa = select(ContaPagar).where(
        ContaPagar.data_emissao.between(periodo["data_inicio"], periodo["data_fim"]),
        or_(
            ContaPagar.id_categoria == categoria_despesa.id_categoria,
            ContaPagar.id_compra.in_([c.id_compra for c in compras_categoria])
        ),
        ContaPagar.id_empresa == empresa_id
    )
    result_contas_despesa = await db_session.execute(query_contas_despesa)
    contas_despesa = result_contas_despesa.scalars().all()
    
    # Assert
    # Verificar se há pelo menos alguns resultados para testar
    assert len(vendas_categoria) > 0, f"Nenhuma venda encontrada para a categoria {categoria_receita.nome}"
    assert len(compras_categoria) > 0, f"Nenhuma compra encontrada para a categoria {categoria_despesa.nome}"
    
    # Verificar se as vendas têm a categoria correta
    for venda in vendas_categoria:
        assert venda.id_categoria == categoria_receita.id_categoria, (
            f"Venda {venda.id_venda} não pertence à categoria filtrada"
        )
    
    # Verificar se as compras têm a categoria correta
    for compra in compras_categoria:
        assert compra.id_categoria == categoria_despesa.id_categoria, (
            f"Compra {compra.id_compra} não pertence à categoria filtrada"
        )
    
    # Verificar se as contas a receber estão associadas às vendas da categoria
    for conta in contas_receita:
        if conta.id_venda:
            assert conta.id_venda in [v.id_venda for v in vendas_categoria], (
                f"Conta a receber {conta.id_conta_receber} associada a uma venda que não pertence à categoria filtrada"
            ) 