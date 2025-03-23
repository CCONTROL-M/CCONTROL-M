# Multi-Tenancy no CCONTROL-M

Este documento descreve a implementação de multi-tenancy (isolamento de dados entre empresas) no CCONTROL-M.

## Visão Geral

O CCONTROL-M utiliza uma abordagem combinada para garantir o isolamento de dados entre diferentes empresas:

1. **Middleware de Tenant**: Extrai o ID da empresa do token JWT e o disponibiliza para toda a aplicação.
2. **Filtragem nos Repositórios**: Todos os repositórios filtram automaticamente consultas pelo `id_empresa`.
3. **Row-Level Security (RLS) no PostgreSQL**: Uma camada adicional de segurança no banco de dados.

## Componentes Principais

### 1. Middleware de Tenant

O `TenantMiddleware` extrai o ID da empresa do token JWT e o armazena em um contexto durante a requisição. 
Esse middleware é executado em todas as requisições e disponibiliza o ID da empresa através da função `get_tenant_id()`.

### 2. Repositório Base com Filtros de Tenant

A classe `BaseRepository` implementa automaticamente o isolamento de tenant em todas as operações CRUD:

- Consultas filtram automaticamente por `id_empresa` quando aplicável.
- Inserções adicionam automaticamente o `id_empresa` quando não fornecido.
- Atualizações e exclusões verificam se o registro pertence ao tenant atual.

### 3. Row-Level Security no PostgreSQL

O RLS oferece uma camada adicional de segurança diretamente no banco de dados:

- Políticas aplicadas a todas as tabelas sensíveis.
- Definição do ID do tenant como variável de sessão em cada transação.
- Verificação em nível de banco de dados, impedindo acesso mesmo por consultas SQL diretas.

## Middlewares Ativados

O sistema implementa diversos middlewares que trabalham em conjunto com o multi-tenancy:

1. **Security Middleware**: Valida tokens JWT, verifica CORS e protege contra ataques comuns.
2. **Logging Middleware**: Registra todas as requisições com contexto de tenant.
3. **Performance Middleware**: Monitora tempos de resposta por tenant.
4. **Rate Limiter**: Limita requisições por tenant (100 requisições por minuto por usuário/empresa).
5. **Gzip Middleware**: Comprime respostas para melhorar performance.
6. **Audit Middleware**: Registra ações sensíveis com contexto de tenant.
7. **Validation Middleware**: Valida dados de entrada e adiciona cabeçalhos de segurança.

## Tabelas com Isolamento por Tenant

O sistema aplica isolamento por tenant nas seguintes tabelas:

- `usuario`
- `usuario_empresa`
- `empresa`
- `cliente`
- `fornecedor`
- `categoria` 
- `centro_custo`
- `conta_bancaria`
- `forma_pagamento`
- `lancamento`
- `venda`
- `parcela`
- `compra`
- `produto`
- `log_atividade`
- `log_sistema` 
- `conta_pagar` (Novo módulo)
- `conta_receber` (Novo módulo)

## Como Testar o Multi-Tenancy

### Teste de APIs com Tokens de Diferentes Empresas

1. Faça login com um usuário da empresa A e capture o token JWT.
2. Faça login com um usuário da empresa B e capture outro token JWT.
3. Use ambos os tokens para acessar os mesmos endpoints e verifique se apenas os dados da empresa correspondente são retornados.

Exemplo usando cURL:

```bash
# Login como usuário da empresa A
curl -X POST http://localhost:8000/api/auth/login -d "username=usuario_empresa_a@exemplo.com&password=senha123"

# Login como usuário da empresa B
curl -X POST http://localhost:8000/api/auth/login -d "username=usuario_empresa_b@exemplo.com&password=senha123"

# Consultar clientes com token da empresa A
curl -X GET http://localhost:8000/api/clientes/ -H "Authorization: Bearer {token_empresa_a}"

# Consultar clientes com token da empresa B
curl -X GET http://localhost:8000/api/clientes/ -H "Authorization: Bearer {token_empresa_b}"
```

### Teste de Acesso Cruzado entre Tenants

Tente acessar ou modificar um registro específico de outra empresa:

```bash
# Obter ID de um cliente da empresa A
curl -X GET http://localhost:8000/api/clientes/ -H "Authorization: Bearer {token_empresa_a}"

# Tentar acessar esse cliente específico com token da empresa B
curl -X GET http://localhost:8000/api/clientes/{id_cliente_empresa_a} -H "Authorization: Bearer {token_empresa_b}"
# Deve retornar erro 404 (não encontrado) ou 403 (proibido)
```

### Teste de Criação de Registros

Crie registros com diferentes tokens e verifique se o `id_empresa` é definido corretamente:

```bash
# Criar cliente com token da empresa A
curl -X POST http://localhost:8000/api/clientes/ \
  -H "Authorization: Bearer {token_empresa_a}" \
  -H "Content-Type: application/json" \
  -d '{"nome": "Cliente Teste", "cpf_cnpj": "12345678901", "contato": "contato@teste.com"}'

# Verificar se o cliente foi criado com o id_empresa correto
curl -X GET http://localhost:8000/api/clientes/ -H "Authorization: Bearer {token_empresa_a}"
```

## Testando Contas a Pagar e Receber com Multi-Tenancy

```bash
# Criar conta a pagar com token da empresa A
curl -X POST http://localhost:8000/api/contas-pagar/ \
  -H "Authorization: Bearer {token_empresa_a}" \
  -H "Content-Type: application/json" \
  -d '{
    "descricao": "Pagamento Fornecedor XYZ",
    "valor": 1250.50,
    "data_vencimento": "2023-12-20",
    "id_empresa": "{id_empresa_a}"
  }'

# Verificar se a conta foi criada com o id_empresa correto
curl -X GET http://localhost:8000/api/contas-pagar/ \
  -H "Authorization: Bearer {token_empresa_a}" \
  -d "id_empresa={id_empresa_a}"

# Tentar acessar contas da empresa A usando token da empresa B
curl -X GET http://localhost:8000/api/contas-pagar/ \
  -H "Authorization: Bearer {token_empresa_b}" \
  -d "id_empresa={id_empresa_a}"
# Deve retornar erro 403 (proibido)
```

## Ativando e Desativando o RLS

Para ativar o Row-Level Security no PostgreSQL:

```bash
python -m backend.scripts.apply_rls
```

Para desativar (apenas em ambiente de desenvolvimento/teste):

```bash
python -m backend.scripts.apply_rls --disable
```

## Considerações de Segurança

- O RLS adiciona uma camada extra de segurança, mas não substitui a filtragem na aplicação.
- Todas as consultas diretas ao banco de dados devem ser feitas através dos repositórios.
- Nunca confie apenas no front-end para filtrar dados por empresa.
- Sempre valide o token JWT e extraia o ID da empresa no back-end.
- Os middlewares ativados fornecem camadas adicionais de segurança e monitoramento.

## Referências

- [Documentação do PostgreSQL sobre RLS](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [FastAPI - Dependências e Middlewares](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [SQLAlchemy - Eventos](https://docs.sqlalchemy.org/en/14/core/events.html) 