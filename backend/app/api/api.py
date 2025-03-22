"""
Configuração principal do roteador da API.
"""
from fastapi import APIRouter

from app.api.endpoints import (
    auth,
    users,
    empresas,
    produtos,
    categorias,
    centros_custo,
    reports
)

api_router = APIRouter()

# Rotas de autenticação
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Autenticação"]
)

# Rotas de usuários
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Usuários"]
)

# Rotas de empresas
api_router.include_router(
    empresas.router,
    prefix="/empresas",
    tags=["Empresas"]
)

# Rotas de produtos
api_router.include_router(
    produtos.router,
    prefix="/produtos",
    tags=["Produtos"]
)

# Rotas de categorias
api_router.include_router(
    categorias.router,
    prefix="/categorias",
    tags=["Categorias"]
)

# Rotas de centros de custo
api_router.include_router(
    centros_custo.router,
    prefix="/centros-custo",
    tags=["Centros de Custo"]
)

# Rotas de relatórios
api_router.include_router(
    reports.router,
    prefix="/reports",
    tags=["Relatórios"]
) 