"""Testes para o serviço de parcelas."""
import pytest
from uuid import uuid4
from typing import Callable, AsyncGenerator
from datetime import datetime, date, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.parcela import Parcela
from app.models.venda import Venda
from app.models.cliente import Cliente
from app.models.conta_bancaria import ContaBancaria
from app.schemas.parcela import ParcelaCreate, ParcelaUpdate, StatusParcela
from app.services.parcela_service import ParcelaService

# Fixtures - definição de dados para testes
@pytest.fixture
async def cliente(session: AsyncSession) -> Cliente:
    """Cria um cliente para testes."""
    # Criar um cliente diretamente no banco
    cliente = Cliente(
        id=uuid4(),
        empresa_id=uuid4(),
        nome="Cliente Teste",
        email="cliente@teste.com",
        telefone="1199999999",
        cpf_cnpj="12345678901",
        endereco="Rua de Teste, 123",
        cidade="São Paulo",
        estado="SP",
        cep="01234567",
        observacoes="Cliente para testes",
        ativo=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    session.add(cliente)
    await session.commit()
    await session.refresh(cliente)
    
    return cliente

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
async def venda(session: AsyncSession, cliente: Cliente) -> Venda:
    """Cria uma venda para testes."""
    # Criar uma venda diretamente no banco
    venda = Venda(
        id=uuid4(),
        empresa_id=cliente.empresa_id,
        cliente_id=cliente.id,
        usuario_id=uuid4(),
        data=date.today(),
        valor_total=Decimal("1000.00"),
        desconto=Decimal("100.00"),
        valor_final=Decimal("900.00"),
        status="aberta",
        forma_pagamento="parcelado",
        parcelas=3,
        observacao="Venda para testes",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    session.add(venda)
    await session.commit()
    await session.refresh(venda)
    
    return venda

@pytest.fixture
async def parcela(session: AsyncSession, venda: Venda, conta_bancaria: ContaBancaria) -> Parcela:
    """Cria uma parcela para testes."""
    # Criar uma parcela diretamente no banco
    parcela = Parcela(
        id=uuid4(),
        empresa_id=venda.empresa_id,
        venda_id=venda.id,
        numero=1,
        valor=Decimal("300.00"),
        data_vencimento=date.today() + timedelta(days=30),
        data_pagamento=None,
        status=StatusParcela.pendente,
        forma_pagamento="credito",
        conta_id=conta_bancaria.id,
        observacao="Parcela 1 de 3",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    session.add(parcela)
    await session.commit()
    await session.refresh(parcela)
    
    return parcela

@pytest.fixture
async def parcela_factory(session: AsyncSession) -> Callable[..., AsyncGenerator[Parcela, None]]:
    """Factory para criar parcelas com parâmetros customizados."""
    async def _create_parcela(**kwargs) -> Parcela:
        default_empresa_id = uuid4()  # Geramos um UUID para empresa
        
        # Se não for fornecido venda_id, criamos uma venda
        if "venda_id" not in kwargs:
            # Criar um cliente se não existir
            if "cliente_id" not in kwargs:
                cliente = Cliente(
                    id=uuid4(),
                    empresa_id=kwargs.get("empresa_id", default_empresa_id),
                    nome="Cliente Auto",
                    email="cliente.auto@teste.com",
                    ativo=True
                )
                session.add(cliente)
                await session.commit()
                await session.refresh(cliente)
                cliente_id = cliente.id
            else:
                cliente_id = kwargs["cliente_id"]
            
            # Criar a venda
            venda = Venda(
                id=uuid4(),
                empresa_id=kwargs.get("empresa_id", default_empresa_id),
                cliente_id=cliente_id,
                usuario_id=uuid4(),
                data=date.today(),
                valor_total=Decimal("1000.00"),
                desconto=Decimal("100.00"),
                valor_final=Decimal("900.00"),
                status="aberta",
                forma_pagamento="parcelado",
                parcelas=3
            )
            session.add(venda)
            await session.commit()
            await session.refresh(venda)
            venda_id = venda.id
        else:
            venda_id = kwargs["venda_id"]
            
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
            "empresa_id": kwargs.get("empresa_id", default_empresa_id),
            "venda_id": venda_id,
            "numero": kwargs.get("numero", 1),
            "valor": Decimal("300.00"),
            "data_vencimento": date.today() + timedelta(days=30),
            "data_pagamento": None,
            "status": StatusParcela.pendente,
            "forma_pagamento": "credito",
            "conta_id": conta_id,
            "observacao": f"Parcela {kwargs.get('numero', 1)}",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Sobrescrever valores padrão com valores fornecidos
        defaults.update(kwargs)
        
        parcela = Parcela(**defaults)
        session.add(parcela)
        await session.commit()
        await session.refresh(parcela)
        
        return parcela
    
    return _create_parcela

@pytest.fixture
async def parcelas_lista(session: AsyncSession, venda: Venda, conta_bancaria: ContaBancaria) -> list[Parcela]:
    """Cria uma lista de parcelas para testes."""
    
    # Criar 3 parcelas
    parcelas = []
    
    for i in range(3):
        parcela = Parcela(
            id=uuid4(),
            empresa_id=venda.empresa_id,
            venda_id=venda.id,
            numero=i+1,
            valor=Decimal("300.00"),
            data_vencimento=date.today() + timedelta(days=(i+1)*30),
            data_pagamento=None if i > 0 else date.today(),
            status=StatusParcela.paga if i == 0 else StatusParcela.pendente,
            forma_pagamento="credito",
            conta_id=conta_bancaria.id,
            observacao=f"Parcela {i+1} de 3",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        session.add(parcela)
        await session.commit()
        await session.refresh(parcela)
        
        parcelas.append(parcela)
    
    return parcelas


# Testes do serviço de parcelas
@pytest.mark.asyncio
async def test_criar_parcela(session: AsyncSession, venda: Venda, conta_bancaria: ContaBancaria):
    """Teste de criação de parcela."""
    # Arrange
    service = ParcelaService(session)
    
    dados_parcela = {
        "empresa_id": venda.empresa_id,
        "venda_id": venda.id,
        "numero": 1,
        "valor": Decimal("300.00"),
        "data_vencimento": date.today() + timedelta(days=30),
        "forma_pagamento": "credito",
        "conta_id": conta_bancaria.id,
        "observacao": "Parcela 1 de 3"
    }
    
    parcela_create = ParcelaCreate(**dados_parcela)
    
    # Act
    parcela = await service.create(parcela_create)
    
    # Assert
    assert parcela is not None
    assert parcela.id is not None
    assert parcela.venda_id == venda.id
    assert parcela.numero == 1
    assert parcela.valor == Decimal("300.00")
    assert parcela.data_vencimento == date.today() + timedelta(days=30)
    assert parcela.status == StatusParcela.pendente
    assert parcela.forma_pagamento == "credito"


@pytest.mark.asyncio
async def test_buscar_parcela(session: AsyncSession, parcela: Parcela):
    """Teste de busca de parcela pelo ID."""
    # Arrange
    service = ParcelaService(session)
    
    # Act
    result = await service.get(parcela.id)
    
    # Assert
    assert result is not None
    assert result.id == parcela.id
    assert result.venda_id == parcela.venda_id
    assert result.numero == parcela.numero
    assert result.valor == parcela.valor


@pytest.mark.asyncio
async def test_listar_parcelas_por_venda(session: AsyncSession, parcelas_lista: list[Parcela]):
    """Teste de listagem de parcelas por venda."""
    # Arrange
    service = ParcelaService(session)
    venda_id = parcelas_lista[0].venda_id
    
    # Act
    result, total = await service.list_by_venda(
        venda_id=venda_id,
        skip=0,
        limit=10
    )
    
    # Assert
    assert len(result) == 3
    assert total == 3
    assert all(p.venda_id == venda_id for p in result)


@pytest.mark.asyncio
async def test_listar_parcelas_por_empresa(session: AsyncSession, parcelas_lista: list[Parcela]):
    """Teste de listagem de parcelas por empresa."""
    # Arrange
    service = ParcelaService(session)
    empresa_id = parcelas_lista[0].empresa_id
    
    # Act
    result, total = await service.list(
        empresa_id=empresa_id,
        skip=0,
        limit=10
    )
    
    # Assert
    assert len(result) == 3
    assert total == 3
    assert all(p.empresa_id == empresa_id for p in result)


@pytest.mark.asyncio
async def test_listar_parcelas_por_status(session: AsyncSession, parcelas_lista: list[Parcela]):
    """Teste de listagem de parcelas por status."""
    # Arrange
    service = ParcelaService(session)
    empresa_id = parcelas_lista[0].empresa_id
    
    # Act - Buscar parcelas pendentes
    result_pendentes, total_pendentes = await service.list(
        empresa_id=empresa_id,
        status=StatusParcela.pendente,
        skip=0,
        limit=10
    )
    
    # Act - Buscar parcelas pagas
    result_pagas, total_pagas = await service.list(
        empresa_id=empresa_id,
        status=StatusParcela.paga,
        skip=0,
        limit=10
    )
    
    # Assert
    assert len(result_pendentes) == 2
    assert total_pendentes == 2
    assert all(p.status == StatusParcela.pendente for p in result_pendentes)
    
    assert len(result_pagas) == 1
    assert total_pagas == 1
    assert all(p.status == StatusParcela.paga for p in result_pagas)


@pytest.mark.asyncio
async def test_listar_parcelas_por_periodo(session: AsyncSession, parcelas_lista: list[Parcela]):
    """Teste de listagem de parcelas por período de vencimento."""
    # Arrange
    service = ParcelaService(session)
    empresa_id = parcelas_lista[0].empresa_id
    
    hoje = date.today()
    data_inicio = hoje
    data_fim = hoje + timedelta(days=60)
    
    # Act
    result, total = await service.list(
        empresa_id=empresa_id,
        data_inicio=data_inicio,
        data_fim=data_fim,
        skip=0,
        limit=10
    )
    
    # Assert
    assert len(result) == 2  # As duas primeiras parcelas vencem dentro do período
    assert total == 2
    assert all(data_inicio <= p.data_vencimento <= data_fim for p in result)


@pytest.mark.asyncio
async def test_atualizar_parcela(session: AsyncSession, parcela: Parcela):
    """Teste de atualização de parcela."""
    # Arrange
    service = ParcelaService(session)
    
    dados_atualizacao = {
        "valor": Decimal("350.00"),
        "data_vencimento": date.today() + timedelta(days=45),
        "observacao": "Parcela atualizada para teste"
    }
    
    parcela_update = ParcelaUpdate(**dados_atualizacao)
    
    # Act
    result = await service.update(
        id_parcela=parcela.id,
        parcela=parcela_update
    )
    
    # Assert
    assert result is not None
    assert result.id == parcela.id
    assert result.valor == Decimal("350.00")
    assert result.data_vencimento == date.today() + timedelta(days=45)
    assert result.observacao == "Parcela atualizada para teste"


@pytest.mark.asyncio
async def test_registrar_pagamento(session: AsyncSession, parcela: Parcela):
    """Teste de registro de pagamento de parcela."""
    # Arrange
    service = ParcelaService(session)
    
    data_pagamento = date.today()
    
    # Act
    result = await service.registrar_pagamento(
        id_parcela=parcela.id,
        data_pagamento=data_pagamento,
        conta_id=parcela.conta_id
    )
    
    # Assert
    assert result is not None
    assert result.id == parcela.id
    assert result.status == StatusParcela.paga
    assert result.data_pagamento == data_pagamento


@pytest.mark.asyncio
async def test_cancelar_pagamento(session: AsyncSession, parcela_factory):
    """Teste de cancelamento de pagamento de parcela."""
    # Arrange
    service = ParcelaService(session)
    
    # Criar uma parcela já paga
    parcela = await parcela_factory(
        status=StatusParcela.paga,
        data_pagamento=date.today()
    )
    
    # Act
    result = await service.cancelar_pagamento(
        id_parcela=parcela.id
    )
    
    # Assert
    assert result is not None
    assert result.id == parcela.id
    assert result.status == StatusParcela.pendente
    assert result.data_pagamento is None


@pytest.mark.asyncio
async def test_erro_ao_buscar_parcela_inexistente(session: AsyncSession):
    """Teste de erro ao buscar parcela inexistente."""
    # Arrange
    service = ParcelaService(session)
    id_inexistente = uuid4()
    
    # Act
    result = await service.get(id_inexistente)
    
    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_erro_ao_atualizar_parcela_inexistente(session: AsyncSession):
    """Teste de erro ao atualizar parcela inexistente."""
    # Arrange
    service = ParcelaService(session)
    id_inexistente = uuid4()
    
    dados_atualizacao = {
        "valor": Decimal("400.00"),
        "observacao": "Parcela inexistente"
    }
    
    parcela_update = ParcelaUpdate(**dados_atualizacao)
    
    # Act e Assert
    with pytest.raises(HTTPException) as exc_info:
        await service.update(
            id_parcela=id_inexistente,
            parcela=parcela_update
        )
    
    assert exc_info.value.status_code == 404
    assert "Parcela não encontrada" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_erro_ao_registrar_pagamento_parcela_inexistente(session: AsyncSession):
    """Teste de erro ao registrar pagamento em parcela inexistente."""
    # Arrange
    service = ParcelaService(session)
    id_inexistente = uuid4()
    
    # Act e Assert
    with pytest.raises(HTTPException) as exc_info:
        await service.registrar_pagamento(
            id_parcela=id_inexistente,
            data_pagamento=date.today(),
            conta_id=uuid4()
        )
    
    assert exc_info.value.status_code == 404
    assert "Parcela não encontrada" in str(exc_info.value.detail) 