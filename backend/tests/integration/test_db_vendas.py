import asyncio
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient
import os
import logging
from unittest.mock import patch
from uuid import uuid4
from datetime import date, datetime

from app.main import app
from app.db.session import get_session, create_db_and_tables
from app.models.venda import Venda, VendaItem
from app.models.produto import Produto
from app.models.cliente import Cliente
from app.models.empresa import Empresa
from app.models.usuario import Usuario
from app.models.forma_pagamento import FormaPagamento
from app.schemas.venda import VendaCreate, VendaItemCreate
from app.core.security import create_access_token

# Configurar logger para testes
logger = logging.getLogger("test_integration")


@pytest.fixture(scope="module")
async def test_db():
    """Fixture para criar e disponibilizar o banco de dados de teste."""
    # Criar banco de dados de teste
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_vendas_integration.db"
    
    # Criar tabelas no banco de teste
    await create_db_and_tables()
    
    yield
    
    # Limpar após os testes
    try:
        os.remove("./test_vendas_integration.db")
    except OSError:
        pass


@pytest.fixture
async def async_session():
    """Fixture para sessão assíncrona do SQLAlchemy."""
    async for session in get_session():
        yield session


@pytest.fixture
async def async_client():
    """Fixture para cliente HTTP assíncrono."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def test_data(async_session):
    """Fixture para dados de teste (usuário, empresa, produtos, clientes)."""
    # Criar usuário de teste
    usuario_id = str(uuid4())
    usuario = Usuario(
        id=usuario_id,
        email="vendas@ccontrolm.com.br",
        username="vendas_teste",
        hashed_password="$2b$12$TZ6Fk5WM0vlZ3GoS4Foqae6zq5Zs3S/uKIJDz5TkVQrQR6MXKcd9W",  # senha123
        is_active=True,
        is_superuser=True
    )
    
    # Criar empresa de teste
    empresa_id = str(uuid4())
    empresa = Empresa(
        id=empresa_id,
        nome="Empresa Vendas Teste",
        cnpj="98765432101234",
        telefone="47999999988",
        email="vendas_empresa@teste.com",
        is_active=True,
        usuario_id=usuario_id
    )
    
    # Criar produtos para teste
    produtos = []
    for i in range(3):
        produto_id = str(uuid4())
        produto = Produto(
            id=produto_id,
            codigo=f"PROD-{i}",
            nome=f"Produto Teste {i}",
            descricao=f"Descrição do produto {i}",
            preco_custo=10.0 * (i + 1),
            preco_venda=20.0 * (i + 1),
            unidade="UN",
            categoria="Categoria Teste",
            estoque_atual=100,
            estoque_minimo=10,
            empresa_id=empresa_id,
            usuario_id=usuario_id,
            is_active=True
        )
        produtos.append(produto)
    
    # Criar cliente para teste
    cliente_id = str(uuid4())
    cliente = Cliente(
        id=cliente_id,
        nome="Cliente Teste Vendas",
        email="cliente_vendas@teste.com",
        telefone="47988887777",
        tipo="PF",
        cpf="12345678909",
        empresa_id=empresa_id,
        usuario_id=usuario_id,
        is_active=True
    )
    
    # Criar forma de pagamento para teste
    forma_pagamento_id = str(uuid4())
    forma_pagamento = FormaPagamento(
        id=forma_pagamento_id,
        nome="Cartão de Crédito",
        tipo="credito",
        parcelas_max=12,
        empresa_id=empresa_id,
        usuario_id=usuario_id,
        is_active=True
    )
    
    # Salvar no banco
    async_session.add(usuario)
    async_session.add(empresa)
    for produto in produtos:
        async_session.add(produto)
    async_session.add(cliente)
    async_session.add(forma_pagamento)
    await async_session.commit()
    
    # Retornar dados para uso nos testes
    return {
        "usuario": usuario,
        "empresa": empresa,
        "produtos": produtos,
        "cliente": cliente,
        "forma_pagamento": forma_pagamento
    }


@pytest.fixture
async def authenticated_client(async_client, test_data):
    """Fixture para cliente HTTP autenticado."""
    # Criar token de acesso
    token = create_access_token(
        data={
            "sub": test_data["usuario"].email, 
            "empresa_id": test_data["empresa"].id, 
            "user_id": test_data["usuario"].id
        }
    )
    
    # Configurar cabeçalho de autorização
    async_client.headers.update({"Authorization": f"Bearer {token}"})
    
    yield async_client


@pytest.mark.asyncio
async def test_criar_venda_db(authenticated_client, async_session, test_data, test_db):
    """Testa a criação de uma venda integrada com banco de dados."""
    # Preparar dados para a venda
    produtos = test_data["produtos"]
    itens_venda = []
    valor_total = 0
    
    for i, produto in enumerate(produtos):
        quantidade = i + 1
        preco_unitario = produto.preco_venda
        subtotal = quantidade * preco_unitario
        valor_total += subtotal
        
        itens_venda.append({
            "produto_id": produto.id,
            "quantidade": quantidade,
            "preco_unitario": preco_unitario,
            "subtotal": subtotal
        })
    
    venda_data = {
        "cliente_id": test_data["cliente"].id,
        "data_venda": date.today().isoformat(),
        "forma_pagamento_id": test_data["forma_pagamento"].id,
        "valor_total": valor_total,
        "desconto": 0,
        "parcelas": 1,
        "observacoes": "Venda de teste via API",
        "itens": itens_venda
    }
    
    # Fazer requisição para criar venda
    response = await authenticated_client.post(
        "/api/v1/vendas",
        json=venda_data
    )
    
    # Verificar resposta
    assert response.status_code == 201
    data = response.json()
    assert data["cliente_id"] == test_data["cliente"].id
    assert data["valor_total"] == valor_total
    assert len(data["itens"]) == len(itens_venda)
    
    # Verificar se a venda foi salva no banco
    venda_id = data["id"]
    venda = await async_session.get(Venda, venda_id)
    
    assert venda is not None
    assert venda.cliente_id == test_data["cliente"].id
    assert venda.valor_total == valor_total
    assert venda.empresa_id == test_data["empresa"].id
    
    # Verificar se os itens foram salvos corretamente
    itens_query = await async_session.execute(
        "SELECT * FROM venda_item WHERE venda_id = :venda_id",
        {"venda_id": venda_id}
    )
    itens = itens_query.fetchall()
    
    assert len(itens) == len(itens_venda)
    
    # Verificar se o estoque foi atualizado
    for i, produto in enumerate(produtos):
        await async_session.refresh(produto)
        quantidade_vendida = i + 1
        assert produto.estoque_atual == (100 - quantidade_vendida)


@pytest.mark.asyncio
async def test_listar_vendas_db(authenticated_client, async_session, test_data, test_db):
    """Testa a listagem de vendas integrada com banco de dados."""
    # Criar algumas vendas adicionais para teste
    for i in range(3):
        venda = Venda(
            id=str(uuid4()),
            cliente_id=test_data["cliente"].id,
            data_venda=date.today(),
            forma_pagamento_id=test_data["forma_pagamento"].id,
            valor_total=100.0 * (i + 1),
            desconto=0,
            status="concluida",
            empresa_id=test_data["empresa"].id,
            usuario_id=test_data["usuario"].id
        )
        async_session.add(venda)
    
    await async_session.commit()
    
    # Fazer requisição para listar vendas
    response = await authenticated_client.get("/api/v1/vendas")
    
    # Verificar resposta
    assert response.status_code == 200
    data = response.json()
    
    # Deve haver pelo menos as 3 vendas criadas + a do teste anterior
    assert len(data["items"]) >= 4
    assert data["total"] >= 4


@pytest.mark.asyncio
async def test_obter_venda_por_id_db(authenticated_client, async_session, test_data, test_db):
    """Testa a obtenção de uma venda por ID integrada com banco de dados."""
    # Criar uma venda para teste
    venda_id = str(uuid4())
    venda = Venda(
        id=venda_id,
        cliente_id=test_data["cliente"].id,
        data_venda=date.today(),
        forma_pagamento_id=test_data["forma_pagamento"].id,
        valor_total=500.0,
        desconto=50.0,
        parcelas=2,
        status="concluida",
        empresa_id=test_data["empresa"].id,
        usuario_id=test_data["usuario"].id
    )
    async_session.add(venda)
    
    # Criar alguns itens para a venda
    for i, produto in enumerate(test_data["produtos"]):
        item = VendaItem(
            id=str(uuid4()),
            venda_id=venda_id,
            produto_id=produto.id,
            quantidade=i + 1,
            preco_unitario=produto.preco_venda,
            subtotal=(i + 1) * produto.preco_venda
        )
        async_session.add(item)
    
    await async_session.commit()
    
    # Fazer requisição para obter venda por ID
    response = await authenticated_client.get(f"/api/v1/vendas/{venda_id}")
    
    # Verificar resposta
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == venda_id
    assert data["cliente_id"] == test_data["cliente"].id
    assert data["valor_total"] == 500.0
    assert data["desconto"] == 50.0
    assert len(data["itens"]) == len(test_data["produtos"])


@pytest.mark.asyncio
async def test_cancelar_venda_db(authenticated_client, async_session, test_data, test_db):
    """Testa o cancelamento de uma venda integrado com banco de dados."""
    # Criar uma venda para cancelar
    venda_id = str(uuid4())
    venda = Venda(
        id=venda_id,
        cliente_id=test_data["cliente"].id,
        data_venda=date.today(),
        forma_pagamento_id=test_data["forma_pagamento"].id,
        valor_total=300.0,
        status="concluida",
        empresa_id=test_data["empresa"].id,
        usuario_id=test_data["usuario"].id
    )
    async_session.add(venda)
    
    # Ajustar estoque dos produtos
    produto = test_data["produtos"][0]
    estoque_original = produto.estoque_atual
    
    # Criar um item para a venda
    item = VendaItem(
        id=str(uuid4()),
        venda_id=venda_id,
        produto_id=produto.id,
        quantidade=5,
        preco_unitario=produto.preco_venda,
        subtotal=5 * produto.preco_venda
    )
    async_session.add(item)
    
    # Atualizar estoque do produto
    produto.estoque_atual -= 5
    
    await async_session.commit()
    
    # Fazer requisição para cancelar venda
    response = await authenticated_client.patch(
        f"/api/v1/vendas/{venda_id}/cancelar",
        json={"motivo_cancelamento": "Teste de cancelamento"}
    )
    
    # Verificar resposta
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "cancelada"
    assert data["motivo_cancelamento"] == "Teste de cancelamento"
    
    # Verificar se a venda foi atualizada no banco
    await async_session.refresh(venda)
    assert venda.status == "cancelada"
    assert venda.motivo_cancelamento == "Teste de cancelamento"
    
    # Verificar se o estoque foi restaurado
    await async_session.refresh(produto)
    assert produto.estoque_atual == estoque_original 