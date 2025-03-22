from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import time
import hashlib
from typing import Optional, Callable, Dict, Any, List, Tuple
import re

from app.config.settings import settings
from app.core.security import get_token_data
from app.deps.redis_deps import get_redis
from app.utils.logging_config import get_logger

# Configurar logger
logger = get_logger(__name__)

class RateLimiter:
    """
    Middleware avançado para limitar requisições por IP e/ou usuário.
    Utiliza Redis para armazenar os contadores de requisições.
    """
    
    def __init__(
        self,
        requests_limit: int = 100,
        time_window: int = 60,  # segundos
        by_ip: bool = True,
        by_user: bool = True,
        user_limit_multiplier: float = 2.0,
        exempt_paths: list = None,
        admin_exempt: bool = True,
        route_specific_limits: Dict[str, Tuple[int, int]] = None,
        burst_multiplier: float = 3.0,
        burst_time_window: int = 5,  # segundos
        suspicious_ip_threshold: int = 200,
        suspicious_pattern_threshold: int = 50
    ):
        """
        Inicializa o rate limiter com as configurações fornecidas.
        
        Args:
            requests_limit: Número máximo de requisições permitidas no período
            time_window: Janela de tempo em segundos
            by_ip: Se deve limitar por IP
            by_user: Se deve limitar por usuário autenticado
            user_limit_multiplier: Multiplicador do limite para usuários autenticados
            exempt_paths: Lista de caminhos isentos de rate limiting
            admin_exempt: Se administradores estão isentos de rate limiting
            route_specific_limits: Dicionário com limites específicos por rota (caminho regex: (limite, janela))
            burst_multiplier: Multiplicador para rajadas de tráfego
            burst_time_window: Janela de tempo para detecção de rajadas
            suspicious_ip_threshold: Número de requisições que marca um IP como suspeito
            suspicious_pattern_threshold: Número de requisições com padrão suspeito para alarme
        """
        self.requests_limit = requests_limit
        self.time_window = time_window
        self.by_ip = by_ip
        self.by_user = by_user
        self.user_limit_multiplier = user_limit_multiplier
        self.exempt_paths = exempt_paths or ["/health", "/api/v1/docs", "/api/v1/openapi.json"]
        self.admin_exempt = admin_exempt
        self.route_specific_limits = route_specific_limits or {}
        self.burst_multiplier = burst_multiplier
        self.burst_time_window = burst_time_window
        self.suspicious_ip_threshold = suspicious_ip_threshold
        self.suspicious_pattern_threshold = suspicious_pattern_threshold
        
        # Compilar regexs para rotas específicas
        self.route_patterns = [(re.compile(pattern), limit, window) 
                              for pattern, (limit, window) in self.route_specific_limits.items()]
        
        # Padrões suspeitos que podem indicar ataques
        self.suspicious_patterns = [
            # Padrões de ataque SQL Injection
            re.compile(r"((\%27)|(\'))|(\-\-)|(%23)|(#)", re.IGNORECASE),
            # Padrões de ataque XSS
            re.compile(r"((\%3C)|<)[^\n]+((\%3E)|>)", re.IGNORECASE),
            # Padrões de ataques de injeção de comando
            re.compile(r"(;|\||\`|\\|&|\^)", re.IGNORECASE),
        ]
        
    async def __call__(self, request: Request, call_next: Callable) -> JSONResponse:
        """
        Middleware que processa a requisição e aplica rate limiting.
        """
        # Verifica se o caminho está isento
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)
        
        # Obtém o IP do cliente
        client_ip = self._get_client_ip(request)
        
        # Obtém a rota específica e seus limites, se aplicável
        route_limit, route_window = self._get_route_specific_limits(request.url.path)
        
        # Tenta obter o usuário a partir do token
        user_id = None
        is_admin = False
        
        if self.by_user:
            token_data = await self._get_user_from_token(request)
            if token_data:
                user_id = token_data.get("sub")
                is_admin = token_data.get("is_admin", False)
                
                # Se o usuário for admin e estiver isento, pula a verificação
                if is_admin and self.admin_exempt:
                    return await call_next(request)
        
        # Se não estiver limitando por IP nem por usuário, ou se não conseguiu obter nenhum dos dois
        if not self.by_ip and (not self.by_user or not user_id):
            return await call_next(request)
            
        redis = await get_redis()
        
        # Verificar se a requisição contém padrões suspeitos
        is_suspicious = self._check_suspicious_patterns(request)
        if is_suspicious:
            suspicious_key = f"rate_limit:suspicious:{client_ip}"
            suspicious_count = await self._increment_counter(redis, suspicious_key, 3600)  # 1 hora
            
            # Se exceder o threshold, bloquear temporariamente
            if suspicious_count > self.suspicious_pattern_threshold:
                logger.warning(f"Bloqueando IP suspeito: {client_ip} por excesso de padrões suspeitos")
                await redis.setex(f"rate_limit:block:{client_ip}", 3600, "1")  # Bloquear por 1 hora
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "detail": "Acesso bloqueado devido a padrões de requisição suspeitos."
                    }
                )
        
        # Verificar bloqueio temporário
        is_blocked = await redis.get(f"rate_limit:block:{client_ip}")
        if is_blocked:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "detail": "Acesso temporariamente bloqueado. Tente novamente mais tarde."
                }
            )
        
        # Verificar rajada de tráfego (burst)
        if self.by_ip and client_ip:
            burst_key = f"rate_limit:burst:{client_ip}"
            burst_count = await self._increment_counter(redis, burst_key, self.burst_time_window)
            
            # Se exceder o limite de rajada, bloquear temporariamente
            if burst_count > int(route_limit * self.burst_multiplier):
                logger.warning(f"Bloqueando IP por rajada: {client_ip}")
                await redis.setex(f"rate_limit:block:{client_ip}", 60, "1")  # Bloquear por 1 minuto
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "Muitas requisições em curto período. Por favor, tente novamente mais tarde.",
                        "retry_after": 60
                    }
                )
        
        # Verificar limite por IP
        if self.by_ip and client_ip:
            ip_key = f"rate_limit:ip:{client_ip}:{request.url.path}"
            
            # Verificar se já excedeu o limite por IP
            current_ip_requests = await self._increment_counter(redis, ip_key, route_window)
            
            # Monitorar IPs suspeitos (muitas requisições)
            if current_ip_requests > self.suspicious_ip_threshold:
                logger.warning(f"IP suspeito detectado: {client_ip} ({current_ip_requests} requisições)")
                
            if current_ip_requests > route_limit:
                retry_after = await self._get_retry_after(redis, ip_key)
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "Muitas requisições. Por favor, tente novamente mais tarde.",
                        "retry_after": retry_after
                    },
                    headers={
                        "Retry-After": str(retry_after),
                        "X-RateLimit-Limit": str(route_limit),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(time.time()) + retry_after)
                    }
                )
            
            # Adicionar headers de rate limit
            request.state.rate_limit_headers = {
                "X-RateLimit-Limit": str(route_limit),
                "X-RateLimit-Remaining": str(max(0, route_limit - current_ip_requests)),
                "X-RateLimit-Reset": str(int(time.time()) + await self._get_retry_after(redis, ip_key))
            }
        
        # Verificar limite por usuário
        if self.by_user and user_id:
            user_key = f"rate_limit:user:{user_id}:{request.url.path}"
            user_limit = int(route_limit * self.user_limit_multiplier)
            
            # Verificar se já excedeu o limite por usuário
            current_user_requests = await self._increment_counter(redis, user_key, route_window)
            
            if current_user_requests > user_limit:
                retry_after = await self._get_retry_after(redis, user_key)
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "Muitas requisições. Por favor, tente novamente mais tarde.",
                        "retry_after": retry_after
                    },
                    headers={
                        "Retry-After": str(retry_after),
                        "X-RateLimit-Limit": str(user_limit),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(time.time()) + retry_after)
                    }
                )
                
            # Atualizar headers de rate limit para usuário
            if not hasattr(request.state, "rate_limit_headers"):
                request.state.rate_limit_headers = {}
                
            request.state.rate_limit_headers.update({
                "X-RateLimit-User-Limit": str(user_limit),
                "X-RateLimit-User-Remaining": str(max(0, user_limit - current_user_requests)),
                "X-RateLimit-User-Reset": str(int(time.time()) + await self._get_retry_after(redis, user_key))
            })
                
        # Se passar por todas as verificações, processa a requisição
        response = await call_next(request)
        
        # Adicionar headers de rate limiting à resposta
        if hasattr(request.state, "rate_limit_headers"):
            for header, value in request.state.rate_limit_headers.items():
                response.headers[header] = value
                
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Obtém o IP do cliente a partir do request, considerando proxies.
        """
        # Tenta obter o IP real de trás de proxies
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # Pega apenas o primeiro IP, que deve ser o do cliente
            return forwarded.split(",")[0].strip()
        
        # Se não tiver o header X-Forwarded-For, usa o IP direto
        return request.client.host if request.client else "unknown"
    
    async def _get_user_from_token(self, request: Request) -> Optional[Dict[str, Any]]:
        """
        Extrai e valida o token de autenticação da requisição.
        """
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
            
        token = auth_header.replace("Bearer ", "")
        try:
            return await get_token_data(token)
        except Exception:
            return None
    
    async def _increment_counter(self, redis, key: str, expiry: int) -> int:
        """
        Incrementa o contador no Redis e retorna o valor atual.
        Também define a expiração se for a primeira requisição.
        """
        current = await redis.incr(key)
        
        # Se for a primeira requisição, define a expiração
        if current == 1:
            await redis.expire(key, expiry)
            
        return current
    
    async def _get_retry_after(self, redis, key: str) -> int:
        """
        Calcula quanto tempo o cliente deve esperar antes de tentar novamente.
        """
        ttl = await redis.ttl(key)
        return max(1, ttl)  # Garante que seja pelo menos 1 segundo
    
    def _get_route_specific_limits(self, path: str) -> Tuple[int, int]:
        """
        Retorna limites específicos para uma rota, se existirem.
        Caso contrário, retorna os limites padrão.
        """
        for pattern, limit, window in self.route_patterns:
            if pattern.match(path):
                return limit, window
                
        return self.requests_limit, self.time_window
    
    def _check_suspicious_patterns(self, request: Request) -> bool:
        """
        Verifica se a requisição contém padrões suspeitos que podem indicar ataques.
        """
        # Verificar URL
        url = str(request.url)
        for pattern in self.suspicious_patterns:
            if pattern.search(url):
                logger.warning(f"Padrão suspeito detectado na URL: {url}")
                return True
        
        # Verificar parâmetros de consulta
        for param, value in request.query_params.items():
            for pattern in self.suspicious_patterns:
                if pattern.search(value):
                    logger.warning(f"Padrão suspeito detectado no parâmetro {param}: {value}")
                    return True
        
        # Verificação superficial do User-Agent
        user_agent = request.headers.get("User-Agent", "")
        if not user_agent or len(user_agent) < 10 or "bot" in user_agent.lower():
            return True
        
        return False


# Funções para facilitar o uso do middleware
def create_rate_limiter_middleware():
    """
    Cria uma instância do middleware de rate limiting com as configurações do settings.
    """
    # Definir limites específicos por rota
    route_specific_limits = {
        # Autenticação - mais restritivo para evitar brute force
        r"^/api/v1/auth/.*": (30, 300),  # 30 req por 5 minutos
        
        # Operações sensíveis - mais restritivas
        r"^/api/v1/usuarios.*": (60, 60),  # 60 req por minuto
        r"^/api/v1/empresas.*": (60, 60),  # 60 req por minuto
        
        # Operações comuns - menos restritivas
        r"^/api/v1/clientes.*": (120, 60),  # 120 req por minuto
        r"^/api/v1/produtos.*": (120, 60),  # 120 req por minuto
        r"^/api/v1/lancamentos.*": (150, 60),  # 150 req por minuto
        
        # Pesquisas e relatórios - limites intermediários
        r"^/api/v1/.*/relatorios.*": (50, 60),  # 50 req por minuto
        r"^/api/v1/.*/pesquisar.*": (80, 60),  # 80 req por minuto
    }
    
    return RateLimiter(
        requests_limit=settings.RATE_LIMIT_REQUESTS,
        time_window=settings.RATE_LIMIT_WINDOW,
        by_ip=settings.RATE_LIMIT_BY_IP,
        by_user=settings.RATE_LIMIT_BY_USER,
        user_limit_multiplier=settings.RATE_LIMIT_USER_MULTIPLIER,
        exempt_paths=settings.RATE_LIMIT_EXEMPT_PATHS,
        admin_exempt=settings.RATE_LIMIT_ADMIN_EXEMPT,
        route_specific_limits=route_specific_limits,
        burst_multiplier=3.0,
        burst_time_window=5,
        suspicious_ip_threshold=200,
        suspicious_pattern_threshold=50
    ) 