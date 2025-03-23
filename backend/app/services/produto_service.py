"""
Proxy para o serviço de produtos.

Este arquivo serve como proxy para redirecionar as importações existentes
para a implementação modularizada no pacote produto/.
"""

from app.services.produto import ProdutoService

# Reexportar para compatibilidade com código existente
__all__ = ["ProdutoService"] 