"""
Arquivo de compatibilidade para ContaReceberService.

Este arquivo importa e reexporta a classe ContaReceberService da nova estrutura
modularizada. Mantido para compatibilidade com código existente.

IMPORTANTE: Para novos desenvolvimentos, importe diretamente de app.services.conta_receber.
"""

# Importar da nova estrutura modularizada
from app.services.conta_receber import ContaReceberService

# Reexportar para manter compatibilidade
__all__ = ["ContaReceberService"] 