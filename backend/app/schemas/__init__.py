"""Schemas Pydantic para validação de dados e serialização no sistema CCONTROL-M."""

from .usuario import (
    UsuarioBase, 
    UsuarioCreate, 
    UsuarioUpdate, 
    UsuarioInDB, 
    Usuario, 
    UsuarioList
)
from .empresa import (
    EmpresaBase, 
    EmpresaCreate, 
    EmpresaUpdate, 
    EmpresaInDB, 
    Empresa, 
    EmpresaList
)
from .lancamento import (
    LancamentoBase, 
    LancamentoCreate, 
    LancamentoUpdate, 
    LancamentoInDB, 
    Lancamento, 
    LancamentoList,
    LancamentoDashboard
)
from .categoria import (
    CategoriaBase, 
    CategoriaCreate, 
    CategoriaUpdate, 
    CategoriaInDB, 
    Categoria, 
    CategoriaList
)
from .centro_custo import (
    CentroCustoBase, 
    CentroCustoCreate, 
    CentroCustoUpdate, 
    CentroCustoInDB, 
    CentroCusto, 
    CentroCustoList
)
from .cliente import (
    ClienteBase, 
    ClienteCreate, 
    ClienteUpdate, 
    ClienteInDB, 
    Cliente, 
    ClienteList
)
from .fornecedor import (
    FornecedorBase, 
    FornecedorCreate, 
    FornecedorUpdate, 
    FornecedorInDB, 
    Fornecedor, 
    FornecedorList
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
from .venda import (
    VendaBase, 
    VendaCreate, 
    VendaUpdate, 
    VendaInDB, 
    Venda, 
    VendaList
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
from .token import Token, TokenPayload
from .pagination import PaginatedResponse

# Lista completa de modelos que devem ser exportados
__all__ = [
    # Usuários e empresas
    'Usuario', 'UsuarioCreate', 'UsuarioUpdate', 'UsuarioLogin', 'UsuarioPaginacao',
    'Empresa', 'EmpresaCreate', 'EmpresaUpdate',
    'Token', 'TokenData',
    
    # Clientes e fornecedores
    'Cliente', 'ClienteCreate', 'ClienteUpdate', 'ClientePaginacao',
    'Fornecedor', 'FornecedorCreate', 'FornecedorUpdate', 'FornecedorPaginacao',
    
    # Financeiro
    'ContaBancaria', 'ContaBancariaCreate', 'ContaBancariaUpdate', 'ContaBancariaPaginacao',
    'FormaPagamento', 'FormaPagamentoCreate', 'FormaPagamentoUpdate', 'FormaPagamentoPaginacao',
    'Categoria', 'CategoriaCreate', 'CategoriaUpdate', 'CategoriaPaginacao',
    'CentroCusto', 'CentroCustoCreate', 'CentroCustoUpdate', 'CentroCustoPaginacao',
    'Lancamento', 'LancamentoCreate', 'LancamentoUpdate', 'LancamentoPaginacao',
    'ResumoFinanceiro', 'FluxoCaixa', 'RelatorioFinanceiro',
    
    # Vendas
    'Venda', 'VendaCreate', 'VendaUpdate', 'VendaPaginacao',
    'Parcela', 'ParcelaCreate', 'ParcelaUpdate', 'RelatorioVendas',
    
    # Produtos
    'Produto', 'ProdutoCreate', 'ProdutoUpdate', 'ProdutosPaginados', 'EstoqueUpdate',
    
    # Sistema
    'LogSistema', 'LogSistemaCreate', 'LogSistemaPaginacao',
    'SystemHealthCheck', 'DatabaseMetrics'
]

# Adicionar novos schemas aqui conforme necessário 