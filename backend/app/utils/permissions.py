"""
Módulo para verificação de permissões no sistema CCONTROL-M.

Este módulo contém funções para verificar se um usuário tem permissão para acessar
determinados recursos ou realizar determinadas ações no sistema.
"""
from typing import Any, Dict, Callable, Optional
from uuid import UUID
from fastapi import HTTPException, status, Depends
from functools import wraps
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user
from app.schemas.token import TokenPayload
from app.repositories.permissao_usuario_repository import PermissaoUsuarioRepository
from app.database import get_async_session
from app.schemas.usuario import Usuario


def verify_permission(
    user: Usuario, 
    permission: str, 
    id_empresa: Optional[UUID] = None
) -> bool:
    """
    Verifica se o usuário tem a permissão especificada.
    
    Args:
        user: Usuário a ser verificado
        permission: Permissão requerida no formato "module:action"
        id_empresa: ID da empresa para verificar acesso multi-tenant
        
    Returns:
        True se tem permissão, False caso contrário
    """
    # Admins sempre têm acesso a tudo
    if user.is_admin:
        return True
        
    # Verificar acesso à empresa
    if id_empresa and not user.empresas:
        return False
        
    if id_empresa and user.empresas and id_empresa not in [emp.id_empresa for emp in user.empresas]:
        return False
    
    # Validar permissão específica
    module, action = permission.split(":") if ":" in permission else (permission, None)
    
    # Se o usuário não tem permissões definidas, retorna False
    if not user.permissoes:
        return False
        
    # Verificar permissões do usuário
    for perm in user.permissoes:
        # Verificar permissão para o módulo e ação específica
        if perm.modulo == module:
            if action is None:  # Se apenas o módulo foi especificado
                return True
            
            # Verificar ação específica
            if action == "visualizar" and perm.pode_visualizar:
                return True
            if action == "criar" and perm.pode_criar:
                return True
            if action == "editar" and perm.pode_editar:
                return True
            if action == "excluir" and perm.pode_excluir:
                return True
    
    return False


def require_permission(module: str, action: Optional[str] = None):
    """
    Decorator para verificar permissões em rotas.
    
    Args:
        module: Módulo da permissão
        action: Ação requerida (visualizar, criar, editar, excluir)
        
    Returns:
        Decorator function
    """
    permission = f"{module}:{action}" if action else module
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, current_user: Usuario = Depends(get_current_user), **kwargs):
            # Extrair ID da empresa dos kwargs se presente
            id_empresa = kwargs.get("id_empresa")
            
            # Verificar permissão
            if not verify_permission(current_user, permission, id_empresa):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permissão negada: {permission}"
                )
            
            return await func(*args, current_user=current_user, **kwargs)
        
        return wrapper
    
    return decorator 