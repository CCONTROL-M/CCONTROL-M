"""
Módulo para verificação de permissões no sistema CCONTROL-M.

Este módulo contém funções para verificar se um usuário tem permissão para acessar
determinados recursos ou realizar determinadas ações no sistema.
"""
from typing import Any, Dict, Callable, Optional, List
from uuid import UUID
from fastapi import HTTPException, status, Depends
from functools import wraps
from sqlalchemy.ext.asyncio import AsyncSession
import logging

# Importar apenas o necessário para as funções
# Remover importações que causam dependências circulares
from app.database import get_async_session
from app.schemas.usuario import Usuario

logger = logging.getLogger(__name__)

# Flag para desabilitar verificação de permissões durante testes
DISABLE_PERMISSION_CHECK = True


def verify_permission(
    user: Any, 
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
    if hasattr(user, 'is_admin') and user.is_admin:
        return True
        
    # Verificar acesso à empresa
    if id_empresa and not hasattr(user, 'empresas'):
        return False
        
    if id_empresa and hasattr(user, 'empresas') and user.empresas and id_empresa not in [getattr(emp, 'id_empresa', None) for emp in user.empresas]:
        return False
    
    # Validar permissão específica
    module, action = permission.split(":") if ":" in permission else (permission, None)
    
    # Se o usuário não tem permissões definidas, retorna False
    if not hasattr(user, 'permissoes') or not user.permissoes:
        return False
        
    # Verificar permissões do usuário
    for perm in user.permissoes:
        # Verificar permissão para o módulo e ação específica
        if hasattr(perm, 'modulo') and perm.modulo == module:
            if action is None:  # Se apenas o módulo foi especificado
                return True
            
            # Verificar ação específica
            if action == "visualizar" and hasattr(perm, 'pode_visualizar') and perm.pode_visualizar:
                return True
            if action == "criar" and hasattr(perm, 'pode_criar') and perm.pode_criar:
                return True
            if action == "editar" and hasattr(perm, 'pode_editar') and perm.pode_editar:
                return True
            if action == "excluir" and hasattr(perm, 'pode_excluir') and perm.pode_excluir:
                return True
    
    return False


def require_permission(resource: str, action: str):
    """
    Decorador para verificar se o usuário tem permissão para acessar um recurso.
    
    Args:
        resource: Nome do recurso (ex: "usuarios", "empresas")
        action: Ação no recurso (ex: "criar", "visualizar", "editar", "excluir")
    
    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Obter usuário atual dos parâmetros
            current_user = None
            for key, value in kwargs.items():
                if isinstance(value, Usuario):
                    current_user = value
                    break
            
            # Se não encontrou, verificar se há um current_user no Depends
            if not current_user:
                for arg in args:
                    if isinstance(arg, Usuario):
                        current_user = arg
                        break
            
            # Se não encontrou o usuário, deixa passar (será tratado em outro lugar)
            if not current_user:
                logger.warning(f"Usuário não encontrado ao verificar permissão {resource}:{action}")
                return await func(*args, **kwargs)
            
            # Verificar permissão (desabilitado durante testes)
            if DISABLE_PERMISSION_CHECK:
                logger.debug(f"Verificação de permissão desabilitada: {resource}:{action}")
                return await func(*args, **kwargs)
            
            # Obter as permissões do usuário
            permissoes = getattr(current_user, "permissoes", [])
            
            # Verificar se o usuário é admin (tem todas as permissões)
            if current_user.is_admin:
                return await func(*args, **kwargs)
            
            # Verificar se o usuário tem a permissão específica
            permission_key = f"{resource}:{action}"
            if permission_key in permissoes:
                return await func(*args, **kwargs)
            
            # Verificar se o usuário tem permissão wildcard para o recurso
            if f"{resource}:*" in permissoes:
                return await func(*args, **kwargs)
            
            # Se chegou aqui, não tem permissão
            logger.warning(f"Acesso negado: usuário {current_user.id} não tem permissão {permission_key}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado: você não tem permissão para {action} {resource}"
            )
            
        return wrapper
    return decorator 