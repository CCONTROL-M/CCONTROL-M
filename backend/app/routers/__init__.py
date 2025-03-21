"""Módulo de routers da aplicação."""
from fastapi import APIRouter

from app.routers import auth, usuarios, empresas, clientes, produtos, formas_pagamento, contas_bancarias


# Router principal da API
router = APIRouter()

# Incluir router de autenticação
router.include_router(auth.router)

# Incluir router de usuários
router.include_router(usuarios.router)

# Incluir router de empresas
router.include_router(empresas.router)

# Incluir router de clientes
router.include_router(clientes.router)

# Incluir router de produtos
router.include_router(produtos.router)

# Incluir router de formas de pagamento
router.include_router(formas_pagamento.router)

# Incluir router de contas bancárias
router.include_router(contas_bancarias.router) 