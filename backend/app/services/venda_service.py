"""Serviço para gerenciamento de vendas no sistema CCONTROL-M."""
from uuid import UUID
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
import logging

from app.schemas.venda import VendaCreate, VendaUpdate, Venda, StatusVenda
from app.repositories.venda_repository import VendaRepository
from app.repositories.cliente_repository import ClienteRepository
from app.repositories.parcela_repository import ParcelaRepository
from app.services.log_sistema_service import LogSistemaService
from app.schemas.log_sistema import LogSistemaCreate
from app.database import get_async_session


class VendaService:
    """Serviço para gerenciamento de vendas."""
    
    def __init__(self, 
                 session: AsyncSession = Depends(get_async_session),
                 log_service: LogSistemaService = Depends()):
        """Inicializar serviço com repositórios."""
        self.repository = VendaRepository(session)
        self.cliente_repository = ClienteRepository(session)
        self.parcela_repository = ParcelaRepository(session)
        self.log_service = log_service
        self.logger = logging.getLogger(__name__)
        
    async def get_venda(self, id_venda: UUID, id_empresa: UUID) -> Venda:
        """
        Obter venda pelo ID.
        
        Args:
            id_venda: ID da venda
            id_empresa: ID da empresa para validação de acesso
            
        Returns:
            Venda encontrada
            
        Raises:
            HTTPException: Se a venda não for encontrada
        """
        self.logger.info(f"Buscando venda ID: {id_venda}")
        
        venda = await self.repository.get_by_id(id_venda, id_empresa)
        if not venda:
            self.logger.warning(f"Venda não encontrada: {id_venda}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Venda não encontrada"
            )
        return venda
        
    async def listar_vendas(
        self,
        id_empresa: UUID,
        skip: int = 0,
        limit: int = 100,
        cliente: Optional[str] = None,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        status: Optional[StatusVenda] = None,
        produto: Optional[str] = None,
        forma_pagamento: Optional[str] = None,
        valor_min: Optional[float] = None,
        valor_max: Optional[float] = None
    ) -> Tuple[List[Venda], int]:
        """
        Listar vendas com paginação e filtros.
        
        Args:
            id_empresa: ID da empresa
            skip: Número de registros a pular
            limit: Número máximo de registros a retornar
            cliente: Filtrar por nome do cliente
            data_inicio: Filtrar por data inicial
            data_fim: Filtrar por data final
            status: Filtrar por status da venda
            produto: Filtrar por nome do produto
            forma_pagamento: Filtrar por forma de pagamento
            valor_min: Filtrar por valor mínimo
            valor_max: Filtrar por valor máximo
            
        Returns:
            Lista de vendas e contagem total
        """
        self.logger.info(f"Buscando vendas com filtros: empresa={id_empresa}, cliente={cliente}, status={status}")
        
        filters = [{"id_empresa": id_empresa}]
        
        if cliente:
            filters.append({"cliente__nome__ilike": f"%{cliente}%"})
            
        if data_inicio:
            filters.append({"data_venda__gte": data_inicio})
            
        if data_fim:
            filters.append({"data_venda__lte": data_fim})
            
        if status:
            filters.append({"status": status})
            
        if produto:
            filters.append({"itens__produto__nome__ilike": f"%{produto}%"})
            
        if forma_pagamento:
            filters.append({"forma_pagamento__nome__ilike": f"%{forma_pagamento}%"})
            
        if valor_min is not None:
            filters.append({"valor_total__gte": valor_min})
            
        if valor_max is not None:
            filters.append({"valor_total__lte": valor_max})
            
        return await self.repository.list_with_filters(
            skip=skip,
            limit=limit,
            filters=filters
        )
        
    async def criar_venda(self, venda: VendaCreate, id_usuario: UUID) -> Venda:
        """
        Criar nova venda.
        
        Args:
            venda: Dados da venda a ser criada
            id_usuario: ID do usuário que está criando a venda
            
        Returns:
            Venda criada
            
        Raises:
            HTTPException: Se ocorrer um erro na validação
        """
        self.logger.info(f"Criando nova venda para empresa: {venda.id_empresa}")
        
        # Validar cliente
        if venda.id_cliente:
            cliente = await self.cliente_repository.get_by_id(venda.id_cliente, venda.id_empresa)
            if not cliente:
                self.logger.warning(f"Cliente não encontrado: {venda.id_cliente}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cliente não encontrado"
                )
                
        # Validar valor total
        if venda.valor_total <= 0:
            self.logger.warning(f"Valor total inválido: {venda.valor_total}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valor total deve ser maior que zero"
            )
            
        # Validar status (apenas alguns status são permitidos na criação)
        if venda.status not in [StatusVenda.PENDENTE, StatusVenda.CONCLUIDA, StatusVenda.CANCELADA]:
            self.logger.warning(f"Status inválido para criação: {venda.status}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status inválido para criação de venda"
            )
            
        # Criar venda
        try:
            venda_data = venda.model_dump()
            
            # Adicionar data atual se não fornecida
            if "data_venda" not in venda_data or venda_data["data_venda"] is None:
                venda_data["data_venda"] = datetime.now()
                
            nova_venda = await self.repository.create(venda_data)
            
            # Registrar log
            await self.log_service.registrar_log(
                LogSistemaCreate(
                    id_empresa=venda.id_empresa,
                    id_usuario=id_usuario,
                    acao="criar_venda",
                    descricao=f"Venda criada com ID {nova_venda.id_venda}",
                    dados={"id_venda": str(nova_venda.id_venda), "valor": float(nova_venda.valor_total)}
                )
            )
            
            return nova_venda
        except Exception as e:
            self.logger.error(f"Erro ao criar venda: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao criar venda"
            )
        
    async def atualizar_venda(self, id_venda: UUID, venda: VendaUpdate, id_empresa: UUID, id_usuario: UUID) -> Venda:
        """
        Atualizar venda existente.
        
        Args:
            id_venda: ID da venda a ser atualizada
            venda: Dados para atualização
            id_empresa: ID da empresa para validação de acesso
            id_usuario: ID do usuário que está atualizando a venda
            
        Returns:
            Venda atualizada
            
        Raises:
            HTTPException: Se a venda não for encontrada ou ocorrer erro na validação
        """
        self.logger.info(f"Atualizando venda: {id_venda}")
        
        # Verificar se a venda existe
        venda_atual = await self.get_venda(id_venda, id_empresa)
        
        # Validar cliente se estiver sendo atualizado
        if venda.id_cliente:
            cliente = await self.cliente_repository.get_by_id(venda.id_cliente, id_empresa)
            if not cliente:
                self.logger.warning(f"Cliente não encontrado: {venda.id_cliente}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cliente não encontrado"
                )
                
        # Validar valor total se estiver sendo atualizado
        if venda.valor_total is not None and venda.valor_total <= 0:
            self.logger.warning(f"Valor total inválido: {venda.valor_total}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valor total deve ser maior que zero"
            )
            
        # Validar transição de status
        if venda.status and venda.status != venda_atual.status:
            # Regras de transição de status
            if venda_atual.status == StatusVenda.CANCELADA and venda.status != StatusVenda.CANCELADA:
                self.logger.warning(f"Não é possível alterar uma venda cancelada")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Não é possível alterar o status de uma venda cancelada"
                )
                
            # Demais regras de transição podem ser implementadas conforme necessidade
            # Ex: PENDENTE -> CONCLUIDA, PENDENTE -> CANCELADA, etc.
            
        # Atualizar venda
        try:
            # Remover campos None do modelo de atualização
            update_data = {k: v for k, v in venda.model_dump().items() if v is not None}
            
            venda_atualizada = await self.repository.update(id_venda, update_data, id_empresa)
            
            if not venda_atualizada:
                self.logger.warning(f"Venda não encontrada após tentativa de atualização: {id_venda}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Venda não encontrada"
                )
                
            # Registrar log
            await self.log_service.registrar_log(
                LogSistemaCreate(
                    id_empresa=id_empresa,
                    id_usuario=id_usuario,
                    acao="atualizar_venda",
                    descricao=f"Venda atualizada com ID {id_venda}",
                    dados={"id_venda": str(id_venda), "atualizacoes": update_data}
                )
            )
            
            return venda_atualizada
        except Exception as e:
            self.logger.error(f"Erro ao atualizar venda: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao atualizar venda"
            )
            
    async def cancelar_venda(self, id_venda: UUID, id_empresa: UUID, id_usuario: UUID, motivo: str) -> Venda:
        """
        Cancelar uma venda.
        
        Args:
            id_venda: ID da venda a ser cancelada
            id_empresa: ID da empresa para validação de acesso
            id_usuario: ID do usuário que está cancelando a venda
            motivo: Motivo do cancelamento
            
        Returns:
            Venda cancelada
            
        Raises:
            HTTPException: Se a venda não for encontrada ou já estiver cancelada
        """
        self.logger.info(f"Cancelando venda: {id_venda}")
        
        # Verificar se a venda existe
        venda = await self.get_venda(id_venda, id_empresa)
        
        # Verificar se já está cancelada
        if venda.status == StatusVenda.CANCELADA:
            self.logger.warning(f"Venda já está cancelada: {id_venda}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Venda já está cancelada"
            )
            
        # Cancelar venda
        update_data = {
            "status": StatusVenda.CANCELADA,
            "observacoes": f"CANCELADA: {motivo}" if not venda.observacoes else f"{venda.observacoes}\nCANCELADA: {motivo}"
        }
        
        venda_cancelada = await self.repository.update(id_venda, update_data, id_empresa)
        
        # Registrar log
        await self.log_service.registrar_log(
            LogSistemaCreate(
                id_empresa=id_empresa,
                id_usuario=id_usuario,
                acao="cancelar_venda",
                descricao=f"Venda cancelada com ID {id_venda}",
                dados={"id_venda": str(id_venda), "motivo": motivo}
            )
        )
        
        return venda_cancelada
        
    async def concluir_venda(self, id_venda: UUID, id_empresa: UUID, id_usuario: UUID) -> Venda:
        """
        Concluir uma venda.
        
        Args:
            id_venda: ID da venda a ser concluída
            id_empresa: ID da empresa para validação de acesso
            id_usuario: ID do usuário que está concluindo a venda
            
        Returns:
            Venda concluída
            
        Raises:
            HTTPException: Se a venda não for encontrada ou já estiver concluída/cancelada
        """
        self.logger.info(f"Concluindo venda: {id_venda}")
        
        # Verificar se a venda existe
        venda = await self.get_venda(id_venda, id_empresa)
        
        # Verificar status atual
        if venda.status == StatusVenda.CONCLUIDA:
            self.logger.warning(f"Venda já está concluída: {id_venda}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Venda já está concluída"
            )
            
        if venda.status == StatusVenda.CANCELADA:
            self.logger.warning(f"Não é possível concluir uma venda cancelada: {id_venda}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível concluir uma venda cancelada"
            )
            
        # Concluir venda
        update_data = {"status": StatusVenda.CONCLUIDA}
        
        venda_concluida = await self.repository.update(id_venda, update_data, id_empresa)
        
        # Registrar log
        await self.log_service.registrar_log(
            LogSistemaCreate(
                id_empresa=id_empresa,
                id_usuario=id_usuario,
                acao="concluir_venda",
                descricao=f"Venda concluída com ID {id_venda}",
                dados={"id_venda": str(id_venda)}
            )
        )
        
        return venda_concluida
        
    async def remover_venda(self, id_venda: UUID, id_empresa: UUID, id_usuario: UUID) -> Dict[str, Any]:
        """
        Remover venda pelo ID.
        
        Args:
            id_venda: ID da venda a ser removida
            id_empresa: ID da empresa para validação de acesso
            id_usuario: ID do usuário que está removendo a venda
            
        Returns:
            Mensagem de confirmação
            
        Raises:
            HTTPException: Se a venda não for encontrada ou não puder ser removida
        """
        self.logger.info(f"Removendo venda: {id_venda}")
        
        # Verificar se a venda existe
        venda = await self.get_venda(id_venda, id_empresa)
        
        # Verificar se já tem parcelas ou lançamentos associados
        parcelas = await self.parcela_repository.get_by_venda(id_venda, id_empresa)
        if parcelas and len(parcelas) > 0:
            self.logger.warning(f"Venda possui parcelas associadas: {id_venda}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível remover uma venda com parcelas associadas"
            )
            
        # Remover venda
        await self.repository.delete(id_venda, id_empresa)
        
        # Registrar log
        await self.log_service.registrar_log(
            LogSistemaCreate(
                id_empresa=id_empresa,
                id_usuario=id_usuario,
                acao="remover_venda",
                descricao=f"Venda removida com ID {id_venda}",
                dados={"id_venda": str(id_venda)}
            )
        )
        
        return {"detail": "Venda removida com sucesso"} 