"""
Arquivo de compatibilidade para ContaPagarService.

Este arquivo importa e reexporta a classe ContaPagarService da nova estrutura
modularizada. Mantido para compatibilidade com código existente.

IMPORTANTE: Para novos desenvolvimentos, importe diretamente de app.services.conta_pagar.
"""

# Importar da nova estrutura modularizada
from app.services.conta_pagar import ContaPagarService

# Reexportar para manter compatibilidade
__all__ = ["ContaPagarService"] 