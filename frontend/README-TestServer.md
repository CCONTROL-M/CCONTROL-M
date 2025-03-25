# Configuração do Servidor de Teste

## Visão Geral

O frontend do CCONTROL-M foi temporariamente configurado para se comunicar com o servidor de teste na **porta 8002** em vez do backend principal. Esta configuração permite o desenvolvimento da interface sem depender da conclusão do backend real.

## Alterações Realizadas

1. **Configuração do Axios (frontend/src/services/api.ts)**:
   - URL base alterada para apontar diretamente para `http://localhost:8002/api/v1`
   - Endpoint de verificação de saúde alterado para usar axios direto com `http://localhost:8002/health`
   - Comentada a utilização da variável de ambiente `VITE_API_URL` no arquivo `.env`
   - Adicionado aviso no console indicando o uso do servidor de teste

2. **Serviço de Lançamentos (frontend/src/services/lancamentoService.ts)**:
   - Caminhos das APIs ajustados para não incluir o prefixo `/api/v1/` (já incluído na baseURL)
   - Mantido o parâmetro `id_empresa` para todas as requisições (exigido pelo servidor de teste)
   - Tratamento ajustado para a resposta paginada do servidor de teste

3. **Serviço de Relatórios (frontend/src/services/relatorioService.ts)**:
   - Caminhos das APIs ajustados para não incluir o prefixo `/api/v1/`
   - Removido qualquer fallback automático para mock em caso de falha da API

## Servidor de Teste

O servidor de teste está implementado em `backend/app/test_server.py` e fornece:

- Endpoints completos para operações CRUD de lançamentos financeiros
- Dados simulados que refletem a estrutura esperada do backend real
- Interface Swagger em `http://localhost:8002/docs` para testar APIs

Para iniciar o servidor de teste:
```bash
cd backend
python -m app.test_server
```

## Como Reverter para o Backend Real

Quando o backend real estiver pronto, será necessário:

1. Restaurar o código original em `frontend/src/services/api.ts`:
   - Alterar a URL base de volta para usar a variável de ambiente: `import.meta.env.VITE_API_URL || 'http://localhost:8000'`
   - Restaurar o endpoint de verificação de saúde para `/v1/health`
   - Descomentar a variável `VITE_API_URL` no arquivo `.env`

2. Revisar os caminhos das APIs nos serviços:
   - `frontend/src/services/lancamentoService.ts`
   - `frontend/src/services/relatorioService.ts`
   - Outros serviços que foram modificados

3. Remover o ID de empresa fixo e usar o valor do contexto de autenticação

## Exemplo de Uso

Ao usar este servidor de teste, todas as chamadas de API do frontend deverão funcionar normalmente com o servidor em http://localhost:8002/api/v1, mas os dados retornados serão simulados. Operações de criação, atualização e exclusão não afetarão um banco de dados real.

## Histórico de Atualizações

- **24/03/2025**: Configuração inicial para o servidor de teste
- **25/03/2025**: Atualização com novos endpoints e ajustes nos serviços 