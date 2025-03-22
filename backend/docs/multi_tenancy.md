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

## Referências

- [Documentação do PostgreSQL sobre RLS](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [FastAPI - Dependências e Middlewares](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [SQLAlchemy - Eventos](https://docs.sqlalchemy.org/en/14/core/events.html) 