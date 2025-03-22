from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.config.settings import settings
import time
import logging
from collections import defaultdict
import asyncio
import ipaddress
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        # Dicionário para armazenar as requisições: {ip: [(timestamp, path), ...]}
        self.request_records = defaultdict(list)
        # Lock para acesso concorrente ao dicionário
        self.lock = asyncio.Lock()
        # Iniciar limpeza periódica
        self._setup_periodic_cleanup()
    
    def _setup_periodic_cleanup(self):
        # A cada 10 minutos, limpar registros antigos
        cleanup_interval = 600  # segundos
        
        async def cleanup_old_records():
            while True:
                await asyncio.sleep(cleanup_interval)
                await self._cleanup_records()
        
        # Iniciar tarefa de limpeza em background
        asyncio.create_task(cleanup_old_records())
    
    async def _cleanup_records(self):
        """Limpar registros mais antigos que a janela de tempo"""
        now = time.time()
        window = settings.RATE_LIMIT_WINDOW
        
        async with self.lock:
            # Para cada IP, filtrar apenas registros dentro da janela de tempo
            for ip in list(self.request_records.keys()):
                self.request_records[ip] = [
                    record for record in self.request_records[ip]
                    if now - record[0] < window
                ]
                
                # Remover IPs sem registros
                if not self.request_records[ip]:
                    del self.request_records[ip]
        
        logger.debug(f"Limpeza de registros de rate limit concluída. IPs ativos: {len(self.request_records)}")
    
    def _get_client_ip(self, request: Request) -> str:
        """Obter IP do cliente com suporte a headers de proxy"""
        # Tentar obter do X-Forwarded-For primeiro (pode conter múltiplos IPs)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Pegar o primeiro IP (geralmente o do cliente)
            ip = forwarded_for.split(",")[0].strip()
            # Validar se é um IP válido
            try:
                ipaddress.ip_address(ip)
                return ip
            except ValueError:
                pass
        
        # Caso contrário, usar o IP do cliente diretamente
        client_host = request.client.host if request.client else "0.0.0.0"
        return client_host
    
    async def _is_rate_limited(self, ip: str, path: str) -> bool:
        """Verificar se o IP excedeu o limite de requisições"""
        if not settings.RATE_LIMIT_ENABLED:
            return False
            
        now = time.time()
        window = settings.RATE_LIMIT_WINDOW
        
        async with self.lock:
            # Adicionar registro atual
            self.request_records[ip].append((now, path))
            
            # Filtrar apenas registros dentro da janela de tempo
            recent_requests = [
                record for record in self.request_records[ip]
                if now - record[0] < window
            ]
            
            # Atualizar a lista filtrada
            self.request_records[ip] = recent_requests
            
            # Verificar se excedeu o limite
            return len(recent_requests) > settings.RATE_LIMIT_REQUESTS
    
    async def dispatch(self, request: Request, call_next):
        # Pular verificação para caminhos isentos
        path = request.url.path
        exempt_paths = ["/docs", "/redoc", "/openapi.json", "/health"]
        if any(path.startswith(exempt) for exempt in exempt_paths):
            return await call_next(request)
        
        # Obter IP do cliente
        client_ip = self._get_client_ip(request)
        
        # Verificar rate limit
        is_limited = await self._is_rate_limited(client_ip, path)
        
        if is_limited:
            logger.warning(f"Rate limit excedido para IP {client_ip} no caminho {path}")
            
            # Retornar erro 429 (Too Many Requests)
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Limite de requisições excedido. Por favor, tente novamente mais tarde."
                },
            )
        
        # Continuar com a requisição normalmente
        return await call_next(request) 