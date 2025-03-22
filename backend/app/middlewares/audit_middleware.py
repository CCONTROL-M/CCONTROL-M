from typing import Callable, Optional
from fastapi import Request, Response
import time
import uuid
import json

from app.core.audit import audit_logger_instance
from app.core.security import get_user_from_request


class AuditMiddleware:
    """
    Middleware para registrar automaticamente todas as requisições HTTP no sistema de auditoria.
    """
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """
        Processa a requisição, registra no sistema de auditoria e retorna a resposta.
        
        Args:
            request: O objeto Request da requisição
            call_next: Função para processar a próxima etapa no middleware
            
        Returns:
            Resposta HTTP processada
        """
        # Gerar um ID de requisição único para correlacionar logs
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Registrar o início da requisição e tempo
        start_time = time.time()
        
        # Extrair dados do usuário autenticado (se houver)
        user_data = None
        
        try:
            # Tentar obter informações do usuário a partir do token
            user_data = await get_user_from_request(request)
        except Exception:
            # Ignorar erros na extração do usuário
            pass
            
        # Processar a requisição
        response = None
        error = None
        
        try:
            # Chamar o próximo middleware ou handler da requisição
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            # Registrar exceções não tratadas
            status_code = 500
            error = str(e)
            # Recriar a resposta em caso de erro
            from fastapi.responses import JSONResponse
            response = JSONResponse(
                status_code=status_code,
                content={"detail": "Internal Server Error"}
            )
        finally:
            # Calcular o tempo de processamento
            process_time = time.time() - start_time
            process_time_ms = process_time * 1000
            
            # Adicionar headers de performance (em ms)
            response.headers["X-Process-Time"] = str(int(process_time_ms))
            
            # Adicionar request_id ao cabeçalho de resposta para rastreamento
            response.headers["X-Request-ID"] = request_id
            
            # Registrar a requisição no sistema de auditoria
            await audit_logger_instance.log_request(
                request=request,
                status_code=status_code,
                response_time=process_time_ms,
                error=error,
                user_data=user_data
            )
            
            # Retornar a resposta processada
            return response


# Função para criar o middleware
def create_audit_middleware() -> AuditMiddleware:
    """
    Cria uma instância do middleware de auditoria.
    """
    return AuditMiddleware() 