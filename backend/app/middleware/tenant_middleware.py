"""Middleware de multi-tenancy para o sistema CCONTROL-M.

Este middleware gerencia o contexto de tenant (empresa) nas requisições,
garantindo o isolamento de dados entre diferentes empresas.
Compatível com o Supabase como fonte de dados.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, status, HTTPException
from typing import Optional, Dict, Any
import logging
from jose import jwt
from jose.exceptions import JWTError

from app.schemas.token import TokenPayload
from app.config.settings import settings
from app.utils.logging_config import get_logger

# Configurar logger
logger = get_logger(__name__)

# Contexto para armazenar o tenant atual durante a requisição
context = {}


def get_tenant_id() -> Optional[str]:
    """
    Retorna o ID da empresa (tenant) do contexto atual.
    
    Returns:
        Optional[str]: ID da empresa ou None se não estiver no contexto
    """
    return context.get("tenant_id")


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware para gerenciar multi-tenancy.
    
    Este middleware extrai o ID da empresa do token JWT e o disponibiliza
    para uso durante o processamento da requisição. Compatível com Supabase.
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Processa a requisição, extraindo e armazenando o ID da empresa.
        
        Args:
            request: Requisição HTTP
            call_next: Próximo handler na cadeia de middlewares
            
        Returns:
            Response: Resposta HTTP
        """
        # Limpar o contexto no início da requisição
        context.clear()
        
        # Verificar se há um token de autenticação
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            
            try:
                # Extrair claims do token 
                # Nota: Supabase usa tokens JWT com estrutura específica
                payload = jwt.decode(
                    token,
                    settings.JWT_SECRET,
                    algorithms=["HS256"],
                    options={"verify_signature": settings.VERIFY_JWT}
                )
                
                # No Supabase, o ID do usuário está em 'sub' 
                # Precisamos obter o id_empresa com base no id_usuario
                user_id = payload.get("sub")
                
                if user_id:
                    # No middleware, só armazenamos o ID do usuário
                    # O ID da empresa será obtido no primeiro acesso ao banco
                    context["user_id"] = user_id
                    logger.debug(f"User identificado: {user_id}")
                    
                    # Se o JWT já contiver o ID da empresa, armazenamos diretamente
                    empresa_id = payload.get("empresa_id")
                    if empresa_id:
                        context["tenant_id"] = empresa_id
                        logger.debug(f"Tenant identificado: {empresa_id}")
                else:
                    logger.warning("Token válido, mas não contém ID do usuário")
            except JWTError as e:
                # Apenas logamos o erro, a validação completa ocorre em get_current_user
                logger.warning(f"Erro ao extrair tenant_id do token: {str(e)}")
        
        # Executar o próximo middleware ou endpoint
        response = await call_next(request)
        
        # Limpar o contexto no final da requisição
        context.clear()
        
        return response 