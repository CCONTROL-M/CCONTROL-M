"""Serviço para gerenciamento de formas de pagamento no sistema CCONTROL-M."""
from uuid import UUID
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
import logging

from app.schemas.forma_pagamento import FormaPagamentoCreate, FormaPagamentoUpdate, FormaPagamento
from app.repositories.forma_pagamento_repository import FormaPagamentoRepository
from app.repositories.lancamento_repository import LancamentoRepository
from app.repositories.venda_repository import VendaRepository
from app.services.log_sistema_service import LogSistemaService
from app.schemas.log_sistema import LogSistemaCreate
from app.database import get_async_session


class FormaPagamentoService:
    """Serviço para gerenciamento de formas de pagamento."""
    
    def __init__(self, 
                 session: AsyncSession = Depends(get_async_session),
                 log_service: LogSistemaService = Depends()):
        """Inicializar serviço com repositórios."""
        self.repository = FormaPagamentoRepository(session)
        self.lancamento_repository = LancamentoRepository(session)
        self.venda_repository = VendaRepository(session)
        self.log_service = log_service
        self.logger = logging.getLogger(__name__)
        
    async def get_forma_pagamento(self, id_forma_pagamento: UUID, id_empresa: UUID) -> FormaPagamento:
        """
        Obter forma de pagamento pelo ID.
        
        Args:
            id_forma_pagamento: ID da forma de pagamento
            id_empresa: ID da empresa para validação de acesso
            
        Returns:
            Forma de pagamento encontrada
            
        Raises:
            HTTPException: Se a forma de pagamento não for encontrada
        """
        self.logger.info(f"Buscando forma de pagamento ID: {id_forma_pagamento}")
        
        forma_pagamento = await self.repository.get_by_id(id_forma_pagamento, id_empresa)
        if not forma_pagamento:
            self.logger.warning(f"Forma de pagamento não encontrada: {id_forma_pagamento}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Forma de pagamento não encontrada"
            )
        return forma_pagamento
        
    async def listar_formas_pagamento(
        self,
        id_empresa: UUID,
        skip: int = 0,
        limit: int = 100,
        nome: Optional[str] = None,
        tipo: Optional[str] = None,
        ativo: Optional[bool] = None
    ) -> Tuple[List[FormaPagamento], int]:
        """
        Listar formas de pagamento com paginação e filtros.
        
        Args:
            id_empresa: ID da empresa
            skip: Número de registros a pular
            limit: Número máximo de registros a retornar
            nome: Filtrar por nome
            tipo: Filtrar por tipo (CREDITO, DEBITO, DINHEIRO, etc)
            ativo: Filtrar por status ativo
            
        Returns:
            Lista de formas de pagamento e contagem total
        """
        self.logger.info(f"Buscando formas de pagamento com filtros: empresa={id_empresa}, nome={nome}, tipo={tipo}")
        
        filters = [{"id_empresa": id_empresa}]
        
        if nome:
            filters.append({"nome__ilike": f"%{nome}%"})
            
        if tipo:
            filters.append({"tipo": tipo})
            
        if ativo is not None:
            filters.append({"ativo": ativo})
            
        return await self.repository.list_with_filters(
            skip=skip,
            limit=limit,
            filters=filters
        )
        
    async def criar_forma_pagamento(self, forma_pagamento: FormaPagamentoCreate, id_usuario: UUID) -> FormaPagamento:
        """
        Criar nova forma de pagamento.
        
        Args:
            forma_pagamento: Dados da forma de pagamento a ser criada
            id_usuario: ID do usuário que está criando a forma de pagamento
            
        Returns:
            Forma de pagamento criada
            
        Raises:
            HTTPException: Se ocorrer um erro na validação
        """
        self.logger.info(f"Criando nova forma de pagamento: {forma_pagamento.nome}")
        
        # Verificar se já existe forma de pagamento com o mesmo nome na empresa
        forma_existente = await self.repository.get_by_nome(forma_pagamento.nome, forma_pagamento.id_empresa)
        if forma_existente:
            self.logger.warning(f"Já existe uma forma de pagamento com o nome '{forma_pagamento.nome}' na empresa")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Já existe uma forma de pagamento com o nome '{forma_pagamento.nome}'"
            )
            
        # Criar forma de pagamento
        try:
            forma_pagamento_data = forma_pagamento.model_dump()
            
            # Definir como ativo por padrão se não especificado
            if "ativo" not in forma_pagamento_data or forma_pagamento_data["ativo"] is None:
                forma_pagamento_data["ativo"] = True
                
            nova_forma = await self.repository.create(forma_pagamento_data)
            
            # Registrar log
            await self.log_service.registrar_log(
                LogSistemaCreate(
                    id_empresa=forma_pagamento.id_empresa,
                    id_usuario=id_usuario,
                    acao="criar_forma_pagamento",
                    descricao=f"Forma de pagamento criada: {nova_forma.nome}",
                    dados={"id_forma_pagamento": str(nova_forma.id_forma_pagamento), "nome": nova_forma.nome}
                )
            )
            
            return nova_forma
        except Exception as e:
            self.logger.error(f"Erro ao criar forma de pagamento: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao criar forma de pagamento"
            )
        
    async def atualizar_forma_pagamento(self, id_forma_pagamento: UUID, forma_pagamento: FormaPagamentoUpdate, id_empresa: UUID, id_usuario: UUID) -> FormaPagamento:
        """
        Atualizar forma de pagamento existente.
        
        Args:
            id_forma_pagamento: ID da forma de pagamento a ser atualizada
            forma_pagamento: Dados para atualização
            id_empresa: ID da empresa para validação de acesso
            id_usuario: ID do usuário que está atualizando a forma de pagamento
            
        Returns:
            Forma de pagamento atualizada
            
        Raises:
            HTTPException: Se a forma de pagamento não for encontrada ou ocorrer erro na validação
        """
        self.logger.info(f"Atualizando forma de pagamento: {id_forma_pagamento}")
        
        # Verificar se a forma de pagamento existe
        await self.get_forma_pagamento(id_forma_pagamento, id_empresa)
        
        # Verificar unicidade do nome se estiver sendo atualizado
        if forma_pagamento.nome:
            forma_existente = await self.repository.get_by_nome(forma_pagamento.nome, id_empresa)
            if forma_existente and forma_existente.id_forma_pagamento != id_forma_pagamento:
                self.logger.warning(f"Já existe uma forma de pagamento com o nome '{forma_pagamento.nome}' na empresa")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Já existe uma forma de pagamento com o nome '{forma_pagamento.nome}'"
                )
                
        # Atualizar forma de pagamento
        try:
            # Remover campos None do modelo de atualização
            update_data = {k: v for k, v in forma_pagamento.model_dump().items() if v is not None}
            
            forma_atualizada = await self.repository.update(id_forma_pagamento, update_data, id_empresa)
            
            if not forma_atualizada:
                self.logger.warning(f"Forma de pagamento não encontrada após tentativa de atualização: {id_forma_pagamento}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Forma de pagamento não encontrada"
                )
                
            # Registrar log
            await self.log_service.registrar_log(
                LogSistemaCreate(
                    id_empresa=id_empresa,
                    id_usuario=id_usuario,
                    acao="atualizar_forma_pagamento",
                    descricao=f"Forma de pagamento atualizada: {forma_atualizada.nome}",
                    dados={
                        "id_forma_pagamento": str(id_forma_pagamento),
                        "atualizacoes": update_data
                    }
                )
            )
            
            return forma_atualizada
        except Exception as e:
            self.logger.error(f"Erro ao atualizar forma de pagamento: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao atualizar forma de pagamento"
            )
            
    async def ativar_forma_pagamento(self, id_forma_pagamento: UUID, id_empresa: UUID, id_usuario: UUID) -> FormaPagamento:
        """
        Ativar uma forma de pagamento.
        
        Args:
            id_forma_pagamento: ID da forma de pagamento a ser ativada
            id_empresa: ID da empresa para validação de acesso
            id_usuario: ID do usuário que está ativando a forma de pagamento
            
        Returns:
            Forma de pagamento ativada
            
        Raises:
            HTTPException: Se a forma de pagamento não for encontrada
        """
        self.logger.info(f"Ativando forma de pagamento: {id_forma_pagamento}")
        
        # Verificar se a forma de pagamento existe
        forma_pagamento = await self.get_forma_pagamento(id_forma_pagamento, id_empresa)
        
        # Verificar se já está ativa
        if forma_pagamento.ativo:
            self.logger.warning(f"Forma de pagamento já está ativa: {id_forma_pagamento}")
            return forma_pagamento
            
        # Ativar forma de pagamento
        update_data = {"ativo": True}
        
        forma_atualizada = await self.repository.update(id_forma_pagamento, update_data, id_empresa)
        
        # Registrar log
        await self.log_service.registrar_log(
            LogSistemaCreate(
                id_empresa=id_empresa,
                id_usuario=id_usuario,
                acao="ativar_forma_pagamento",
                descricao=f"Forma de pagamento ativada: {forma_pagamento.nome}",
                dados={"id_forma_pagamento": str(id_forma_pagamento)}
            )
        )
        
        return forma_atualizada
        
    async def desativar_forma_pagamento(self, id_forma_pagamento: UUID, id_empresa: UUID, id_usuario: UUID) -> FormaPagamento:
        """
        Desativar uma forma de pagamento.
        
        Args:
            id_forma_pagamento: ID da forma de pagamento a ser desativada
            id_empresa: ID da empresa para validação de acesso
            id_usuario: ID do usuário que está desativando a forma de pagamento
            
        Returns:
            Forma de pagamento desativada
            
        Raises:
            HTTPException: Se a forma de pagamento não for encontrada
        """
        self.logger.info(f"Desativando forma de pagamento: {id_forma_pagamento}")
        
        # Verificar se a forma de pagamento existe
        forma_pagamento = await self.get_forma_pagamento(id_forma_pagamento, id_empresa)
        
        # Verificar se já está inativa
        if not forma_pagamento.ativo:
            self.logger.warning(f"Forma de pagamento já está inativa: {id_forma_pagamento}")
            return forma_pagamento
            
        # Desativar forma de pagamento
        update_data = {"ativo": False}
        
        forma_atualizada = await self.repository.update(id_forma_pagamento, update_data, id_empresa)
        
        # Registrar log
        await self.log_service.registrar_log(
            LogSistemaCreate(
                id_empresa=id_empresa,
                id_usuario=id_usuario,
                acao="desativar_forma_pagamento",
                descricao=f"Forma de pagamento desativada: {forma_pagamento.nome}",
                dados={"id_forma_pagamento": str(id_forma_pagamento)}
            )
        )
        
        return forma_atualizada
        
    async def remover_forma_pagamento(self, id_forma_pagamento: UUID, id_empresa: UUID, id_usuario: UUID) -> Dict[str, Any]:
        """
        Remover forma de pagamento pelo ID.
        
        Args:
            id_forma_pagamento: ID da forma de pagamento a ser removida
            id_empresa: ID da empresa para validação de acesso
            id_usuario: ID do usuário que está removendo a forma de pagamento
            
        Returns:
            Mensagem de confirmação
            
        Raises:
            HTTPException: Se a forma de pagamento não for encontrada ou não puder ser removida
        """
        self.logger.info(f"Removendo forma de pagamento: {id_forma_pagamento}")
        
        # Verificar se a forma de pagamento existe
        forma_pagamento = await self.get_forma_pagamento(id_forma_pagamento, id_empresa)
        
        # Verificar se tem lançamentos associados
        tem_lancamentos = await self.lancamento_repository.has_by_forma_pagamento(id_forma_pagamento, id_empresa)
        if tem_lancamentos:
            self.logger.warning(f"Forma de pagamento possui lançamentos associados: {id_forma_pagamento}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível remover uma forma de pagamento com lançamentos associados"
            )
            
        # Verificar se tem vendas associadas
        tem_vendas = await self.venda_repository.has_by_forma_pagamento(id_forma_pagamento, id_empresa)
        if tem_vendas:
            self.logger.warning(f"Forma de pagamento possui vendas associadas: {id_forma_pagamento}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível remover uma forma de pagamento com vendas associadas"
            )
            
        # Remover forma de pagamento
        await self.repository.delete(id_forma_pagamento, id_empresa)
        
        # Registrar log
        await self.log_service.registrar_log(
            LogSistemaCreate(
                id_empresa=id_empresa,
                id_usuario=id_usuario,
                acao="remover_forma_pagamento",
                descricao=f"Forma de pagamento removida: {forma_pagamento.nome}",
                dados={"id_forma_pagamento": str(id_forma_pagamento), "nome": forma_pagamento.nome}
            )
        )
        
        return {"detail": f"Forma de pagamento '{forma_pagamento.nome}' removida com sucesso"} 