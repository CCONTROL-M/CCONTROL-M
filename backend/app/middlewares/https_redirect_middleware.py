from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse
from starlette.types import ASGIApp
import logging

logger = logging.getLogger(__name__)

class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """
    Middleware para redirecionar requisições HTTP para HTTPS.
    
    Verifica se a requisição foi feita via HTTP e, se for o caso, 
    redireciona para o mesmo caminho, mas utilizando HTTPS.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        logger.info("Middleware de redirecionamento HTTPS inicializado")
    
    async def dispatch(self, request: Request, call_next):
        # Verificar se a solicitação já está usando HTTPS
        proto = request.headers.get("X-Forwarded-Proto", "").lower()
        host = request.headers.get("X-Forwarded-Host") or request.headers.get("Host", "")
        
        is_https = (
            proto == "https" or 
            request.headers.get("X-Forwarded-Ssl") == "on" or
            request.headers.get("X-Forwarded-Scheme", "").lower() == "https" or
            request.url.scheme == "https"
        )
        
        # Se não estiver usando HTTPS, redirecionar para HTTPS
        if not is_https:
            # Construir URL HTTPS
            url = request.url.replace(scheme="https")
            
            # Registrar o redirecionamento
            logger.info(f"Redirecionando solicitação de {request.url} para {url}")
            
            # Retornar resposta de redirecionamento permanente
            return RedirectResponse(url=str(url), status_code=301)
        
        # Se já estiver usando HTTPS, continuar normalmente
        return await call_next(request) 