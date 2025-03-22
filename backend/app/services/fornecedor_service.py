"""Serviço para gerenciamento de fornecedores no sistema CCONTROL-M."""
from uuid import UUID
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
import logging

from app.schemas.fornecedor import FornecedorCreate, FornecedorUpdate, Fornecedor
from app.repositories.fornecedor_repository import FornecedorRepository
from app.database import get_async_session
from app.utils.validators import validar_cnpj


class FornecedorService:
    """Serviço para gerenciamento de fornecedores."""
    
    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        """Inicializar serviço com repositório."""
        self.repository = FornecedorRepository(session)
        self.logger = logging.getLogger(__name__)
        
    async def get_fornecedor(self, id_fornecedor: UUID, id_empresa: UUID) -> Fornecedor:
        """
        Obter fornecedor pelo ID.
        
        Args:
            id_fornecedor: ID do fornecedor
            id_empresa: ID da empresa para validação de acesso
            
        Returns:
            Fornecedor encontrado
            
        Raises:
            HTTPException: Se o fornecedor não for encontrado
        """
        self.logger.info(f"Buscando fornecedor ID: {id_fornecedor}")
        
        fornecedor = await self.repository.get_by_id(id_fornecedor, id_empresa)
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
        Listar fornecedores com paginação e filtros.
        
        Args:
            id_empresa: ID da empresa para filtrar
            skip: Número de registros a pular
            limit: Número máximo de registros a retornar
            nome: Filtrar por nome
            cnpj: Filtrar por CNPJ
            ativo: Filtrar por status
            avaliacao: Filtrar por avaliação
            
        Returns:
            Lista de fornecedores e contagem total
        """
        self.logger.info(f"Buscando fornecedores da empresa {id_empresa} com filtros: nome={nome}, cnpj={cnpj}")
        
        return await self.repository.list_with_filters(
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
        Criar novo fornecedor.
        
        Args:
            fornecedor: Dados do fornecedor a ser criado
            
        Returns:
            Fornecedor criado
            
        Raises:
            HTTPException: Se ocorrer um erro na validação
        """
        self.logger.info(f"Criando novo fornecedor: {fornecedor.nome} para empresa {fornecedor.id_empresa}")
        
        # Validar CNPJ
        if fornecedor.cnpj and not validar_cnpj(fornecedor.cnpj):
            self.logger.warning(f"CNPJ inválido: {fornecedor.cnpj}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CNPJ inválido"
            )
        
        # Validar avaliação
        if fornecedor.avaliacao is not None and (fornecedor.avaliacao < 0 or fornecedor.avaliacao > 5):
            self.logger.warning(f"Avaliação inválida: {fornecedor.avaliacao}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Avaliação deve estar entre 0 e 5"
            )
        
        # Converter para dicionário para enviar ao repositório
        fornecedor_data = fornecedor.model_dump()
        
        # Criar fornecedor no repositório
        try:
            return await self.repository.create_fornecedor(fornecedor_data)
        except HTTPException as e:
            self.logger.warning(f"Erro ao criar fornecedor: {e.detail}")
            raise
        except Exception as e:
            self.logger.error(f"Erro inesperado ao criar fornecedor: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao criar fornecedor"
            )
        
    async def atualizar_fornecedor(self, id_fornecedor: UUID, fornecedor: FornecedorUpdate, id_empresa: UUID) -> Fornecedor:
        """
        Atualizar fornecedor existente.
        
        Args:
            id_fornecedor: ID do fornecedor a ser atualizado
            fornecedor: Dados para atualização
            id_empresa: ID da empresa para validação de acesso
            
        Returns:
            Fornecedor atualizado
            
        Raises:
            HTTPException: Se o fornecedor não for encontrado ou ocorrer erro na validação
        """
        self.logger.info(f"Atualizando fornecedor: {id_fornecedor}")
        
        # Verificar se o fornecedor existe
        await self.get_fornecedor(id_fornecedor, id_empresa)
        
        # Validar CNPJ se estiver sendo atualizado
        if fornecedor.cnpj and not validar_cnpj(fornecedor.cnpj):
            self.logger.warning(f"CNPJ inválido: {fornecedor.cnpj}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CNPJ inválido"
            )
            
        # Validar avaliação se estiver sendo atualizada
        if fornecedor.avaliacao is not None and (fornecedor.avaliacao < 0 or fornecedor.avaliacao > 5):
            self.logger.warning(f"Avaliação inválida: {fornecedor.avaliacao}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Avaliação deve estar entre 0 e 5"
            )
        
        # Remover campos None do modelo de atualização
        update_data = {k: v for k, v in fornecedor.model_dump().items() if v is not None}
        
        # Atualizar fornecedor
        try:
            fornecedor_atualizado = await self.repository.update_fornecedor(
                id_fornecedor=id_fornecedor,
                data=update_data,
                id_empresa=id_empresa
            )
            
            if not fornecedor_atualizado:
                self.logger.warning(f"Fornecedor não encontrado após tentativa de atualização: {id_fornecedor}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Fornecedor não encontrado ou não pertence à empresa"
                )
            
            return fornecedor_atualizado
        except HTTPException as e:
            self.logger.warning(f"Erro ao atualizar fornecedor: {e.detail}")
            raise
        except Exception as e:
            self.logger.error(f"Erro inesperado ao atualizar fornecedor: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao atualizar fornecedor"
            )
        
    async def remover_fornecedor(self, id_fornecedor: UUID, id_empresa: UUID) -> Dict[str, Any]:
        """
        Remover fornecedor pelo ID.
        
        Args:
            id_fornecedor: ID do fornecedor a ser removido
            id_empresa: ID da empresa para validação de acesso
            
        Returns:
            Mensagem de confirmação
            
        Raises:
            HTTPException: Se o fornecedor não for encontrado
        """
        self.logger.info(f"Removendo fornecedor: {id_fornecedor}")
        
        # Verificar se o fornecedor existe
        await self.get_fornecedor(id_fornecedor, id_empresa)
        
        # Verificar se o fornecedor está sendo usado em lançamentos ou compras
        # TODO: Implementar verificação de uso quando repository estiver atualizado
        
        # Tentar remover o fornecedor
        resultado = await self.repository.delete(id_fornecedor, id_empresa)
        
        if not resultado:
            self.logger.warning(f"Fornecedor não encontrado após tentativa de remoção: {id_fornecedor}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fornecedor não encontrado ou não pertence à empresa"
            )
            
        self.logger.info(f"Fornecedor removido com sucesso: {id_fornecedor}")
        return {"detail": "Fornecedor removido com sucesso"} 