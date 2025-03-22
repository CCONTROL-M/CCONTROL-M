# Resumo dos Serviços Implementados - CCONTROL-M

Este documento apresenta um resumo dos serviços implementados no sistema CCONTROL-M, detalhando as funcionalidades de cada um e seus métodos principais.

## Arquitetura de Serviços

Todos os serviços seguem um padrão consistente:
- Herdam funcionalidades comuns
- Suportam multi-tenancy (validação por `id_empresa`)
- Utilizam operações assíncronas (`async/await`)
- Implementam validações de negócio específicas
- Registram logs de atividades
- Implementam tratamento centralizado de erros

## Serviços Implementados

### 1. LogSistemaService

**Função:** Gerenciar o registro de logs para auditoria e rastreabilidade do sistema.

**Métodos principais:**
- `registrar_log`: Registra uma nova entrada de log
- `listar_logs`: Lista logs com filtros e paginação
- `get_log`: Recupera um log específico por ID

### 2. EmpresaService

**Função:** Gerenciar o cadastro e administração de empresas (tenants).

**Métodos principais:**
- `get_empresa`: Obtém empresa por ID
- `listar_empresas`: Lista empresas com filtros e paginação
- `criar_empresa`: Cria nova empresa com validação de CNPJ único
- `atualizar_empresa`: Atualiza dados da empresa
- `ativar_empresa`: Ativa uma empresa
- `desativar_empresa`: Desativa uma empresa

### 3. UsuarioService

**Função:** Gerenciar usuários do sistema e suas permissões.

**Métodos principais:**
- `get_usuario`: Obtém usuário por ID
- `get_by_email`: Obtém usuário por email
- `listar_usuarios`: Lista usuários com filtros
- `criar_usuario`: Cria novo usuário com validação de email único
- `atualizar_usuario`: Atualiza dados do usuário
- `verificar_senha`: Verifica a senha do usuário
- `ativar_usuario`: Ativa um usuário
- `desativar_usuario`: Desativa um usuário

### 4. ClienteService

**Função:** Gerenciar o cadastro de clientes.

**Métodos principais:**
- `get_cliente`: Obtém cliente por ID
- `listar_clientes`: Lista clientes com filtros e paginação
- `criar_cliente`: Cria novo cliente com validação de CPF/CNPJ único
- `atualizar_cliente`: Atualiza dados do cliente
- `remover_cliente`: Remove cliente, verificando integridade de dados

### 5. FornecedorService

**Função:** Gerenciar o cadastro de fornecedores.

**Métodos principais:**
- `get_fornecedor`: Obtém fornecedor por ID
- `listar_fornecedores`: Lista fornecedores com filtros e paginação
- `criar_fornecedor`: Cria novo fornecedor com validação de CNPJ único
- `atualizar_fornecedor`: Atualiza dados do fornecedor
- `remover_fornecedor`: Remove fornecedor, verificando integridade de dados

### 6. VendaService

**Função:** Gerenciar o processo de vendas.

**Métodos principais:**
- `get_venda`: Obtém venda por ID
- `listar_vendas`: Lista vendas com diversos filtros
- `criar_venda`: Cria nova venda com validações
- `atualizar_venda`: Atualiza venda existente
- `cancelar_venda`: Cancela uma venda
- `concluir_venda`: Marca uma venda como concluída
- `remover_venda`: Remove venda, verificando integridade referencial

### 7. ParcelaService

**Função:** Gerenciar parcelas de vendas e pagamentos.

**Métodos principais:**
- `get_parcela`: Obtém parcela por ID
- `listar_parcelas`: Lista parcelas com filtros
- `criar_parcela`: Cria nova parcela com validações
- `atualizar_parcela`: Atualiza parcela existente
- `registrar_pagamento`: Registra pagamento de parcela
- `cancelar_parcela`: Cancela parcela
- `remover_parcela`: Remove parcela, verificando integridade

### 8. LancamentoService

**Função:** Gerenciar lançamentos financeiros (receitas e despesas).

**Métodos principais:**
- `get_lancamento`: Obtém lançamento por ID
- `listar_lancamentos`: Lista lançamentos com filtros avançados
- `criar_lancamento`: Cria novo lançamento com validações
- `atualizar_lancamento`: Atualiza lançamento existente
- `efetivar_lancamento`: Efetiva um lançamento
- `cancelar_lancamento`: Cancela um lançamento
- `remover_lancamento`: Remove lançamento, verificando status

### 9. FormaPagamentoService

**Função:** Gerenciar formas de pagamento disponíveis.

**Métodos principais:**
- `get_forma_pagamento`: Obtém forma de pagamento por ID
- `listar_formas_pagamento`: Lista formas de pagamento com filtros
- `criar_forma_pagamento`: Cria nova forma de pagamento
- `atualizar_forma_pagamento`: Atualiza forma de pagamento
- `ativar_forma_pagamento`: Ativa forma de pagamento
- `desativar_forma_pagamento`: Desativa forma de pagamento
- `remover_forma_pagamento`: Remove forma de pagamento, verificando uso

### 10. ContaBancariaService

**Função:** Gerenciar contas bancárias, saldos e transações.

**Métodos principais:**
- `get_conta_bancaria`: Obtém conta bancária por ID
- `listar_contas_bancarias`: Lista contas bancárias com filtros
- `criar_conta_bancaria`: Cria nova conta bancária com validação
- `atualizar_conta_bancaria`: Atualiza conta bancária
- `ajustar_saldo`: Realiza ajuste manual de saldo
- `ativar_conta_bancaria`: Ativa conta bancária
- `desativar_conta_bancaria`: Desativa conta bancária
- `remover_conta_bancaria`: Remove conta bancária, verificando uso

### 11. CentroCustoService

**Função:** Gerenciar centros de custo para classificação contábil.

**Métodos principais:**
- `get_centro_custo`: Obtém centro de custo por ID
- `listar_centros_custo`: Lista centros de custo com filtros
- `criar_centro_custo`: Cria novo centro de custo
- `atualizar_centro_custo`: Atualiza centro de custo
- `ativar_centro_custo`: Ativa centro de custo
- `desativar_centro_custo`: Desativa centro de custo
- `remover_centro_custo`: Remove centro de custo, verificando uso

### 12. CategoriaService

**Função:** Gerenciar categorias para classificação de lançamentos.

**Métodos principais:**
- `get_categoria`: Obtém categoria por ID
- `listar_categorias`: Lista categorias com filtros
- `criar_categoria`: Cria nova categoria com validação
- `atualizar_categoria`: Atualiza categoria existente
- `ativar_categoria`: Ativa categoria
- `desativar_categoria`: Desativa categoria
- `remover_categoria`: Remove categoria, verificando uso

## Validações e Regras de Negócio

Todos os serviços implementam validações específicas, incluindo:

- **Validações de Multi-tenancy**: Garantindo que cada empresa acesse apenas seus dados
- **Validações de Unicidade**: Prevenindo duplicação de dados (nome, CPF/CNPJ, etc.)
- **Validações de Integridade**: Prevenindo exclusão de registros referenciados
- **Validações de Estado**: Verificando status correto para operações (ativo/inativo)
- **Validações de Formato**: Garantindo formato correto para CPF, CNPJ, email, etc.
- **Verificações de Permissão**: Garantindo que usuários acessem somente recursos autorizados

## Logs e Auditoria

Todos os serviços registram logs detalhados sobre operações realizadas, incluindo:
- Usuário que realizou a operação
- Data e hora da operação
- Ação realizada (criar, atualizar, remover, etc.)
- Detalhes da operação
- Empresa (tenant) relacionada

## Tratamento de Erros

Os serviços usam um sistema centralizado de tratamento de erros, lançando HTTPExceptions padronizadas com:
- Códigos de status HTTP apropriados
- Mensagens de erro detalhadas e amigáveis
- Registro de erros em logs para debugging 