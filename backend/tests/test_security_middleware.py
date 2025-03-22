"""
Testes para o middleware de segurança.

Verifica todas as funcionalidades do SecurityMiddleware e suas camadas de proteção.
"""
import pytest
from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient
from starlette.middleware.base import BaseHTTPMiddleware
from unittest.mock import AsyncMock, MagicMock, patch
import json

from app.middlewares.security_middleware import SecurityMiddleware, create_security_middleware


# App de teste para os middlewares
@pytest.fixture
def test_app():
    """Cria uma aplicação FastAPI de teste"""
    app = FastAPI()
    
    @app.get("/test")
    def test_route():
        return {"message": "Test route"}
    
    @app.post("/test/json")
    async def test_json_route(request: Request):
        json_data = await request.json()
        return json_data
    
    @app.get("/test/params")
    def test_params_route(request: Request):
        return {"params": dict(request.query_params)}
    
    @app.get("/test/headers")
    def test_headers_route(request: Request):
        return {"headers": dict(request.headers)}
    
    @app.post("/api/v1/auth/login")
    def login_route():
        return {"token": "test_token"}
        
    @app.post("/api/v1/usuarios")
    def sensitive_route():
        return {"message": "Sensitive route"}
    
    return app


@pytest.fixture
def test_client(test_app):
    """Cria um cliente de teste com o middleware de segurança aplicado"""
    app = test_app
    app.add_middleware(SecurityMiddleware)
    return TestClient(app)


class TestSecurityMiddleware:
    """Testes para o middleware de segurança"""

    def test_normal_request(self, test_client):
        """Testa que requisições normais passam pelo middleware"""
        response = test_client.get("/test")
        assert response.status_code == 200
        assert response.json() == {"message": "Test route"}

    def test_content_length_limit(self, test_client):
        """Testa que requisições muito grandes são rejeitadas"""
        with patch('app.middlewares.security_middleware.SecurityMiddleware._check_content_length', return_value=True):
            response = test_client.post("/test/json", json={"data": "test"})
            assert response.status_code == 413
            assert "Requisição muito grande" in response.json()["detail"]

    def test_content_type_validation(self, test_client):
        """Testa validação de Content-Type"""
        # Enviar uma requisição POST com Content-Type inválido
        headers = {"Content-Type": "text/csv"}
        with patch('app.middlewares.security_middleware.settings', MagicMock(CORS_ALLOWED_ORIGINS=["http://testserver"])):
            response = test_client.post(
                "/test/json", 
                data="test,data", 
                headers=headers
            )
            assert response.status_code == 415
            assert "Content-Type não suportado" in response.json()["detail"]

    def test_csrf_protection(self, test_client):
        """Testa proteção CSRF"""
        # Testar rota sensível sem token CSRF
        with patch('app.middlewares.security_middleware.settings', MagicMock(CORS_ALLOWED_ORIGINS=["http://testserver"])):
            response = test_client.post("/api/v1/usuarios", json={"name": "Test"})
            assert response.status_code == 403
            assert "Token CSRF ausente" in response.json()["detail"]
            
        # Testar rota pública (não deve requerir CSRF)
        response = test_client.post("/api/v1/auth/login", json={"email": "test@example.com", "password": "password"})
        assert response.status_code == 200

    def test_param_validation(self, test_client):
        """Testa validação de parâmetros de URL"""
        with patch('app.utils.validation.validate_url_params', return_value=False):
            response = test_client.get("/test/params?invalid=param")
            assert response.status_code == 400
            assert "Parâmetros de consulta não permitidos" in response.json()["detail"]

    def test_dangerous_patterns_detection(self, test_client):
        """Testa detecção de padrões perigosos em URL e parâmetros"""
        with patch('app.middlewares.security_middleware.SecurityMiddleware._check_dangerous_patterns', return_value=True):
            response = test_client.get("/test/params?sql=SELECT%20*%20FROM%20users")
            assert response.status_code == 403
            assert "Requisição bloqueada" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_request_body_check(self):
        """Testa verificação de padrões perigosos no corpo da requisição"""
        middleware = SecurityMiddleware(None)
        
        # Criar um request mockado com corpo contendo padrões de ataque
        mock_request = AsyncMock()
        mock_request.headers = {"content-type": "application/json"}
        mock_request.body.return_value = json.dumps({
            "name": "Test",
            "comment": "<script>alert('XSS')</script>"
        }).encode()
        
        # Com patch para has_attack_input retornando True
        with patch('app.middlewares.security_middleware.has_attack_input', return_value=True):
            result = await middleware._check_request_body(mock_request)
            assert result is not None
            assert result.status_code == 400
            assert json.loads(result.body)["detail"] == "Conteúdo JSON contém padrões de ataque"

    def test_security_headers(self, test_client):
        """Testa adição de cabeçalhos de segurança"""
        response = test_client.get("/test")
        assert response.status_code == 200
        
        # Verificar cabeçalhos de segurança
        assert "Content-Security-Policy" in response.headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "X-XSS-Protection" in response.headers
        assert "Referrer-Policy" in response.headers
        assert "Permissions-Policy" in response.headers

    def test_client_ip_extraction(self):
        """Testa extração do IP real do cliente"""
        middleware = SecurityMiddleware(None)
        
        # Testar com X-Forwarded-For
        mock_request = MagicMock()
        mock_request.headers = {"X-Forwarded-For": "192.168.1.1, 10.0.0.1"}
        assert middleware._get_client_ip(mock_request) == "192.168.1.1"
        
        # Testar sem X-Forwarded-For
        mock_request = MagicMock()
        mock_request.headers = {}
        mock_request.client.host = "127.0.0.1"
        assert middleware._get_client_ip(mock_request) == "127.0.0.1"
        
        # Testar sem client
        mock_request = MagicMock()
        mock_request.headers = {}
        mock_request.client = None
        assert middleware._get_client_ip(mock_request) == "unknown"

    def test_create_security_middleware(self):
        """Testa a função de criação do middleware"""
        middleware = create_security_middleware()
        assert isinstance(middleware, SecurityMiddleware)


@pytest.mark.asyncio
async def test_dispatch_flow():
    """Testa o fluxo completo do dispatch do middleware"""
    # Criar um middleware de teste
    middleware = SecurityMiddleware(None)
    
    # Criar um mock para call_next
    mock_call_next = AsyncMock()
    mock_response = Response(content="Test response")
    mock_call_next.return_value = mock_response
    
    # Criar um request mockado sem problemas
    mock_request = AsyncMock()
    mock_request.method = "GET"
    mock_request.url = MagicMock()
    mock_request.url.path = "/test"
    mock_request.query_params = {}
    mock_request.headers = {}
    mock_request.client = MagicMock()
    mock_request.client.host = "127.0.0.1"
    mock_request.state = MagicMock()
    
    # Patcear todas as verificações para retornarem resultados "seguros"
    with patch.multiple(
        'app.middlewares.security_middleware.SecurityMiddleware',
        _check_content_length=MagicMock(return_value=False),
        _check_dangerous_patterns=MagicMock(return_value=False),
        _validate_csrf=MagicMock(return_value=None),
        _check_request_body=AsyncMock(return_value=None),
        _add_security_headers=MagicMock(return_value=mock_response)
    ):
        # Testar o dispatch
        response = await middleware.dispatch(mock_request, mock_call_next)
        
        # Verificar que call_next foi chamado
        mock_call_next.assert_called_once_with(mock_request)
        
        # Verificar que a resposta foi processada
        assert response == mock_response 