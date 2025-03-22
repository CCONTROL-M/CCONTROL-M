"""APIs e rotas do sistema CCONTROL-M."""
from fastapi import APIRouter

from app.routers import (
    auth,
    usuarios,
    empresas,
    categorias,
    clientes,
    fornecedores,
    centro_custos,
    produtos,
    lancamentos,
    vendas,  # Reativado
    parcelas,  # Reativado
    compras,   # Adicionado
    permissoes,
)

# Importar o novo router de clientes com validação avançada
# from app.routers import clientes_router

# Router principal que agrega todas as rotas da API
api_router = APIRouter()

# Incluir as rotas específicas
api_router.include_router(auth.router)
api_router.include_router(usuarios.router)
api_router.include_router(empresas.router)
api_router.include_router(categorias.router)

# Substituir o router de clientes original pelo router com validação avançada
api_router.include_router(clientes.router)  # Usar o router original
# api_router.include_router(clientes_router.router)

api_router.include_router(fornecedores.router)
api_router.include_router(centro_custos.router)
api_router.include_router(produtos.router)
api_router.include_router(lancamentos.router)
api_router.include_router(vendas.router)  # Reativado
api_router.include_router(parcelas.router)  # Reativado
api_router.include_router(compras.router)  # Adicionado
api_router.include_router(permissoes.router) 