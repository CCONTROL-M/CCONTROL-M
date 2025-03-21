import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime

from app.main import app
from app.dependencies import get_current_user
from app.database import get_db
from tests.conftest import override_get_db

# Cliente de teste
client = TestClient(app)

# Mock de usuário administrador para os testes
test_admin = {
    "id_usuario": "12345678-1234-5678-1234-567812345678",
    "id_empresa": "98765432-9876-5432-9876-543298765432",
    "nome": "Admin Teste",
    "email": "admin@exemplo.com",
    "tipo_usuario": "superadmin",
    "telas_permitidas": {"monitoring": True}
}

# Mock de dados para métricas
mock_metrics = {
    "connections_active": 5,
    "connections_idle": 10,
    "connections_idle_in_transaction": 0,
    "connections_total": 15,
    "max_connections": 100,
    "connection_usage_percent": 15.0,
    "db_size": "150 MB",
    "tx_per_second": 25.5,
    "query_avg_time": 8.3,
    "tables_count": 15,
    "cache_hit_ratio": 98.5,
    "slow_queries_count": 2,
    "last_updated": datetime.now().isoformat()
}

# Mock de consultas lentas
mock_slow_queries = [
    {
        "query": "SELECT * FROM tabela WHERE coluna = 'valor'",
        "execution_time": 2500.0,
        "timestamp": datetime.now().isoformat(),
        "client_info": "app_web"
    },
    {
        "query": "UPDATE tabela SET coluna = 'novo_valor'",
        "execution_time": 1800.0,
        "timestamp": datetime.now().isoformat(),
        "client_info": "app_mobile"
    }
]

# Mock para resultados de benchmark
mock_benchmark_results = {
    "duration_total": 5.32,
    "queries_executed": 10,
    "slow_queries_detected": 2,
    "avg_query_time": 532.0,
    "results": [
        {"query": "SELECT 1", "time": 55.2, "is_slow": False},
        {"query": "SELECT * FROM usuarios", "time": 950.3, "is_slow": True}
    ]
}

@pytest.fixture
def setup_mocks():
    # Sobrescrever a dependência para os testes
    original_dep = app.dependency_overrides.copy()
    app.dependency_overrides[get_current_user] = lambda: test_admin
    app.dependency_overrides[get_db] = override_get_db
    
    yield
    
    # Restaurar dependências originais
    app.dependency_overrides = original_dep

# Testes para endpoints de monitoramento
@patch("app.utils.db_monitor.get_db_metrics")
def test_get_metrics(mock_get_metrics, setup_mocks):
    """Teste para obter métricas do sistema"""
    mock_get_metrics.return_value = mock_metrics
    
    response = client.get("/api/monitoring/metrics")
    assert response.status_code == 200
    
    data = response.json()
    assert "connections_active" in data
    assert data["connections_total"] == mock_metrics["connections_total"]
    assert data["db_size"] == mock_metrics["db_size"]

@patch("app.utils.db_monitor.get_slow_queries")
def test_get_slow_queries(mock_get_slow_queries, setup_mocks):
    """Teste para obter consultas lentas"""
    mock_get_slow_queries.return_value = mock_slow_queries
    
    response = client.get("/api/monitoring/slow-queries")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == len(mock_slow_queries)
    assert data[0]["query"] == mock_slow_queries[0]["query"]
    assert data[1]["execution_time"] == mock_slow_queries[1]["execution_time"]

@patch("app.utils.db_monitor.reset_metrics")
def test_reset_metrics(mock_reset_metrics, setup_mocks):
    """Teste para resetar métricas"""
    response = client.post("/api/monitoring/reset-metrics")
    assert response.status_code == 204
    mock_reset_metrics.assert_called_once()

@patch("app.scripts.monitor_db.run_benchmark")
def test_run_benchmark(mock_run_benchmark, setup_mocks):
    """Teste para executar benchmark"""
    mock_run_benchmark.return_value = mock_benchmark_results
    
    response = client.post("/api/monitoring/run-benchmark")
    assert response.status_code == 200
    
    data = response.json()
    assert "duration_total" in data
    assert data["queries_executed"] == mock_benchmark_results["queries_executed"]
    assert len(data["results"]) == len(mock_benchmark_results["results"])
    assert data["results"][1]["is_slow"] == True 