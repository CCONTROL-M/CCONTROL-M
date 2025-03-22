"""Router para logs do sistema."""
import logging
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.services.log_sistema_service import LogSistemaService
from app.schemas.log_sistema import LogSistema, LogSistemaList
from app.dependencies import get_current_user


logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/logs",
    tags=["Logs"],
    responses={404: {"description": "Log não encontrado"}},
)


@router.get("/", response_model=LogSistemaList)
async def listar_logs(
    id_empresa: Optional[UUID] = None,
    id_usuario: Optional[UUID] = None,
    acao: Optional[str] = None,
    busca: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    ordenar_por: str = Query("created_at", regex=r"^[a-zA-Z_]+$"),
    ordem: str = Query("desc", regex=r"^(asc|desc)$"),
    usuario_atual: dict = Depends(get_current_user),
    service: LogSistemaService = Depends()
):
    """
    Retorna uma lista paginada de logs do sistema com filtros opcionais.
    
    Apenas administradores podem visualizar logs de todas as empresas.
    Usuários comuns só podem ver logs da própria empresa.
    """
    logger.info(f"Listando logs do sistema. Usuário: {usuario_atual['id_usuario']}")
    
    # Verificar permissões (apenas admin pode ver logs de todas as empresas)
    if usuario_atual.get("tipo_usuario") != "ADMIN" and not id_empresa:
        id_empresa = usuario_atual.get("id_empresa")
    
    # Se não for admin e tentar ver logs de outra empresa, bloquear
    if (usuario_atual.get("tipo_usuario") != "ADMIN" 
            and id_empresa and id_empresa != usuario_atual.get("id_empresa")):
        raise HTTPException(
            status_code=403,
            detail="Sem permissão para visualizar logs de outras empresas"
        )
    
    return await service.get_logs(
        id_empresa=id_empresa,
        id_usuario=id_usuario,
        acao=acao,
        busca=busca,
        skip=skip,
        limit=limit,
        ordenar_por=ordenar_por,
        ordem=ordem
    )


@router.get("/{id_log}", response_model=LogSistema)
async def obter_log(
    id_log: UUID,
    usuario_atual: dict = Depends(get_current_user),
    service: LogSistemaService = Depends()
):
    """
    Retorna um log específico pelo ID.
    
    Apenas administradores e usuários da mesma empresa podem visualizar o log.
    """
    logger.info(f"Obtendo log {id_log}. Usuário: {usuario_atual['id_usuario']}")
    
    log = await service.get_log_by_id(id_log)
    
    # Verificar permissões (apenas admin pode ver logs de outras empresas)
    if (usuario_atual.get("tipo_usuario") != "ADMIN" 
            and log.id_empresa and log.id_empresa != usuario_atual.get("id_empresa")):
        raise HTTPException(
            status_code=403,
            detail="Sem permissão para visualizar logs de outras empresas"
        )
    
    return log


@router.delete("/limpar")
async def limpar_logs_antigos(
    dias: int = Query(90, ge=1, le=365),
    id_empresa: Optional[UUID] = None,
    usuario_atual: dict = Depends(get_current_user),
    service: LogSistemaService = Depends()
):
    """
    Remove logs mais antigos que o número de dias especificado.
    
    Apenas administradores podem remover logs de todas as empresas.
    Usuários comuns só podem remover logs da própria empresa.
    """
    logger.info(f"Limpando logs antigos (mais de {dias} dias). Usuário: {usuario_atual['id_usuario']}")
    
    # Verificar permissões (apenas admin pode limpar logs de todas as empresas)
    if usuario_atual.get("tipo_usuario") != "ADMIN" and not id_empresa:
        id_empresa = usuario_atual.get("id_empresa")
    
    # Se não for admin e tentar limpar logs de outra empresa, bloquear
    if (usuario_atual.get("tipo_usuario") != "ADMIN" 
            and id_empresa and id_empresa != usuario_atual.get("id_empresa")):
        raise HTTPException(
            status_code=403,
            detail="Sem permissão para limpar logs de outras empresas"
        )
    
    quantidade = await service.limpar_logs_antigos(
        dias=dias,
        id_empresa=id_empresa
    )
    
    return {"mensagem": f"Removidos {quantidade} logs antigos (mais de {dias} dias)"} 