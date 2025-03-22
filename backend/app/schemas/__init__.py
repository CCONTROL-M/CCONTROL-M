"""Schemas Pydantic para validação de dados e serialização no sistema CCONTROL-M."""

# flake8: noqa
from .usuario import (
    UsuarioBase,
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioInDB,
    UsuarioResponse,
    Usuario,
    UsuarioList
)
from .token import Token, TokenPayload
from .empresa import (
    EmpresaBase,
    EmpresaCreate,
    EmpresaUpdate,
    EmpresaInDB,
    EmpresaResponse,
    Empresa,
    EmpresaList
)
from .pagination import (
    PaginationParams,
    PaginatedResponse,
)
from .fornecedor import (
    FornecedorBase,
    FornecedorCreate,
    FornecedorUpdate,
    FornecedorInDB,
    FornecedorResponse,
    Fornecedor,
    FornecedorList
)
from .categoria import (
    CategoriaBase,
    CategoriaCreate,
    CategoriaUpdate,
    CategoriaInDB,
    CategoriaResponse,
    Categoria,
    CategoriaList
)
from .centro_custo import (
    CentroCustoBase,
    CentroCustoCreate,
    CentroCustoUpdate,
    CentroCustoInDB,
    CentroCustoResponse,
    CentroCusto,
    CentroCustoList
)
from .lancamento import (
    LancamentoBase,
    LancamentoCreate,
    LancamentoUpdate,
    LancamentoInDB,
    Lancamento,
    LancamentoList
)
from .cliente import (
    ClienteBase,
    ClienteCreate,
    ClienteUpdate,
    ClienteInDB,
    Cliente,
    ClienteList
)
from .conta_bancaria import (
    ContaBancariaBase,
    ContaBancariaCreate,
    ContaBancariaUpdate,
    ContaBancariaInDB,
    ContaBancaria,
    ContaBancariaList
)
from .forma_pagamento import (
    FormaPagamentoBase,
    FormaPagamentoCreate,
    FormaPagamentoUpdate,
    FormaPagamentoInDB,
    FormaPagamento,
    FormaPagamentoList
)
from .parcela import (
    ParcelaBase,
    ParcelaCreate,
    ParcelaUpdate,
    ParcelaInDB,
    Parcela,
    ParcelaList
)
from .produto import (
    ProdutoBase,
    ProdutoCreate,
    ProdutoUpdate,
    ProdutoInDB,
    Produto,
    ProdutoList
)
from .venda import (
    VendaBase,
    VendaCreate,
    VendaUpdate,
    VendaInDB,
    Venda,
    VendaList
)
from .log_sistema import (
    LogSistemaBase,
    LogSistemaCreate,
    LogSistemaInDB,
    LogSistema,
    LogSistemaList
)
from .permissao_usuario import (
    PermissaoUsuarioBase,
    PermissaoUsuarioCreate,
    PermissaoUsuarioUpdate,
    PermissaoUsuarioInDB,
    PermissaoUsuario,
    PermissaoUsuarioList
)

# Lista completa de modelos que devem ser exportados
__all__ = [
    # Usuários e empresas
    'Usuario', 'UsuarioCreate', 'UsuarioUpdate', 'UsuarioList',
    'Empresa', 'EmpresaCreate', 'EmpresaUpdate', 'EmpresaList',
    'Token', 'TokenPayload',
    
    # Clientes e fornecedores
    'Cliente', 'ClienteCreate', 'ClienteUpdate', 'ClienteList',
    'Fornecedor', 'FornecedorCreate', 'FornecedorUpdate', 'FornecedorList',
    
    # Financeiro
    'ContaBancaria', 'ContaBancariaCreate', 'ContaBancariaUpdate', 'ContaBancariaList',
    'FormaPagamento', 'FormaPagamentoCreate', 'FormaPagamentoUpdate', 'FormaPagamentoList',
    'Categoria', 'CategoriaCreate', 'CategoriaUpdate', 'CategoriaList',
    'CentroCusto', 'CentroCustoCreate', 'CentroCustoUpdate', 'CentroCustoList',
    'Lancamento', 'LancamentoCreate', 'LancamentoUpdate', 'LancamentoList',
    
    # Vendas
    'Venda', 'VendaCreate', 'VendaUpdate', 'VendaList',
    'Parcela', 'ParcelaCreate', 'ParcelaUpdate', 'ParcelaList',
    
    # Produtos
    'ProdutoResponse', 'ProdutoCreate', 'ProdutoUpdate', 'ProdutoList',
    
    # Sistema
    'LogSistema', 'LogSistemaCreate', 'LogSistemaList',
    'PaginatedResponse'
]

# Adicionar novos schemas aqui conforme necessário 