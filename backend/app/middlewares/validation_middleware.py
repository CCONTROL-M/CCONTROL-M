from fastapi import Request, Response
from typing import Callable, Dict, Any
import re
import json
from datetime import datetime

from app.core.config import settings


class ValidationMiddleware:
    """
    Middleware para validação adicional de requisições e adição de cabeçalhos de segurança.
    """
    
    def __init__(
        self,
        max_content_length: int = settings.MAX_UPLOAD_SIZE,
        add_security_headers: bool = True,
        validate_json: bool = True,
        sanitize_params: bool = True
    ):
        """
        Inicializa o middleware com as configurações fornecidas.
        
        Args:
            max_content_length: Tamanho máximo permitido para o corpo da requisição
            add_security_headers: Se deve adicionar cabeçalhos de segurança
            validate_json: Se deve validar o JSON nas requisições POST/PUT/PATCH
            sanitize_params: Se deve sanitizar parâmetros de consulta
        """
        self.max_content_length = max_content_length
        self.add_security_headers = add_security_headers
        self.validate_json = validate_json
        self.sanitize_params = sanitize_params
        
        # Compilar regex para identificar possíveis injeções
        self.sql_injection_pattern = re.compile(
            r"(\b(select|insert|update|delete|drop|alter|create|truncate|declare)\b|\b(from|where|group by|order by)\b|--|;|\bor\b|\band\b)",
            re.IGNORECASE
        )
        
        # Regex para XSS
        self.xss_pattern = re.compile(
            r"(<script|javascript:|on\w+\s*=|alert\(|confirm\(|prompt\(|\beval\b|\bexec\b|<iframe|<embed|<object)",
            re.IGNORECASE
        )
        
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """
        Processa a requisição, valida e adiciona cabeçalhos de segurança.
        
        Args:
            request: O objeto Request da requisição
            call_next: Função para processar a próxima etapa no middleware
            
        Returns:
            Resposta HTTP processada
        """
        # Validar tamanho do conteúdo
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_content_length:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=413,
                content={"detail": f"Requisição muito grande. Máximo permitido é {self.max_content_length} bytes."}
            )
        
        # Validar parâmetros de consulta
        if self.sanitize_params and request.query_params:
            for key, value in request.query_params.items():
                # Verificar possíveis injeções nos parâmetros
                if self._check_for_injection(value):
                    from fastapi.responses import JSONResponse
                    return JSONResponse(
                        status_code=400,
                        content={"detail": f"Parâmetro de consulta inválido: {key}"}
                    )
        
        # Validar JSON para métodos que geralmente têm corpo
        if self.validate_json and request.method in ("POST", "PUT", "PATCH"):
            try:
                content_type = request.headers.get("content-type", "")
                if "application/json" in content_type:
                    body = await request.body()
                    if body:
                        try:
                            # Verificar se o JSON é válido
                            json_data = json.loads(body)
                            
                            # Verificar possíveis injeções no JSON
                            if self._check_json_for_injection(json_data):
                                from fastapi.responses import JSONResponse
                                return JSONResponse(
                                    status_code=400,
                                    content={"detail": "Conteúdo JSON inválido ou potencialmente malicioso"}
                                )
                        except json.JSONDecodeError:
                            from fastapi.responses import JSONResponse
                            return JSONResponse(
                                status_code=400,
                                content={"detail": "JSON inválido no corpo da requisição"}
                            )
            except Exception:
                # Ignorar erros na validação do corpo
                pass
        
        # Processar a requisição normalmente
        response = await call_next(request)
        
        # Adicionar cabeçalhos de segurança à resposta
        if self.add_security_headers:
            self._add_security_headers(response)
        
        return response
    
    def _check_for_injection(self, value: str) -> bool:
        """
        Verifica se um valor contém padrões suspeitos de injeção.
        
        Args:
            value: Valor a ser verificado
            
        Returns:
            True se encontrar padrões suspeitos, False caso contrário
        """
        if not value or not isinstance(value, str):
            return False
            
        # Verificar SQL Injection
        if self.sql_injection_pattern.search(value):
            return True
            
        # Verificar XSS
        if self.xss_pattern.search(value):
            return True
            
        return False
        
    def _check_json_for_injection(self, data: Any) -> bool:
        """
        Verifica recursivamente um objeto JSON por padrões suspeitos.
        
        Args:
            data: Dados JSON a serem verificados
            
        Returns:
            True se encontrar padrões suspeitos, False caso contrário
        """
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(key, str) and self._check_for_injection(key):
                    return True
                if self._check_json_for_injection(value):
                    return True
        elif isinstance(data, list):
            for item in data:
                if self._check_json_for_injection(item):
                    return True
        elif isinstance(data, str):
            return self._check_for_injection(data)
            
        return False
    
    def _add_security_headers(self, response: Response) -> None:
        """
        Adiciona cabeçalhos de segurança à resposta HTTP.
        
        Args:
            response: Objeto Response a ser modificado
        """
        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "img-src 'self' data: https:; "
            "style-src 'self' 'unsafe-inline' https:; "
            "script-src 'self' https:; "
            "connect-src 'self' https:; "
            "frame-src 'self' https:; "
            "object-src 'none'"
        )
        
        # Prevenir detecção automática de MIME types
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Controle de frameamento (prevenir clickjacking)
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        
        # Controle de cache
        if not response.headers.get("Cache-Control"):
            response.headers["Cache-Control"] = "no-store, max-age=0"
            
        # Cross-site Scripting Protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Strict Transport Security (apenas em produção)
        if settings.APP_ENV == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
        # Permissions Policy (restringir recursos do navegador)
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
        
        # Desabilitar o caching de informações sensíveis
        if response.status_code in (401, 403):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"


# Função para criar o middleware
def create_validation_middleware() -> ValidationMiddleware:
    """
    Cria uma instância do middleware de validação.
    """
    return ValidationMiddleware() 