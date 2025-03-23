"""Serviço para gerenciamento de clientes no sistema CCONTROL-M."""
from uuid import UUID
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, Depends
import logging
from datetime import datetime

from app.schemas.cliente import ClienteCreate, ClienteUpdate, Cliente
from app.repositories.cliente_repository import ClienteRepository
from app.database import get_async_session
from app.utils.validators import validar_cpf_cnpj
from app.schemas.pagination import PaginatedResponse
from app.services.auditoria_service import AuditoriaService


# Configurar logger
logger = logging.getLogger(__name__)


class ClienteService:
    """Serviço para gerenciamento de clientes."""
    
    def __init__(self, 
                 session: AsyncSession = Depends(get_async_session),
                 auditoria_service: AuditoriaService = Depends()):
        """Inicializar serviço com repositórios."""
        self.repository = ClienteRepository(session)
        self.auditoria_service = auditoria_service
        self.logger = logger
    
    async def get_cliente(self, id_cliente: UUID, id_empresa: UUID) -> Cliente:
        """
        Obter cliente pelo ID com verificação de empresa.
        
        Args:
            id_cliente: ID do cliente
            id_empresa: ID da empresa para validação
            
        Returns:
            Cliente: Dados do cliente
            
        Raises:
            HTTPException: Se o cliente não for encontrado ou não pertencer à empresa
        """
        async with get_async_session() as session:
            repository = ClienteRepository(session)
            cliente = await repository.get_by_id(id_cliente, id_empresa)
            
            if not cliente:
                self.logger.warning(f"Cliente ID={id_cliente} não encontrado")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente não encontrado"
                )
            
            # Verificar se o cliente pertence à empresa
            if cliente.id_empresa != id_empresa:
                self.logger.warning(f"Acesso negado a cliente ID={id_cliente} da empresa {cliente.id_empresa} (solicitado por {id_empresa})")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cliente não pertence à empresa informada"
                )
                
            return cliente
    
    async def listar_clientes(
        self,
        id_empresa: UUID,
        skip: int = 0,
        limit: int = 100,
        nome: Optional[str] = None,
        cpf_cnpj: Optional[str] = None,
        ativo: Optional[bool] = None
    ) -> Tuple[List[Cliente], int]:
        """
        Listar clientes com filtros e paginação.
        
        Args:
            id_empresa: ID da empresa
            skip: Registros para pular
            limit: Limite de registros
            nome: Filtro por nome
            cpf_cnpj: Filtro por CPF/CNPJ
            ativo: Filtro por status
            
        Returns:
            Tuple[List[Cliente], int]: Lista de clientes e contagem total
        """
        async with get_async_session() as session:
            repository = ClienteRepository(session)
            
            # Construir filtros
            filters = {}
            if nome:
                filters["nome"] = nome
            if cpf_cnpj:
                filters["cpf_cnpj"] = cpf_cnpj
            if ativo is not None:
                filters["ativo"] = ativo
                
            self.logger.info(f"Listando clientes com filtros: {filters}")
            
            # Buscar clientes com filtros
            return await repository.list_with_filters(
                skip=skip,
                limit=limit,
                id_empresa=id_empresa,
                **filters
            )
    
    async def criar_cliente(self, cliente: ClienteCreate) -> Cliente:
        """
        Criar novo cliente com validações.
        
        Args:
            cliente: Dados do cliente a ser criado
            
        Returns:
            Cliente: Cliente criado
            
        Raises:
            HTTPException: Se houver erro de validação ou conflito
        """
        async with get_async_session() as session:
            repository = ClienteRepository(session)
            
            # Validar CPF/CNPJ
            if not validar_cpf_cnpj(cliente.cpf_cnpj):
                self.logger.warning(f"CPF/CNPJ inválido: {cliente.cpf_cnpj}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="CPF/CNPJ inválido"
                )
            
            # Verificar duplicidade de CPF/CNPJ na mesma empresa
            existente = await repository.get_by_cpf_cnpj_empresa(
                cpf_cnpj=cliente.cpf_cnpj, 
                id_empresa=cliente.id_empresa
            )
            
            if existente:
                self.logger.warning(f"CPF/CNPJ {cliente.cpf_cnpj} já cadastrado para empresa {cliente.id_empresa}")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="CPF/CNPJ já cadastrado para outro cliente desta empresa"
                )
            
            # Criar cliente
            self.logger.info(f"Criando cliente: {cliente.nome}, CPF/CNPJ: {cliente.cpf_cnpj}")
            return await repository.create(cliente.dict())
    
    async def atualizar_cliente(self, id_cliente: UUID, cliente: ClienteUpdate, id_empresa: UUID) -> Cliente:
        """
        Atualizar cliente existente com validações.
        
        Args:
            id_cliente: ID do cliente
            cliente: Dados para atualização
            id_empresa: ID da empresa para validação
            
        Returns:
            Cliente: Cliente atualizado
            
        Raises:
            HTTPException: Se o cliente não for encontrado ou houver erro de validação
        """
        async with get_async_session() as session:
            repository = ClienteRepository(session)
            
            # Verificar se o cliente existe e pertence à empresa
            existente = await repository.get_by_id(id_cliente, id_empresa)
            
            if not existente:
                self.logger.warning(f"Cliente ID={id_cliente} não encontrado")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente não encontrado"
                )
                
            if existente.id_empresa != id_empresa:
                self.logger.warning(f"Acesso negado a cliente ID={id_cliente} da empresa {existente.id_empresa} (solicitado por {id_empresa})")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cliente não pertence à empresa informada"
                )
            
            # Preparar dados para atualização
            dados_atualizacao = cliente.dict(exclude_unset=True)
            
            # Validar CPF/CNPJ se estiver sendo modificado
            if "cpf_cnpj" in dados_atualizacao:
                if not validar_cpf_cnpj(dados_atualizacao["cpf_cnpj"]):
                    self.logger.warning(f"CPF/CNPJ inválido: {dados_atualizacao['cpf_cnpj']}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="CPF/CNPJ inválido"
                    )
                
                # Verificar se o novo CPF/CNPJ já está em uso
                if dados_atualizacao["cpf_cnpj"] != existente.cpf_cnpj:
                    cliente_existente = await repository.get_by_cpf_cnpj_empresa(
                        cpf_cnpj=dados_atualizacao["cpf_cnpj"],
                        id_empresa=id_empresa
                    )
                    
                    if cliente_existente and cliente_existente.id_cliente != id_cliente:
                        self.logger.warning(f"CPF/CNPJ {dados_atualizacao['cpf_cnpj']} já cadastrado para cliente {cliente_existente.id_cliente}")
                        raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail="CPF/CNPJ já cadastrado para outro cliente"
                        )
            
            # Atualizar cliente
            self.logger.info(f"Atualizando cliente ID={id_cliente}: {dados_atualizacao}")
            return await repository.update(id_cliente, dados_atualizacao, id_empresa)
    
    async def remover_cliente(self, id_cliente: UUID, id_empresa: UUID) -> Dict[str, Any]:
        """
        Remover cliente pelo ID.
        
        Args:
            id_cliente: ID do cliente
            id_empresa: ID da empresa para validação
            
        Returns:
            Dict: Mensagem de sucesso
            
        Raises:
            HTTPException: Se o cliente não for encontrado ou não puder ser removido
        """
        async with get_async_session() as session:
            repository = ClienteRepository(session)
            
            # Verificar se o cliente existe e pertence à empresa
            cliente = await repository.get_by_id(id_cliente, id_empresa)
            
            if not cliente:
                self.logger.warning(f"Cliente ID={id_cliente} não encontrado")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente não encontrado"
                )
                
            if cliente.id_empresa != id_empresa:
                self.logger.warning(f"Acesso negado a cliente ID={id_cliente} da empresa {cliente.id_empresa} (solicitado por {id_empresa})")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cliente não pertence à empresa informada"
                )
            
            # TODO: Verificar se o cliente possui vendas ou outros registros relacionados
            # Aqui pode ser adicionada uma verificação para evitar exclusão de clientes com registros dependentes
            
            # Remover cliente
            self.logger.info(f"Removendo cliente ID={id_cliente}, nome={cliente.nome}")
            await repository.delete(id_cliente, id_empresa)
            
            return {"message": "Cliente removido com sucesso"}

    async def create(
        self,
        cliente: ClienteCreate,
        usuario_id: UUID,
        empresa_id: UUID
    ) -> Cliente:
        """
        Criar um novo cliente.
        
        Args:
            cliente: Dados do cliente a ser criado
            usuario_id: ID do usuário que está criando
            empresa_id: ID da empresa
            
        Returns:
            Cliente criado
            
        Raises:
            HTTPException: Se houver erro na criação
        """
        try:
            # Verificar se documento já existe
            if await self.repository.get_by_documento(cliente.documento, empresa_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Documento já cadastrado"
                )
            
            # Criar cliente
            novo_cliente = await self.repository.create(cliente, empresa_id)
            
            # Registrar ação
            await self.auditoria_service.registrar_acao(
                usuario_id=usuario_id,
                acao="CRIAR_CLIENTE",
                detalhes={
                    "id_cliente": str(novo_cliente.id_cliente),
                    "nome": novo_cliente.nome,
                    "tipo": novo_cliente.tipo,
                    "documento": novo_cliente.documento
                },
                empresa_id=empresa_id
            )
            
            return novo_cliente
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Erro ao criar cliente: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao criar cliente"
            )

    async def update(
        self,
        id_cliente: UUID,
        cliente: ClienteUpdate,
        usuario_id: UUID,
        empresa_id: UUID
    ) -> Cliente:
        """
        Atualizar um cliente existente.
        
        Args:
            id_cliente: ID do cliente a ser atualizado
            cliente: Dados atualizados do cliente
            usuario_id: ID do usuário que está atualizando
            empresa_id: ID da empresa
            
        Returns:
            Cliente atualizado
            
        Raises:
            HTTPException: Se houver erro na atualização
        """
        try:
            # Buscar cliente existente
            cliente_atual = await self.repository.get_by_id(id_cliente)
            if not cliente_atual:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente não encontrado"
                )
            
            # Verificar documento se alterado
            if cliente.documento and cliente.documento != cliente_atual.documento:
                if await self.repository.get_by_documento(cliente.documento, empresa_id):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Documento já cadastrado"
                    )
            
            # Atualizar cliente
            cliente_atualizado = await self.repository.update(id_cliente, cliente)
            
            # Registrar ação
            await self.auditoria_service.registrar_acao(
                usuario_id=usuario_id,
                acao="ATUALIZAR_CLIENTE",
                detalhes={
                    "id_cliente": str(id_cliente),
                    "alteracoes": cliente.model_dump(exclude_unset=True)
                },
                empresa_id=empresa_id
            )
            
            return cliente_atualizado
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Erro ao atualizar cliente: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao atualizar cliente"
            )

    async def delete(
        self,
        id_cliente: UUID,
        usuario_id: UUID,
        empresa_id: UUID
    ) -> None:
        """
        Excluir um cliente.
        
        Args:
            id_cliente: ID do cliente a ser excluído
            usuario_id: ID do usuário que está excluindo
            empresa_id: ID da empresa
            
        Raises:
            HTTPException: Se houver erro na exclusão
        """
        try:
            # Buscar cliente
            cliente = await self.repository.get_by_id(id_cliente)
            if not cliente:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente não encontrado"
                )
            
            # Excluir cliente
            await self.repository.delete(id_cliente)
            
            # Registrar ação
            await self.auditoria_service.registrar_acao(
                usuario_id=usuario_id,
                acao="EXCLUIR_CLIENTE",
                detalhes={
                    "id_cliente": str(id_cliente),
                    "nome": cliente.nome,
                    "tipo": cliente.tipo,
                    "documento": cliente.documento
                },
                empresa_id=empresa_id
            )
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Erro ao excluir cliente: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao excluir cliente"
            )

    async def get_by_id(
        self,
        id_cliente: UUID,
        usuario_id: UUID,
        empresa_id: UUID
    ) -> Cliente:
        """
        Buscar um cliente pelo ID.
        
        Args:
            id_cliente: ID do cliente a ser buscado
            usuario_id: ID do usuário que está buscando
            empresa_id: ID da empresa
            
        Returns:
            Cliente encontrado
            
        Raises:
            HTTPException: Se o cliente não for encontrado
        """
        try:
            cliente = await self.repository.get_by_id(id_cliente)
            if not cliente:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente não encontrado"
                )
                
            # Registrar ação de consulta
            await self.auditoria_service.registrar_acao(
                usuario_id=usuario_id,
                acao="CONSULTAR_CLIENTE",
                detalhes={"id_cliente": str(id_cliente)},
                empresa_id=empresa_id
            )
                
            return cliente
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Erro ao buscar cliente: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao buscar cliente"
            )

    async def get_multi(
        self,
        empresa_id: UUID,
        skip: int = 0,
        limit: int = 100,
        tipo: Optional[str] = None,
        status: Optional[str] = None,
        busca: Optional[str] = None
    ) -> PaginatedResponse[Cliente]:
        """
        Buscar múltiplos clientes com filtros.
        
        Args:
            empresa_id: ID da empresa
            skip: Número de registros para pular
            limit: Número máximo de registros
            tipo: Filtrar por tipo de cliente
            status: Filtrar por status
            busca: Termo para busca
            
        Returns:
            Lista paginada de clientes
        """
        try:
            clientes, total = await self.repository.get_multi(
                empresa_id=empresa_id,
                skip=skip,
                limit=limit,
                tipo=tipo,
                status=status,
                busca=busca
            )
            
            return PaginatedResponse(
                items=clientes,
                total=total,
                page=skip // limit + 1 if limit > 0 else 1,
                size=limit,
                pages=(total + limit - 1) // limit if limit > 0 else 1
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar clientes: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao buscar clientes"
            ) 