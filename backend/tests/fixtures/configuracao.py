"""Fixtures para testes de configurações."""
import pytest
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.configuracao import Configuracao
from app.services.configuracao_service import ConfiguracaoService
from app.services.auditoria_service import AuditoriaService


@pytest.fixture
async def configuracao_factory(
    session: AsyncSession
) -> AsyncGenerator[Configuracao, None]:
    """Fixture factory para criar configurações para testes."""
    created_configs = []

    async def create_config(
        chave: str = "TAXA_JUROS",
        valor: str = "2.5",
        descricao: str = "Taxa de juros padrão",
        tipo: str = "decimal"
    ) -> Configuracao:
        """Cria uma configuração para teste."""
        service = ConfiguracaoService(
            session=session,
            auditoria_service=AuditoriaService(session=session)
        )
        config = await service.create(
            chave=chave,
            valor=valor,
            descricao=descricao,
            tipo=tipo
        )
        created_configs.append(config)
        return config

    yield create_config

    # Cleanup
    for config in created_configs:
        await session.delete(config)
    await session.commit()


@pytest.fixture
async def configuracao(configuracao_factory) -> Configuracao:
    """Fixture que retorna uma configuração para teste."""
    return await configuracao_factory()


@pytest.fixture
async def configuracoes_lista(configuracao_factory) -> list[Configuracao]:
    """Fixture que retorna uma lista de configurações para teste."""
    configs = []
    configuracoes = [
        {
            "chave": "TAXA_JUROS",
            "valor": "2.5",
            "descricao": "Taxa de juros padrão",
            "tipo": "decimal"
        },
        {
            "chave": "DIAS_VENCIMENTO",
            "valor": "30",
            "descricao": "Dias padrão para vencimento",
            "tipo": "inteiro"
        },
        {
            "chave": "NOME_EMPRESA",
            "valor": "Minha Empresa",
            "descricao": "Nome da empresa",
            "tipo": "texto"
        },
        {
            "chave": "ENVIAR_EMAIL",
            "valor": "true",
            "descricao": "Enviar e-mail de notificação",
            "tipo": "booleano"
        },
        {
            "chave": "LOGO_URL",
            "valor": "https://exemplo.com/logo.png",
            "descricao": "URL do logo da empresa",
            "tipo": "texto"
        }
    ]
    
    for config in configuracoes:
        configuracao = await configuracao_factory(
            chave=config["chave"],
            valor=config["valor"],
            descricao=config["descricao"],
            tipo=config["tipo"]
        )
        configs.append(configuracao)
    return configs 