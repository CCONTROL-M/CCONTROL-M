"""Serviço para gerenciamento de centros de custo no sistema CCONTROL-M."""
from uuid import UUID
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
import logging
from datetime import datetime

from app.schemas.centro_custo import CentroCustoCreate, CentroCustoUpdate, CentroCusto
from app.repositories.centro_custo_repository import CentroCustoRepository
from app.repositories.lancamento_repository import LancamentoRepository
from app.services.log_sistema_service import LogSistemaService
from app.schemas.log_sistema import LogSistemaCreate
from app.database import get_async_session
from app.schemas.pagination import PaginatedResponse
from app.services.auditoria_service import AuditoriaService


# Configurar logger
logger = logging.getLogger(__name__)


class CentroCustoService:
    """Serviço para gerenciamento de centros de custo."""
    
    def __init__(self, 
                 session: AsyncSession = Depends(get_async_session),
                 log_service: LogSistemaService = Depends(),
                 auditoria_service: AuditoriaService = Depends()):
        """Inicializar serviço com repositórios."""
        self.repository = CentroCustoRepository(session)
        self.lancamento_repository = LancamentoRepository(session)
        self.log_service = log_service
        self.auditoria_service = auditoria_service
        self.logger = logger
        
    async def get_centro_custo(self, id_centro_custo: UUID, id_empresa: UUID) -> CentroCusto:
        """
        Obter centro de custo pelo ID.
        
        Args:
            id_centro_custo: ID do centro de custo
            id_empresa: ID da empresa para validação de acesso
            
        Returns:
            Centro de custo encontrado
            
        Raises:
            HTTPException: Se o centro de custo não for encontrado
        """
        self.logger.info(f"Buscando centro de custo ID: {id_centro_custo}")
        
        centro_custo = await self.repository.get_by_id(id_centro_custo, id_empresa)
        if not centro_custo:
            self.logger.warning(f"Centro de custo não encontrado: {id_centro_custo}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Centro de custo não encontrado"
            )
        return centro_custo
        
    async def listar_centros_custo(
        self,
        id_empresa: UUID,
        skip: int = 0,
        limit: int = 100,
        nome: Optional[str] = None,
        ativo: Optional[bool] = None
    ) -> Tuple[List[CentroCusto], int]:
        """
        Listar centros de custo com paginação e filtros.
        
        Args:
            id_empresa: ID da empresa
            skip: Número de registros a pular
            limit: Número máximo de registros a retornar
            nome: Filtrar por nome
            ativo: Filtrar por status ativo
            
        Returns:
            Lista de centros de custo e contagem total
        """
        self.logger.info(f"Buscando centros de custo com filtros: empresa={id_empresa}, nome={nome}")
        
        filters = [{"id_empresa": id_empresa}]
        
        if nome:
            filters.append({"nome__ilike": f"%{nome}%"})
            
        if ativo is not None:
            filters.append({"ativo": ativo})
            
        return await self.repository.list_with_filters(
            skip=skip,
            limit=limit,
            filters=filters
        )
        
    async def criar_centro_custo(self, centro_custo: CentroCustoCreate, id_usuario: UUID) -> CentroCusto:
        """
        Criar novo centro de custo.
        
        Args:
            centro_custo: Dados do centro de custo a ser criado
            id_usuario: ID do usuário que está criando o centro de custo
            
        Returns:
            Centro de custo criado
            
        Raises:
            HTTPException: Se ocorrer um erro na validação
        """
        self.logger.info(f"Criando novo centro de custo: {centro_custo.nome}")
        
        # Verificar se já existe centro de custo com mesmo nome na empresa
        centro_existente = await self.repository.get_by_nome(centro_custo.nome, centro_custo.id_empresa)
        if centro_existente:
            self.logger.warning(f"Já existe um centro de custo com o nome '{centro_custo.nome}' na empresa")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Já existe um centro de custo com o nome '{centro_custo.nome}'"
            )
            
        # Criar centro de custo
        try:
            centro_custo_data = centro_custo.model_dump()
            
            # Definir como ativo por padrão se não especificado
            if "ativo" not in centro_custo_data or centro_custo_data["ativo"] is None:
                centro_custo_data["ativo"] = True
                
            novo_centro = await self.repository.create(centro_custo_data)
            
            # Registrar log
            await self.log_service.registrar_log(
                LogSistemaCreate(
                    id_empresa=centro_custo.id_empresa,
                    id_usuario=id_usuario,
                    acao="criar_centro_custo",
                    descricao=f"Centro de custo criado: {novo_centro.nome}",
                    dados={
                        "id_centro_custo": str(novo_centro.id_centro_custo), 
                        "nome": novo_centro.nome
                    }
                )
            )
            
            # Registrar ação
            await self.auditoria_service.registrar_acao(
                usuario_id=id_usuario,
                acao="CRIAR_CENTRO_CUSTO",
                detalhes={
                    "id_centro_custo": str(novo_centro.id_centro_custo),
                    "nome": novo_centro.nome,
                    "tipo": novo_centro.tipo
                },
                empresa_id=centro_custo.id_empresa
            )
            
            return novo_centro
        except Exception as e:
            self.logger.error(f"Erro ao criar centro de custo: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao criar centro de custo"
            )
        
    async def atualizar_centro_custo(self, id_centro_custo: UUID, centro_custo: CentroCustoUpdate, id_empresa: UUID, id_usuario: UUID) -> CentroCusto:
        """
        Atualizar centro de custo existente.
        
        Args:
            id_centro_custo: ID do centro de custo a ser atualizado
            centro_custo: Dados para atualização
            id_empresa: ID da empresa para validação de acesso
            id_usuario: ID do usuário que está atualizando o centro de custo
            
        Returns:
            Centro de custo atualizado
            
        Raises:
            HTTPException: Se o centro de custo não for encontrado ou ocorrer erro na validação
        """
        self.logger.info(f"Atualizando centro de custo: {id_centro_custo}")
        
        # Verificar se o centro de custo existe
        await self.get_centro_custo(id_centro_custo, id_empresa)
        
        # Verificar unicidade do nome se estiver sendo atualizado
        if centro_custo.nome:
            centro_existente = await self.repository.get_by_nome(centro_custo.nome, id_empresa)
            if centro_existente and centro_existente.id_centro_custo != id_centro_custo:
                self.logger.warning(f"Já existe um centro de custo com o nome '{centro_custo.nome}' na empresa")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Já existe um centro de custo com o nome '{centro_custo.nome}'"
                )
                
        # Atualizar centro de custo
        try:
            # Remover campos None do modelo de atualização
            update_data = {k: v for k, v in centro_custo.model_dump().items() if v is not None}
                
            centro_atualizado = await self.repository.update(id_centro_custo, update_data, id_empresa)
            
            if not centro_atualizado:
                self.logger.warning(f"Centro de custo não encontrado após tentativa de atualização: {id_centro_custo}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Centro de custo não encontrado"
                )
                
            # Registrar log
            await self.log_service.registrar_log(
                LogSistemaCreate(
                    id_empresa=id_empresa,
                    id_usuario=id_usuario,
                    acao="atualizar_centro_custo",
                    descricao=f"Centro de custo atualizado: {centro_atualizado.nome}",
                    dados={
                        "id_centro_custo": str(id_centro_custo),
                        "atualizacoes": update_data
                    }
                )
            )
            
            # Registrar ação
            await self.auditoria_service.registrar_acao(
                usuario_id=id_usuario,
                acao="ATUALIZAR_CENTRO_CUSTO",
                detalhes={
                    "id_centro_custo": str(id_centro_custo),
                    "alteracoes": update_data
                },
                empresa_id=id_empresa
            )
            
            return centro_atualizado
        except Exception as e:
            self.logger.error(f"Erro ao atualizar centro de custo: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao atualizar centro de custo"
            )
            
    async def ativar_centro_custo(self, id_centro_custo: UUID, id_empresa: UUID, id_usuario: UUID) -> CentroCusto:
        """
        Ativar um centro de custo.
        
        Args:
            id_centro_custo: ID do centro de custo a ser ativado
            id_empresa: ID da empresa para validação de acesso
            id_usuario: ID do usuário que está ativando o centro de custo
            
        Returns:
            Centro de custo ativado
            
        Raises:
            HTTPException: Se o centro de custo não for encontrado
        """
        self.logger.info(f"Ativando centro de custo: {id_centro_custo}")
        
        # Verificar se o centro de custo existe
        centro_custo = await self.get_centro_custo(id_centro_custo, id_empresa)
        
        # Verificar se já está ativo
        if centro_custo.ativo:
            self.logger.warning(f"Centro de custo já está ativo: {id_centro_custo}")
            return centro_custo
            
        # Ativar centro de custo
        update_data = {"ativo": True}
        
        centro_atualizado = await self.repository.update(id_centro_custo, update_data, id_empresa)
        
        # Registrar log
        await self.log_service.registrar_log(
            LogSistemaCreate(
                id_empresa=id_empresa,
                id_usuario=id_usuario,
                acao="ativar_centro_custo",
                descricao=f"Centro de custo ativado: {centro_custo.nome}",
                dados={"id_centro_custo": str(id_centro_custo)}
            )
        )
        
        # Registrar ação
        await self.auditoria_service.registrar_acao(
            usuario_id=id_usuario,
            acao="ATIVAR_CENTRO_CUSTO",
            detalhes={"id_centro_custo": str(id_centro_custo)},
            empresa_id=id_empresa
        )
        
        return centro_atualizado
        
    async def desativar_centro_custo(self, id_centro_custo: UUID, id_empresa: UUID, id_usuario: UUID) -> CentroCusto:
        """
        Desativar um centro de custo.
        
        Args:
            id_centro_custo: ID do centro de custo a ser desativado
            id_empresa: ID da empresa para validação de acesso
            id_usuario: ID do usuário que está desativando o centro de custo
            
        Returns:
            Centro de custo desativado
            
        Raises:
            HTTPException: Se o centro de custo não for encontrado
        """
        self.logger.info(f"Desativando centro de custo: {id_centro_custo}")
        
        # Verificar se o centro de custo existe
        centro_custo = await self.get_centro_custo(id_centro_custo, id_empresa)
        
        # Verificar se já está inativo
        if not centro_custo.ativo:
            self.logger.warning(f"Centro de custo já está inativo: {id_centro_custo}")
            return centro_custo
            
        # Desativar centro de custo
        update_data = {"ativo": False}
        
        centro_atualizado = await self.repository.update(id_centro_custo, update_data, id_empresa)
        
        # Registrar log
        await self.log_service.registrar_log(
            LogSistemaCreate(
                id_empresa=id_empresa,
                id_usuario=id_usuario,
                acao="desativar_centro_custo",
                descricao=f"Centro de custo desativado: {centro_custo.nome}",
                dados={"id_centro_custo": str(id_centro_custo)}
            )
        )
        
        # Registrar ação
        await self.auditoria_service.registrar_acao(
            usuario_id=id_usuario,
            acao="DESATIVAR_CENTRO_CUSTO",
            detalhes={"id_centro_custo": str(id_centro_custo)},
            empresa_id=id_empresa
        )
        
        return centro_atualizado
        
    async def remover_centro_custo(self, id_centro_custo: UUID, id_empresa: UUID, id_usuario: UUID) -> Dict[str, Any]:
        """
        Remover centro de custo pelo ID.
        
        Args:
            id_centro_custo: ID do centro de custo a ser removido
            id_empresa: ID da empresa para validação de acesso
            id_usuario: ID do usuário que está removendo o centro de custo
            
        Returns:
            Mensagem de confirmação
            
        Raises:
            HTTPException: Se o centro de custo não for encontrado ou não puder ser removido
        """
        self.logger.info(f"Removendo centro de custo: {id_centro_custo}")
        
        # Verificar se o centro de custo existe
        centro_custo = await self.get_centro_custo(id_centro_custo, id_empresa)
        
        # Verificar se tem lançamentos associados
        tem_lancamentos = await self.lancamento_repository.has_by_centro_custo(id_centro_custo, id_empresa)
        if tem_lancamentos:
            self.logger.warning(f"Centro de custo possui lançamentos associados: {id_centro_custo}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível remover um centro de custo com lançamentos associados"
            )
            
        # Remover centro de custo
        await self.repository.delete(id_centro_custo, id_empresa)
        
        # Registrar log
        await self.log_service.registrar_log(
            LogSistemaCreate(
                id_empresa=id_empresa,
                id_usuario=id_usuario,
                acao="remover_centro_custo",
                descricao=f"Centro de custo removido: {centro_custo.nome}",
                dados={"id_centro_custo": str(id_centro_custo), "nome": centro_custo.nome}
            )
        )
        
        # Registrar ação
        await self.auditoria_service.registrar_acao(
            usuario_id=id_usuario,
            acao="EXCLUIR_CENTRO_CUSTO",
            detalhes={
                "id_centro_custo": str(id_centro_custo),
                "nome": centro_custo.nome,
                "tipo": centro_custo.tipo
            },
            empresa_id=id_empresa
        )
        
        return {"detail": f"Centro de custo '{centro_custo.nome}' removido com sucesso"} 