# Exportação de Relatórios - Guia Rápido

## Uso Básico

```python
from app.utils.export import create_report_exporter

# Criar exportador
exporter = create_report_exporter()

# Exportar PDF
pdf_file = await exporter.export_to_pdf(
    data=dados,
    template_name="base_report.html",
    output_filename="relatorio.pdf",
    title="Meu Relatório"
)

# Exportar Excel
excel_file = await exporter.export_to_excel(
    data=dados,
    output_filename="relatorio.xlsx",
    sheet_name="Dados"
)
```

## Endpoint da API

```python
POST /api/reports/export/{report_type}
```

Tipos: `produtos`, `centros_custo`, `categorias`
Formatos: `pdf`, `excel`

## Filtros

```python
filters = {
    "search": "termo",
    "categoria_id": 1,
    "data_inicio": "2023-01-01",
    "data_fim": "2023-12-31",
    "status": "ativo"
}
```

## Requisitos

- Python 3.8+
- wkhtmltopdf
- Dependências: pandas, pdfkit, jinja2, openpyxl

## Estrutura de Dados

```python
# Produtos
{
    "Código": "123",
    "Nome": "Produto",
    "Categoria": "Cat 1",
    "Preço": "R$ 99,90",
    "Estoque": 10
}

# Centros de Custo
{
    "Código": "CC001",
    "Nome": "Centro 1",
    "Descrição": "Desc",
    "Status": "Ativo"
}

# Categorias
{
    "Código": "CAT1",
    "Nome": "Categoria 1",
    "Descrição": "Desc",
    "Produtos": 5
}
```

## Troubleshooting Rápido

1. PDF não gera:
   - Instale wkhtmltopdf
   - Configure PATH

2. Excel com erro:
   - Verifique formato dos dados
   - Limite de 1M linhas

3. Template não encontrado:
   - Verifique pasta templates/reports/
   - Nome correto do arquivo

## Links Úteis

- Documentação completa: `docs/reports.md`
- Testes: `tests/test_reports.py`
- Template base: `templates/reports/base_report.html` 