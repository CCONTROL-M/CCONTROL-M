"""Serviço para gerenciamento de vendas no sistema CCONTROL-M."""
from uuid import UUID
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
import logging

from app.schemas.venda import VendaCreate, VendaUpdate, Venda, StatusVenda, ItemVenda as ItemVendaSchema
from app.repositories.venda_repository import VendaRepository
from app.repositories.cliente_repository import ClienteRepository
from app.repositories.parcela_repository import ParcelaRepository
from app.repositories.produto_repository import ProdutoRepository
from app.services.log_sistema_service import LogSistemaService
from app.schemas.log_sistema import LogSistemaCreate
from app.database import get_async_session, db_session


class VendaService:
    """Serviço para gerenciamento de vendas."""
    
    def __init__(self, 
                 session: AsyncSession = Depends(get_async_session),
                 log_service: LogSistemaService = Depends()):
        """Inicializar serviço com repositórios."""
        self.repository = VendaRepository(session)
        self.cliente_repository = ClienteRepository(session)
        self.parcela_repository = ParcelaRepository(session)
        self.produto_repository = ProdutoRepository(session)
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
                detail=f"Venda não encontrada com ID: {id_venda}"
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
            skip: Registros para pular
            limit: Limite de registros
            cliente: Filtrar por nome do cliente
            data_inicio: Filtrar a partir desta data
            data_fim: Filtrar até esta data
            status: Filtrar por status
            produto: Filtrar por nome do produto
            forma_pagamento: Filtrar por forma de pagamento
            valor_min: Filtrar por valor mínimo
            valor_max: Filtrar por valor máximo
            
        Returns:
            Tuple com lista de vendas e contagem total
        """
        self.logger.info(f"Listando vendas da empresa: {id_empresa}")
        
        # Converter cliente para ID se fornecido
        id_cliente = None
        if cliente:
            # Implementar lógica para buscar cliente por nome
            pass
        
        try:
            vendas, total = await self.repository.get_by_empresa(
                id_empresa=id_empresa,
                skip=skip,
                limit=limit,
                data_inicio=data_inicio,
                data_fim=data_fim,
                id_cliente=id_cliente,
                status=status.value if status else None,
                forma_pagamento=UUID(forma_pagamento) if forma_pagamento else None
            )
            
            return vendas, total
        except Exception as e:
            self.logger.error(f"Erro ao listar vendas: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao listar vendas"
            )
    
    async def criar_venda(self, venda: VendaCreate, id_usuario: UUID) -> Venda:
        """
        Criar nova venda.
        
        Args:
            venda: Dados da venda
            id_usuario: ID do usuário que está criando a venda
            
        Returns:
            Venda criada
            
        Raises:
            HTTPException: Em caso de erro na validação ou criação
        """
        self.logger.info(f"Criando nova venda para cliente: {venda.id_cliente}")
        
        try:
            # Verificar se o cliente existe
            cliente = await self.cliente_repository.get_by_id(venda.id_cliente, venda.id_empresa)
            if not cliente:
                self.logger.warning(f"Cliente não encontrado: {venda.id_cliente}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente não encontrado"
                )
            
            # Preparar dados da venda
            venda_data = venda.dict()
            venda_data["data_venda"] = datetime.now()
            venda_data["status"] = "pendente"
            venda_data["valor_total"] = 0  # Será calculado após adicionar itens
            
            # Criar venda
            venda_obj = await self.repository.create(venda_data)
            
            # Adicionar itens, se fornecidos
            if venda.itens:
                for item in venda.itens:
                    await self.adicionar_item_venda(
                        id_venda=venda_obj.id_venda,
                        id_empresa=venda.id_empresa,
                        item=item
                    )
            
            # Registrar log
            log = LogSistemaCreate(
                acao="criar",
                tabela="vendas",
                id_registro=str(venda_obj.id_venda),
                id_usuario=id_usuario,
                id_empresa=venda.id_empresa,
                detalhes=f"Venda criada para cliente {cliente.nome}"
            )
            await self.log_service.registrar_log(log)
            
            # Comitar transação
            await self.repository.commit()
            
            # Retornar venda completa
            return await self.repository.get_with_items(venda_obj.id_venda, venda.id_empresa)
        except HTTPException:
            await self.repository.rollback()
            raise
        except Exception as e:
            await self.repository.rollback()
            self.logger.error(f"Erro ao criar venda: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao criar venda: {str(e)}"
            )
    
    async def atualizar_venda(self, id_venda: UUID, venda: VendaUpdate, id_empresa: UUID, id_usuario: UUID) -> Venda:
        """
        Atualizar venda existente.
        
        Args:
            id_venda: ID da venda a ser atualizada
            venda: Dados para atualização
            id_empresa: ID da empresa para validação
            id_usuario: ID do usuário que está realizando a atualização
            
        Returns:
            Venda atualizada
            
        Raises:
            HTTPException: Em caso de erro na validação ou atualização
        """
        self.logger.info(f"Atualizando venda: {id_venda}")
        
        try:
            # Verificar se a venda existe
            venda_atual = await self.get_venda(id_venda, id_empresa)
            
            # Verificar se a venda pode ser editada (status != cancelado ou concluído)
            if venda_atual.status in ["cancelado", "concluido"]:
                self.logger.warning(f"Tentativa de editar venda {id_venda} com status {venda_atual.status}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Não é possível editar venda com status {venda_atual.status}"
                )
            
            # Se o cliente foi alterado, verificar se existe
            if venda.id_cliente and venda.id_cliente != venda_atual.id_cliente:
                cliente = await self.cliente_repository.get_by_id(venda.id_cliente, id_empresa)
                if not cliente:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Cliente não encontrado"
                    )
            
            # Preparar dados para atualização
            venda_data = venda.dict(exclude_unset=True)
            
            # Atualizar venda
            venda_obj = await self.repository.update(id_venda, id_empresa, venda_data)
            if not venda_obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Venda não encontrada"
                )
            
            # Registrar log
            log = LogSistemaCreate(
                acao="atualizar",
                tabela="vendas",
                id_registro=str(id_venda),
                id_usuario=id_usuario,
                id_empresa=id_empresa,
                detalhes=f"Venda atualizada: {venda_data}"
            )
            await self.log_service.registrar_log(log)
            
            # Comitar alterações
            await self.repository.commit()
            
            # Buscar venda atualizada com itens
            return await self.repository.get_with_items(id_venda, id_empresa)
        except HTTPException:
            await self.repository.rollback()
            raise
        except Exception as e:
            await self.repository.rollback()
            self.logger.error(f"Erro ao atualizar venda: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao atualizar venda: {str(e)}"
            )
    
    async def cancelar_venda(self, id_venda: UUID, id_empresa: UUID, id_usuario: UUID, motivo: str) -> Venda:
        """
        Cancelar uma venda.
        
        Args:
            id_venda: ID da venda
            id_empresa: ID da empresa
            id_usuario: ID do usuário que está cancelando
            motivo: Motivo do cancelamento
            
        Returns:
            Venda cancelada
            
        Raises:
            HTTPException: Em caso de erro na validação ou cancelamento
        """
        self.logger.info(f"Cancelando venda: {id_venda}")
        
        try:
            # Verificar se a venda existe
            venda_atual = await self.get_venda(id_venda, id_empresa)
            
            # Verificar se a venda já está cancelada
            if venda_atual.status == "cancelado":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Venda já está cancelada"
                )
            
            # Verificar se a venda já está concluída
            if venda_atual.status == "concluido":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Não é possível cancelar uma venda concluída"
                )
            
            # Cancelar venda
            venda_cancelada = await self.repository.cancelar_venda(id_venda, id_empresa)
            if not venda_cancelada:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Venda não encontrada"
                )
            
            # Registrar log
            log = LogSistemaCreate(
                acao="cancelar",
                tabela="vendas",
                id_registro=str(id_venda),
                id_usuario=id_usuario,
                id_empresa=id_empresa,
                detalhes=f"Venda cancelada. Motivo: {motivo}"
            )
            await self.log_service.registrar_log(log)
            
            # Comitar alterações
            await self.repository.commit()
            
            return venda_cancelada
        except HTTPException:
            await self.repository.rollback()
            raise
        except Exception as e:
            await self.repository.rollback()
            self.logger.error(f"Erro ao cancelar venda: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao cancelar venda: {str(e)}"
            )
    
    async def concluir_venda(self, id_venda: UUID, id_empresa: UUID, id_usuario: UUID) -> Venda:
        """
        Concluir uma venda (alterar status para concluído).
        
        Args:
            id_venda: ID da venda
            id_empresa: ID da empresa
            id_usuario: ID do usuário que está concluindo
            
        Returns:
            Venda concluída
            
        Raises:
            HTTPException: Em caso de erro na validação ou conclusão
        """
        self.logger.info(f"Concluindo venda: {id_venda}")
        
        try:
            # Verificar se a venda existe
            venda_atual = await self.get_venda(id_venda, id_empresa)
            
            # Verificar status atual
            if venda_atual.status == "concluido":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Venda já está concluída"
                )
            
            if venda_atual.status == "cancelado":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Não é possível concluir uma venda cancelada"
                )
            
            # Atualizar status para concluído
            venda_data = {"status": "concluido", "data_conclusao": datetime.now()}
            venda_obj = await self.repository.update(id_venda, id_empresa, venda_data)
            
            # Registrar log
            log = LogSistemaCreate(
                acao="concluir",
                tabela="vendas",
                id_registro=str(id_venda),
                id_usuario=id_usuario,
                id_empresa=id_empresa,
                detalhes="Venda concluída"
            )
            await self.log_service.registrar_log(log)
            
            # Comitar alterações
            await self.repository.commit()
            
            return venda_obj
        except HTTPException:
            await self.repository.rollback()
            raise
        except Exception as e:
            await self.repository.rollback()
            self.logger.error(f"Erro ao concluir venda: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao concluir venda: {str(e)}"
            )
    
    async def remover_venda(self, id_venda: UUID, id_empresa: UUID, id_usuario: UUID) -> Dict[str, Any]:
        """
        Remover uma venda.
        
        Args:
            id_venda: ID da venda
            id_empresa: ID da empresa
            id_usuario: ID do usuário que está removendo
            
        Returns:
            Mensagem de confirmação
            
        Raises:
            HTTPException: Em caso de erro na validação ou remoção
        """
        self.logger.info(f"Removendo venda: {id_venda}")
        
        try:
            # Verificar se a venda existe
            venda = await self.get_venda(id_venda, id_empresa)
            
            # Remover venda
            resultado = await self.repository.delete(id_venda, id_empresa)
            if not resultado:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Venda não encontrada"
                )
            
            # Registrar log
            log = LogSistemaCreate(
                acao="remover",
                tabela="vendas",
                id_registro=str(id_venda),
                id_usuario=id_usuario,
                id_empresa=id_empresa,
                detalhes=f"Venda removida: {venda.id_venda}"
            )
            await self.log_service.registrar_log(log)
            
            # Comitar alterações
            await self.repository.commit()
            
            return {"mensagem": "Venda removida com sucesso"}
        except HTTPException:
            await self.repository.rollback()
            raise
        except Exception as e:
            await self.repository.rollback()
            self.logger.error(f"Erro ao remover venda: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao remover venda: {str(e)}"
            )
    
    async def adicionar_item_venda(
        self, 
        id_venda: UUID, 
        id_empresa: UUID, 
        item: ItemVendaSchema
    ) -> ItemVendaSchema:
        """
        Adicionar item a uma venda.
        
        Args:
            id_venda: ID da venda
            id_empresa: ID da empresa
            item: Dados do item a ser adicionado
            
        Returns:
            Item adicionado
            
        Raises:
            HTTPException: Em caso de erro na validação ou adição
        """
        self.logger.info(f"Adicionando item à venda: {id_venda}, produto: {item.id_produto}")
        
        try:
            # Verificar se a venda existe
            venda = await self.get_venda(id_venda, id_empresa)
            
            # Verificar se o produto existe
            produto = await self.produto_repository.get_by_id(item.id_produto, id_empresa)
            if not produto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Produto não encontrado"
                )
            
            # Verificar se a venda pode ser editada
            if venda.status in ["cancelado", "concluido"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Não é possível adicionar itens a uma venda com status {venda.status}"
                )
            
            # Preparar dados do item
            item_data = item.dict()
            
            # Adicionar item à venda
            novo_item = await self.repository.create_item_venda(id_venda, id_empresa, item_data)
            if not novo_item:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Não foi possível adicionar o item à venda"
                )
            
            # Comitar alterações
            await self.repository.commit()
            
            return ItemVendaSchema.from_orm(novo_item)
        except HTTPException:
            await self.repository.rollback()
            raise
        except Exception as e:
            await self.repository.rollback()
            self.logger.error(f"Erro ao adicionar item à venda: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao adicionar item à venda: {str(e)}"
            )
    
    async def atualizar_item_venda(
        self, 
        id_venda: UUID, 
        id_item: UUID, 
        id_empresa: UUID, 
        item: ItemVendaSchema
    ) -> ItemVendaSchema:
        """
        Atualizar item de uma venda.
        
        Args:
            id_venda: ID da venda
            id_item: ID do item
            id_empresa: ID da empresa
            item: Dados atualizados do item
            
        Returns:
            Item atualizado
            
        Raises:
            HTTPException: Em caso de erro na validação ou atualização
        """
        self.logger.info(f"Atualizando item {id_item} da venda: {id_venda}")
        
        try:
            # Verificar se a venda existe
            venda = await self.get_venda(id_venda, id_empresa)
            
            # Verificar se a venda pode ser editada
            if venda.status in ["cancelado", "concluido"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Não é possível editar itens de uma venda com status {venda.status}"
                )
            
            # Preparar dados do item
            item_data = item.dict(exclude_unset=True)
            
            # Se o produto foi alterado, verificar se existe
            if item.id_produto:
                produto = await self.produto_repository.get_by_id(item.id_produto, id_empresa)
                if not produto:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Produto não encontrado"
                    )
            
            # Atualizar item
            item_atualizado = await self.repository.update_item_venda(id_venda, id_item, id_empresa, item_data)
            if not item_atualizado:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Item não encontrado"
                )
            
            # Comitar alterações
            await self.repository.commit()
            
            return ItemVendaSchema.from_orm(item_atualizado)
        except HTTPException:
            await self.repository.rollback()
            raise
        except Exception as e:
            await self.repository.rollback()
            self.logger.error(f"Erro ao atualizar item da venda: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao atualizar item da venda: {str(e)}"
            )
    
    async def remover_item_venda(self, id_venda: UUID, id_item: UUID, id_empresa: UUID) -> Dict[str, Any]:
        """
        Remover item de uma venda.
        
        Args:
            id_venda: ID da venda
            id_item: ID do item
            id_empresa: ID da empresa
            
        Returns:
            Mensagem de confirmação
            
        Raises:
            HTTPException: Em caso de erro na validação ou remoção
        """
        self.logger.info(f"Removendo item {id_item} da venda: {id_venda}")
        
        try:
            # Verificar se a venda existe
            venda = await self.get_venda(id_venda, id_empresa)
            
            # Verificar se a venda pode ser editada
            if venda.status in ["cancelado", "concluido"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Não é possível remover itens de uma venda com status {venda.status}"
                )
            
            # Remover item
            resultado = await self.repository.delete_item_venda(id_venda, id_item, id_empresa)
            if not resultado:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Item não encontrado"
                )
            
            # Comitar alterações
            await self.repository.commit()
            
            return {"mensagem": "Item removido com sucesso"}
        except HTTPException:
            await self.repository.rollback()
            raise
        except Exception as e:
            await self.repository.rollback()
            self.logger.error(f"Erro ao remover item da venda: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao remover item da venda: {str(e)}"
            ) 