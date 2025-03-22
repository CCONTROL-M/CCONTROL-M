"""Serviço para gerenciamento de fornecedores no sistema CCONTROL-M."""
from uuid import UUID
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
import logging

from app.schemas.fornecedor import FornecedorCreate, FornecedorUpdate, Fornecedor
from app.repositories.fornecedor_repository import FornecedorRepository
from app.database import db_async_session
from app.utils.validators import validar_cnpj


class FornecedorService:
    """Serviço para gerenciamento de fornecedores."""
    
    def __init__(self):
        """Inicializar serviço com logger."""
        self.logger = logging.getLogger(__name__)
        
    async def get_fornecedor(self, id_fornecedor: UUID, id_empresa: UUID) -> Fornecedor:
        """
        Busca um fornecedor pelo ID.
        
        Args:
            id_fornecedor: ID do fornecedor
            id_empresa: ID da empresa
            
        Returns:
            Fornecedor: Dados do fornecedor
            
        Raises:
            HTTPException: Se o fornecedor não for encontrado
        """
        self.logger.info(f"Buscando fornecedor ID: {id_fornecedor}")
        
        async with db_async_session() as session:
            repository = FornecedorRepository(session)
            fornecedor = await repository.get_by_id(id_fornecedor, id_empresa)
            
            if not fornecedor:
                self.logger.warning(f"Fornecedor não encontrado: {id_fornecedor}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Fornecedor não encontrado"
                )
                
            return fornecedor
    
    async def listar_fornecedores(
        self,
        id_empresa: UUID,
        skip: int = 0,
        limit: int = 100,
        nome: Optional[str] = None,
        cnpj: Optional[str] = None,
        ativo: Optional[bool] = None,
        avaliacao: Optional[int] = None
    ) -> Tuple[List[Fornecedor], int]:
        """
        Lista fornecedores com filtros e paginação.
        
        Args:
            id_empresa: ID da empresa
            skip: Registros para pular
            limit: Limite de registros
            nome: Filtrar por nome
            cnpj: Filtrar por CNPJ
            ativo: Filtrar por status (ativo/inativo)
            avaliacao: Filtrar por avaliação
            
        Returns:
            Tuple[List[Fornecedor], int]: Lista de fornecedores e contagem total
        """
        self.logger.info(f"Buscando fornecedores da empresa {id_empresa} com filtros: nome={nome}, cnpj={cnpj}")
        
        async with db_async_session() as session:
            repository = FornecedorRepository(session)
            return await repository.list_with_filters(
                skip=skip,
                limit=limit,
                id_empresa=id_empresa,
                nome=nome,
                cnpj=cnpj,
                ativo=ativo,
                avaliacao=avaliacao
            )
    
    async def criar_fornecedor(self, fornecedor: FornecedorCreate) -> Fornecedor:
        """
        Cria um novo fornecedor.
        
        Args:
            fornecedor: Dados do fornecedor
            
        Returns:
            Fornecedor: Dados do fornecedor criado
            
        Raises:
            HTTPException: Se ocorrer um erro na validação ou criação
        """
        self.logger.info(f"Criando fornecedor: {fornecedor.nome}")
        
        # Validar CNPJ se fornecido
        if fornecedor.cnpj:
            if not validar_cnpj(fornecedor.cnpj):
                self.logger.warning(f"CNPJ inválido: {fornecedor.cnpj}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="CNPJ inválido"
                )
        
        # Preparar dados
        fornecedor_data = fornecedor.dict()
        
        # Criar fornecedor no repositório
        async with db_async_session() as session:
            repository = FornecedorRepository(session)
            try:
                return await repository.create_fornecedor(fornecedor_data)
            except HTTPException as e:
                self.logger.warning(f"Erro ao criar fornecedor: {e.detail}")
                raise e
            except Exception as e:
                self.logger.error(f"Erro ao criar fornecedor: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Erro ao criar fornecedor"
                )
    
    async def atualizar_fornecedor(self, id_fornecedor: UUID, fornecedor: FornecedorUpdate, id_empresa: UUID) -> Fornecedor:
        """
        Atualiza um fornecedor existente.
        
        Args:
            id_fornecedor: ID do fornecedor
            fornecedor: Dados atualizados
            id_empresa: ID da empresa
            
        Returns:
            Fornecedor: Dados do fornecedor atualizado
            
        Raises:
            HTTPException: Se ocorrer um erro na validação ou atualização
        """
        self.logger.info(f"Atualizando fornecedor: {id_fornecedor}")
        
        async with db_async_session() as session:
            repository = FornecedorRepository(session)
            
            # Verificar se o fornecedor existe
            fornecedor_atual = await repository.get_by_id(id_fornecedor, id_empresa)
            if not fornecedor_atual:
                self.logger.warning(f"Fornecedor não encontrado: {id_fornecedor}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Fornecedor não encontrado"
                )
            
            # Validar CNPJ se estiver sendo atualizado
            update_data = fornecedor.dict(exclude_unset=True)
            if "cnpj" in update_data and update_data["cnpj"]:
                if not validar_cnpj(update_data["cnpj"]):
                    self.logger.warning(f"CNPJ inválido: {update_data['cnpj']}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="CNPJ inválido"
                    )
            
            # Atualizar fornecedor
            try:
                fornecedor_atualizado = await repository.update_fornecedor(
                    id_fornecedor=id_fornecedor,
                    data=update_data,
                    id_empresa=id_empresa
                )
                return fornecedor_atualizado
            except HTTPException as e:
                self.logger.warning(f"Erro ao atualizar fornecedor: {e.detail}")
                raise e
            except Exception as e:
                self.logger.error(f"Erro ao atualizar fornecedor: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Erro ao atualizar fornecedor"
                )
    
    async def remover_fornecedor(self, id_fornecedor: UUID, id_empresa: UUID) -> Dict[str, Any]:
        """
        Remove um fornecedor.
        
        Args:
            id_fornecedor: ID do fornecedor
            id_empresa: ID da empresa
            
        Returns:
            Dict[str, Any]: Mensagem de sucesso
            
        Raises:
            HTTPException: Se ocorrer um erro na remoção
        """
        self.logger.info(f"Removendo fornecedor: {id_fornecedor}")
        
        async with db_async_session() as session:
            repository = FornecedorRepository(session)
            
            # Verificar se o fornecedor existe
            fornecedor = await repository.get_by_id(id_fornecedor, id_empresa)
            if not fornecedor:
                self.logger.warning(f"Fornecedor não encontrado: {id_fornecedor}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Fornecedor não encontrado"
                )
            
            # Verificar se o fornecedor está sendo usado em lançamentos ou compras
            # TODO: Implementar verificação de uso quando repository estiver atualizado
            
            # Tentar remover o fornecedor
            resultado = await repository.delete(id_fornecedor, id_empresa)
            
            if not resultado:
                self.logger.error(f"Erro ao remover fornecedor: {id_fornecedor}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Erro ao remover fornecedor"
                )
            
            return {"message": "Fornecedor removido com sucesso"} 