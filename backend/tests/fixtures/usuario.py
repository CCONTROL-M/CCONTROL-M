"""Fixtures para testes de usuários."""
import pytest
from typing import AsyncGenerator
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.usuario import Usuario
from app.services.usuario_service import UsuarioService
from app.services.auditoria_service import AuditoriaService


@pytest.fixture
async def usuario_factory(session: AsyncSession) -> AsyncGenerator[Usuario, None]:
    """Fixture factory para criar usuários para testes."""
    created_users = []

    async def create_user(
        nome: str = "Usuário Teste",
        email: str = "usuario@teste.com",
        senha: str = "Senha@123",
        id_empresa: str = str(uuid4()),
        tipo_usuario: str = "operador",
        telas_permitidas: dict = None,
        ativo: bool = True
    ) -> Usuario:
        """Cria um usuário para teste."""
        if telas_permitidas is None:
            telas_permitidas = {"vendas": True, "clientes": True}

        service = UsuarioService(
            session=session,
            auditoria_service=AuditoriaService(session=session)
        )

        usuario = await service.create(
            nome=nome,
            email=email,
            senha=senha,
            id_empresa=id_empresa,
            tipo_usuario=tipo_usuario,
            telas_permitidas=telas_permitidas,
            ativo=ativo
        )
        created_users.append(usuario)
        return usuario

    yield create_user

    # Cleanup
    for usuario in created_users:
        await session.delete(usuario)
    await session.commit()


@pytest.fixture
async def usuario(usuario_factory) -> Usuario:
    """Fixture que retorna um usuário para teste."""
    return await usuario_factory()


@pytest.fixture
async def usuarios_lista(usuario_factory) -> list[Usuario]:
    """Fixture que retorna uma lista de usuários para teste."""
    usuarios = []
    for i in range(5):
        usuario = await usuario_factory(
            nome=f"Usuário {i}",
            email=f"usuario{i}@teste.com",
            tipo_usuario="operador" if i % 2 == 0 else "adm",
            ativo=True if i < 4 else False
        )
        usuarios.append(usuario)
    return usuarios 