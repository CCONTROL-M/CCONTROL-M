"""Módulo de routers para a API do CCONTROL-M."""

from app.routers.usuarios import router as usuarios_router
from app.routers.empresas import router as empresas_router
from app.routers.clientes import router as clientes_router
from app.routers.produtos import router as produtos_router

# Lista de routers exportados
__all__ = ["usuarios_router", "empresas_router", "clientes_router", "produtos_router"]

# Exportar todos os módulos de rota disponíveis
from app.routers import empresas
from app.routers import clientes
from app.routers import categorias
from app.routers import centro_custos
from app.routers import logs_sistema
from app.routers import vendas
from app.routers import lancamentos
from app.routers import formas_pagamento
from app.routers import contas_bancarias
import app.routers.fornecedores
from app.routers import produtos
from app.routers import monitoring 