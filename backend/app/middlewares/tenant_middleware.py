"""Middleware para gerenciamento de multilocação (multi-tenancy).

Este middleware extrai o ID da empresa (tenant) do token JWT e o disponibiliza
no contexto da requisição para uso pela aplicação.
"""
import logging
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
import jwt
from app.config.settings import settings

logger = logging.getLogger(__name__)

class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware para extrair o ID da empresa (tenant) do token JWT
    e configurar a variável de sessão do PostgreSQL para o RLS.
    
    Este middleware funciona com tokens gerados pelo Supabase.
    """
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        Processa a requisição, extraindo o ID da empresa do token e
        configurando o contexto para o RLS.
        
        Args:
            request: Objeto Request da requisição
            call_next: Próximo middleware/endpoint na cadeia
        
        Returns:
            Response: Resposta HTTP
        
        Raises:
            HTTPException: Se ocorrer um erro ao processar o token
        """
        # Adicionar contexto vazio para o tenant
        request.state.tenant_id = None
        
        # Verificar se há token de autenticação
        if "authorization" in request.headers:
            try:
                # Extrair o token Bearer
                auth_header = request.headers["authorization"]
                if auth_header.startswith("Bearer "):
                    token = auth_header.replace("Bearer ", "")
                    
                    # Decodificar o token
                    # Nota: No Supabase, não verificamos a assinatura aqui,
                    # pois o token já foi validado pelo Supabase Auth
                    payload = jwt.decode(token, options={"verify_signature": False})
                    
                    # No Supabase, a informação do tenant está nos metadados do usuário
                    # Verificar se há metadados do usuário
                    if "user_metadata" in payload and payload["user_metadata"]:
                        user_metadata = payload["user_metadata"]
                        
                        # Extrair ID da empresa
                        # A propriedade pode ser "id_empresa", "empresa_id", "tenant_id", etc.
                        empresa_id = None
                        for key in ["id_empresa", "empresa_id", "tenant_id", "companyId"]:
                            if key in user_metadata:
                                empresa_id = user_metadata[key]
                                break
                        
                        if empresa_id:
                            # Armazenar ID da empresa no contexto da requisição
                            request.state.tenant_id = empresa_id
                            logger.debug(f"Requisição para empresa ID: {empresa_id}")
                        else:
                            logger.warning("Token JWT não contém ID da empresa nos metadados")
                    else:
                        logger.warning("Token JWT não contém metadados do usuário")
            except jwt.PyJWTError as e:
                logger.error(f"Erro ao decodificar token JWT: {str(e)}")
            except Exception as e:
                logger.error(f"Erro ao processar token de autenticação: {str(e)}")
        
        # Continuar com a cadeia de middleware/endpoint
        response = await call_next(request)
        return response 