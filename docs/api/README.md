# Documentação da API - CCONTROL-M

## 🔍 Visão Geral

A API do CCONTROL-M segue os princípios REST e utiliza JSON para comunicação. Todas as requisições devem incluir o token JWT no header de autorização.

## 🔐 Autenticação

### Login

```http
POST /api/auth/login
```

**Request Body:**
```json
{
    "email": "usuario@exemplo.com",
    "password": "senha123"
}
```

**Response (200 OK):**
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 3600
}
```

### Refresh Token

```http
POST /api/auth/refresh
```

**Request Headers:**
```
Authorization: Bearer {refresh_token}
```

**Response (200 OK):**
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 3600
}
```

## 📦 Produtos

### Listar Produtos

```http
GET /api/produtos
```

**Query Parameters:**
- `page`: Número da página (default: 1)
- `per_page`: Itens por página (default: 10)
- `search`: Termo de busca
- `categoria_id`: Filtrar por categoria
- `order_by`: Campo para ordenação
- `order`: asc/desc

**Response (200 OK):**
```json
{
    "items": [
        {
            "id": 1,
            "codigo": "PROD001",
            "nome": "Produto 1",
            "descricao": "Descrição do produto",
            "preco": 99.90,
            "estoque": 100,
            "categoria": {
                "id": 1,
                "nome": "Categoria 1"
            },
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        }
    ],
    "total": 100,
    "page": 1,
    "per_page": 10,
    "total_pages": 10
}
```

### Criar Produto

```http
POST /api/produtos
```

**Request Body:**
```json
{
    "codigo": "PROD001",
    "nome": "Produto 1",
    "descricao": "Descrição do produto",
    "preco": 99.90,
    "estoque": 100,
    "categoria_id": 1
}
```

**Response (201 Created):**
```json
{
    "id": 1,
    "codigo": "PROD001",
    "nome": "Produto 1",
    "descricao": "Descrição do produto",
    "preco": 99.90,
    "estoque": 100,
    "categoria": {
        "id": 1,
        "nome": "Categoria 1"
    },
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
}
```

## 💰 Vendas

### Criar Venda

```http
POST /api/vendas
```

**Request Body:**
```json
{
    "cliente_id": 1,
    "items": [
        {
            "produto_id": 1,
            "quantidade": 2,
            "preco_unitario": 99.90
        }
    ],
    "forma_pagamento_id": 1,
    "parcelas": [
        {
            "numero": 1,
            "valor": 199.80,
            "vencimento": "2023-02-01"
        }
    ]
}
```

**Response (201 Created):**
```json
{
    "id": 1,
    "codigo": "V001",
    "cliente": {
        "id": 1,
        "nome": "Cliente 1"
    },
    "items": [
        {
            "produto": {
                "id": 1,
                "nome": "Produto 1"
            },
            "quantidade": 2,
            "preco_unitario": 99.90,
            "subtotal": 199.80
        }
    ],
    "valor_total": 199.80,
    "forma_pagamento": {
        "id": 1,
        "nome": "Cartão de Crédito"
    },
    "parcelas": [
        {
            "numero": 1,
            "valor": 199.80,
            "vencimento": "2023-02-01",
            "status": "pendente"
        }
    ],
    "created_at": "2023-01-01T00:00:00Z"
}
```

## 📊 Relatórios

### Exportar Relatório

```http
POST /api/reports/export/{report_type}
```

**Path Parameters:**
- `report_type`: Tipo do relatório (produtos, centros_custo, categorias)

**Query Parameters:**
- `format`: Formato de saída (pdf, excel)

**Request Body:**
```json
{
    "filters": {
        "search": "termo",
        "categoria_id": 1,
        "data_inicio": "2023-01-01",
        "data_fim": "2023-12-31",
        "status": "ativo"
    }
}
```

**Response (200 OK):**
```json
{
    "file_path": "/reports/produtos_20231231_235959.pdf"
}
```

## 👥 Clientes

### Listar Clientes

```http
GET /api/clientes
```

**Query Parameters:**
- `page`: Número da página (default: 1)
- `per_page`: Itens por página (default: 10)
- `search`: Termo de busca
- `status`: Status do cliente (ativo/inativo)

**Response (200 OK):**
```json
{
    "items": [
        {
            "id": 1,
            "nome": "Cliente 1",
            "email": "cliente@exemplo.com",
            "cpf_cnpj": "123.456.789-00",
            "telefone": "(11) 99999-9999",
            "endereco": {
                "cep": "12345-678",
                "logradouro": "Rua Exemplo",
                "numero": "123",
                "complemento": "Apto 1",
                "bairro": "Centro",
                "cidade": "São Paulo",
                "uf": "SP"
            },
            "status": "ativo",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        }
    ],
    "total": 100,
    "page": 1,
    "per_page": 10,
    "total_pages": 10
}
```

## 📝 Códigos de Erro

| Código | Descrição |
|--------|-----------|
| 400 | Bad Request - Requisição inválida |
| 401 | Unauthorized - Não autenticado |
| 403 | Forbidden - Sem permissão |
| 404 | Not Found - Recurso não encontrado |
| 422 | Unprocessable Entity - Validação falhou |
| 429 | Too Many Requests - Rate limit excedido |
| 500 | Internal Server Error - Erro interno |

### Exemplo de Erro

```json
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Erro de validação",
        "details": [
            {
                "field": "email",
                "message": "Email inválido"
            }
        ]
    }
}
```

## 🔄 Rate Limiting

A API possui limite de requisições por IP/usuário:

- 100 requisições por minuto para endpoints públicos
- 1000 requisições por minuto para endpoints autenticados
- 50 requisições por minuto para endpoints de relatórios

Headers de resposta incluem:
- `X-RateLimit-Limit`: Limite total
- `X-RateLimit-Remaining`: Requisições restantes
- `X-RateLimit-Reset`: Timestamp de reset

## 📚 Webhooks

### Configurar Webhook

```http
POST /api/webhooks
```

**Request Body:**
```json
{
    "url": "https://seu-dominio.com/webhook",
    "events": ["venda.created", "venda.updated"],
    "secret": "seu_secret_key"
}
```

**Response (201 Created):**
```json
{
    "id": "whk_123",
    "url": "https://seu-dominio.com/webhook",
    "events": ["venda.created", "venda.updated"],
    "created_at": "2023-01-01T00:00:00Z"
}
```

### Formato do Payload

```json
{
    "id": "evt_123",
    "type": "venda.created",
    "created_at": "2023-01-01T00:00:00Z",
    "data": {
        "venda_id": 1,
        "status": "concluida",
        "valor_total": 199.80
    }
}
```

## 🔒 CORS

A API suporta CORS com as seguintes configurações:

- Origens permitidas: Configurável por ambiente
- Métodos permitidos: GET, POST, PUT, DELETE, OPTIONS
- Headers permitidos: Content-Type, Authorization
- Credentials: true
- Max age: 86400 (24 horas)

## 📦 Versionamento

A API é versionada via URL:
- v1: `/api/v1/` (atual)
- v2: `/api/v2/` (beta)

## 📄 OpenAPI/Swagger

Documentação interativa disponível em:
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json` 