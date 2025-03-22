"""
Middleware de segurança integrado para o sistema CCONTROL-M.

Este middleware implementa várias camadas de proteção:
1. Validação robusta de dados de entrada
2. Proteção contra ataques comuns (XSS, CSRF, SQL Injection)
3. Implementação de cabeçalhos de segurança
4. Verificação de integridade de dados
"""
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Dict, Any, List, Set, Optional
import re
import json
import time
from datetime import datetime
import hashlib
import secrets
import base64
from starlette.datastructures import MutableHeaders

from app.config.settings import settings
from app.utils.logging_config import get_logger
from app.utils.validation import detect_attack_patterns, has_attack_input
from app.utils.validation import sanitize_string, validate_url_params


# Configurar logger
logger = get_logger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware avançado de segurança que integra múltiplas camadas de proteção.
    """
    
    def __init__(
        self,
        app,
        max_content_length: int = getattr(settings, "MAX_UPLOAD_SIZE", 5 * 1024 * 1024),
        allowed_content_types: Set[str] = None,
        block_high_risk_countries: bool = False,
        enforce_csrf_protection: bool = True,
        enforce_content_type: bool = True,
        sanitize_inputs: bool = True
    ):
        """
        Inicializa o middleware com configurações personalizadas.
        
        Args:
            app: A aplicação ASGI
            max_content_length: Tamanho máximo do corpo da requisição (padrão: 5MB)
            allowed_content_types: Tipos de conteúdo permitidos
            block_high_risk_countries: Se deve bloquear países de alto risco
            enforce_csrf_protection: Se deve aplicar proteção CSRF
            enforce_content_type: Se deve verificar Content-Type
            sanitize_inputs: Se deve sanitizar entradas
        """
        super().__init__(app)
        self.max_content_length = max_content_length
        self.allowed_content_types = allowed_content_types or {
            "application/json", 
            "application/x-www-form-urlencoded", 
            "multipart/form-data"
        }
        self.block_high_risk_countries = block_high_risk_countries
        self.enforce_csrf_protection = enforce_csrf_protection
        self.enforce_content_type = enforce_content_type
        self.sanitize_inputs = sanitize_inputs
        
        # Lista de rotas que são públicas (não necessitam de proteção CSRF)
        self.csrf_exempt_routes = {
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/refresh",
            "/api/v1/health",
            "/api/v1/docs",
            "/api/v1/openapi.json"
        }
        
        # Lista de rotas sensíveis (requerem validação extra)
        self.sensitive_routes = {
            "/api/v1/usuarios",
            "/api/v1/empresas",
            "/api/v1/auth/reset-password",
            "/api/v1/config"
        }
        
        # Parâmetros permitidos por rota para prevenir parameter pollution
        self.allowed_params = {
            "default": ["page", "size", "sort", "order", "q", "filter"],
            "/api/v1/usuarios": ["page", "size", "sort", "order", "email", "nome", "ativo", "role"],
            "/api/v1/clientes": ["page", "size", "sort", "order", "nome", "documento", "cidade", "uf", "situacao"],
            "/api/v1/produtos": ["page", "size", "sort", "order", "nome", "categoria", "codigo", "ativo", "preco_min", "preco_max"]
        }
        
        # Padrões para detectar ataques
        self.dangerous_patterns = {
            "sql_injection": re.compile(r"(\b(select|insert|update|delete|drop|alter|create|truncate|declare)\b|\b(from|where|group by|order by)\b|--|;|\bor\b|\band\b)", re.IGNORECASE),
            "path_traversal": re.compile(r"(\.\.\/|\.\.\\|~\/|\~\\|\/etc\/|\\etc\\|\/bin\/|\\bin\\)", re.IGNORECASE),
            "command_injection": re.compile(r"(;|\||`|\\|&|\^|\$\(|\${)", re.IGNORECASE),
        }
        
        logger.info("Middleware de segurança inicializado com sucesso")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Processa a requisição aplicando as verificações de segurança.
        
        Args:
            request: O objeto Request da requisição
            call_next: Função para processar o próximo middleware
            
        Returns:
            Resposta HTTP
        """
        # Adicionar tempo de início para métricas
        request.state.start_time = time.time()
        
        # Verificar limite de tamanho do conteúdo
        if self._check_content_length(request):
            return JSONResponse(
                status_code=413,
                content={"detail": f"Requisição muito grande. Máximo permitido é {self.max_content_length} bytes."}
            )
        
        # Verificar Content-Type se for POST/PUT/PATCH
        if self.enforce_content_type and request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            if not any(allowed in content_type for allowed in self.allowed_content_types):
                return JSONResponse(
                    status_code=415,
                    content={"detail": f"Content-Type não suportado: {content_type}"}
                )
        
        # Verificar proteção CSRF para métodos não idempotentes
        if self.enforce_csrf_protection and request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            # Pular verificação para rotas isentas
            if not any(request.url.path.startswith(path) for path in self.csrf_exempt_routes):
                csrf_result = self._validate_csrf(request)
                if csrf_result:
                    return csrf_result
        
        # Validar parâmetros da URL (parameter pollution)
        if request.query_params:
            params_route = next((path for path in self.allowed_params if request.url.path.startswith(path)), "default")
            allowed = self.allowed_params.get(params_route, self.allowed_params["default"])
            
            if not validate_url_params(dict(request.query_params), allowed):
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Parâmetros de consulta não permitidos"}
                )
        
        # Verificar padrões perigosos na URL e parâmetros
        if self._check_dangerous_patterns(request):
            # Registrar tentativa de ataque
            logger.warning(
                f"Possível ataque detectado: {request.method} {request.url.path}",
                extra={
                    "ip": self._get_client_ip(request),
                    "user_agent": request.headers.get("user-agent"),
                    "params": dict(request.query_params)
                }
            )
            return JSONResponse(
                status_code=403,
                content={"detail": "Requisição bloqueada por questões de segurança"}
            )
            
        # Verificar JSON para ataques em requisições com corpo
        if request.method in ["POST", "PUT", "PATCH"]:
            body_check_result = await self._check_request_body(request)
            if body_check_result:
                return body_check_result
        
        # Gerar nonce para CSP se necessário
        nonce = secrets.token_hex(16)
        request.state.csp_nonce = nonce
        
        # Processar a requisição
        response = await call_next(request)
        
        # Adicionar cabeçalhos de segurança
        return self._add_security_headers(response, nonce)
    
    def _check_content_length(self, request: Request) -> bool:
        """
        Verifica se o tamanho do conteúdo excede o limite.
        
        Args:
            request: O objeto Request
            
        Returns:
            True se exceder o limite, False caso contrário
        """
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_content_length:
            return True
        return False
    
    def _validate_csrf(self, request: Request) -> Optional[JSONResponse]:
        """
        Valida proteção CSRF para métodos não seguros.
        
        Args:
            request: O objeto Request
            
        Returns:
            JSONResponse de erro se a validação falhar, None caso contrário
        """
        # Verificar se o token CSRF está no cabeçalho
        csrf_token = request.headers.get("X-CSRF-Token")
        if not csrf_token:
            return JSONResponse(
                status_code=403,
                content={"detail": "Token CSRF ausente"}
            )
            
        # Verificar se o Origin/Referer corresponde ao host
        origin = request.headers.get("Origin", "")
        referer = request.headers.get("Referer", "")
        host = request.headers.get("Host", "")
        
        if origin and not origin.endswith(host):
            if not any(allowed in origin for allowed in settings.CORS_ALLOWED_ORIGINS):
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Origin não permitido"}
                )
                
        if referer and not any(ref in referer for ref in [host] + list(settings.CORS_ALLOWED_ORIGINS)):
            return JSONResponse(
                status_code=403,
                content={"detail": "Referer não permitido"}
            )
            
        return None
    
    def _check_dangerous_patterns(self, request: Request) -> bool:
        """
        Verifica padrões perigosos na URL e parâmetros.
        
        Args:
            request: O objeto Request
            
        Returns:
            True se encontrar padrões perigosos, False caso contrário
        """
        # Verificar caminho
        path = request.url.path
        for pattern_name, pattern in self.dangerous_patterns.items():
            if pattern.search(path):
                logger.warning(f"Padrão perigoso ({pattern_name}) detectado no caminho: {path}")
                return True
                
        # Verificar parâmetros de consulta
        for key, value in request.query_params.items():
            # Sanitizar valores se configurado
            if self.sanitize_inputs:
                value = sanitize_string(value)
                
            for pattern_name, pattern in self.dangerous_patterns.items():
                if pattern.search(value):
                    logger.warning(f"Padrão perigoso ({pattern_name}) detectado no parâmetro {key}: {value}")
                    return True
                    
            # Verificar padrões de ataque específicos
            attacks = detect_attack_patterns(value)
            if attacks:
                logger.warning(f"Ataques detectados no parâmetro {key}: {', '.join(attacks)}")
                return True
                
        return False
    
    async def _check_request_body(self, request: Request) -> Optional[JSONResponse]:
        """
        Verifica o corpo da requisição para padrões perigosos.
        
        Args:
            request: O objeto Request
            
        Returns:
            JSONResponse de erro se encontrar problemas, None caso contrário
        """
        try:
            content_type = request.headers.get("content-type", "")
            
            # Verificar apenas para JSON
            if "application/json" in content_type:
                body = await request.body()
                if body:
                    try:
                        # Verificar se é um JSON válido
                        json_data = json.loads(body)
                        
                        # Verificar padrões de ataque
                        if has_attack_input(json_data):
                            logger.warning(
                                f"Ataques detectados no corpo JSON: {request.method} {request.url.path}",
                                extra={"ip": self._get_client_ip(request)}
                            )
                            return JSONResponse(
                                status_code=400,
                                content={"detail": "Conteúdo JSON contém padrões de ataque"}
                            )
                    except json.JSONDecodeError:
                        return JSONResponse(
                            status_code=400,
                            content={"detail": "JSON inválido no corpo da requisição"}
                        )
        except Exception as e:
            logger.error(f"Erro ao verificar corpo da requisição: {str(e)}")
            
        return None
    
    def _add_security_headers(self, response: Response, nonce: str) -> Response:
        """
        Adiciona cabeçalhos de segurança à resposta.
        
        Args:
            response: O objeto Response
            nonce: Valor nonce para CSP
            
        Returns:
            Resposta com cabeçalhos de segurança adicionados
        """
        # Content Security Policy com nonce
        response.headers["Content-Security-Policy"] = (
            f"default-src 'self'; "
            f"script-src 'self' 'nonce-{nonce}' https:; "
            f"style-src 'self' 'unsafe-inline' https:; "
            f"img-src 'self' data: https:; "
            f"connect-src 'self' https:; "
            f"font-src 'self' https:; "
            f"object-src 'none'; "
            f"media-src 'self'; "
            f"frame-src 'self';"
        )
        
        # Outros cabeçalhos de segurança
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy
        response.headers["Permissions-Policy"] = (
            "accelerometer=(), "
            "camera=(), "
            "geolocation=(), "
            "gyroscope=(), "
            "magnetometer=(), "
            "microphone=(), "
            "payment=(), "
            "usb=()"
        )
        
        # Strict-Transport-Security em produção
        if settings.APP_ENV == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # Cabeçalhos para respostas de erro
        if response.status_code in (401, 403, 500):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            
        # Adicionar header com tempo de processamento
        if hasattr(response, "request") and hasattr(response.request.state, "start_time"):
            process_time = time.time() - response.request.state.start_time
            response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
            
        return response
        
    def _get_client_ip(self, request: Request) -> str:
        """
        Obtém o IP real do cliente, considerando proxies.
        
        Args:
            request: O objeto Request
            
        Returns:
            String com o IP do cliente
        """
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            # Pegar o primeiro IP, que deve ser o do cliente
            return x_forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"


# Função para criar o middleware
def create_security_middleware():
    """
    Cria uma instância do middleware de segurança.
    
    Returns:
        Instância configurada do SecurityMiddleware
    """
    async def security_middleware(request: Request, call_next):
        """
        Aplica cabeçalhos de segurança às respostas HTTP.
        
        Args:
            request: Requisição HTTP
            call_next: Próximo handler na cadeia de middlewares
            
        Returns:
            Response: Resposta HTTP com cabeçalhos de segurança
        """
        # Validar autenticação básica para endpoint de métricas
        if settings.METRICS_BASIC_AUTH and request.url.path == "/api/metrics":
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Basic "):
                # Retornar erro 401 Unauthorized com cabeçalho WWW-Authenticate
                headers = {"WWW-Authenticate": "Basic realm=\"Prometheus Metrics\""}
                return create_error_response(401, "Unauthorized", "Autenticação necessária", headers)
            
            # Extrair e validar credenciais
            encoded_credentials = auth_header.split(" ")[1]
            try:
                decoded = base64.b64decode(encoded_credentials).decode("utf-8")
                username, password = decoded.split(":")
                if username != settings.METRICS_USERNAME or password != settings.METRICS_PASSWORD:
                    return create_error_response(401, "Unauthorized", "Credenciais inválidas")
            except Exception:
                return create_error_response(401, "Unauthorized", "Credenciais inválidas")
        
        # Processar requisição
        response = await call_next(request)
        
        # Adicionar cabeçalhos de segurança, se habilitados
        if settings.SECURITY_HEADERS:
            headers = MutableHeaders(response.headers)
            
            # Prevenção contra ataques XSS
            headers.append("X-XSS-Protection", "1; mode=block")
            
            # Prevenção contra ataques de sniffing de MIME type
            headers.append("X-Content-Type-Options", "nosniff")
            
            # Prevenção contra ataques de clickjacking
            headers.append("X-Frame-Options", "DENY")
            
            # Restrição de referrer para melhorar privacidade
            headers.append("Referrer-Policy", "strict-origin-when-cross-origin")
            
            # CSP para restringir origens de recursos (básico)
            # Em produção, esta política deve ser mais restritiva
            if settings.APP_ENV == "production":
                headers.append(
                    "Content-Security-Policy",
                    "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; "
                    "img-src 'self' data:; font-src 'self' data:; connect-src 'self'"
                )
            
            # Permissões para recursos específicos
            headers.append("Permissions-Policy", "camera=(), microphone=(), geolocation=(), interest-cohort=()")
            
            # HSTS para forçar HTTPS em navegadores (apenas em prod e se habilitado)
            if settings.HSTS_ENABLED and settings.APP_ENV == "production":
                headers.append(
                    "Strict-Transport-Security",
                    f"max-age={settings.HSTS_MAX_AGE}; includeSubDomains; preload"
                )
                
            # Remover Server e X-Powered-By para reduzir fingerprinting
            if "Server" in headers:
                del headers["Server"]
            if "X-Powered-By" in headers:
                del headers["X-Powered-By"]
        
        return response
    
    return security_middleware


def create_error_response(status_code: int, error: str, message: str, headers: dict = None):
    """
    Cria uma resposta de erro com cabeçalhos opcionais.
    
    Args:
        status_code: Código de status HTTP
        error: Tipo de erro
        message: Mensagem de erro
        headers: Cabeçalhos adicionais (opcional)
        
    Returns:
        Resposta HTTP com erro formatado
    """
    from starlette.responses import JSONResponse
    
    content = {"error": error, "message": message}
    return JSONResponse(
        status_code=status_code,
        content=content,
        headers=headers or {}
    ) 