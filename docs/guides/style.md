# Guia de Estilo - CCONTROL-M

## 🎨 Visão Geral

Este guia define os padrões de código e estilo para o projeto CCONTROL-M. Seguir estas diretrizes é essencial para manter a consistência e qualidade do código.

## 📝 Princípios Gerais

1. **Clareza**: Código claro é melhor que código esperto
2. **Consistência**: Siga os padrões estabelecidos
3. **Simplicidade**: Evite complexidade desnecessária
4. **Documentação**: Documente o necessário, não o óbvio
5. **Testabilidade**: Escreva código testável

## 🐍 Python

### Formatação

- Use Black com configuração padrão
- Linha máxima de 88 caracteres
- Use 4 espaços para indentação
- Uma linha em branco entre funções
- Duas linhas em branco entre classes

```python
# ✅ CERTO
def calculate_total(items: List[dict]) -> float:
    """Calcula o total dos items."""
    return sum(item["price"] * item["quantity"] for item in items)


def apply_discount(total: float, discount: float) -> float:
    """Aplica desconto ao total."""
    return total * (1 - discount)


class OrderService:
    """Serviço para gerenciar pedidos."""

    def __init__(self, db: Session):
        self.db = db
```

### Imports

- Agrupe imports em: stdlib, third-party, local
- Ordene alfabeticamente dentro dos grupos
- Use imports absolutos

```python
# ✅ CERTO
from datetime import datetime
from typing import List, Optional

import pandas as pd
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
```

### Nomeação

- Classes: PascalCase
- Funções/variáveis: snake_case
- Constantes: SCREAMING_SNAKE_CASE
- Módulos: snake_case
- Type vars: PascalCase

```python
# ✅ CERTO
MAX_CONNECTIONS = 100
DEFAULT_TIMEOUT = 30

class UserService:
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        pass

def calculate_total_price(items: List[dict]) -> float:
    pass

# ❌ ERRADO
maxConnections = 100
def GetUserById(userId):
    pass
```

### Type Hints

- Use type hints em todas as funções
- Use Optional para valores que podem ser None
- Use Union para múltiplos tipos
- Use TypeVar para genéricos

```python
# ✅ CERTO
from typing import Optional, List, Union, TypeVar

T = TypeVar("T")

def get_first_item(items: List[T]) -> Optional[T]:
    return items[0] if items else None

def process_data(data: Union[str, bytes]) -> dict:
    pass

# ❌ ERRADO
def get_user(id):
    pass
```

### Docstrings

- Use estilo Google
- Inclua Args, Returns, Raises quando relevante
- Seja conciso mas completo

```python
# ✅ CERTO
def calculate_total(
    items: List[dict],
    tax_rate: float = 0.0
) -> float:
    """Calcula o total dos items com taxa.

    Args:
        items: Lista de items com preço e quantidade
        tax_rate: Taxa percentual a ser aplicada

    Returns:
        Total calculado com taxa

    Raises:
        ValueError: Se tax_rate for negativo
    """
    if tax_rate < 0:
        raise ValueError("Taxa não pode ser negativa")
    
    subtotal = sum(item["price"] * item["quantity"] for item in items)
    return subtotal * (1 + tax_rate)
```

### Classes

- Use dataclasses quando apropriado
- Implemente `__str__` e `__repr__`
- Use property para getters/setters
- Evite herança múltipla

```python
# ✅ CERTO
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Order:
    id: int
    total: float
    created_at: datetime

    def __str__(self) -> str:
        return f"Order({self.id}: R${self.total:.2f})"

    @property
    def is_paid(self) -> bool:
        return self.status == "paid"
```

### Exceções

- Crie exceções específicas
- Use context managers
- Capture exceções específicas
- Documente exceções

```python
# ✅ CERTO
class OrderError(Exception):
    """Base exception for order operations."""
    pass

class InvalidOrderStatus(OrderError):
    """Raised when order status transition is invalid."""
    pass

try:
    with transaction.atomic():
        order.process()
except InvalidOrderStatus as e:
    logger.error("Failed to process order: %s", str(e))
    raise
```

## 🗃️ SQL

### Queries

- Use CTEs para queries complexas
- Nomeie índices e constraints
- Use prepared statements
- Comente queries complexas

```sql
-- ✅ CERTO
WITH monthly_sales AS (
    SELECT 
        DATE_TRUNC('month', sale_date) as month,
        SUM(total) as total_sales
    FROM sales
    GROUP BY 1
)
SELECT 
    month,
    total_sales,
    LAG(total_sales) OVER (ORDER BY month) as prev_month_sales
FROM monthly_sales
ORDER BY month;

-- Índices
CREATE INDEX idx_sales_date_total 
ON sales (sale_date, total);

-- Constraints
ALTER TABLE orders
ADD CONSTRAINT fk_orders_users
FOREIGN KEY (user_id) REFERENCES users(id);
```

## 📊 Banco de Dados

### Tabelas

- Use snake_case para nomes
- Adicione comentários
- Use tipos apropriados
- Defina constraints

```sql
-- ✅ CERTO
CREATE TABLE user_orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    total DECIMAL(10,2) NOT NULL CHECK (total >= 0),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_status CHECK (
        status IN ('pending', 'paid', 'cancelled')
    )
);

COMMENT ON TABLE user_orders IS 'Pedidos dos usuários';
COMMENT ON COLUMN user_orders.status IS 'Status atual do pedido';
```

## 🧪 Testes

### Estrutura

- Um arquivo de teste por módulo
- Use fixtures quando apropriado
- Agrupe testes relacionados
- Nomeie testes descritivamente

```python
# ✅ CERTO
import pytest
from datetime import datetime

@pytest.fixture
def sample_order():
    return Order(
        id=1,
        total=100.0,
        created_at=datetime.now()
    )

class TestOrderService:
    def test_calculate_total_with_tax(self, sample_order):
        """Testa cálculo de total com taxa."""
        service = OrderService()
        assert service.calculate_total(sample_order, tax=0.1) == 110.0

    def test_invalid_tax_raises_error(self, sample_order):
        """Testa que taxa negativa gera erro."""
        with pytest.raises(ValueError):
            OrderService().calculate_total(sample_order, tax=-0.1)
```

## 📝 Logs

### Formato

- Use structured logging
- Inclua contexto relevante
- Use níveis apropriados
- Evite dados sensíveis

```python
# ✅ CERTO
import structlog

logger = structlog.get_logger()

def process_order(order_id: int):
    logger.info("processing_order", order_id=order_id)
    try:
        # Processamento
        logger.debug(
            "order_details",
            order_id=order_id,
            total=total,
            items_count=len(items)
        )
    except Exception as e:
        logger.error(
            "order_processing_failed",
            order_id=order_id,
            error=str(e)
        )
        raise
```

## 🔒 Segurança

### Boas Práticas

- Nunca exponha secrets no código
- Use prepared statements
- Valide todas as entradas
- Escape output HTML
- Use HTTPS sempre

```python
# ✅ CERTO
from markupsafe import escape
from app.core.config import settings

# Secrets em variáveis de ambiente
database_url = settings.DATABASE_URL

# Prepared statements
def get_user(email: str):
    return db.execute(
        select(User).where(User.email == email)
    ).scalar_one_or_none()

# Escape HTML
@app.get("/user/{user_id}")
def user_profile(user_id: int):
    user = get_user(user_id)
    return HTMLResponse(f"<div>{escape(user.name)}</div>")
```

## 📚 Documentação

### Padrões

- README.md em cada diretório
- Docstrings em todas as funções/classes
- Comentários para código complexo
- Exemplos de uso
- Diagramas quando necessário

```markdown
# Módulo de Pedidos

## Descrição
Gerencia o ciclo de vida dos pedidos.

## Uso
```python
from app.orders import OrderService

service = OrderService()
order = service.create_order(items=[...])
```

## Classes
- `Order`: Modelo de pedido
- `OrderService`: Serviço de pedidos
- `OrderRepository`: Repositório de pedidos
```

## 🔄 Git

### Commits

- Use commits semânticos
- Mensagens em português
- Limite de 72 caracteres
- Descreva o "por quê"

```bash
# ✅ CERTO
git commit -m "feat: Implementa sistema de exportação de relatórios

Adiciona suporte para exportação em PDF e Excel,
com opções de filtros e formatação customizada."

# ❌ ERRADO
git commit -m "fixes"
```

### Branches

- feature/nome-da-feature
- fix/nome-do-fix
- docs/nome-da-doc
- refactor/nome-do-refactor

```bash
# ✅ CERTO
git checkout -b feature/relatorios-pdf
git checkout -b fix/calculo-total
git checkout -b docs/api-endpoints

# ❌ ERRADO
git checkout -b new-stuff
```

## 🎨 Frontend

### Componentes

- Um componente por arquivo
- Props tipadas
- Documentação com JSDoc
- Testes unitários

```typescript
// ✅ CERTO
interface OrderProps {
    id: number;
    total: number;
    status: 'pending' | 'paid' | 'cancelled';
    onStatusChange: (id: number, status: string) => void;
}

/**
 * Exibe detalhes de um pedido com opções de atualização.
 */
export function OrderDetails({
    id,
    total,
    status,
    onStatusChange
}: OrderProps) {
    return (
        <div className="order-details">
            <h2>Pedido #{id}</h2>
            <p>Total: R${total.toFixed(2)}</p>
            <StatusSelect
                value={status}
                onChange={(newStatus) => onStatusChange(id, newStatus)}
            />
        </div>
    );
}
```

## 📱 Mobile

### React Native

- Use Expo quando possível
- Componentes funcionais
- Hooks customizados
- Estilos com StyleSheet

```typescript
// ✅ CERTO
import { StyleSheet } from 'react-native';

export function ProductCard({ product }) {
    return (
        <View style={styles.card}>
            <Image
                source={{ uri: product.image }}
                style={styles.image}
            />
            <Text style={styles.title}>{product.name}</Text>
            <Text style={styles.price}>
                R${product.price.toFixed(2)}
            </Text>
        </View>
    );
}

const styles = StyleSheet.create({
    card: {
        padding: 16,
        borderRadius: 8,
        backgroundColor: '#fff',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
    },
    image: {
        width: '100%',
        height: 200,
        borderRadius: 4,
    },
    title: {
        fontSize: 16,
        fontWeight: 'bold',
        marginTop: 8,
    },
    price: {
        fontSize: 14,
        color: '#666',
        marginTop: 4,
    },
});
```

## 🔍 Code Review

### Checklist

1. **Funcionalidade**
   - Atende aos requisitos?
   - Casos de borda tratados?
   - Erros tratados?

2. **Código**
   - Segue o style guide?
   - Bem documentado?
   - Testado adequadamente?

3. **Performance**
   - Queries otimizadas?
   - Cache quando apropriado?
   - Recursos utilizados eficientemente?

4. **Segurança**
   - Inputs validados?
   - Dados sensíveis protegidos?
   - Autenticação/autorização correta?

## 📈 Métricas de Qualidade

- Cobertura de testes > 80%
- Complexidade ciclomática < 10
- Duplicação de código < 5%
- Dívida técnica < 5 dias
- Documentação atualizada

## 🔄 Processo de Review

1. **Auto-review**
   - Execute todos os testes
   - Verifique o style guide
   - Documente alterações

2. **Peer Review**
   - Pelo menos 1 aprovação
   - Comentários construtivos
   - Sugestões de melhorias

3. **Final Check**
   - CI/CD passou
   - Conflitos resolvidos
   - Documentação atualizada 