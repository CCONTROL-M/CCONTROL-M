"""
Pacote de serviços para gerenciamento de produtos no CCONTROL-M.

Este pacote contém serviços especializados para diferentes aspectos
do gerenciamento de produtos, organizados de forma modular.
"""

# Exportar classes principais para facilitar importação
from app.services.produto.produto_service import ProdutoService
from app.services.produto.produto_query_service import ProdutoQueryService
from app.services.produto.produto_estoque_service import ProdutoEstoqueService

__all__ = [
    "ProdutoService",
    "ProdutoQueryService",
    "ProdutoEstoqueService"
] 