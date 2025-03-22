"""
Router para o módulo de Clientes com validação avançada.

Este módulo implementa operações CRUD para clientes com validação robusta de dados.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.db.session import get_db
from app.schemas.cliente_validado import (
    ClienteCreate, ClienteUpdate, ClienteResponse, SituacaoCliente
)
from app.core.security import get_current_user_with_permissions
from app.models.usuario import Usuario
from app.core.audit import log_sensitive_operation
from app.utils.logging_config import get_logger

# Configurar logger
logger = get_logger(__name__)

# Criar router
router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"],
    dependencies=[Depends(get_current_user_with_permissions(["clientes:ler"]))],
)


@router.post(
    "",
    response_model=ClienteResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user_with_permissions(["clientes:criar"]))],
)
async def criar_cliente(
    cliente: ClienteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_with_permissions(["clientes:criar"]))
):
    """
    Cria um novo cliente com validação avançada de dados.
    
    Realiza validações complexas nos dados do cliente:
    - Valida documento (CPF/CNPJ) de acordo com o tipo de cliente
    - Garante formato padronizado para contatos
    - Sanitiza inputs para evitar ataques
    - Verifica informações de endereço
    
    Args:
        cliente: Dados do cliente a ser criado
        db: Sessão do banco de dados
        current_user: Usuário autenticado realizando a operação
        
    Returns:
        Cliente criado com dados validados
    """
    try:
        # TODO: Implementar integração com o repositório para salvar no banco
        # Por enquanto, simulamos o retorno
        
        logger.info(
            f"Cliente criado: {cliente.nome} ({cliente.tipo})",
            extra={"user_id": current_user.id, "empresa_id": current_user.empresa_id}
        )
        
        # Registrar operação sensível
        await log_sensitive_operation(
            db=db,
            user=current_user,
            action="cliente:criar",
            resource_type="cliente", 
            resource_id=None,  # Ainda não temos o ID
            details=f"Criação de cliente: {cliente.nome} ({cliente.documento})"
        )
        
        # Simular resposta
        return ClienteResponse(
            id=1,
            tipo=cliente.tipo,
            nome=cliente.nome,
            nome_fantasia=cliente.nome_fantasia,
            documento=cliente.documento,
            inscricao_estadual=cliente.inscricao_estadual,
            data_nascimento=cliente.data_nascimento,
            limite_credito=cliente.limite_credito,
            situacao=cliente.situacao,
            observacoes=cliente.observacoes,
            enderecos=cliente.enderecos,
            contatos=cliente.contatos,
            created_at=datetime.now().date(),
            updated_at=None
        )
    except ValueError as e:
        logger.error(f"Erro de validação ao criar cliente: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao criar cliente: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar a solicitação"
        )


@router.get(
    "",
    response_model=List[ClienteResponse],
    dependencies=[Depends(get_current_user_with_permissions(["clientes:ler"]))],
)
async def listar_clientes(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_with_permissions(["clientes:ler"])),
    nome: Optional[str] = Query(None, description="Filtrar por nome"),
    documento: Optional[str] = Query(None, description="Filtrar por documento (CPF/CNPJ)"),
    situacao: Optional[SituacaoCliente] = Query(None, description="Filtrar por situação"),
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=500, description="Número máximo de registros para retornar")
):
    """
    Lista clientes com opções de filtro e paginação.
    
    Args:
        db: Sessão do banco de dados
        current_user: Usuário autenticado realizando a operação
        nome: Filtro por nome do cliente
        documento: Filtro por documento do cliente
        situacao: Filtro por situação do cliente
        skip: Quantidade de registros para pular (paginação)
        limit: Quantidade máxima de registros para retornar (paginação)
        
    Returns:
        Lista de clientes que correspondem aos filtros
    """
    try:
        # TODO: Implementar integração com o repositório para buscar do banco
        # Por enquanto, simulamos o retorno
        
        logger.info(
            f"Listagem de clientes solicitada",
            extra={
                "user_id": current_user.id, 
                "empresa_id": current_user.empresa_id,
                "filtros": {
                    "nome": nome,
                    "documento": documento,
                    "situacao": situacao.value if situacao else None
                }
            }
        )
        
        # Simular resposta
        return [
            ClienteResponse(
                id=1,
                tipo="pessoa_fisica",
                nome="Cliente Teste",
                nome_fantasia=None,
                documento="123.456.789-00",
                inscricao_estadual=None,
                data_nascimento=datetime(1990, 1, 1).date(),
                limite_credito=1000.0,
                situacao=SituacaoCliente.ATIVO,
                observacoes=None,
                enderecos=[
                    {
                        "logradouro": "Rua Teste",
                        "numero": "123",
                        "complemento": "Apto 101",
                        "bairro": "Centro",
                        "cidade": "São Paulo",
                        "uf": "SP",
                        "cep": "01234-567",
                        "principal": True
                    }
                ],
                contatos=[
                    {
                        "tipo": "celular",
                        "valor": "(11) 98765-4321",
                        "principal": True,
                        "observacao": None
                    },
                    {
                        "tipo": "email",
                        "valor": "teste@exemplo.com",
                        "principal": False,
                        "observacao": None
                    }
                ],
                created_at=datetime.now().date(),
                updated_at=None
            )
        ]
    except Exception as e:
        logger.error(f"Erro ao listar clientes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar a solicitação"
        )


@router.get(
    "/{cliente_id}",
    response_model=ClienteResponse,
    dependencies=[Depends(get_current_user_with_permissions(["clientes:ler"]))],
)
async def obter_cliente(
    cliente_id: int = Path(..., ge=1, description="ID do cliente"),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_with_permissions(["clientes:ler"]))
):
    """
    Obtém os detalhes de um cliente específico.
    
    Args:
        cliente_id: ID do cliente a ser obtido
        db: Sessão do banco de dados
        current_user: Usuário autenticado realizando a operação
        
    Returns:
        Dados detalhados do cliente
    """
    try:
        # TODO: Implementar integração com o repositório para buscar do banco
        # Por enquanto, simulamos o retorno
        
        logger.info(
            f"Detalhes do cliente {cliente_id} solicitados",
            extra={"user_id": current_user.id, "empresa_id": current_user.empresa_id}
        )
        
        # Simular resposta
        return ClienteResponse(
            id=cliente_id,
            tipo="pessoa_fisica",
            nome="Cliente Teste",
            nome_fantasia=None,
            documento="123.456.789-00",
            inscricao_estadual=None,
            data_nascimento=datetime(1990, 1, 1).date(),
            limite_credito=1000.0,
            situacao=SituacaoCliente.ATIVO,
            observacoes=None,
            enderecos=[
                {
                    "logradouro": "Rua Teste",
                    "numero": "123",
                    "complemento": "Apto 101",
                    "bairro": "Centro",
                    "cidade": "São Paulo",
                    "uf": "SP",
                    "cep": "01234-567",
                    "principal": True
                }
            ],
            contatos=[
                {
                    "tipo": "celular",
                    "valor": "(11) 98765-4321",
                    "principal": True,
                    "observacao": None
                },
                {
                    "tipo": "email",
                    "valor": "teste@exemplo.com",
                    "principal": False,
                    "observacao": None
                }
            ],
            created_at=datetime.now().date(),
            updated_at=None
        )
    except Exception as e:
        logger.error(f"Erro ao obter cliente {cliente_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar a solicitação"
        )


@router.put(
    "/{cliente_id}",
    response_model=ClienteResponse,
    dependencies=[Depends(get_current_user_with_permissions(["clientes:editar"]))],
)
async def atualizar_cliente(
    cliente: ClienteUpdate,
    cliente_id: int = Path(..., ge=1, description="ID do cliente"),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_with_permissions(["clientes:editar"]))
):
    """
    Atualiza os dados de um cliente existente.
    
    Args:
        cliente: Dados do cliente a serem atualizados
        cliente_id: ID do cliente a ser atualizado
        db: Sessão do banco de dados
        current_user: Usuário autenticado realizando a operação
        
    Returns:
        Cliente atualizado com dados validados
    """
    try:
        # TODO: Implementar integração com o repositório para atualizar no banco
        # Por enquanto, simulamos o retorno
        
        logger.info(
            f"Cliente {cliente_id} atualizado",
            extra={"user_id": current_user.id, "empresa_id": current_user.empresa_id}
        )
        
        # Registrar operação sensível
        await log_sensitive_operation(
            db=db,
            user=current_user,
            action="cliente:atualizar",
            resource_type="cliente", 
            resource_id=cliente_id,
            details=f"Atualização de cliente ID {cliente_id}"
        )
        
        # Simular resposta
        return ClienteResponse(
            id=cliente_id,
            tipo="pessoa_fisica",
            nome=cliente.nome or "Cliente Teste",
            nome_fantasia=cliente.nome_fantasia,
            documento="123.456.789-00",
            inscricao_estadual=cliente.inscricao_estadual,
            data_nascimento=cliente.data_nascimento or datetime(1990, 1, 1).date(),
            limite_credito=cliente.limite_credito or 1000.0,
            situacao=cliente.situacao or SituacaoCliente.ATIVO,
            observacoes=cliente.observacoes,
            enderecos=[
                {
                    "logradouro": "Rua Teste",
                    "numero": "123",
                    "complemento": "Apto 101",
                    "bairro": "Centro",
                    "cidade": "São Paulo",
                    "uf": "SP",
                    "cep": "01234-567",
                    "principal": True
                }
            ],
            contatos=[
                {
                    "tipo": "celular",
                    "valor": "(11) 98765-4321",
                    "principal": True,
                    "observacao": None
                },
                {
                    "tipo": "email",
                    "valor": "teste@exemplo.com",
                    "principal": False,
                    "observacao": None
                }
            ],
            created_at=datetime.now().date(),
            updated_at=datetime.now().date()
        )
    except ValueError as e:
        logger.error(f"Erro de validação ao atualizar cliente {cliente_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao atualizar cliente {cliente_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar a solicitação"
        )


@router.delete(
    "/{cliente_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user_with_permissions(["clientes:excluir"]))],
)
async def excluir_cliente(
    cliente_id: int = Path(..., ge=1, description="ID do cliente"),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_with_permissions(["clientes:excluir"]))
):
    """
    Remove um cliente do sistema.
    
    Args:
        cliente_id: ID do cliente a ser removido
        db: Sessão do banco de dados
        current_user: Usuário autenticado realizando a operação
    """
    try:
        # TODO: Implementar integração com o repositório para excluir do banco
        # Por enquanto, simulamos a operação
        
        logger.info(
            f"Cliente {cliente_id} excluído",
            extra={"user_id": current_user.id, "empresa_id": current_user.empresa_id}
        )
        
        # Registrar operação sensível
        await log_sensitive_operation(
            db=db,
            user=current_user,
            action="cliente:excluir",
            resource_type="cliente", 
            resource_id=cliente_id,
            details=f"Exclusão de cliente ID {cliente_id}"
        )
        
        # Sem retorno para operação de exclusão
        return None
    except Exception as e:
        logger.error(f"Erro ao excluir cliente {cliente_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar a solicitação"
        ) 