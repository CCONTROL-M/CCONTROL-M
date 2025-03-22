# Sistema de Exportação de Relatórios - CCONTROL-M

## Visão Geral

O sistema de exportação de relatórios do CCONTROL-M permite gerar relatórios em PDF e Excel com formatação profissional, suporte a filtros e múltiplos tipos de relatório.

## Requisitos

- Python 3.8+
- wkhtmltopdf instalado no sistema (para geração de PDFs)
- Dependências Python listadas em `requirements.txt`:
  - pandas>=2.0.0
  - pdfkit>=1.0.0
  - jinja2>=3.1.2
  - openpyxl>=3.1.2

## Instalação do wkhtmltopdf

### Windows
1. Baixe o instalador em: https://wkhtmltopdf.org/downloads.html
2. Execute o instalador
3. O executável será instalado em: `C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe`

### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install wkhtmltopdf
```

### macOS
```bash
brew install wkhtmltopdf
```

## Estrutura do Sistema

```
backend/
├── app/
│   ├── api/
│   │   └── endpoints/
│   │       └── reports.py      # Endpoints da API
│   │   ├── core/
│   │   │   └── pdf_config.py      # Configurações do PDF
│   │   ├── schemas/
│   │   │   └── reports.py         # Schemas do Pydantic
│   │   ├── templates/
│   │   │   └── reports/
│   │   │       └── base_report.html  # Template base
│   │   └── utils/
│   │       └── export.py          # Classe principal
│   └── tests/
│       └── test_reports.py        # Testes
```

## Tipos de Relatório Disponíveis

1. **Produtos** (`ReportType.PRODUTOS`)
   - Código
   - Nome
   - Categoria
   - Preço
   - Estoque
   - Última Atualização

2. **Centros de Custo** (`ReportType.CENTROS_CUSTO`)
   - Código
   - Nome
   - Descrição
   - Status
   - Criado em

3. **Categorias** (`ReportType.CATEGORIAS`)
   - Código
   - Nome
   - Descrição
   - Produtos
   - Criado em

## Uso da API

### Endpoint

```
POST /api/reports/export/{report_type}
```

### Parâmetros

- `report_type`: Tipo do relatório (`produtos`, `centros_custo`, `categorias`)
- `format`: Formato de saída (`pdf`, `excel`)
- `filters`: Filtros opcionais

### Exemplo de Requisição

```python
import requests

url = "http://localhost:8000/api/reports/export/produtos"
headers = {
    "Authorization": f"Bearer {token}"
}
data = {
    "format": "pdf",
    "filters": {
        "search": "produto",
        "categoria_id": 1,
        "data_inicio": "2023-01-01",
        "data_fim": "2023-12-31"
    }
}

response = requests.post(url, json=data, headers=headers)
arquivo = response.json()  # Caminho do arquivo gerado
```

## Filtros Disponíveis

- `search`: Termo de busca geral
- `categoria_id`: ID da categoria (apenas para produtos)
- `data_inicio`: Data inicial do período
- `data_fim`: Data final do período
- `status`: Status (ativo/inativo)

## Personalização

### Template HTML

O template base (`base_report.html`) pode ser personalizado editando:

- Estilos CSS
- Layout
- Cabeçalhos/Rodapés
- Formatação de dados

### Estilos Excel

Os estilos do Excel podem ser configurados em `export.py`:

```python
excel_styles = {
    'header': {
        'font': Font(bold=True, size=12),
        'fill': PatternFill(start_color='CCE5FF'),
        # ...
    },
    'data': {
        'font': Font(size=11),
        # ...
    }
}
```

## Configurações do PDF

Configurações do wkhtmltopdf em `pdf_config.py`:

```python
DEFAULT_PDF_OPTIONS = {
    'page-size': 'A4',
    'margin-top': '20mm',
    'orientation': 'Portrait',
    'encoding': 'UTF-8',
    'image-quality': 100,
    # ...
}
```

## Exemplos de Uso

### 1. Relatório de Produtos em PDF

```python
from app.utils.export import create_report_exporter

exporter = create_report_exporter()
output_file = await exporter.export_to_pdf(
    data=produtos_data,
    template_name="base_report.html",
    output_filename="produtos.pdf",
    title="Relatório de Produtos",
    subtitle="Lista Completa"
)
```

### 2. Relatório de Centros de Custo em Excel

```python
output_file = await exporter.export_to_excel(
    data=centros_data,
    output_filename="centros_custo.xlsx",
    sheet_name="Centros de Custo",
    title="Relatório de Centros de Custo",
    freeze_panes="B2"
)
```

## Testes

Execute os testes com:

```bash
pytest tests/test_reports.py -v
```

## Troubleshooting

### Problemas Comuns

1. **wkhtmltopdf não encontrado**
   - Verifique se está instalado
   - Configure o caminho em `settings.WKHTMLTOPDF_PATH`

2. **Erro de Template**
   - Verifique se o template existe em `templates/reports/`
   - Verifique a sintaxe Jinja2

3. **Erro de Permissão**
   - Verifique permissões nas pastas `reports/` e `templates/`

4. **Memória Insuficiente**
   - Reduza o tamanho do conjunto de dados
   - Use paginação para grandes relatórios

## Boas Práticas

1. **Limpeza de Arquivos**
   - Implemente rotina para limpar arquivos antigos
   - Use o diretório temporário do sistema

2. **Segurança**
   - Valide todos os inputs
   - Limite o tamanho dos dados
   - Sanitize nomes de arquivo

3. **Performance**
   - Use async/await para operações I/O
   - Implemente cache quando possível
   - Otimize consultas ao banco de dados

## Contribuindo

1. Faça fork do projeto
2. Crie uma branch para sua feature
3. Adicione testes
4. Envie um pull request

## Suporte

Para dúvidas ou problemas:
1. Consulte a documentação
2. Verifique os logs
3. Abra uma issue no repositório 