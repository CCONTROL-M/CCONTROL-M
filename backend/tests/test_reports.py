"""
Testes para o sistema de exportação de relatórios.
"""
import os
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.produto import Produto
from app.models.categoria import Categoria
from app.models.centro_custo import CentroCusto
from app.schemas.reports import ReportType, ReportFormat, ReportFilter
from app.utils.export import create_report_exporter
from tests.utils.utils import random_lower_string, random_email
from tests.utils.user import create_random_user
from tests.utils.empresa import create_random_empresa
from tests.utils.produto import create_random_produto
from tests.utils.categoria import create_random_categoria
from tests.utils.centro_custo import create_random_centro_custo

client = TestClient(app)

def test_create_report_exporter():
    """Testa a criação do exportador de relatórios."""
    exporter = create_report_exporter()
    assert exporter is not None
    assert os.path.exists(exporter.template_dir)
    assert os.path.exists(exporter.output_dir)

@pytest.mark.asyncio
async def test_export_produtos_pdf(db: Session):
    """Testa a exportação de relatório de produtos em PDF."""
    # Criar dados de teste
    empresa = create_random_empresa(db)
    user = create_random_user(db, empresa_id=empresa.id)
    categoria = create_random_categoria(db, empresa_id=empresa.id)
    produto = create_random_produto(db, empresa_id=empresa.id, categoria_id=categoria.id)
    
    # Criar exportador
    exporter = create_report_exporter()
    
    # Preparar dados
    data = [{
        "Código": produto.codigo,
        "Nome": produto.nome,
        "Categoria": categoria.nome,
        "Preço": f"R$ {produto.preco:.2f}",
        "Estoque": produto.estoque,
        "Última Atualização": produto.updated_at.strftime("%d/%m/%Y %H:%M")
    }]
    
    # Exportar relatório
    output_file = await exporter.export_to_pdf(
        data=data,
        template_name="base_report.html",
        output_filename="test_produtos.pdf",
        title="Relatório de Produtos",
        subtitle="Teste de Exportação"
    )
    
    assert os.path.exists(output_file)
    assert output_file.endswith(".pdf")

@pytest.mark.asyncio
async def test_export_produtos_excel(db: Session):
    """Testa a exportação de relatório de produtos em Excel."""
    # Criar dados de teste
    empresa = create_random_empresa(db)
    user = create_random_user(db, empresa_id=empresa.id)
    categoria = create_random_categoria(db, empresa_id=empresa.id)
    produto = create_random_produto(db, empresa_id=empresa.id, categoria_id=categoria.id)
    
    # Criar exportador
    exporter = create_report_exporter()
    
    # Preparar dados
    data = [{
        "Código": produto.codigo,
        "Nome": produto.nome,
        "Categoria": categoria.nome,
        "Preço": f"R$ {produto.preco:.2f}",
        "Estoque": produto.estoque,
        "Última Atualização": produto.updated_at.strftime("%d/%m/%Y %H:%M")
    }]
    
    # Exportar relatório
    output_file = await exporter.export_to_excel(
        data=data,
        output_filename="test_produtos.xlsx",
        sheet_name="Produtos",
        title="Relatório de Produtos",
        subtitle="Teste de Exportação"
    )
    
    assert os.path.exists(output_file)
    assert output_file.endswith(".xlsx")

def test_report_endpoint_unauthorized():
    """Testa acesso não autorizado ao endpoint de relatórios."""
    response = client.post(
        "/api/reports/export/produtos",
        json={"format": "pdf"}
    )
    assert response.status_code == 401

def test_report_endpoint_authorized(db: Session):
    """Testa acesso autorizado ao endpoint de relatórios."""
    # Criar usuário e obter token
    empresa = create_random_empresa(db)
    user = create_random_user(db, empresa_id=empresa.id)
    
    login_data = {
        "username": user.email,
        "password": "testpass123"  # Senha padrão definida em create_random_user
    }
    
    response = client.post("/api/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Testar endpoint com autenticação
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/api/reports/export/produtos",
        headers=headers,
        json={"format": "pdf"}
    )
    assert response.status_code == 200
    assert response.json().endswith(".pdf")

def test_invalid_report_type():
    """Testa tipo de relatório inválido."""
    with pytest.raises(ValueError):
        ReportType("invalid_type")

def test_report_filter_validation():
    """Testa validação dos filtros de relatório."""
    # Teste com datas válidas
    filter_data = {
        "search": "test",
        "categoria_id": 1,
        "data_inicio": "2023-01-01T00:00:00",
        "data_fim": "2023-12-31T23:59:59",
        "status": "ativo"
    }
    filter_obj = ReportFilter(**filter_data)
    assert filter_obj.search == "test"
    assert filter_obj.categoria_id == 1
    assert isinstance(filter_obj.data_inicio, datetime)
    assert isinstance(filter_obj.data_fim, datetime)
    assert filter_obj.status == "ativo"
    
    # Teste com dados inválidos
    with pytest.raises(ValueError):
        ReportFilter(categoria_id="invalid")  # Deve ser inteiro

@pytest.mark.asyncio
async def test_report_data_filtering(db: Session):
    """Testa filtragem de dados para relatórios."""
    # Criar dados de teste
    empresa = create_random_empresa(db)
    categoria1 = create_random_categoria(db, empresa_id=empresa.id)
    categoria2 = create_random_categoria(db, empresa_id=empresa.id)
    
    # Criar produtos em diferentes categorias
    produto1 = create_random_produto(db, empresa_id=empresa.id, categoria_id=categoria1.id)
    produto2 = create_random_produto(db, empresa_id=empresa.id, categoria_id=categoria2.id)
    
    # Testar filtro por categoria
    filters = ReportFilter(categoria_id=categoria1.id)
    
    from app.api.endpoints.reports import _get_report_data
    data = await _get_report_data(
        report_type=ReportType.PRODUTOS,
        filters=filters,
        db=db,
        current_user=create_random_user(db, empresa_id=empresa.id)
    )
    
    assert len(data) == 1
    assert data[0]["Código"] == produto1.codigo

def test_cleanup():
    """Limpa arquivos de teste após os testes."""
    test_files = [
        "test_produtos.pdf",
        "test_produtos.xlsx"
    ]
    
    for file in test_files:
        file_path = os.path.join("reports", file)
        if os.path.exists(file_path):
            os.remove(file_path) 