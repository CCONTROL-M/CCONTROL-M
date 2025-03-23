"""Testes de integração para validar a implementação do AuditoriaService."""
import pytest
from uuid import uuid4
from decimal import Decimal
from datetime import datetime, date, timedelta
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.services.auditoria_service import AuditoriaService
from app.services.fornecedor_service import FornecedorService
from app.services.produto_service import ProdutoService
from app.services.conta_bancaria_service import ContaBancariaService
from app.services.forma_pagamento_service import FormaPagamentoService
from app.services.categoria_service import CategoriaService
from app.services.centro_custo_service import CentroCustoService
from app.services.conta_pagar_service import ContaPagarService
from app.services.conta_receber_service import ContaReceberService
from app.services.lancamento_service import LancamentoService

from app.schemas.fornecedor import FornecedorCreate
from app.schemas.produto import ProdutoCreate
from app.schemas.conta_bancaria import ContaBancariaCreate
from app.schemas.forma_pagamento import FormaPagamentoCreate
from app.schemas.categoria import CategoriaCreate
from app.schemas.centro_custo import CentroCustoCreate
from app.schemas.conta_pagar import ContaPagarCreate
from app.schemas.conta_receber import ContaReceberCreate
from app.schemas.lancamento import LancamentoCreate

@pytest.fixture
async def services(db_session: AsyncSession) -> AsyncGenerator:
    """Fixture para criar instâncias dos serviços para teste."""
    auditoria_service = AuditoriaService(db_session)
    
    fornecedor_service = FornecedorService(db_session, auditoria_service)
    produto_service = ProdutoService(db_session, auditoria_service)
    conta_bancaria_service = ContaBancariaService(db_session, auditoria_service)
    forma_pagamento_service = FormaPagamentoService(db_session, auditoria_service)
    categoria_service = CategoriaService(db_session, auditoria_service)
    centro_custo_service = CentroCustoService(db_session, auditoria_service)
    conta_pagar_service = ContaPagarService(db_session, auditoria_service)
    conta_receber_service = ContaReceberService(db_session, auditoria_service)
    lancamento_service = LancamentoService(db_session, auditoria_service)
    
    yield {
        "auditoria": auditoria_service,
        "fornecedor": fornecedor_service,
        "produto": produto_service,
        "conta_bancaria": conta_bancaria_service,
        "forma_pagamento": forma_pagamento_service,
        "categoria": categoria_service,
        "centro_custo": centro_custo_service,
        "conta_pagar": conta_pagar_service,
        "conta_receber": conta_receber_service,
        "lancamento": lancamento_service
    }

@pytest.mark.asyncio
async def test_fornecedor_auditoria(services):
    """Testar registro de auditoria nas operações de fornecedor."""
    id_empresa = uuid4()
    id_usuario = uuid4()
    
    # Criar fornecedor
    fornecedor_data = FornecedorCreate(
        nome="Fornecedor Teste",
        tipo="PJ",
        documento="12345678901234",
        id_empresa=id_empresa
    )
    
    fornecedor = await services["fornecedor"].criar_fornecedor(
        fornecedor_data, 
        id_usuario
    )
    
    # Verificar se a ação foi registrada
    acoes, _ = await services["auditoria"].listar_acoes(
        empresa_id=id_empresa,
        tipo_acao="CRIAR_FORNECEDOR"
    )
    assert len(acoes) == 1
    assert acoes[0].detalhes["nome"] == "Fornecedor Teste"

@pytest.mark.asyncio
async def test_produto_auditoria(services):
    """Testar registro de auditoria nas operações de produto."""
    id_empresa = uuid4()
    id_usuario = uuid4()
    
    # Criar produto
    produto_data = ProdutoCreate(
        nome="Produto Teste",
        codigo="PRD001",
        valor=Decimal("99.99"),
        id_empresa=id_empresa
    )
    
    produto = await services["produto"].create(
        produto_data,
        id_usuario,
        id_empresa
    )
    
    # Verificar se a ação foi registrada
    acoes, _ = await services["auditoria"].listar_acoes(
        empresa_id=id_empresa,
        tipo_acao="CRIAR_PRODUTO"
    )
    assert len(acoes) == 1
    assert acoes[0].detalhes["nome"] == "Produto Teste"

@pytest.mark.asyncio
async def test_conta_bancaria_auditoria(services):
    """Testar registro de auditoria nas operações de conta bancária."""
    id_empresa = uuid4()
    id_usuario = uuid4()
    
    # Criar conta bancária
    conta_data = ContaBancariaCreate(
        banco="Banco Teste",
        agencia="1234",
        numero="56789-0",
        id_empresa=id_empresa
    )
    
    conta = await services["conta_bancaria"].criar_conta_bancaria(
        conta_data,
        id_usuario
    )
    
    # Verificar se a ação foi registrada
    acoes, _ = await services["auditoria"].listar_acoes(
        empresa_id=id_empresa,
        tipo_acao="CRIAR_CONTA_BANCARIA"
    )
    assert len(acoes) == 1
    assert acoes[0].detalhes["banco"] == "Banco Teste"

@pytest.mark.asyncio
async def test_lancamento_auditoria(services):
    """Testar registro de auditoria nas operações de lançamento."""
    id_empresa = uuid4()
    id_usuario = uuid4()
    
    # Criar lançamento
    lancamento_data = LancamentoCreate(
        valor=Decimal("150.00"),
        data=date.today(),
        tipo="RECEITA",
        status="PENDENTE",
        id_empresa=id_empresa
    )
    
    lancamento = await services["lancamento"].create(
        lancamento_data,
        id_usuario,
        id_empresa
    )
    
    # Verificar se a ação foi registrada
    acoes, _ = await services["auditoria"].listar_acoes(
        empresa_id=id_empresa,
        tipo_acao="CRIAR_LANCAMENTO"
    )
    assert len(acoes) == 1
    assert float(acoes[0].detalhes["valor"]) == 150.00

@pytest.mark.asyncio
async def test_forma_pagamento_auditoria(services):
    """Testar registro de auditoria nas operações de forma de pagamento."""
    id_empresa = uuid4()
    id_usuario = uuid4()
    
    # Criar forma de pagamento
    forma_data = FormaPagamentoCreate(
        nome="Cartão de Crédito",
        tipo="CARTAO",
        id_empresa=id_empresa
    )
    
    forma = await services["forma_pagamento"].create(
        forma_data,
        id_usuario,
        id_empresa
    )
    
    # Verificar se a ação foi registrada
    acoes, _ = await services["auditoria"].listar_acoes(
        empresa_id=id_empresa,
        tipo_acao="CRIAR_FORMA_PAGAMENTO"
    )
    assert len(acoes) == 1
    assert acoes[0].detalhes["nome"] == "Cartão de Crédito"

@pytest.mark.asyncio
async def test_categoria_auditoria(services):
    """Testar registro de auditoria nas operações de categoria."""
    id_empresa = uuid4()
    id_usuario = uuid4()
    
    # Criar categoria
    categoria_data = CategoriaCreate(
        nome="Alimentação",
        tipo="DESPESA",
        id_empresa=id_empresa
    )
    
    categoria = await services["categoria"].create(
        categoria_data,
        id_usuario,
        id_empresa
    )
    
    # Verificar se a ação foi registrada
    acoes, _ = await services["auditoria"].listar_acoes(
        empresa_id=id_empresa,
        tipo_acao="CRIAR_CATEGORIA"
    )
    assert len(acoes) == 1
    assert acoes[0].detalhes["nome"] == "Alimentação"

@pytest.mark.asyncio
async def test_centro_custo_auditoria(services):
    """Testar registro de auditoria nas operações de centro de custo."""
    id_empresa = uuid4()
    id_usuario = uuid4()
    
    # Criar centro de custo
    centro_data = CentroCustoCreate(
        nome="Marketing",
        codigo="MKT",
        id_empresa=id_empresa
    )
    
    centro = await services["centro_custo"].create(
        centro_data,
        id_usuario,
        id_empresa
    )
    
    # Verificar se a ação foi registrada
    acoes, _ = await services["auditoria"].listar_acoes(
        empresa_id=id_empresa,
        tipo_acao="CRIAR_CENTRO_CUSTO"
    )
    assert len(acoes) == 1
    assert acoes[0].detalhes["nome"] == "Marketing"

@pytest.mark.asyncio
async def test_conta_pagar_auditoria(services):
    """Testar registro de auditoria nas operações de conta a pagar."""
    id_empresa = uuid4()
    id_usuario = uuid4()
    
    # Criar conta a pagar
    conta_data = ContaPagarCreate(
        descricao="Aluguel",
        valor=Decimal("2000.00"),
        data_vencimento=date.today(),
        status="PENDENTE",
        id_empresa=id_empresa
    )
    
    conta = await services["conta_pagar"].create(
        conta_data,
        id_usuario,
        id_empresa
    )
    
    # Verificar se a ação foi registrada
    acoes, _ = await services["auditoria"].listar_acoes(
        empresa_id=id_empresa,
        tipo_acao="CRIAR_CONTA_PAGAR"
    )
    assert len(acoes) == 1
    assert acoes[0].detalhes["descricao"] == "Aluguel"

@pytest.mark.asyncio
async def test_conta_receber_auditoria(services):
    """Testar registro de auditoria nas operações de conta a receber."""
    id_empresa = uuid4()
    id_usuario = uuid4()
    
    # Criar conta a receber
    conta_data = ContaReceberCreate(
        descricao="Venda #123",
        valor=Decimal("500.00"),
        data_vencimento=date.today(),
        status="PENDENTE",
        id_empresa=id_empresa
    )
    
    conta = await services["conta_receber"].create(
        conta_data,
        id_usuario,
        id_empresa
    )
    
    # Verificar se a ação foi registrada
    acoes, _ = await services["auditoria"].listar_acoes(
        empresa_id=id_empresa,
        tipo_acao="CRIAR_CONTA_RECEBER"
    )
    assert len(acoes) == 1
    assert acoes[0].detalhes["descricao"] == "Venda #123"

@pytest.mark.asyncio
async def test_multiplas_acoes_auditoria(services):
    """Testar registro de múltiplas ações de auditoria."""
    id_empresa = uuid4()
    id_usuario = uuid4()
    
    # Criar múltiplas entidades
    fornecedor_data = FornecedorCreate(
        nome="Fornecedor Teste",
        tipo="PJ",
        documento="12345678901234",
        id_empresa=id_empresa
    )
    
    produto_data = ProdutoCreate(
        nome="Produto Teste",
        codigo="PRD001",
        valor=Decimal("99.99"),
        id_empresa=id_empresa
    )
    
    categoria_data = CategoriaCreate(
        nome="Alimentação",
        tipo="DESPESA",
        id_empresa=id_empresa
    )
    
    # Criar as entidades
    await services["fornecedor"].criar_fornecedor(fornecedor_data, id_usuario)
    await services["produto"].create(produto_data, id_usuario, id_empresa)
    await services["categoria"].create(categoria_data, id_usuario, id_empresa)
    
    # Verificar se todas as ações foram registradas
    acoes, _ = await services["auditoria"].listar_acoes(
        empresa_id=id_empresa
    )
    assert len(acoes) == 3
    
    # Verificar se podemos filtrar por tipo de ação
    acoes_fornecedor, _ = await services["auditoria"].listar_acoes(
        empresa_id=id_empresa,
        tipo_acao="CRIAR_FORNECEDOR"
    )
    assert len(acoes_fornecedor) == 1
    
    acoes_produto, _ = await services["auditoria"].listar_acoes(
        empresa_id=id_empresa,
        tipo_acao="CRIAR_PRODUTO"
    )
    assert len(acoes_produto) == 1
    
    acoes_categoria, _ = await services["auditoria"].listar_acoes(
        empresa_id=id_empresa,
        tipo_acao="CRIAR_CATEGORIA"
    )
    assert len(acoes_categoria) == 1

@pytest.mark.asyncio
async def test_atualizacao_auditoria(services):
    """Testar registro de auditoria nas operações de atualização."""
    id_empresa = uuid4()
    id_usuario = uuid4()
    
    # Criar fornecedor
    fornecedor_data = FornecedorCreate(
        nome="Fornecedor Original",
        tipo="PJ",
        documento="12345678901234",
        id_empresa=id_empresa
    )
    
    fornecedor = await services["fornecedor"].criar_fornecedor(
        fornecedor_data,
        id_usuario
    )
    
    # Atualizar fornecedor
    fornecedor_atualizado = {
        "nome": "Fornecedor Atualizado",
        "tipo": "PJ",
        "documento": "12345678901234"
    }
    
    await services["fornecedor"].atualizar_fornecedor(
        fornecedor.id,
        fornecedor_atualizado,
        id_usuario
    )
    
    # Verificar se ambas as ações foram registradas
    acoes, _ = await services["auditoria"].listar_acoes(
        empresa_id=id_empresa
    )
    assert len(acoes) == 2
    
    acoes_atualizacao, _ = await services["auditoria"].listar_acoes(
        empresa_id=id_empresa,
        tipo_acao="ATUALIZAR_FORNECEDOR"
    )
    assert len(acoes_atualizacao) == 1
    assert acoes_atualizacao[0].detalhes["nome"] == "Fornecedor Atualizado"

@pytest.mark.asyncio
async def test_exclusao_auditoria(services):
    """Testar registro de auditoria nas operações de exclusão."""
    id_empresa = uuid4()
    id_usuario = uuid4()
    
    # Criar produto
    produto_data = ProdutoCreate(
        nome="Produto para Excluir",
        codigo="PRD999",
        valor=Decimal("99.99"),
        id_empresa=id_empresa
    )
    
    produto = await services["produto"].create(
        produto_data,
        id_usuario,
        id_empresa
    )
    
    # Excluir produto
    await services["produto"].delete(
        produto.id,
        id_usuario,
        id_empresa
    )
    
    # Verificar se ambas as ações foram registradas
    acoes, _ = await services["auditoria"].listar_acoes(
        empresa_id=id_empresa
    )
    assert len(acoes) == 2
    
    acoes_exclusao, _ = await services["auditoria"].listar_acoes(
        empresa_id=id_empresa,
        tipo_acao="EXCLUIR_PRODUTO"
    )
    assert len(acoes_exclusao) == 1
    assert acoes_exclusao[0].detalhes["nome"] == "Produto para Excluir"

@pytest.mark.asyncio
async def test_consulta_auditoria(services):
    """Testar registro de auditoria nas operações de consulta."""
    id_empresa = uuid4()
    id_usuario = uuid4()
    
    # Criar categoria
    categoria_data = CategoriaCreate(
        nome="Categoria Teste",
        tipo="DESPESA",
        id_empresa=id_empresa
    )
    
    categoria = await services["categoria"].create(
        categoria_data,
        id_usuario,
        id_empresa
    )
    
    # Consultar categoria
    await services["categoria"].get_by_id(
        categoria.id,
        id_usuario,
        id_empresa
    )
    
    # Verificar se ambas as ações foram registradas
    acoes, _ = await services["auditoria"].listar_acoes(
        empresa_id=id_empresa
    )
    assert len(acoes) == 2
    
    acoes_consulta, _ = await services["auditoria"].listar_acoes(
        empresa_id=id_empresa,
        tipo_acao="CONSULTAR_CATEGORIA"
    )
    assert len(acoes_consulta) == 1
    assert acoes_consulta[0].detalhes["id"] == str(categoria.id)

@pytest.mark.asyncio
async def test_filtros_auditoria(services):
    """Testar filtros de auditoria."""
    id_empresa = uuid4()
    id_usuario = uuid4()
    outro_id_usuario = uuid4()
    
    # Criar múltiplas ações com usuários diferentes
    fornecedor_data = FornecedorCreate(
        nome="Fornecedor Teste",
        tipo="PJ",
        documento="12345678901234",
        id_empresa=id_empresa
    )
    
    produto_data = ProdutoCreate(
        nome="Produto Teste",
        codigo="PRD001",
        valor=Decimal("99.99"),
        id_empresa=id_empresa
    )
    
    await services["fornecedor"].criar_fornecedor(fornecedor_data, id_usuario)
    await services["produto"].create(produto_data, outro_id_usuario, id_empresa)
    
    # Testar filtro por usuário
    acoes_usuario1, _ = await services["auditoria"].listar_acoes(
        empresa_id=id_empresa,
        usuario_id=id_usuario
    )
    assert len(acoes_usuario1) == 1
    
    acoes_usuario2, _ = await services["auditoria"].listar_acoes(
        empresa_id=id_empresa,
        usuario_id=outro_id_usuario
    )
    assert len(acoes_usuario2) == 1
    
    # Testar filtro por período
    data_inicio = datetime.now() - timedelta(days=1)
    data_fim = datetime.now() + timedelta(days=1)
    
    acoes_periodo, _ = await services["auditoria"].listar_acoes(
        empresa_id=id_empresa,
        data_inicio=data_inicio,
        data_fim=data_fim
    )
    assert len(acoes_periodo) == 2 