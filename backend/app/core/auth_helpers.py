"""
Helpers personalizados para autenticação e segurança.

Este módulo contém classes e funções auxiliares para autenticação e segurança.
"""
from typing import List, Optional
from fastapi import Request, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.models import OAuthFlowPassword

class OAuth2PasswordBearerWithExceptions(OAuth2PasswordBearer):
    """
    Versão personalizada do OAuth2PasswordBearer que permite rotas de exceção.
    """
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[dict] = None,
        auto_error: bool = True,
        exception_paths: List[str] = None
    ):
        """
        Inicializa o bearer com lista de caminhos de exceção.
        
        Args:
            tokenUrl: URL para obtenção do token
            scheme_name: Nome do esquema
            scopes: Escopos suportados
            auto_error: Se deve retornar erro automático
            exception_paths: Lista de caminhos que não exigem autenticação
        """
        self.exception_paths = exception_paths or []
        
        # Inicializar o fluxo OAuth
        flows = OAuthFlowsModel(password=OAuthFlowPassword(tokenUrl=tokenUrl, scopes=scopes or {}))
        
        # Chamar o construtor da classe pai
        super().__init__(
            tokenUrl=tokenUrl,
            scheme_name=scheme_name,
            scopes=scopes,
            auto_error=auto_error
        )
    
    async def __call__(self, request: Request) -> Optional[str]:
        """
        Verifica se o request precisa de autenticação com base no caminho.
        
        Args:
            request: Objeto Request com os dados da requisição
            
        Returns:
            str: Token de autenticação ou None
            
        Raises:
            HTTPException: Se a autenticação for necessária e falhar
        """
        # Verificar se o caminho está na lista de exceções
        for path in self.exception_paths:
            if request.url.path.startswith(path):
                return None
        
        # Para outros caminhos, verificar autenticação normalmente
        authorization = request.headers.get("Authorization")
        
        if not authorization:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token de autenticação não fornecido",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
                
        scheme, token = get_authorization_scheme_param(authorization)
        
        if scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Esquema de autenticação inválido",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
                
        return token 