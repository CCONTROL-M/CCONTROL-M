"""
Módulo de serviços do CCONTROL-M.

Este módulo contém os serviços responsáveis pela lógica de negócio
e regras da aplicação.
"""

# Serviços Base
from app.services.base_service import BaseService
from app.services.auditoria_service import AuditoriaService
from app.services.log_sistema_service import LogSistemaService

# Serviços Refatorados
from app.services.produto import ProdutoService, ProdutoQueryService, ProdutoEstoqueService
from app.services.venda import VendaService, VendaItemService, VendaStatusService, VendaQueryService
from app.services.conta_receber import ContaReceberService
from app.services.conta_pagar import ContaPagarService, ContaPagarQueryService, ContaPagarOperationsService

# Serviços Legados
from app.services.usuario_service import UsuarioService
from app.services.permissao_service import PermissaoService
from app.services.empresa_service import EmpresaService
from app.services.cliente_service import ClienteService
from app.services.fornecedor_service import FornecedorService
from app.services.categoria_service import CategoriaService
from app.services.centro_custo_service import CentroCustoService
from app.services.forma_pagamento_service import FormaPagamentoService
from app.services.conta_bancaria_service import ContaBancariaService
from app.services.lancamento_service import LancamentoService
from app.services.compra_service import CompraService
from app.services.parcela_service import ParcelaService


__all__ = [
    # Base
    "BaseService",
    "AuditoriaService",
    "LogSistemaService",
    
    # Módulos Refatorados
    "ProdutoService",
    "ProdutoQueryService",
    "ProdutoEstoqueService",
    "VendaService",
    "VendaItemService",
    "VendaStatusService",
    "VendaQueryService",
    "ContaReceberService",
    "ContaPagarService", 
    "ContaPagarQueryService",
    "ContaPagarOperationsService",
    
    # Legados
    "UsuarioService",
    "PermissaoService",
    "EmpresaService", 
    "ClienteService",
    "FornecedorService", 
    "CategoriaService",
    "CentroCustoService",
    "FormaPagamentoService",
    "ContaBancariaService",
    "LancamentoService",
    "CompraService",
    "ParcelaService"
] 