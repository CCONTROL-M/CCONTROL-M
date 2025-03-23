"""Testes para o serviço de lançamentos."""
import pytest
from uuid import uuid4
from typing import Callable, AsyncGenerator
from datetime import datetime, date, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.lancamento import Lancamento
from app.models.categoria import Categoria
from app.models.conta_bancaria import ContaBancaria
from app.schemas.lancamento import LancamentoCreate, LancamentoUpdate, TipoLancamento
from app.services.lancamento_service import LancamentoService

# Fixtures - definição de dados para testes
@pytest.fixture
async def categoria(session: AsyncSession) -> Categoria:
    """Cria uma categoria para testes."""
    # Criar uma categoria diretamente no banco
    categoria = Categoria(
        id=uuid4(),
        empresa_id=uuid4(),
        nome="Categoria Teste",
        descricao="Categoria para testes",
        tipo="receita",
        ativo=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    session.add(categoria)
    await session.commit()
    await session.refresh(categoria)
    
    return categoria

@pytest.fixture
async def conta_bancaria(session: AsyncSession) -> ContaBancaria:
    """Cria uma conta bancária para testes."""
    # Criar uma conta bancária diretamente no banco
    conta = ContaBancaria(
        id=uuid4(),
        empresa_id=uuid4(),
        nome="Conta Teste",
        banco="Banco Teste",
        agencia="1234",
        numero="12345-6",
        tipo="corrente",
        saldo_inicial=Decimal("1000.00"),
        saldo_atual=Decimal("1000.00"),
        ativa=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    session.add(conta)
    await session.commit()
    await session.refresh(conta)
    
    return conta

@pytest.fixture
async def lancamento(session: AsyncSession, categoria: Categoria, conta_bancaria: ContaBancaria) -> Lancamento:
    """Cria um lançamento para testes."""
    # Criar um lançamento diretamente no banco
    lancamento = Lancamento(
        id=uuid4(),
        empresa_id=categoria.empresa_id,
        descricao="Lançamento Teste",
        valor=Decimal("100.00"),
        data=date.today(),
        tipo=TipoLancamento.receita,
        categoria_id=categoria.id,
        conta_id=conta_bancaria.id,
        observacao="Lançamento para testes",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    session.add(lancamento)
    await session.commit()
    await session.refresh(lancamento)
    
    return lancamento

@pytest.fixture
async def lancamento_factory(session: AsyncSession) -> Callable[..., AsyncGenerator[Lancamento, None]]:
    """Factory para criar lançamentos com parâmetros customizados."""
    async def _create_lancamento(**kwargs) -> Lancamento:
        default_empresa_id = uuid4()  # Geramos um UUID para empresa
        
        # Se não for fornecido categoria_id, criamos uma categoria
        if "categoria_id" not in kwargs:
            categoria = Categoria(
                id=uuid4(),
                empresa_id=kwargs.get("empresa_id", default_empresa_id),
                nome="Categoria Auto",
                descricao="Categoria automática para testes",
                tipo=kwargs.get("tipo", TipoLancamento.receita),
                ativo=True
            )
            session.add(categoria)
            await session.commit()
            await session.refresh(categoria)
            categoria_id = categoria.id
        else:
            categoria_id = kwargs["categoria_id"]
            
        # Se não for fornecido conta_id, criamos uma conta
        if "conta_id" not in kwargs:
            conta = ContaBancaria(
                id=uuid4(),
                empresa_id=kwargs.get("empresa_id", default_empresa_id),
                nome="Conta Auto",
                banco="Banco Auto",
                agencia="1234",
                numero="12345-6",
                tipo="corrente",
                saldo_inicial=Decimal("1000.00"),
                saldo_atual=Decimal("1000.00"),
                ativa=True
            )
            session.add(conta)
            await session.commit()
            await session.refresh(conta)
            conta_id = conta.id
        else:
            conta_id = kwargs["conta_id"]
        
        # Valores padrão para testes
        defaults = {
            "id": uuid4(),
            "empresa_id": default_empresa_id,
            "descricao": f"Lançamento {uuid4().hex[:8]}",
            "valor": Decimal("100.00"),
            "data": date.today(),
            "tipo": TipoLancamento.receita,
            "categoria_id": categoria_id,
            "conta_id": conta_id,
            "observacao": "Lançamento automático para testes",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Sobrescrever valores padrão com valores fornecidos
        defaults.update(kwargs)
        
        lancamento = Lancamento(**defaults)
        session.add(lancamento)
        await session.commit()
        await session.refresh(lancamento)
        
        return lancamento
    
    return _create_lancamento

@pytest.fixture
async def lancamentos_lista(session: AsyncSession, lancamento_factory) -> list[Lancamento]:
    """Cria uma lista de lançamentos para testes."""
    # ID da empresa comum para todos os lançamentos
    empresa_id = uuid4()
    
    # Criar categorias
    categoria_receita = Categoria(
        id=uuid4(),
        empresa_id=empresa_id,
        nome="Receita",
        descricao="Categoria de receita",
        tipo="receita",
        ativo=True
    )
    
    categoria_despesa = Categoria(
        id=uuid4(),
        empresa_id=empresa_id,
        nome="Despesa",
        descricao="Categoria de despesa",
        tipo="despesa",
        ativo=True
    )
    
    session.add(categoria_receita)
    session.add(categoria_despesa)
    await session.commit()
    await session.refresh(categoria_receita)
    await session.refresh(categoria_despesa)
    
    # Criar conta bancária
    conta = ContaBancaria(
        id=uuid4(),
        empresa_id=empresa_id,
        nome="Conta Teste",
        banco="Banco Teste",
        agencia="1234",
        numero="12345-6",
        tipo="corrente",
        saldo_inicial=Decimal("1000.00"),
        saldo_atual=Decimal("1000.00"),
        ativa=True
    )
    
    session.add(conta)
    await session.commit()
    await session.refresh(conta)
    
    # Criar 5 lançamentos (3 receitas, 2 despesas)
    lancamentos = []
    
    hoje = date.today()
    
    # Receitas
    for i in range(3):
        lancamento = await lancamento_factory(
            empresa_id=empresa_id,
            descricao=f"Receita {i+1}",
            valor=Decimal(f"{(i+1)*100}.00"),
            data=hoje - timedelta(days=i),
            tipo=TipoLancamento.receita,
            categoria_id=categoria_receita.id,
            conta_id=conta.id
        )
        lancamentos.append(lancamento)
    
    # Despesas
    for i in range(2):
        lancamento = await lancamento_factory(
            empresa_id=empresa_id,
            descricao=f"Despesa {i+1}",
            valor=Decimal(f"{(i+1)*50}.00"),
            data=hoje - timedelta(days=i+3),
            tipo=TipoLancamento.despesa,
            categoria_id=categoria_despesa.id,
            conta_id=conta.id
        )
        lancamentos.append(lancamento)
    
    return lancamentos


# Testes do serviço de lançamentos
@pytest.mark.asyncio
async def test_criar_lancamento(session: AsyncSession, categoria: Categoria, conta_bancaria: ContaBancaria):
    """Teste de criação de lançamento."""
    # Arrange
    service = LancamentoService(session)
    
    dados_lancamento = {
        "empresa_id": categoria.empresa_id,
        "descricao": "Novo Lançamento",
        "valor": Decimal("150.00"),
        "data": date.today(),
        "tipo": TipoLancamento.receita,
        "categoria_id": categoria.id,
        "conta_id": conta_bancaria.id,
        "observacao": "Novo lançamento para teste"
    }
    
    lancamento_create = LancamentoCreate(**dados_lancamento)
    
    # Act
    lancamento = await service.create(lancamento_create)
    
    # Assert
    assert lancamento is not None
    assert lancamento.id is not None
    assert lancamento.descricao == "Novo Lançamento"
    assert lancamento.valor == Decimal("150.00")
    assert lancamento.tipo == TipoLancamento.receita
    assert lancamento.empresa_id == categoria.empresa_id
    assert lancamento.categoria_id == categoria.id
    assert lancamento.conta_id == conta_bancaria.id


@pytest.mark.asyncio
async def test_buscar_lancamento(session: AsyncSession, lancamento: Lancamento):
    """Teste de busca de lançamento pelo ID."""
    # Arrange
    service = LancamentoService(session)
    
    # Act
    result = await service.get(lancamento.id)
    
    # Assert
    assert result is not None
    assert result.id == lancamento.id
    assert result.descricao == lancamento.descricao
    assert result.valor == lancamento.valor
    assert result.tipo == lancamento.tipo


@pytest.mark.asyncio
async def test_listar_lancamentos(session: AsyncSession, lancamentos_lista: list[Lancamento]):
    """Teste de listagem de lançamentos."""
    # Arrange
    service = LancamentoService(session)
    empresa_id = lancamentos_lista[0].empresa_id
    
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
async def test_listar_lancamentos_por_tipo(session: AsyncSession, lancamentos_lista: list[Lancamento]):
    """Teste de listagem de lançamentos por tipo."""
    # Arrange
    service = LancamentoService(session)
    empresa_id = lancamentos_lista[0].empresa_id
    
    # Act - Buscar apenas receitas
    result_receitas, total_receitas = await service.list(
        empresa_id=empresa_id,
        tipo=TipoLancamento.receita,
        skip=0,
        limit=10
    )
    
    # Act - Buscar apenas despesas
    result_despesas, total_despesas = await service.list(
        empresa_id=empresa_id,
        tipo=TipoLancamento.despesa,
        skip=0,
        limit=10
    )
    
    # Assert
    assert len(result_receitas) == 3
    assert total_receitas == 3
    assert all(l.tipo == TipoLancamento.receita for l in result_receitas)
    
    assert len(result_despesas) == 2
    assert total_despesas == 2
    assert all(l.tipo == TipoLancamento.despesa for l in result_despesas)


@pytest.mark.asyncio
async def test_listar_lancamentos_por_periodo(session: AsyncSession, lancamentos_lista: list[Lancamento]):
    """Teste de listagem de lançamentos por período."""
    # Arrange
    service = LancamentoService(session)
    empresa_id = lancamentos_lista[0].empresa_id
    
    hoje = date.today()
    data_inicio = hoje - timedelta(days=2)
    data_fim = hoje
    
    # Act
    result, total = await service.list(
        empresa_id=empresa_id,
        data_inicio=data_inicio,
        data_fim=data_fim,
        skip=0,
        limit=10
    )
    
    # Assert
    assert len(result) == 3
    assert total == 3
    assert all(data_inicio <= l.data <= data_fim for l in result)


@pytest.mark.asyncio
async def test_atualizar_lancamento(session: AsyncSession, lancamento: Lancamento):
    """Teste de atualização de lançamento."""
    # Arrange
    service = LancamentoService(session)
    
    dados_atualizacao = {
        "descricao": "Lançamento Atualizado",
        "valor": Decimal("200.00"),
        "observacao": "Lançamento atualizado para teste"
    }
    
    lancamento_update = LancamentoUpdate(**dados_atualizacao)
    
    # Act
    result = await service.update(
        id_lancamento=lancamento.id,
        lancamento=lancamento_update
    )
    
    # Assert
    assert result is not None
    assert result.id == lancamento.id
    assert result.descricao == "Lançamento Atualizado"
    assert result.valor == Decimal("200.00")
    assert result.observacao == "Lançamento atualizado para teste"


@pytest.mark.asyncio
async def test_excluir_lancamento(session: AsyncSession, lancamento: Lancamento):
    """Teste de exclusão de lançamento."""
    # Arrange
    service = LancamentoService(session)
    
    # Act
    result = await service.delete(lancamento.id)
    
    # Assert
    assert result is True
    
    # Verificar se foi realmente excluído
    resultado = await service.get(lancamento.id)
    assert resultado is None


@pytest.mark.asyncio
async def test_erro_ao_buscar_lancamento_inexistente(session: AsyncSession):
    """Teste de erro ao buscar lançamento inexistente."""
    # Arrange
    service = LancamentoService(session)
    id_inexistente = uuid4()
    
    # Act
    result = await service.get(id_inexistente)
    
    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_erro_ao_atualizar_lancamento_inexistente(session: AsyncSession):
    """Teste de erro ao atualizar lançamento inexistente."""
    # Arrange
    service = LancamentoService(session)
    id_inexistente = uuid4()
    
    dados_atualizacao = {
        "descricao": "Lançamento Inexistente",
        "valor": Decimal("300.00")
    }
    
    lancamento_update = LancamentoUpdate(**dados_atualizacao)
    
    # Act e Assert
    with pytest.raises(HTTPException) as exc_info:
        await service.update(
            id_lancamento=id_inexistente,
            lancamento=lancamento_update
        )
    
    assert exc_info.value.status_code == 404
    assert "Lançamento não encontrado" in str(exc_info.value.detail) 