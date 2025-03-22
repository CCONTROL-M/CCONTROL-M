# Guia de Contribuição - CCONTROL-M

## 🌟 Introdução

Obrigado por considerar contribuir para o CCONTROL-M! Este documento fornece as diretrizes e melhores práticas para contribuir com o projeto.

## 📋 Código de Conduta

Este projeto segue um Código de Conduta que todos os contribuidores devem respeitar. Por favor, leia [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) antes de contribuir.

## 🚀 Como Contribuir

### 1. Preparando o Ambiente

1. Fork o repositório
2. Clone seu fork:
```bash
git clone https://github.com/seu-usuario/CCONTROL-M.git
cd CCONTROL-M
```

3. Adicione o upstream:
```bash
git remote add upstream https://github.com/CCONTROL-M/CCONTROL-M.git
```

4. Crie uma branch para sua contribuição:
```bash
git checkout -b feature/nome-da-feature
```

### 2. Desenvolvimento

#### Padrões de Código

- Siga o PEP 8 para Python
- Use Black para formatação
- Docstrings no estilo Google
- Type hints obrigatórios
- Testes unitários para novas funcionalidades
- Comentários em português do Brasil

#### Commits

- Use commits semânticos:
  - `feat:` Nova funcionalidade
  - `fix:` Correção de bug
  - `docs:` Documentação
  - `style:` Formatação
  - `refactor:` Refatoração
  - `test:` Testes
  - `chore:` Tarefas de manutenção

Exemplo:
```bash
git commit -m "feat: Implementa sistema de exportação de relatórios"
```

#### Testes

- Escreva testes para novas funcionalidades
- Mantenha a cobertura de testes acima de 80%
- Execute a suite de testes antes de submeter:
```bash
pytest
```

### 3. Submetendo Contribuições

1. Atualize sua branch:
```bash
git fetch upstream
git rebase upstream/main
```

2. Execute os testes:
```bash
pytest
```

3. Push para seu fork:
```bash
git push origin feature/nome-da-feature
```

4. Abra um Pull Request

#### Template do Pull Request

```markdown
## Descrição
Descreva as mudanças realizadas

## Tipo de Mudança
- [ ] Bug fix
- [ ] Nova feature
- [ ] Breaking change
- [ ] Documentação

## Checklist
- [ ] Testes adicionados/atualizados
- [ ] Documentação atualizada
- [ ] Código formatado com Black
- [ ] Type hints adicionados
- [ ] Testes passando
```

### 4. Revisão de Código

- Responda aos comentários dos revisores
- Faça as alterações solicitadas
- Mantenha a discussão profissional e construtiva
- Atualize a branch quando necessário

## 📝 Diretrizes de Código

### Python

```python
from typing import List, Optional
from datetime import datetime

class UserService:
    """Serviço para operações de usuário."""

    def __init__(self, db: Session):
        """Inicializa o serviço.

        Args:
            db: Sessão do banco de dados
        """
        self.db = db

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Busca usuário por ID.

        Args:
            user_id: ID do usuário

        Returns:
            Objeto User se encontrado
        """
        return await User.get(self.db, id=user_id)
```

### SQL

```sql
-- Use CTE para queries complexas
WITH ranked_sales AS (
    SELECT 
        product_id,
        SUM(quantity) as total_quantity,
        RANK() OVER (ORDER BY SUM(quantity) DESC) as rank
    FROM sales
    GROUP BY product_id
)
SELECT * FROM ranked_sales WHERE rank <= 10;
```

### Testes

```python
def test_calculate_total():
    """Testa cálculo de total com diferentes cenários."""
    items = [
        {"price": 100, "quantity": 2},
        {"price": 50, "quantity": 1}
    ]
    
    assert calculate_total(items) == 250
    assert calculate_total(items, tax_rate=0.1) == 275
    assert calculate_total(items, discount=50) == 200
```

## 🏗️ Arquitetura

### Estrutura de Diretórios

```
CCONTROL-M/
├── backend/
│   ├── alembic/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── utils/
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
└── docs/
```

### Padrões de Projeto

- Repository Pattern para acesso a dados
- Service Layer para lógica de negócio
- Factory Pattern para criação de objetos
- Strategy Pattern para comportamentos variáveis
- Observer Pattern para eventos

## 🔒 Segurança

### Diretrizes

1. Nunca commite secrets
2. Use variáveis de ambiente
3. Valide todas as entradas
4. Use prepared statements
5. Implemente rate limiting
6. Mantenha dependências atualizadas

### Exemplos

```python
# ❌ ERRADO
password = "senha123"  # Hard-coded
query = f"SELECT * FROM users WHERE email = '{email}'"  # SQL Injection

# ✅ CERTO
password = os.getenv("DB_PASSWORD")
query = select(User).where(User.email == email)
```

## 📚 Documentação

### Tipos de Documentação

1. Docstrings
2. README.md
3. Documentação da API
4. Guias de usuário
5. Documentação técnica

### Exemplo de Docstring

```python
def calculate_total(
    items: List[dict],
    tax_rate: float = 0.0,
    discount: float = 0.0
) -> float:
    """Calcula total com taxa e desconto.

    Args:
        items: Lista de items com preço e quantidade
        tax_rate: Percentual de taxa
        discount: Valor do desconto

    Returns:
        Valor total calculado

    Raises:
        ValueError: Se tax_rate for negativo
    """
    if tax_rate < 0:
        raise ValueError("Taxa não pode ser negativa")
    
    subtotal = sum(item["price"] * item["quantity"] for item in items)
    total = subtotal * (1 + tax_rate) - discount
    return round(total, 2)
```

## 🐛 Reportando Bugs

### Template de Issue

```markdown
## Descrição do Bug
Descreva o bug de forma clara e concisa

## Como Reproduzir
1. Vá para '...'
2. Clique em '....'
3. Role até '....'
4. Veja o erro

## Comportamento Esperado
Descreva o que deveria acontecer

## Screenshots
Se aplicável, adicione screenshots

## Ambiente
- OS: [Windows/Linux/Mac]
- Browser: [Chrome/Firefox/Safari]
- Versão: [v1.0.0]

## Contexto Adicional
Adicione qualquer outro contexto sobre o problema
```

## 🎯 Sugestões de Features

### Template de Feature Request

```markdown
## Problema Relacionado
Descreva o problema que sua feature resolve

## Solução Proposta
Descreva a solução que você gostaria

## Alternativas Consideradas
Descreva alternativas que você considerou

## Contexto Adicional
Adicione qualquer outro contexto ou screenshots
```

## 📅 Processo de Release

1. Atualize a versão em `pyproject.toml`
2. Atualize o CHANGELOG.md
3. Crie uma tag de versão
4. Push para main
5. GitHub Actions fará o deploy

## 🤝 Comunidade

- Discord: [Link]
- Forum: [Link]
- Stack Overflow: Tag [ccontrol-m]
- Twitter: [@ccontrolm]

## 📞 Contato

- Email: contribuicoes@ccontrol-m.com
- Discord: [Server Link]
- GitHub Discussions 