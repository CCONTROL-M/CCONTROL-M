"""Fixtures para testes de empresas."""
import pytest
from typing import AsyncGenerator, Callable
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.empresa import Empresa
from app.models.usuario import Usuario
from app.schemas.empresa import EmpresaCreate
from app.services.empresa_service import EmpresaService
from app.services.auditoria_service import AuditoriaService

from tests.fixtures.usuario import usuario


@pytest.fixture
async def empresa_factory(
    session: AsyncSession,
    usuario: Usuario
) -> AsyncGenerator[Callable[..., AsyncGenerator[Empresa, None]], None]:
    """
    Fixture que cria uma factory para empresas.
    Permite criar empresas com dados customizados para testes.
    """
    empresas_criadas = []

    async def create_empresa(
        *,
        usuario_id: uuid4 | None = None,
        razao_social: str = "Empresa Teste LTDA",
        nome_fantasia: str = "Empresa Teste",
        cnpj: str = "12.345.678/0001-99",
        email: str = "empresa@teste.com",
        telefone: str = "(11) 99999-9999",
        endereco: str | None = None,
        observacao: str | None = None
    ) -> Empresa:
        """Cria uma empresa com os dados fornecidos."""
        if usuario_id is None:
            usuario_id = str(usuario.id_usuario)
        if endereco is None:
            endereco = "Rua Teste, 123, São Paulo - SP"
        if observacao is None:
            observacao = "Empresa de teste"

        service = EmpresaService(
            session=session,
            auditoria_service=AuditoriaService(session=session)
        )
        empresa_data = {
            "razao_social": razao_social,
            "nome_fantasia": nome_fantasia,
            "cnpj": cnpj,
            "email": email,
            "telefone": telefone,
            "endereco": endereco,
            "observacao": observacao
        }
        empresa_create = EmpresaCreate(**empresa_data)
        empresa = await service.create(empresa_create, usuario_id)
        empresas_criadas.append(empresa)
        return empresa

    yield create_empresa

    # Cleanup - remover empresas criadas
    for empresa in empresas_criadas:
        await session.delete(empresa)
    await session.commit()


@pytest.fixture
async def empresa(
    empresa_factory: Callable[..., AsyncGenerator[Empresa, None]]
) -> AsyncGenerator[Empresa, None]:
    """
    Fixture que cria uma empresa padrão para testes.
    """
    empresa = await empresa_factory()
    yield empresa


@pytest.fixture
async def empresas_lista(
    empresa_factory: Callable[..., AsyncGenerator[Empresa, None]]
) -> AsyncGenerator[list[Empresa], None]:
    """
    Fixture que cria uma lista de empresas para testes.
    """
    empresas = []
    for i in range(5):
        empresa = await empresa_factory(
            razao_social=f"Empresa {i} LTDA",
            nome_fantasia=f"Empresa {i}",
            cnpj=f"12.345.678/{i:04d}-99",
            email=f"empresa{i}@teste.com",
            telefone=f"(11) 9{i}{i}{i}{i}-{i}{i}{i}{i}"
        )
        empresas.append(empresa)
    
    yield empresas 