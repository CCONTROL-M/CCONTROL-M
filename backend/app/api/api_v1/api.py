from fastapi import APIRouter
from app.api.api_v1.endpoints import (
    usuarios,
    auth,
    empresas,
    clientes,
    lancamentos,
    fornecedores,
    plano_contas,
    vendas,
    controle_caixa,
    dashboard,
    meios_pagamento,
    health,
)

api_router = APIRouter()

# Definir rota base para cada endpoint
api_router.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
api_router.include_router(usuarios.router, prefix="/usuarios", tags=["Usuários"])
api_router.include_router(empresas.router, prefix="/empresas", tags=["Empresas"])
api_router.include_router(clientes.router, prefix="/clientes", tags=["Clientes"])
api_router.include_router(fornecedores.router, prefix="/fornecedores", tags=["Fornecedores"])
api_router.include_router(plano_contas.router, prefix="/plano-contas", tags=["Plano de Contas"])
api_router.include_router(lancamentos.router, prefix="/lancamentos", tags=["Lançamentos Financeiros"])
api_router.include_router(vendas.router, prefix="/vendas", tags=["Vendas"])
api_router.include_router(controle_caixa.router, prefix="/controle-caixa", tags=["Controle de Caixa"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(meios_pagamento.router, prefix="/meios-pagamento", tags=["Meios de Pagamento"])
api_router.include_router(health.router, prefix="/health", tags=["Health Check"])

# Exportar o router configurado 