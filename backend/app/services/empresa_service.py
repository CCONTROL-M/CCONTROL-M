"""Serviço para gerenciamento de empresas no sistema CCONTROL-M."""
from uuid import UUID
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
import logging

from app.schemas.empresa import EmpresaCreate, EmpresaUpdate, Empresa
from app.repositories.empresa_repository import EmpresaRepository
from app.database import get_async_session
from app.utils.validators import validar_cnpj


class EmpresaService:
    """Serviço para gerenciamento de empresas."""
    
    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        """Inicializar serviço com repositório."""
        self.repository = EmpresaRepository(session)
        self.logger = logging.getLogger(__name__)
        
    async def get_empresa(self, id_empresa: UUID) -> Empresa:
        """
        Obter empresa pelo ID.
        
        Args:
            id_empresa: ID da empresa
            
        Returns:
            Empresa encontrada
            
        Raises:
            HTTPException: Se a empresa não for encontrada
        """
        self.logger.info(f"Buscando empresa ID: {id_empresa}")
        
        empresa = await self.repository.get_by_id(id_empresa)
        if not empresa:
            self.logger.warning(f"Empresa não encontrada: {id_empresa}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Empresa não encontrada"
            )
        return empresa
        
    async def listar_empresas(
        self,
        skip: int = 0,
        limit: int = 100,
        nome: Optional[str] = None,
        cnpj: Optional[str] = None,
        ativo: Optional[bool] = None
    ) -> Tuple[List[Empresa], int]:
        """
        Listar empresas com paginação e filtros.
        
        Args:
            skip: Número de registros a pular
            limit: Número máximo de registros a retornar
            nome: Filtrar por nome
            cnpj: Filtrar por CNPJ
            ativo: Filtrar por status
            
        Returns:
            Lista de empresas e contagem total
        """
        self.logger.info(f"Buscando empresas com filtros: nome={nome}, cnpj={cnpj}, ativo={ativo}")
        
        filters = []
        
        if nome:
            filters.append({"nome__ilike": f"%{nome}%"})
            
        if cnpj:
            filters.append({"cnpj__ilike": f"%{cnpj}%"})
            
        if ativo is not None:
            filters.append({"ativo": ativo})
            
        return await self.repository.list_with_filters(
            skip=skip,
            limit=limit,
            filters=filters
        )
        
    async def criar_empresa(self, empresa: EmpresaCreate) -> Empresa:
        """
        Criar nova empresa.
        
        Args:
            empresa: Dados da empresa a ser criada
            
        Returns:
            Empresa criada
            
        Raises:
            HTTPException: Se ocorrer um erro na validação
        """
        self.logger.info(f"Criando nova empresa: {empresa.nome}")
        
        # Validar CNPJ
        if empresa.cnpj and not validar_cnpj(empresa.cnpj):
            self.logger.warning(f"CNPJ inválido: {empresa.cnpj}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CNPJ inválido"
            )
        
        # Verificar se já existe empresa com o mesmo CNPJ
        empresa_existente = await self.repository.get_by_cnpj(empresa.cnpj)
        if empresa_existente:
            self.logger.warning(f"CNPJ já cadastrado: {empresa.cnpj}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe uma empresa cadastrada com este CNPJ"
            )
        
        # Converter para dicionário para enviar ao repositório
        empresa_data = empresa.model_dump()
        
        # Criar empresa no repositório
        try:
            return await self.repository.create(empresa_data)
        except HTTPException as e:
            self.logger.warning(f"Erro ao criar empresa: {e.detail}")
            raise
        except Exception as e:
            self.logger.error(f"Erro inesperado ao criar empresa: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao criar empresa"
            )
        
    async def atualizar_empresa(self, id_empresa: UUID, empresa: EmpresaUpdate) -> Empresa:
        """
        Atualizar empresa existente.
        
        Args:
            id_empresa: ID da empresa a ser atualizada
            empresa: Dados para atualização
            
        Returns:
            Empresa atualizada
            
        Raises:
            HTTPException: Se a empresa não for encontrada ou ocorrer erro na validação
        """
        self.logger.info(f"Atualizando empresa: {id_empresa}")
        
        # Verificar se a empresa existe
        await self.get_empresa(id_empresa)
        
        # Validar CNPJ se estiver sendo atualizado
        if empresa.cnpj and not validar_cnpj(empresa.cnpj):
            self.logger.warning(f"CNPJ inválido: {empresa.cnpj}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CNPJ inválido"
            )
            
        # Verificar se já existe outra empresa com o mesmo CNPJ
        if empresa.cnpj:
            empresa_existente = await self.repository.get_by_cnpj(empresa.cnpj)
            if empresa_existente and empresa_existente.id_empresa != id_empresa:
                self.logger.warning(f"CNPJ já cadastrado em outra empresa: {empresa.cnpj}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Já existe uma empresa cadastrada com este CNPJ"
                )
        
        # Remover campos None do modelo de atualização
        update_data = {k: v for k, v in empresa.model_dump().items() if v is not None}
        
        # Atualizar empresa
        try:
            empresa_atualizada = await self.repository.update(id_empresa, update_data)
            
            if not empresa_atualizada:
                self.logger.warning(f"Empresa não encontrada após tentativa de atualização: {id_empresa}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Empresa não encontrada"
                )
            
            return empresa_atualizada
        except HTTPException as e:
            self.logger.warning(f"Erro ao atualizar empresa: {e.detail}")
            raise
        except Exception as e:
            self.logger.error(f"Erro inesperado ao atualizar empresa: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao atualizar empresa"
            )
        
    async def desativar_empresa(self, id_empresa: UUID) -> Dict[str, Any]:
        """
        Desativar empresa pelo ID.
        
        Args:
            id_empresa: ID da empresa a ser desativada
            
        Returns:
            Mensagem de confirmação
            
        Raises:
            HTTPException: Se a empresa não for encontrada
        """
        self.logger.info(f"Desativando empresa: {id_empresa}")
        
        # Verificar se a empresa existe
        empresa = await self.get_empresa(id_empresa)
        
        # Verificar se já está inativa
        if not empresa.ativo:
            self.logger.warning(f"Empresa já está inativa: {id_empresa}")
            return {"detail": "Empresa já está inativa"}
        
        # Desativar empresa
        update_data = {"ativo": False}
        await self.repository.update(id_empresa, update_data)
        
        self.logger.info(f"Empresa desativada com sucesso: {id_empresa}")
        return {"detail": "Empresa desativada com sucesso"}
        
    async def ativar_empresa(self, id_empresa: UUID) -> Dict[str, Any]:
        """
        Ativar empresa pelo ID.
        
        Args:
            id_empresa: ID da empresa a ser ativada
            
        Returns:
            Mensagem de confirmação
            
        Raises:
            HTTPException: Se a empresa não for encontrada
        """
        self.logger.info(f"Ativando empresa: {id_empresa}")
        
        # Verificar se a empresa existe
        empresa = await self.get_empresa(id_empresa)
        
        # Verificar se já está ativa
        if empresa.ativo:
            self.logger.warning(f"Empresa já está ativa: {id_empresa}")
            return {"detail": "Empresa já está ativa"}
        
        # Ativar empresa
        update_data = {"ativo": True}
        await self.repository.update(id_empresa, update_data)
        
        self.logger.info(f"Empresa ativada com sucesso: {id_empresa}")
        return {"detail": "Empresa ativada com sucesso"} 