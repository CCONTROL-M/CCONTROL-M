"""
Arquivo de compatibilidade para VendaService.

Este arquivo importa e reexporta a classe VendaService da nova estrutura
modularizada. Mantido para compatibilidade com código existente.

IMPORTANTE: Para novos desenvolvimentos, importe diretamente de app.services.venda.
"""

# Importar da nova estrutura modularizada
from app.services.venda import VendaService

# Reexportar para manter compatibilidade
__all__ = ["VendaService"] 