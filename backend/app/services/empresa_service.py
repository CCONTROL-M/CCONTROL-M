"""Serviço para gerenciamento de empresas no sistema CCONTROL-M."""
from uuid import UUID
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
import logging
from datetime import datetime

from app.schemas.empresa import EmpresaCreate, EmpresaUpdate, Empresa
from app.repositories.empresa_repository import EmpresaRepository
from app.database import get_async_session
from app.utils.validators import validar_cnpj
from app.schemas.pagination import PaginatedResponse
from app.services.auditoria_service import AuditoriaService


# Configurar logger
logger = logging.getLogger(__name__)


class EmpresaService:
    """Serviço para gerenciamento de empresas."""
    
    def __init__(self, 
                 session: AsyncSession = Depends(get_async_session),
                 auditoria_service: AuditoriaService = Depends()):
        """Inicializar serviço com repositórios."""
        self.repository = EmpresaRepository(session)
        self.auditoria_service = auditoria_service
        self.logger = logger
        
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
        
    async def criar_empresa(self, empresa: EmpresaCreate, usuario_id: UUID) -> Empresa:
        """
        Criar nova empresa.
        
        Args:
            empresa: Dados da empresa a ser criada
            usuario_id: ID do usuário que está criando
            
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
            # Criar empresa
            nova_empresa = await self.repository.create(empresa_data)
            
            # Registrar ação
            await self.auditoria_service.registrar_acao(
                usuario_id=usuario_id,
                acao="CRIAR_EMPRESA",
                detalhes={
                    "id_empresa": str(nova_empresa.id_empresa),
                    "razao_social": nova_empresa.razao_social,
                    "nome_fantasia": nova_empresa.nome_fantasia,
                    "cnpj": nova_empresa.cnpj
                },
                empresa_id=nova_empresa.id_empresa
            )
            
            return nova_empresa
        except HTTPException as e:
            self.logger.warning(f"Erro ao criar empresa: {e.detail}")
            raise
        except Exception as e:
            self.logger.error(f"Erro inesperado ao criar empresa: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao criar empresa"
            )
        
    async def atualizar_empresa(self, id_empresa: UUID, empresa: EmpresaUpdate, usuario_id: UUID) -> Empresa:
        """
        Atualizar empresa existente.
        
        Args:
            id_empresa: ID da empresa a ser atualizada
            empresa: Dados para atualização
            usuario_id: ID do usuário que está atualizando
            
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
            
            # Registrar ação
            await self.auditoria_service.registrar_acao(
                usuario_id=usuario_id,
                acao="ATUALIZAR_EMPRESA",
                detalhes={
                    "id_empresa": str(id_empresa),
                    "alteracoes": update_data
                },
                empresa_id=id_empresa
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
        
    async def desativar_empresa(self, id_empresa: UUID, usuario_id: UUID) -> Dict[str, Any]:
        """
        Desativar empresa pelo ID.
        
        Args:
            id_empresa: ID da empresa a ser desativada
            usuario_id: ID do usuário que está desativando
            
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
        
        # Registrar ação
        await self.auditoria_service.registrar_acao(
            usuario_id=usuario_id,
            acao="DESATIVAR_EMPRESA",
            detalhes={
                "id_empresa": str(id_empresa),
                "razao_social": empresa.razao_social,
                "nome_fantasia": empresa.nome_fantasia,
                "cnpj": empresa.cnpj
            },
            empresa_id=id_empresa
        )
        
        self.logger.info(f"Empresa desativada com sucesso: {id_empresa}")
        return {"detail": "Empresa desativada com sucesso"}
        
    async def ativar_empresa(self, id_empresa: UUID, usuario_id: UUID) -> Dict[str, Any]:
        """
        Ativar empresa pelo ID.
        
        Args:
            id_empresa: ID da empresa a ser ativada
            usuario_id: ID do usuário que está ativando
            
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
        
        # Registrar ação
        await self.auditoria_service.registrar_acao(
            usuario_id=usuario_id,
            acao="ATIVAR_EMPRESA",
            detalhes={
                "id_empresa": str(id_empresa),
                "razao_social": empresa.razao_social,
                "nome_fantasia": empresa.nome_fantasia,
                "cnpj": empresa.cnpj
            },
            empresa_id=id_empresa
        )
        
        self.logger.info(f"Empresa ativada com sucesso: {id_empresa}")
        return {"detail": "Empresa ativada com sucesso"}

    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        busca: Optional[str] = None
    ) -> PaginatedResponse[Empresa]:
        """
        Buscar múltiplas empresas com filtros.
        
        Args:
            skip: Número de registros para pular
            limit: Número máximo de registros
            status: Filtrar por status
            busca: Termo para busca
            
        Returns:
            Lista paginada de empresas
        """
        try:
            empresas, total = await self.repository.get_multi(
                skip=skip,
                limit=limit,
                status=status,
                busca=busca
            )
            
            return PaginatedResponse(
                items=empresas,
                total=total,
                page=skip // limit + 1 if limit > 0 else 1,
                size=limit,
                pages=(total + limit - 1) // limit if limit > 0 else 1
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar empresas: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao buscar empresas"
            ) 