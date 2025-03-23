"""Testes para o serviço de clientes."""
import pytest
from uuid import uuid4
from typing import Callable, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.cliente import Cliente
from app.models.empresa import Empresa
from app.models.usuario import Usuario
from app.schemas.cliente import ClienteCreate, ClienteUpdate
from app.services.cliente_service import ClienteService
from app.services.auditoria_service import AuditoriaService

from tests.fixtures.cliente import cliente, cliente_factory, clientes_lista
from tests.fixtures.empresa import empresa, empresas_lista
from tests.fixtures.usuario import usuario


@pytest.mark.asyncio
async def test_criar_cliente(
    session: AsyncSession,
    cliente_factory: Callable[..., AsyncGenerator[Cliente, None]],
    empresa: Empresa,
    usuario: Usuario
):
    """Teste de criação de cliente."""
    # Arrange
    nome = "Cliente Teste"
    email = "cliente@teste.com"
    telefone = "(11) 99999-9999"
    cpf_cnpj = "123.456.789-00"
    
    # Act
    cliente = await cliente_factory(
        empresa=empresa,
        usuario_id=str(usuario.id_usuario),
        nome=nome,
        email=email,
        telefone=telefone,
        cpf_cnpj=cpf_cnpj
    )
    
    # Assert
    assert cliente.id_cliente is not None
    assert cliente.empresa_id == empresa.id_empresa
    assert cliente.usuario_id == usuario.id_usuario
    assert cliente.nome == nome
    assert cliente.email == email
    assert cliente.telefone == telefone
    assert cliente.cpf_cnpj == cpf_cnpj


@pytest.mark.asyncio
async def test_atualizar_cliente(
    session: AsyncSession,
    cliente: Cliente
):
    """Teste de atualização de cliente."""
    # Arrange
    service = ClienteService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    novo_nome = "Cliente Atualizado"
    novo_email = "atualizado@teste.com"
    novo_telefone = "(11) 88888-8888"
    
    cliente_update = ClienteUpdate(
        nome=novo_nome,
        email=novo_email,
        telefone=novo_telefone
    )
    
    # Act
    cliente_atualizado = await service.update(
        cliente.id_cliente,
        cliente_update,
        cliente.usuario_id,
        cliente.empresa_id
    )
    
    # Assert
    assert cliente_atualizado.id_cliente == cliente.id_cliente
    assert cliente_atualizado.nome == novo_nome
    assert cliente_atualizado.email == novo_email
    assert cliente_atualizado.telefone == novo_telefone


@pytest.mark.asyncio
async def test_buscar_cliente(
    session: AsyncSession,
    cliente: Cliente
):
    """Teste de busca de cliente por ID."""
    # Arrange
    service = ClienteService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    # Act
    cliente_encontrado = await service.get_by_id(cliente.id_cliente, cliente.empresa_id)
    
    # Assert
    assert cliente_encontrado is not None
    assert cliente_encontrado.id_cliente == cliente.id_cliente
    assert cliente_encontrado.nome == cliente.nome
    assert cliente_encontrado.email == cliente.email


@pytest.mark.asyncio
async def test_listar_clientes(
    session: AsyncSession,
    clientes_lista: list[Cliente]
):
    """Teste de listagem de clientes."""
    # Arrange
    service = ClienteService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    empresa_id = clientes_lista[0].empresa_id
    
    # Act
    resultado = await service.get_multi(
        empresa_id=empresa_id,
        skip=0,
        limit=10
    )
    
    # Assert
    assert resultado.total == 5
    assert len(resultado.items) == 5
    assert resultado.page == 1
    assert all(cliente.empresa_id == empresa_id for cliente in resultado.items)


@pytest.mark.asyncio
async def test_buscar_cliente_por_cpf_cnpj(
    session: AsyncSession,
    cliente: Cliente
):
    """Teste de busca de cliente por CPF/CNPJ."""
    # Arrange
    service = ClienteService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    # Act
    cliente_encontrado = await service.get_by_cpf_cnpj(
        cliente.cpf_cnpj,
        cliente.empresa_id
    )
    
    # Assert
    assert cliente_encontrado is not None
    assert cliente_encontrado.id_cliente == cliente.id_cliente
    assert cliente_encontrado.cpf_cnpj == cliente.cpf_cnpj


@pytest.mark.asyncio
async def test_buscar_cliente_por_email(
    session: AsyncSession,
    cliente: Cliente
):
    """Teste de busca de cliente por email."""
    # Arrange
    service = ClienteService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    # Act
    cliente_encontrado = await service.get_by_email(
        cliente.email,
        cliente.empresa_id
    )
    
    # Assert
    assert cliente_encontrado is not None
    assert cliente_encontrado.id_cliente == cliente.id_cliente
    assert cliente_encontrado.email == cliente.email


@pytest.mark.asyncio
async def test_filtrar_clientes_por_nome(
    session: AsyncSession,
    cliente_factory: Callable[..., AsyncGenerator[Cliente, None]]
):
    """Teste de filtro de clientes por nome."""
    # Arrange
    service = ClienteService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    empresa_id = uuid4()
    nome_busca = "João"
    
    # Criar clientes com nomes diferentes
    await cliente_factory(
        empresa_id=empresa_id,
        nome="João Silva"
    )
    await cliente_factory(
        empresa_id=empresa_id,
        nome="Maria Souza"
    )
    
    # Act
    resultado = await service.get_multi(
        empresa_id=empresa_id,
        nome=nome_busca
    )
    
    # Assert
    assert resultado.total == 1
    assert all(nome_busca in cliente.nome for cliente in resultado.items)


@pytest.mark.asyncio
async def test_erro_ao_criar_cliente_cpf_cnpj_duplicado(
    session: AsyncSession,
    cliente: Cliente,
    cliente_factory: Callable[..., AsyncGenerator[Cliente, None]]
):
    """Teste de erro ao criar cliente com CPF/CNPJ duplicado."""
    # Arrange
    service = ClienteService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await cliente_factory(
            empresa_id=cliente.empresa_id,
            cpf_cnpj=cliente.cpf_cnpj
        )
    assert excinfo.value.status_code == 400
    assert "já cadastrado" in str(excinfo.value.detail)


@pytest.mark.asyncio
async def test_erro_ao_criar_cliente_email_duplicado(
    session: AsyncSession,
    cliente: Cliente,
    cliente_factory: Callable[..., AsyncGenerator[Cliente, None]]
):
    """Teste de erro ao criar cliente com email duplicado."""
    # Arrange
    service = ClienteService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await cliente_factory(
            empresa_id=cliente.empresa_id,
            email=cliente.email
        )
    assert excinfo.value.status_code == 400
    assert "já cadastrado" in str(excinfo.value.detail)


@pytest.mark.asyncio
async def test_erro_ao_buscar_cliente_inexistente(session: AsyncSession):
    """Teste de erro ao buscar cliente inexistente."""
    # Arrange
    service = ClienteService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await service.get_by_id(uuid4(), uuid4())
    assert excinfo.value.status_code == 404
    assert "não encontrado" in str(excinfo.value.detail)


@pytest.mark.asyncio
async def test_erro_ao_atualizar_cliente_inexistente(session: AsyncSession):
    """Teste de erro ao atualizar cliente inexistente."""
    # Arrange
    service = ClienteService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    cliente_update = ClienteUpdate(nome="Teste")
    
    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await service.update(uuid4(), cliente_update, uuid4(), uuid4())
    assert excinfo.value.status_code == 404
    assert "não encontrado" in str(excinfo.value.detail) 