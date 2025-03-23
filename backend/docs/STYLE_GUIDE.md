# Guia de Estilo e Nomenclatura do CCONTROL-M

Este documento estabelece os padrões de nomenclatura e estilo a serem seguidos no desenvolvimento do sistema CCONTROL-M.

## Padrões de Nomenclatura

### Estrutura de arquivos e módulos

| Componente      | Padrão de Nomenclatura | Exemplo              | Observações                                |
|-----------------|------------------------|----------------------|--------------------------------------------|
| **Models**      | Singular               | `cliente.py`         | Representa uma entidade única              |
| **Schemas**     | Singular               | `cliente.py`         | Define a estrutura de uma entidade única   |
| **Repositories**| Singular + Repository  | `cliente_repository.py` | Acessa uma entidade no banco            |
| **Services**    | Singular + Service     | `cliente_service.py` | Lógica de negócio para uma entidade       |
| **Routers**     | Plural                 | `clientes.py`        | Endpoint API que gerencia múltiplas entidades |
| **Tabelas BD**  | Plural                 | `clientes`           | Armazena múltiplas instâncias da entidade  |

### Nomenclatura de funções

* **GET/Consulta**: Prefixo `get_`, `find_`, `list_`
* **CREATE**: Prefixo `create_`, `add_`
* **UPDATE**: Prefixo `update_`
* **DELETE**: Prefixo `delete_`, `remove_`

### Nomenclatura de variáveis

* Uso de `snake_case` para todas as variáveis
* Prefixo `id_` para identificadores primários (ex: `id_cliente`)
* Prefixo `id_` para chaves estrangeiras (ex: `id_empresa`)

### Nomenclatura de classes

* Uso de `PascalCase` para todas as classes
* Sufixos específicos por tipo:
  * Models: Nome da entidade (ex: `Cliente`)
  * Schemas: Nome da entidade + sufixo (ex: `ClienteCreate`, `ClienteResponse`)
  * Services: Nome da entidade + `Service` (ex: `ClienteService`)
  * Repositories: Nome da entidade + `Repository` (ex: `ClienteRepository`)

## Estrutura de Diretórios

```
backend/
├── app/
│   ├── models/          # Modelos SQLAlchemy (singular)
│   ├── schemas/         # Schemas Pydantic (singular)
│   ├── repositories/    # Repositórios de acesso a dados (singular)
│   ├── services/        # Serviços de lógica de negócios (singular)
│   │   └── [entidade]/  # Para serviços modularizados
│   ├── routers/         # Rotas API FastAPI (plural)
│   └── ...
├── migrations/          # Migrações de banco de dados
│   └── versions/        # Arquivos de migração específicos
└── ...
```

## Padrões de Código

### Imports

* Imports agrupados por fonte na seguinte ordem:
  1. Bibliotecas padrão Python
  2. Bibliotecas de terceiros
  3. Módulos da aplicação
* Separar grupos de imports com uma linha em branco
* Ordenar imports alfabeticamente dentro de cada grupo

### Docstrings

* Docstrings para todas as funções públicas
* Formato de docstring:
```python
def função_exemplo(param1: str, param2: int) -> bool:
    """
    Breve descrição da função.
    
    Args:
        param1: Descrição do primeiro parâmetro
        param2: Descrição do segundo parâmetro
        
    Returns:
        Descrição do valor de retorno
        
    Raises:
        ExceptionType: Descrição da exceção
    """
```

## Considerações sobre Refatoração

Durante a refatoração do código para seguir estes padrões:

1. Priorizar a consistência do padrão de nomenclatura
2. Atualizar referências e imports ao renomear arquivos
3. Assegurar que todas as migrações de banco de dados sejam atualizadas
4. Manter a retrocompatibilidade quando possível

Este guia de estilo deve ser seguido em todo o desenvolvimento do projeto CCONTROL-M. 