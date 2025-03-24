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
    vendas,
    parcelas,
    compras,
    permissoes,
    contas_pagar,
    contas_receber,
    logs_sistema,
    auditoria,
    dashboard,
)

from app.routers.auth import router as auth_router
from app.routers.empresas import router as empresas_router
from app.routers.usuarios import router as usuarios_router
from app.routers.logs_sistema import router as logs_sistema_router
from app.routers.categorias import router as categorias_router
from app.routers.centro_custos import router as centro_custos_router
from app.routers.fornecedores import router as fornecedores_router
from app.routers.clientes import router as clientes_router
from app.routers.produtos import router as produtos_router
from app.routers.contas_bancarias import router as contas_bancarias_router
from app.routers.formas_pagamento import router as formas_pagamento_router
from app.routers.vendas import router as vendas_router
from app.routers.compras import router as compras_router
from app.routers.parcelas import router as parcelas_router
from app.routers.lancamentos import router as lancamentos_router
from app.routers.contas_pagar import router as contas_pagar_router
from app.routers.contas_receber import router as contas_receber_router
from app.routers.permissoes import router as permissoes_router
from app.routers.auditoria import router as auditoria_router
from app.routers.dashboard import router as dashboard_router

# Router principal que agrega todas as rotas da API
api_router = APIRouter()

# Incluir todas as rotas
api_router.include_router(auth_router, prefix="/auth", tags=["Autenticação"])
api_router.include_router(empresas_router, prefix="/empresas", tags=["Empresas"])
api_router.include_router(usuarios_router, prefix="/usuarios", tags=["Usuários"])
api_router.include_router(logs_sistema_router, prefix="/logs", tags=["Logs do Sistema"])
api_router.include_router(categorias_router, prefix="/categorias", tags=["Categorias"])
api_router.include_router(centro_custos_router, prefix="/centros-custo", tags=["Centros de Custo"])
api_router.include_router(fornecedores_router, prefix="/fornecedores", tags=["Fornecedores"])
api_router.include_router(clientes_router, prefix="/clientes", tags=["Clientes"])
api_router.include_router(produtos_router, prefix="/produtos", tags=["Produtos"])
api_router.include_router(contas_bancarias_router, prefix="/contas-bancarias", tags=["Contas Bancárias"])
api_router.include_router(formas_pagamento_router, prefix="/formas-pagamento", tags=["Formas de Pagamento"])
api_router.include_router(vendas_router, prefix="/vendas", tags=["Vendas"])
api_router.include_router(compras_router, prefix="/compras", tags=["Compras"])
api_router.include_router(parcelas_router, prefix="/parcelas", tags=["Parcelas"])
api_router.include_router(lancamentos_router, prefix="/lancamentos", tags=["Lançamentos"])
api_router.include_router(contas_pagar_router, prefix="/contas-pagar", tags=["Contas a Pagar"])
api_router.include_router(contas_receber_router, prefix="/contas-receber", tags=["Contas a Receber"])
api_router.include_router(permissoes_router, prefix="/permissoes", tags=["Permissões"])
api_router.include_router(auditoria_router, prefix="/auditoria", tags=["Auditoria"])
api_router.include_router(dashboard_router, tags=["Dashboard"])

# Exportar o router para uso em main.py 