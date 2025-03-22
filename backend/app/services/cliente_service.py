"""Serviço para gerenciamento de clientes no sistema CCONTROL-M."""
from uuid import UUID
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
import logging

from app.schemas.cliente import ClienteCreate, ClienteUpdate, Cliente
from app.repositories.cliente_repository import ClienteRepository
from app.database import get_async_session
from app.utils.validators import validar_cpf_cnpj


class ClienteService:
    """Serviço para gerenciamento de clientes."""
    
    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        """Inicializar serviço com repositório."""
        self.repository = ClienteRepository(session)
        self.logger = logging.getLogger(__name__)
        
    async def get_cliente(self, id_cliente: UUID, id_empresa: UUID) -> Cliente:
        """
        Obter cliente pelo ID.
        
        Args:
            id_cliente: ID do cliente
            id_empresa: ID da empresa para validação de acesso
            
        Returns:
            Cliente encontrado
            
        Raises:
            HTTPException: Se o cliente não for encontrado
        """
        self.logger.info(f"Buscando cliente ID: {id_cliente}")
        
        cliente = await self.repository.get_by_id(id_cliente, id_empresa)
        if not cliente:
            self.logger.warning(f"Cliente não encontrado: {id_cliente}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado"
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
        Listar clientes com paginação e filtros.
        
        Args:
            id_empresa: ID da empresa para filtrar
            skip: Número de registros a pular
            limit: Número máximo de registros a retornar
            nome: Filtrar por nome
            cpf_cnpj: Filtrar por CPF/CNPJ
            ativo: Filtrar por status
            
        Returns:
            Lista de clientes e contagem total
        """
        self.logger.info(f"Buscando clientes da empresa {id_empresa} com filtros: nome={nome}, cpf_cnpj={cpf_cnpj}")
        
        return await self.repository.list_with_filters(
            skip=skip,
            limit=limit,
            id_empresa=id_empresa,
            nome=nome,
            cpf_cnpj=cpf_cnpj,
            ativo=ativo
        )
        
    async def criar_cliente(self, cliente: ClienteCreate) -> Cliente:
        """
        Criar novo cliente.
        
        Args:
            cliente: Dados do cliente a ser criado
            
        Returns:
            Cliente criado
            
        Raises:
            HTTPException: Se ocorrer um erro na validação
        """
        self.logger.info(f"Criando novo cliente: {cliente.nome} para empresa {cliente.id_empresa}")
        
        # Validar CPF/CNPJ
        if cliente.cpf_cnpj and not validar_cpf_cnpj(cliente.cpf_cnpj):
            self.logger.warning(f"CPF/CNPJ inválido: {cliente.cpf_cnpj}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF/CNPJ inválido"
            )
        
        # Converter para dicionário para enviar ao repositório
        cliente_data = cliente.model_dump()
        
        # Criar cliente no repositório
        try:
            return await self.repository.create_cliente(cliente_data)
        except HTTPException as e:
            self.logger.warning(f"Erro ao criar cliente: {e.detail}")
            raise
        except Exception as e:
            self.logger.error(f"Erro inesperado ao criar cliente: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao criar cliente"
            )
        
    async def atualizar_cliente(self, id_cliente: UUID, cliente: ClienteUpdate, id_empresa: UUID) -> Cliente:
        """
        Atualizar cliente existente.
        
        Args:
            id_cliente: ID do cliente a ser atualizado
            cliente: Dados para atualização
            id_empresa: ID da empresa para validação de acesso
            
        Returns:
            Cliente atualizado
            
        Raises:
            HTTPException: Se o cliente não for encontrado ou ocorrer erro na validação
        """
        self.logger.info(f"Atualizando cliente: {id_cliente}")
        
        # Verificar se o cliente existe
        await self.get_cliente(id_cliente, id_empresa)
        
        # Validar CPF/CNPJ se estiver sendo atualizado
        if cliente.cpf_cnpj and not validar_cpf_cnpj(cliente.cpf_cnpj):
            self.logger.warning(f"CPF/CNPJ inválido: {cliente.cpf_cnpj}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF/CNPJ inválido"
            )
        
        # Remover campos None do modelo de atualização
        update_data = {k: v for k, v in cliente.model_dump().items() if v is not None}
        
        # Atualizar cliente
        try:
            cliente_atualizado = await self.repository.update_cliente(
                id_cliente=id_cliente,
                data=update_data,
                id_empresa=id_empresa
            )
            
            if not cliente_atualizado:
                self.logger.warning(f"Cliente não encontrado após tentativa de atualização: {id_cliente}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente não encontrado ou não pertence à empresa"
                )
            
            return cliente_atualizado
        except HTTPException as e:
            self.logger.warning(f"Erro ao atualizar cliente: {e.detail}")
            raise
        except Exception as e:
            self.logger.error(f"Erro inesperado ao atualizar cliente: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao atualizar cliente"
            )
        
    async def remover_cliente(self, id_cliente: UUID, id_empresa: UUID) -> Dict[str, Any]:
        """
        Remover cliente pelo ID.
        
        Args:
            id_cliente: ID do cliente a ser removido
            id_empresa: ID da empresa para validação de acesso
            
        Returns:
            Mensagem de confirmação
            
        Raises:
            HTTPException: Se o cliente não for encontrado
        """
        self.logger.info(f"Removendo cliente: {id_cliente}")
        
        # Verificar se o cliente existe
        await self.get_cliente(id_cliente, id_empresa)
        
        # Verificar se o cliente está sendo usado em lançamentos ou vendas
        # TODO: Implementar verificação de uso quando repository estiver atualizado
        
        # Tentar remover o cliente
        resultado = await self.repository.delete(id_cliente, id_empresa)
        
        if not resultado:
            self.logger.warning(f"Cliente não encontrado após tentativa de remoção: {id_cliente}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado ou não pertence à empresa"
            )
            
        self.logger.info(f"Cliente removido com sucesso: {id_cliente}")
        return {"detail": "Cliente removido com sucesso"} 