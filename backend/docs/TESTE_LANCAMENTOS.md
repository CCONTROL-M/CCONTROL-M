# Servidor de Teste para Lançamentos Financeiros

Para facilitar o desenvolvimento e testes da API de lançamentos financeiros, foi criado um servidor de teste simples que implementa as principais funcionalidades da rota `/api/v1/lancamentos`.

## Como Executar o Servidor de Teste

1. Navegue até o diretório `backend`:

```bash
cd backend
```

2. Execute o servidor de teste:

```bash
python test_server.py
```

O servidor será iniciado em `http://localhost:8000`.

## Endpoints Disponíveis

### 1. Verificação de Saúde

**Endpoint:** `GET /health`

**Exemplo de Uso:**

```bash
# Usando curl
curl -X GET "http://localhost:8000/health"

# Usando PowerShell
Invoke-RestMethod -Uri 'http://localhost:8000/health' -Method GET
```

**Resposta:**

```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

### 2. Listar Lançamentos Financeiros

**Endpoint:** `GET /api/v1/lancamentos`

**Parâmetros de Query:**

| Parâmetro | Tipo | Obrigatório | Descrição | Exemplo |
|-----------|------|-------------|-----------|---------|
| id_empresa | UUID | Sim | ID da empresa | `3fa85f64-5717-4562-b3fc-2c963f66afa6` |
| tipo | String | Não | Filtrar por tipo (RECEITA, DESPESA) | `DESPESA` |
| status | String | Não | Filtrar por status (PENDENTE, PAGO, CANCELADO) | `PENDENTE` |
| page | Integer | Não | Página atual (padrão: 1) | `1` |
| page_size | Integer | Não | Itens por página (padrão: 10, máximo: 100) | `10` |

**Exemplos de Uso:**

1. **Listar todos os lançamentos:**

```bash
# Usando curl
curl -X GET "http://localhost:8000/api/v1/lancamentos?id_empresa=3fa85f64-5717-4562-b3fc-2c963f66afa6"

# Usando PowerShell
Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/lancamentos?id_empresa=3fa85f64-5717-4562-b3fc-2c963f66afa6' -Method GET
```

2. **Filtrar por tipo:**

```bash
# Usando curl
curl -X GET "http://localhost:8000/api/v1/lancamentos?id_empresa=3fa85f64-5717-4562-b3fc-2c963f66afa6&tipo=RECEITA"

# Usando PowerShell
Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/lancamentos?id_empresa=3fa85f64-5717-4562-b3fc-2c963f66afa6&tipo=RECEITA' -Method GET
```

3. **Filtrar por status:**

```bash
# Usando curl
curl -X GET "http://localhost:8000/api/v1/lancamentos?id_empresa=3fa85f64-5717-4562-b3fc-2c963f66afa6&status=PENDENTE"

# Usando PowerShell
Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/lancamentos?id_empresa=3fa85f64-5717-4562-b3fc-2c963f66afa6&status=PENDENTE' -Method GET
```

4. **Paginação personalizada:**

```bash
# Usando curl
curl -X GET "http://localhost:8000/api/v1/lancamentos?id_empresa=3fa85f64-5717-4562-b3fc-2c963f66afa6&page=2&page_size=5"

# Usando PowerShell
Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/lancamentos?id_empresa=3fa85f64-5717-4562-b3fc-2c963f66afa6&page=2&page_size=5' -Method GET
```

## Dados de Teste

O servidor de teste gera automaticamente 20 lançamentos de teste com as seguintes características:

- Alternância entre RECEITA e DESPESA
- Status variados (PENDENTE, PAGO, CANCELADO)
- Valores incrementais (100, 200, 300, etc.)
- Datas distribuídas ao longo do ano 2023

## Personalização

O arquivo `test_server.py` pode ser modificado para adicionar mais funcionalidades ou ajustar o comportamento existente:

- Adicionar mais filtros
- Alterar a quantidade ou formato dos dados de teste
- Implementar novas rotas
- Adicionar validação de parâmetros

## Integração com o Projeto Principal

Este servidor de teste foi desenvolvido como solução temporária enquanto a implementação na aplicação principal é concluída. Os principais problemas que estão sendo resolvidos no aplicativo principal incluem:

1. Configuração correta do router em `app/routers/lancamentos.py`
2. Importação e inclusão do router em `app/routers/__init__.py`
3. Mapeamento correto das rotas na aplicação principal
4. Configuração do RLS do Supabase
5. Implementação da lógica de negócios no service e repository

Quando a implementação estiver completa no aplicativo principal, o servidor de teste não será mais necessário, e toda a funcionalidade estará disponível na API padrão. 