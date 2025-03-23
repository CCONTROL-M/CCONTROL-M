# Camada de Serviços - CCONTROL-M

Este diretório contém a camada de serviços do sistema CCONTROL-M, responsável pela implementação da lógica de negócio da aplicação.

## Estrutura

A estrutura de serviços foi reorganizada para seguir boas práticas de modularização:

- **Serviços Simples**: Implementados como um único arquivo `[nome]_service.py`
- **Serviços Complexos**: Implementados como pacotes em pastas específicas (exemplo: `/venda`)

## Padrão para Serviços Complexos

Serviços complexos são organizados como pacotes com a seguinte estrutura:

```
services/
└── nome_servico/
    ├── __init__.py            # Exporta as classes principais do pacote
    ├── nome_servico.py        # Implementa a classe principal (funciona como fachada)
    └── nome_servico_xpto.py   # Implementa funcionalidades específicas
```

### Exemplo: Serviço de Vendas

O serviço de vendas foi modularizado para separar responsabilidades:

```
services/
└── venda/
    ├── __init__.py            # Exporta VendaService e outras classes
    ├── venda_service.py       # Classe principal que coordena os outros serviços
    ├── venda_query_service.py # Serviço para consultas e listagens 
    ├── venda_item_service.py  # Serviço para gerenciamento de itens
    └── venda_status_service.py # Serviço para controle de status
```

## Princípios de Design

1. **Separação de Responsabilidades**: Cada serviço deve ter uma responsabilidade bem definida
2. **Princípio da Fachada**: A classe principal serve como ponto de entrada unificado
3. **Injeção de Dependências**: Dependências são injetadas via constructor
4. **Regras de Negócio Centralizadas**: Validações e regras ficam nos serviços, não nos repositórios

## Como Implementar Novos Serviços

### Para Serviços Simples

Crie um arquivo `novo_service.py` seguindo o padrão:

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.repositories.novo_repository import NovoRepository

class NovoService:
    def __init__(
        self,
        session: AsyncSession = Depends(get_async_session)
    ):
        self.repository = NovoRepository(session)
        
    async def metodo_exemplo(self):
        # Implementação
        pass
```

### Para Serviços Complexos

1. Crie uma pasta com o nome do serviço e os arquivos necessários
2. Implemente a fachada principal e os serviços especializados
3. Exporte as classes no arquivo `__init__.py`

## Quando Modularizar um Serviço

Considere modularizar um serviço quando:

1. Tiver mais de 300 linhas de código
2. Implementar múltiplas responsabilidades distintas
3. Conter muitos métodos (mais de 10-15)
4. Existirem grupos de métodos relacionados que podem ser agrupados 