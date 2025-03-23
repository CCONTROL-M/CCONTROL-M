# Plano de Refatoração de Testes CCONTROL-M

Este documento apresenta o plano de ação para reorganizar os testes duplicados e melhorar a estrutura de testes do projeto.

## Problemas Identificados

1. **Duplicação de Diretórios**: Existem duas pastas de testes (`/app/tests` e `/tests`)
2. **Testes Duplicados**: Alguns testes aparecem em vários lugares
3. **Organização Inconsistente**: Falta de padronização na estrutura
4. **Pastas Vazias**: Diretórios criados mas sem conteúdo

## Nova Estrutura Proposta

```
/backend/tests/
├── unit/                  # Testes unitários
│   ├── repositories/      # Testes específicos de repositórios  
│   ├── services/          # Testes específicos de serviços
│   └── schemas/           # Testes de validação de schemas
├── integration/           # Testes de integração
│   ├── api/               # Testes das APIs
│   └── db/                # Testes de integração com banco de dados
├── e2e/                   # Testes end-to-end
└── fixtures/              # Dados de teste compartilhados
```

## Prioridades de Migração

1. **Fase 1 - Consolidação de Diretórios**
   - Mover todos os testes de `/app/tests` para `/tests`
   - Eliminar a pasta `/app/tests`

2. **Fase 2 - Reorganização por Camada**
   - Migrar testes para as pastas adequadas
   - Seguir padrão: `test_[nome_arquivo]_[parte_testada].py`

3. **Fase 3 - Eliminação de Duplicação**
   - Identificar e consolidar testes duplicados
   - Manter a versão mais completa/recente

## Convenções de Nomenclatura

- **Arquivos**: `test_[nome_módulo].py`
- **Classes**: `Test[NomeFuncionalidade]`
- **Métodos**: `test_[ação]_[cenário]`

Exemplo:
```python
# test_produto_service.py
class TestProdutoService:
    def test_criar_produto_valido(self):
        # ...
    
    def test_criar_produto_invalido(self):
        # ...
```

## Mapeamento de Testes Duplicados

| Arquivo Original | Novo Local | Observações |
|------------------|------------|-------------|
| `app/tests/test_duplicados.md` | Remover após migração | Documento de análise |
| `tests/test_clientes.py` | `tests/unit/services/test_cliente_service.py` | Migrar testes unitários |
| `tests/test_clientes_router.py` | `tests/integration/api/test_cliente_api.py` | Migrar testes de API |
| `tests/test_fornecedores.py` | `tests/unit/services/test_fornecedor_service.py` | Migrar testes unitários |
| `tests/routers/test_lancamentos.py` | `tests/integration/api/test_lancamento_api.py` | Migrar testes de API |

## Responsabilidades e Prazos

A primeira fase de consolidação deve ser concluída o mais rapidamente possível, pois a duplicação está causando problemas de inicialização. As demais fases podem ser implementadas gradualmente. 