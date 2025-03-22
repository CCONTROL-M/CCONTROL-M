# Catálogo de Erros - CCONTROL-M

Este documento lista todos os códigos de erro que podem ser retornados pela API do CCONTROL-M, suas causas e soluções recomendadas.

## Formato dos Erros

Todas as respostas de erro seguem um formato consistente:

```json
{
  "status_code": 400,
  "message": "Mensagem de erro detalhada",
  "error_code": "ERROR_CODE",
  "details": {
    "campo_com_problema": ["Descrição do problema"],
    "additional_info": "Informações adicionais quando disponíveis"
  }
}
```

## Códigos de Erro HTTP

| Código HTTP | Descrição                | Quando Ocorre                                          |
|-------------|--------------------------|--------------------------------------------------------|
| 400         | Bad Request              | Requisição mal formada ou dados inválidos              |
| 401         | Unauthorized             | Credenciais ausentes ou inválidas                      |
| 403         | Forbidden                | Sem permissão para acessar o recurso                   |
| 404         | Not Found                | Recurso não encontrado                                 |
| 409         | Conflict                 | Conflito com o estado atual do recurso                 |
| 422         | Unprocessable Entity     | Entidade não pôde ser processada (validação falhou)    |
| 429         | Too Many Requests        | Limite de requisições excedido                         |
| 500         | Internal Server Error    | Erro interno do servidor                               |
| 503         | Service Unavailable      | Serviço temporariamente indisponível                   |

## Códigos de Erro Específicos

### Autenticação e Autorização (AUTH_*)

| Código de Erro           | Descrição                              | Solução                                                    |
|--------------------------|----------------------------------------|------------------------------------------------------------|
| AUTH_INVALID_CREDENTIALS | Credenciais inválidas                  | Verificar usuário e senha                                  |
| AUTH_TOKEN_EXPIRED       | Token de acesso expirado               | Renovar token usando refresh_token                         |
| AUTH_INVALID_TOKEN       | Token inválido ou mal formatado        | Gerar um novo token                                        |
| AUTH_INSUFFICIENT_PERM   | Permissões insuficientes               | Solicitar acesso ao recurso                                |
| AUTH_ACCOUNT_LOCKED      | Conta bloqueada após tentativas        | Aguardar ou contatar administrador                         |
| AUTH_ACCOUNT_INACTIVE    | Conta inativa ou não verificada        | Ativar conta ou verificar e-mail                           |

### Validação de Dados (VAL_*)

| Código de Erro           | Descrição                              | Solução                                                    |
|--------------------------|----------------------------------------|------------------------------------------------------------|
| VAL_REQUIRED_FIELD       | Campo obrigatório ausente              | Incluir o campo obrigatório na requisição                  |
| VAL_INVALID_FORMAT       | Formato de dados inválido              | Corrigir o formato do campo especificado                   |
| VAL_INVALID_LENGTH       | Comprimento inválido                   | Respeitar os limites de comprimento do campo               |
| VAL_INVALID_VALUE        | Valor fora do intervalo permitido      | Enviar valor dentro do intervalo aceitável                 |
| VAL_INVALID_DATE         | Data inválida ou fora do período       | Verificar formato da data e período permitido              |
| VAL_INVALID_DOCUMENT     | Documento inválido (CPF/CNPJ)          | Verificar número e dígito verificador                      |

### Recursos (RES_*)

| Código de Erro           | Descrição                              | Solução                                                    |
|--------------------------|----------------------------------------|------------------------------------------------------------|
| RES_NOT_FOUND            | Recurso não encontrado                 | Verificar ID ou criar o recurso                            |
| RES_ALREADY_EXISTS       | Recurso já existe                      | Verificar cadastro duplicado ou usar update                |
| RES_LOCKED               | Recurso bloqueado para edição          | Aguardar liberação ou contatar administrador               |
| RES_RELATED_EXISTS       | Existem recursos relacionados          | Remover dependências antes ou usar soft delete             |
| RES_INVALID_STATUS       | Status inválido para operação          | Verificar fluxo correto de status                          |
| RES_VERSION_CONFLICT     | Conflito de versões (concorrência)     | Obter versão mais recente e tentar novamente               |

### Negócio (BIZ_*)

| Código de Erro           | Descrição                              | Solução                                                    |
|--------------------------|----------------------------------------|------------------------------------------------------------|
| BIZ_INSUFFICIENT_STOCK   | Estoque insuficiente                   | Verificar disponibilidade de produtos                      |
| BIZ_INVALID_PAYMENT      | Pagamento inválido ou recusado         | Verificar dados de pagamento e saldo                       |
| BIZ_ORDER_COMPLETED      | Pedido já finalizado                   | Não é possível modificar pedido finalizado                 |
| BIZ_CREDIT_LIMIT         | Limite de crédito excedido             | Verificar limite de crédito do cliente                     |
| BIZ_INVALID_OPERATION    | Operação inválida pelo estado atual    | Verificar estado do recurso e operação                     |
| BIZ_INVALID_DISCOUNT     | Desconto acima do permitido            | Verificar política de descontos                            |

### Sistema (SYS_*)

| Código de Erro           | Descrição                              | Solução                                                    |
|--------------------------|----------------------------------------|------------------------------------------------------------|
| SYS_DATABASE_ERROR       | Erro de banco de dados                 | Tente novamente ou reporte o erro                          |
| SYS_INTEGRATION_ERROR    | Erro de integração com serviço externo | Verificar serviço ou tentar novamente                      |
| SYS_MAINTENANCE          | Sistema em manutenção                  | Tentar novamente mais tarde                                |
| SYS_RATE_LIMITED         | Limite de requisições excedido         | Aguardar e respeitar limites de API                        |
| SYS_RESOURCE_EXHAUSTED   | Recurso esgotado (cota, espaço)        | Liberação de recursos ou upgrade                           |
| SYS_INTERNAL_ERROR       | Erro interno do servidor               | Reportar o erro com detalhes                               |

## Exemplos de Erros Comuns

### Autenticação Inválida

```json
{
  "status_code": 401,
  "message": "Credenciais inválidas",
  "error_code": "AUTH_INVALID_CREDENTIALS",
  "details": {
    "info": "Usuário ou senha incorretos"
  }
}
```

### Validação de Dados

```json
{
  "status_code": 422,
  "message": "Erro de validação",
  "error_code": "VAL_INVALID_FORMAT",
  "details": {
    "cnpj": ["CNPJ com formato inválido"],
    "email": ["Formato de e-mail inválido"]
  }
}
```

### Recurso Não Encontrado

```json
{
  "status_code": 404,
  "message": "Recurso não encontrado",
  "error_code": "RES_NOT_FOUND",
  "details": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "type": "cliente"
  }
}
```

### Limite de Requisições

```json
{
  "status_code": 429,
  "message": "Muitas requisições",
  "error_code": "SYS_RATE_LIMITED",
  "details": {
    "limit": 100,
    "period": "1 minuto",
    "retry_after": 30
  }
}
```

## Como Reportar Erros

Ao encontrar um erro não documentado ou inesperado, por favor, encaminhe as seguintes informações para suporte@ccontrol-m.com.br:

1. Código de erro e mensagem completa
2. Data e hora da ocorrência
3. Endpoint e método utilizado
4. Dados da requisição (sem informações sensíveis)
5. ID da requisição (se disponível no header X-Request-ID)

## Monitoramento e Resolução

A equipe do CCONTROL-M monitora ativamente os erros reportados e trabalha para corrigi-los nas próximas atualizações. Erros críticos são tratados com prioridade. 