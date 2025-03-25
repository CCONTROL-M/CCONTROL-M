# Documentação da API de Lançamentos Financeiros

## Visão Geral

A API de lançamentos financeiros do CCONTROL-M permite gerenciar as movimentações financeiras (receitas e despesas) de uma empresa. Cada lançamento possui informações como valor, data, tipo (receita ou despesa), status (pendente, pago, cancelado), além de relacionamentos com categorias, centros de custo e contas bancárias.

## Base URL

```
http://localhost:8000/api/v1
```

## Endpoints

### Listar Lançamentos Financeiros

Retorna uma lista paginada de lançamentos financeiros com diversos filtros.

**Endpoint:** `GET /api/v1/lancamentos`

**Parâmetros de Query:**

| Parâmetro | Tipo | Obrigatório | Descrição | Exemplo |
|-----------|------|-------------|-----------|---------|
| id_empresa | UUID | Sim | ID da empresa | `3fa85f64-5717-4562-b3fc-2c963f66afa6` |
| tipo | String | Não | Filtrar por tipo (RECEITA, DESPESA) | `DESPESA` |
| id_categoria | UUID | Não | Filtrar por categoria | `3fa85f64-5717-4562-b3fc-2c963f66afa6` |
| id_centro_custo | UUID | Não | Filtrar por centro de custo | `3fa85f64-5717-4562-b3fc-2c963f66afa6` |
| id_conta | UUID | Não | Filtrar por conta bancária | `3fa85f64-5717-4562-b3fc-2c963f66afa6` |
| status | String | Não | Filtrar por status (PENDENTE, PAGO, CANCELADO) | `PENDENTE` |
| data_inicio | String | Não | Data inicial (formato YYYY-MM-DD) | `2023-01-01` |
| data_fim | String | Não | Data final (formato YYYY-MM-DD) | `2023-12-31` |
| page | Integer | Não | Página atual (padrão: 1) | `1` |
| page_size | Integer | Não | Itens por página (padrão: 10, máximo: 100) | `10` |

**Exemplo de Requisição:**

```
GET /api/v1/lancamentos?id_empresa=3fa85f64-5717-4562-b3fc-2c963f66afa6&tipo=DESPESA&status=PENDENTE&page=1&page_size=10
```

**Resposta:**

```json
{
  "items": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "descricao": "Pagamento fornecedor XYZ",
      "valor": 1500.00,
      "data_lancamento": "2023-05-10",
      "data_pagamento": "2023-05-15",
      "tipo": "DESPESA",
      "status": "PAGO",
      "id_categoria": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "id_empresa": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    },
    {
      "id": "4fa85f64-5717-4562-b3fc-2c963f66afa7",
      "descricao": "Aluguel escritório",
      "valor": 2500.00,
      "data_lancamento": "2023-05-12",
      "data_pagamento": null,
      "tipo": "DESPESA",
      "status": "PENDENTE",
      "id_categoria": "5fa85f64-5717-4562-b3fc-2c963f66afa8",
      "id_empresa": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    }
  ],
  "total": 45,
  "page": 1,
  "pages": 5,
  "page_size": 10
}
```

**Códigos de Status:**

- `200 OK`: Lista de lançamentos obtida com sucesso
- `401 Unauthorized`: Não autenticado
- `403 Forbidden`: Sem permissão para acessar este recurso
- `422 Unprocessable Entity`: Erro de validação nos parâmetros

### Obter Lançamento por ID

Retorna os detalhes de um lançamento financeiro específico.

**Endpoint:** `GET /api/v1/lancamentos/{id_lancamento}`

**Parâmetros de Path:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| id_lancamento | UUID | ID do lançamento |

**Parâmetros de Query:**

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| id_empresa | UUID | Sim | ID da empresa para verificação de acesso |

**Exemplo de Requisição:**

```
GET /api/v1/lancamentos/3fa85f64-5717-4562-b3fc-2c963f66afa6?id_empresa=3fa85f64-5717-4562-b3fc-2c963f66afa6
```

**Resposta:**

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "descricao": "Pagamento fornecedor XYZ",
  "valor": 1500.00,
  "data_lancamento": "2023-05-10",
  "data_pagamento": "2023-05-15",
  "tipo": "DESPESA",
  "status": "PAGO",
  "id_categoria": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "id_empresa": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "categoria": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "nome": "Fornecedores",
    "tipo": "DESPESA"
  },
  "centro_custo": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "nome": "Administrativo"
  },
  "conta": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "nome": "Conta Principal",
    "banco": "Banco XYZ"
  }
}
```

## Exemplos de Uso

### Exemplo 1: Listar todas as despesas pendentes de uma empresa

```bash
# Usando curl
curl -X GET "http://localhost:8000/api/v1/lancamentos?id_empresa=3fa85f64-5717-4562-b3fc-2c963f66afa6&tipo=DESPESA&status=PENDENTE" -H "Authorization: Bearer SEU_TOKEN_JWT"

# Usando PowerShell
Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/lancamentos?id_empresa=3fa85f64-5717-4562-b3fc-2c963f66afa6&tipo=DESPESA&status=PENDENTE' -Method GET -Headers @{Authorization = "Bearer SEU_TOKEN_JWT"}
```

### Exemplo 2: Listar lançamentos em um período específico

```bash
# Usando curl
curl -X GET "http://localhost:8000/api/v1/lancamentos?id_empresa=3fa85f64-5717-4562-b3fc-2c963f66afa6&data_inicio=2023-01-01&data_fim=2023-01-31" -H "Authorization: Bearer SEU_TOKEN_JWT"

# Usando PowerShell
Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/lancamentos?id_empresa=3fa85f64-5717-4562-b3fc-2c963f66afa6&data_inicio=2023-01-01&data_fim=2023-01-31' -Method GET -Headers @{Authorization = "Bearer SEU_TOKEN_JWT"}
```

### Exemplo 3: Obter detalhes de um lançamento específico

```bash
# Usando curl
curl -X GET "http://localhost:8000/api/v1/lancamentos/3fa85f64-5717-4562-b3fc-2c963f66afa6?id_empresa=3fa85f64-5717-4562-b3fc-2c963f66afa6" -H "Authorization: Bearer SEU_TOKEN_JWT"

# Usando PowerShell
Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/lancamentos/3fa85f64-5717-4562-b3fc-2c963f66afa6?id_empresa=3fa85f64-5717-4562-b3fc-2c963f66afa6' -Method GET -Headers @{Authorization = "Bearer SEU_TOKEN_JWT"}
```

## Observações Importantes

1. A rota de lançamentos requer autenticação JWT.
2. As permissões do usuário são verificadas para cada operação (visualização, criação, edição).
3. O Row Level Security (RLS) do Supabase é aplicado, garantindo que os usuários só possam visualizar lançamentos de empresas às quais têm acesso.
4. Para filtros de data, o formato deve ser YYYY-MM-DD (ISO 8601).
5. O parâmetro `id_empresa` é obrigatório para todas as operações para garantir o escopo correto dos dados. 