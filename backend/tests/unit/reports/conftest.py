"""Fixtures para testes de relatórios financeiros."""
import pytest
import asyncio
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any, AsyncGenerator
import uuid
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.base import Base
from app.models.lancamento import Lancamento
from app.models.cliente import Cliente
from app.models.fornecedor import Fornecedor
from app.models.centro_custo import CentroCusto
from app.models.conta_bancaria import ContaBancaria
from app.models.categoria import Categoria
from app.models.venda import Venda
from app.models.compra import Compra
from app.models.parcela import Parcela
from app.models.conta_pagar import ContaPagar
from app.models.conta_receber import ContaReceber
from app.models.empresa import Empresa
from app.models.usuario import Usuario


@pytest.fixture
def event_loop():
    """Cria um novo event loop para cada teste."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_sqlite_engine():
    """Cria um engine SQLite assíncrono em memória para testes."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def async_session_factory(async_sqlite_engine):
    """Cria uma fábrica de sessões assíncronas para SQLite."""
    factory = async_sessionmaker(
        async_sqlite_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )
    
    return factory


@pytest.fixture
async def db_session(async_session_factory) -> AsyncGenerator[AsyncSession, None]:
    """Cria uma sessão de banco de dados para cada teste."""
    async with async_session_factory() as session:
        yield session


@pytest.fixture
async def empresa_mock(db_session) -> Empresa:
    """Cria uma empresa de teste para usar nos relatórios."""
    empresa = Empresa(
        id_empresa=uuid.uuid4(),
        nome="Empresa Teste Ltda",
        cnpj="12.345.678/0001-99",
        email="contato@empresateste.com",
        telefone="(11) 3456-7890",
        ativo=True,
        data_criacao=datetime.now()
    )
    
    db_session.add(empresa)
    await db_session.commit()
    await db_session.refresh(empresa)
    
    return empresa


@pytest.fixture
async def usuario_mock(db_session, empresa_mock) -> Usuario:
    """Cria um usuário de teste."""
    usuario = Usuario(
        id_usuario=uuid.uuid4(),
        nome="Usuário Teste",
        email="usuario@teste.com",
        senha_hash="hash_senha",
        id_empresa=empresa_mock.id_empresa,
        ativo=True,
        admin=True,
        data_criacao=datetime.now()
    )
    
    db_session.add(usuario)
    await db_session.commit()
    await db_session.refresh(usuario)
    
    return usuario


@pytest.fixture
async def centro_custos(db_session, empresa_mock) -> List[CentroCusto]:
    """Cria centros de custo para testes."""
    centros = [
        CentroCusto(
            id_centro_custo=uuid.uuid4(),
            nome="Administrativo",
            descricao="Despesas administrativas",
            id_empresa=empresa_mock.id_empresa,
            ativo=True
        ),
        CentroCusto(
            id_centro_custo=uuid.uuid4(),
            nome="Comercial",
            descricao="Vendas e marketing",
            id_empresa=empresa_mock.id_empresa,
            ativo=True
        ),
        CentroCusto(
            id_centro_custo=uuid.uuid4(),
            nome="Operacional",
            descricao="Operações e produção",
            id_empresa=empresa_mock.id_empresa,
            ativo=True
        )
    ]
    
    for centro in centros:
        db_session.add(centro)
    
    await db_session.commit()
    
    for centro in centros:
        await db_session.refresh(centro)
    
    return centros


@pytest.fixture
async def contas_bancarias(db_session, empresa_mock) -> List[ContaBancaria]:
    """Cria contas bancárias para testes."""
    contas = [
        ContaBancaria(
            id_conta_bancaria=uuid.uuid4(),
            nome="Conta Principal",
            banco="Banco Teste",
            agencia="1234",
            conta="12345-6",
            tipo="corrente",
            saldo_inicial=Decimal("10000.00"),
            id_empresa=empresa_mock.id_empresa,
            ativo=True,
            data_abertura=date.today() - timedelta(days=365)
        ),
        ContaBancaria(
            id_conta_bancaria=uuid.uuid4(),
            nome="Conta Reserva",
            banco="Banco Secundário",
            agencia="5678",
            conta="56789-0",
            tipo="poupanca",
            saldo_inicial=Decimal("5000.00"),
            id_empresa=empresa_mock.id_empresa,
            ativo=True,
            data_abertura=date.today() - timedelta(days=180)
        )
    ]
    
    for conta in contas:
        db_session.add(conta)
    
    await db_session.commit()
    
    for conta in contas:
        await db_session.refresh(conta)
    
    return contas


@pytest.fixture
async def categorias(db_session, empresa_mock) -> List[Categoria]:
    """Cria categorias para testes."""
    categorias_list = [
        Categoria(
            id_categoria=uuid.uuid4(),
            nome="Vendas de Produtos",
            tipo="receita",
            id_empresa=empresa_mock.id_empresa,
            ativo=True
        ),
        Categoria(
            id_categoria=uuid.uuid4(),
            nome="Vendas de Serviços",
            tipo="receita",
            id_empresa=empresa_mock.id_empresa,
            ativo=True
        ),
        Categoria(
            id_categoria=uuid.uuid4(),
            nome="Compra de Materiais",
            tipo="despesa",
            id_empresa=empresa_mock.id_empresa,
            ativo=True
        ),
        Categoria(
            id_categoria=uuid.uuid4(),
            nome="Salários",
            tipo="despesa",
            id_empresa=empresa_mock.id_empresa,
            ativo=True
        ),
        Categoria(
            id_categoria=uuid.uuid4(),
            nome="Impostos",
            tipo="despesa",
            id_empresa=empresa_mock.id_empresa,
            ativo=True
        )
    ]
    
    for categoria in categorias_list:
        db_session.add(categoria)
    
    await db_session.commit()
    
    for categoria in categorias_list:
        await db_session.refresh(categoria)
    
    return categorias_list


@pytest.fixture
async def clientes(db_session, empresa_mock) -> List[Cliente]:
    """Cria clientes para testes."""
    clientes_list = [
        Cliente(
            id_cliente=uuid.uuid4(),
            nome="Cliente A",
            email="clientea@email.com",
            telefone="11-1111-1111",
            documento="123.456.789-00",
            id_empresa=empresa_mock.id_empresa,
            ativo=True
        ),
        Cliente(
            id_cliente=uuid.uuid4(),
            nome="Cliente B",
            email="clienteb@email.com",
            telefone="22-2222-2222",
            documento="987.654.321-00",
            id_empresa=empresa_mock.id_empresa,
            ativo=True
        ),
        Cliente(
            id_cliente=uuid.uuid4(),
            nome="Cliente C",
            email="clientec@email.com",
            telefone="33-3333-3333",
            documento="111.222.333-00",
            id_empresa=empresa_mock.id_empresa,
            ativo=True
        )
    ]
    
    for cliente in clientes_list:
        db_session.add(cliente)
    
    await db_session.commit()
    
    for cliente in clientes_list:
        await db_session.refresh(cliente)
    
    return clientes_list


@pytest.fixture
async def fornecedores(db_session, empresa_mock) -> List[Fornecedor]:
    """Cria fornecedores para testes."""
    fornecedores_list = [
        Fornecedor(
            id_fornecedor=uuid.uuid4(),
            nome="Fornecedor X",
            email="fornecedorx@email.com",
            telefone="44-4444-4444",
            documento="12.345.678/0001-00",
            id_empresa=empresa_mock.id_empresa,
            ativo=True
        ),
        Fornecedor(
            id_fornecedor=uuid.uuid4(),
            nome="Fornecedor Y",
            email="fornecedory@email.com",
            telefone="55-5555-5555",
            documento="98.765.432/0001-00",
            id_empresa=empresa_mock.id_empresa,
            ativo=True
        )
    ]
    
    for fornecedor in fornecedores_list:
        db_session.add(fornecedor)
    
    await db_session.commit()
    
    for fornecedor in fornecedores_list:
        await db_session.refresh(fornecedor)
    
    return fornecedores_list


@pytest.fixture
async def vendas(db_session, empresa_mock, clientes, categorias) -> List[Venda]:
    """Cria vendas para testes."""
    # Obter categoria de receita
    categoria_receita = next(cat for cat in categorias if cat.tipo == "receita")
    
    # Data base (um mês atrás)
    data_base = date.today() - timedelta(days=30)
    
    vendas_list = [
        Venda(
            id_venda=uuid.uuid4(),
            data_venda=data_base,
            valor_total=Decimal("1500.00"),
            descricao="Venda de produtos",
            id_cliente=clientes[0].id_cliente,
            id_categoria=categoria_receita.id_categoria,
            id_empresa=empresa_mock.id_empresa,
            status="concluida"
        ),
        Venda(
            id_venda=uuid.uuid4(),
            data_venda=data_base + timedelta(days=5),
            valor_total=Decimal("2500.00"),
            descricao="Venda de serviços",
            id_cliente=clientes[1].id_cliente,
            id_categoria=categoria_receita.id_categoria,
            id_empresa=empresa_mock.id_empresa,
            status="concluida"
        ),
        Venda(
            id_venda=uuid.uuid4(),
            data_venda=data_base + timedelta(days=15),
            valor_total=Decimal("1200.00"),
            descricao="Venda mista",
            id_cliente=clientes[2].id_cliente,
            id_categoria=categoria_receita.id_categoria,
            id_empresa=empresa_mock.id_empresa,
            status="concluida"
        ),
        Venda(
            id_venda=uuid.uuid4(),
            data_venda=data_base + timedelta(days=25),
            valor_total=Decimal("1800.00"),
            descricao="Venda especial",
            id_cliente=clientes[0].id_cliente,
            id_categoria=categoria_receita.id_categoria,
            id_empresa=empresa_mock.id_empresa,
            status="concluida"
        )
    ]
    
    for venda in vendas_list:
        db_session.add(venda)
    
    await db_session.commit()
    
    for venda in vendas_list:
        await db_session.refresh(venda)
    
    return vendas_list


@pytest.fixture
async def compras(db_session, empresa_mock, fornecedores, categorias) -> List[Compra]:
    """Cria compras para testes."""
    # Obter categoria de despesa
    categoria_despesa = next(cat for cat in categorias if cat.tipo == "despesa")
    
    # Data base (um mês atrás)
    data_base = date.today() - timedelta(days=30)
    
    compras_list = [
        Compra(
            id_compra=uuid.uuid4(),
            data_compra=data_base + timedelta(days=2),
            valor_total=Decimal("800.00"),
            descricao="Compra de materiais",
            id_fornecedor=fornecedores[0].id_fornecedor,
            id_categoria=categoria_despesa.id_categoria,
            id_empresa=empresa_mock.id_empresa,
            status="concluida"
        ),
        Compra(
            id_compra=uuid.uuid4(),
            data_compra=data_base + timedelta(days=10),
            valor_total=Decimal("1200.00"),
            descricao="Compra de equipamentos",
            id_fornecedor=fornecedores[1].id_fornecedor,
            id_categoria=categoria_despesa.id_categoria,
            id_empresa=empresa_mock.id_empresa,
            status="concluida"
        ),
        Compra(
            id_compra=uuid.uuid4(),
            data_compra=data_base + timedelta(days=20),
            valor_total=Decimal("950.00"),
            descricao="Compra de insumos",
            id_fornecedor=fornecedores[0].id_fornecedor,
            id_categoria=categoria_despesa.id_categoria,
            id_empresa=empresa_mock.id_empresa,
            status="concluida"
        )
    ]
    
    for compra in compras_list:
        db_session.add(compra)
    
    await db_session.commit()
    
    for compra in compras_list:
        await db_session.refresh(compra)
    
    return compras_list


@pytest.fixture
async def contas_receber(db_session, empresa_mock, clientes, vendas) -> List[ContaReceber]:
    """Cria contas a receber para testes."""
    contas_list = []
    
    # Para cada venda, criar uma conta a receber
    for i, venda in enumerate(vendas):
        # Algumas contas já recebidas, outras pendentes
        status = "recebido" if i % 2 == 0 else "pendente"
        data_recebimento = date.today() - timedelta(days=5) if status == "recebido" else None
        
        conta = ContaReceber(
            id_conta_receber=uuid.uuid4(),
            descricao=f"Recebimento - {venda.descricao}",
            valor=venda.valor_total,
            data_emissao=venda.data_venda,
            data_vencimento=venda.data_venda + timedelta(days=30),
            data_recebimento=data_recebimento,
            id_cliente=venda.id_cliente,
            id_venda=venda.id_venda,
            id_empresa=empresa_mock.id_empresa,
            status=status
        )
        
        contas_list.append(conta)
        db_session.add(conta)
    
    # Adicionar uma conta atrasada para teste de juros
    conta_atrasada = ContaReceber(
        id_conta_receber=uuid.uuid4(),
        descricao="Conta atrasada para teste de juros",
        valor=Decimal("2000.00"),
        data_emissao=date.today() - timedelta(days=60),
        data_vencimento=date.today() - timedelta(days=30),
        data_recebimento=None,
        id_cliente=clientes[0].id_cliente,
        id_venda=None,
        id_empresa=empresa_mock.id_empresa,
        status="atrasado"
    )
    
    contas_list.append(conta_atrasada)
    db_session.add(conta_atrasada)
    
    await db_session.commit()
    
    for conta in contas_list:
        await db_session.refresh(conta)
    
    return contas_list


@pytest.fixture
async def contas_pagar(db_session, empresa_mock, fornecedores, compras, categorias) -> List[ContaPagar]:
    """Cria contas a pagar para testes."""
    contas_list = []
    
    # Obter categoria de despesa
    categoria_salarios = next((cat for cat in categorias if cat.nome == "Salários"), categorias[2])
    
    # Para cada compra, criar uma conta a pagar
    for i, compra in enumerate(compras):
        # Algumas contas já pagas, outras pendentes
        status = "pago" if i % 2 == 0 else "pendente"
        data_pagamento = date.today() - timedelta(days=3) if status == "pago" else None
        
        conta = ContaPagar(
            id_conta_pagar=uuid.uuid4(),
            descricao=f"Pagamento - {compra.descricao}",
            valor=compra.valor_total,
            data_emissao=compra.data_compra,
            data_vencimento=compra.data_compra + timedelta(days=15),
            data_pagamento=data_pagamento,
            id_fornecedor=compra.id_fornecedor,
            id_compra=compra.id_compra,
            id_empresa=empresa_mock.id_empresa,
            status=status
        )
        
        contas_list.append(conta)
        db_session.add(conta)
    
    # Adicionar uma conta de salário
    conta_salario = ContaPagar(
        id_conta_pagar=uuid.uuid4(),
        descricao="Pagamento de salários",
        valor=Decimal("5000.00"),
        data_emissao=date.today() - timedelta(days=10),
        data_vencimento=date.today() + timedelta(days=5),
        data_pagamento=None,
        id_fornecedor=None,
        id_compra=None,
        id_categoria=categoria_salarios.id_categoria,
        id_empresa=empresa_mock.id_empresa,
        status="pendente"
    )
    
    contas_list.append(conta_salario)
    db_session.add(conta_salario)
    
    # Adicionar uma conta atrasada para teste de juros
    conta_atrasada = ContaPagar(
        id_conta_pagar=uuid.uuid4(),
        descricao="Fornecedor atrasado para teste de juros",
        valor=Decimal("1500.00"),
        data_emissao=date.today() - timedelta(days=45),
        data_vencimento=date.today() - timedelta(days=15),
        data_pagamento=None,
        id_fornecedor=fornecedores[0].id_fornecedor,
        id_compra=None,
        id_empresa=empresa_mock.id_empresa,
        status="atrasado"
    )
    
    contas_list.append(conta_atrasada)
    db_session.add(conta_atrasada)
    
    await db_session.commit()
    
    for conta in contas_list:
        await db_session.refresh(conta)
    
    return contas_list


@pytest.fixture
async def parcelas(db_session, empresa_mock, vendas, compras) -> List[Parcela]:
    """Cria parcelas para teste."""
    parcelas_list = []
    
    # Data base
    data_base = date.today() - timedelta(days=30)
    
    # Criar parcelas para algumas vendas
    for i, venda in enumerate(vendas[:2]):
        # Dividir em 3 parcelas
        valor_parcela = venda.valor_total / 3
        
        for j in range(3):
            status = "pago" if j == 0 else ("atrasado" if j == 1 and i == 0 else "pendente")
            data_pagamento = data_base + timedelta(days=j*30) if status == "pago" else None
            data_vencimento = data_base + timedelta(days=j*30 + 30)
            
            parcela = Parcela(
                id_parcela=uuid.uuid4(),
                numero=j+1,
                valor=valor_parcela,
                data_vencimento=data_vencimento,
                data_pagamento=data_pagamento,
                id_venda=venda.id_venda,
                id_empresa=empresa_mock.id_empresa,
                status=status
            )
            
            parcelas_list.append(parcela)
            db_session.add(parcela)
    
    # Criar parcelas para algumas compras
    for compra in compras[:1]:
        # Dividir em 2 parcelas
        valor_parcela = compra.valor_total / 2
        
        for j in range(2):
            status = "pago" if j == 0 else "pendente"
            data_pagamento = data_base + timedelta(days=j*15) if status == "pago" else None
            data_vencimento = data_base + timedelta(days=j*15 + 15)
            
            parcela = Parcela(
                id_parcela=uuid.uuid4(),
                numero=j+1,
                valor=valor_parcela,
                data_vencimento=data_vencimento,
                data_pagamento=data_pagamento,
                id_compra=compra.id_compra,
                id_empresa=empresa_mock.id_empresa,
                status=status
            )
            
            parcelas_list.append(parcela)
            db_session.add(parcela)
    
    await db_session.commit()
    
    for parcela in parcelas_list:
        await db_session.refresh(parcela)
    
    return parcelas_list


@pytest.fixture
async def lancamentos(db_session, empresa_mock, centro_custos, contas_bancarias, categorias) -> List[Lancamento]:
    """Cria lançamentos para testes."""
    lancamentos_list = []
    
    # Conta principal
    conta_principal = contas_bancarias[0]
    
    # Obter categorias
    cat_receita = next(cat for cat in categorias if cat.tipo == "receita")
    cat_despesa = next(cat for cat in categorias if cat.tipo == "despesa")
    
    # Data base (um mês atrás)
    data_base = date.today() - timedelta(days=30)
    
    # Criar lançamentos de receita e despesa
    for i in range(10):
        tipo = "receita" if i % 2 == 0 else "despesa"
        categoria = cat_receita if tipo == "receita" else cat_despesa
        centro_custo = centro_custos[i % len(centro_custos)]
        
        # Valores variam para criar diversidade
        valor = Decimal(f"{500 + i * 100}.{i * 10}")
        
        lancamento = Lancamento(
            id_lancamento=uuid.uuid4(),
            descricao=f"Lançamento de {tipo} #{i+1}",
            valor=valor,
            tipo=tipo,
            data_lancamento=data_base + timedelta(days=i*3),
            id_conta_bancaria=conta_principal.id_conta_bancaria,
            id_categoria=categoria.id_categoria,
            id_centro_custo=centro_custo.id_centro_custo,
            id_empresa=empresa_mock.id_empresa
        )
        
        lancamentos_list.append(lancamento)
        db_session.add(lancamento)
    
    await db_session.commit()
    
    for lancamento in lancamentos_list:
        await db_session.refresh(lancamento)
    
    return lancamentos_list


@pytest.fixture
def periodo_relatorio():
    """Define o período para o relatório."""
    data_inicio = date.today() - timedelta(days=60)
    data_fim = date.today() + timedelta(days=30)
    return {
        "data_inicio": data_inicio,
        "data_fim": data_fim
    }


@pytest.fixture
async def dados_completos(
    db_session, 
    empresa_mock, 
    usuario_mock, 
    centro_custos, 
    contas_bancarias,
    categorias,
    clientes,
    fornecedores,
    vendas,
    compras,
    contas_receber,
    contas_pagar,
    parcelas,
    lancamentos,
    periodo_relatorio
):
    """Fixture que combina todos os dados para os testes."""
    return {
        "empresa": empresa_mock,
        "usuario": usuario_mock,
        "centro_custos": centro_custos,
        "contas_bancarias": contas_bancarias,
        "categorias": categorias,
        "clientes": clientes,
        "fornecedores": fornecedores,
        "vendas": vendas,
        "compras": compras,
        "contas_receber": contas_receber,
        "contas_pagar": contas_pagar,
        "parcelas": parcelas,
        "lancamentos": lancamentos,
        "periodo": periodo_relatorio
    } 