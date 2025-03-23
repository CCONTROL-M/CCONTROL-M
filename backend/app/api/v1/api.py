"""Configuração principal da API."""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    usuarios,
    auth,
    empresas,
    fornecedores,
    categorias,
    contas_pagar
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(usuarios.router)
api_router.include_router(empresas.router)
api_router.include_router(fornecedores.router)
api_router.include_router(categorias.router)
api_router.include_router(contas_pagar.router) 