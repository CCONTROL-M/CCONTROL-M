"""Serviço especializado para gerenciamento de status de vendas."""
from uuid import UUID
from typing import Dict, Any, Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.venda_repository import VendaRepository
from app.schemas.venda import Venda, StatusVenda
from app.services.auditoria_service import AuditoriaService


class VendaStatusService:
    """Serviço especializado para gerenciamento de status de vendas."""

    def __init__(
        self,
        session: AsyncSession,
        auditoria_service: AuditoriaService
    ):
        """Inicializa o serviço com a sessão do banco de dados."""
        self.repository = VendaRepository(session)
        self.auditoria_service = auditoria_service
    
    async def _validar_acesso_venda(self, id_venda: UUID, id_empresa: UUID) -> Venda:
        """
        Valida se a venda existe e pertence à empresa.
        
        Args:
            id_venda: ID da venda
            id_empresa: ID da empresa
            
        Returns:
            Venda encontrada
            
        Raises:
            HTTPException: Se a venda não existir ou não pertencer à empresa
        """
        venda = await self.repository.get_by_id(id_venda)
        
        if not venda:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Venda não encontrada"
            )
            
        if venda.id_empresa != id_empresa:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso não autorizado a esta venda"
            )
            
        return venda
    
    async def cancelar_venda(
        self, 
        id_venda: UUID, 
        id_empresa: UUID, 
        id_usuario: UUID, 
        motivo: str
    ) -> Venda:
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
            HTTPException: Se ocorrer algum erro durante a operação
        """
        # Validar acesso e obter venda
        venda = await self._validar_acesso_venda(id_venda, id_empresa)
        
        # Verificar se a venda pode ser cancelada
        if venda.status == StatusVenda.CANCELADA:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Venda já está cancelada"
            )
            
        if venda.status == StatusVenda.CONCLUIDA:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível cancelar uma venda concluída"
            )
        
        # Cancelar venda
        try:
            venda_cancelada = await self.repository.atualizar_status_venda(
                id_venda=id_venda,
                novo_status=StatusVenda.CANCELADA,
                usuario_id=id_usuario,
                motivo=motivo
            )
            
            # Registrar auditoria
            await self.auditoria_service.registrar_acao(
                entidade="venda",
                acao="cancel",
                id_registro=str(id_venda),
                dados_anteriores=venda.dict(),
                dados_novos=venda_cancelada.dict(),
                id_usuario=id_usuario
            )
            
            return venda_cancelada
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erro ao cancelar venda: {str(e)}"
            )
    
    async def concluir_venda(
        self, 
        id_venda: UUID, 
        id_empresa: UUID, 
        id_usuario: UUID
    ) -> Venda:
        """
        Concluir uma venda.
        
        Args:
            id_venda: ID da venda a ser concluída
            id_empresa: ID da empresa para validação de acesso
            id_usuario: ID do usuário que está concluindo a venda
            
        Returns:
            Venda concluída
            
        Raises:
            HTTPException: Se ocorrer algum erro durante a operação
        """
        # Validar acesso e obter venda
        venda = await self._validar_acesso_venda(id_venda, id_empresa)
        
        # Verificar se a venda pode ser concluída
        if venda.status == StatusVenda.CONCLUIDA:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Venda já está concluída"
            )
            
        if venda.status == StatusVenda.CANCELADA:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível concluir uma venda cancelada"
            )
        
        # Verificar se a venda tem itens
        itens = await self.repository.listar_itens_venda(id_venda)
        if not itens:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível concluir uma venda sem itens"
            )
        
        # Concluir venda
        try:
            venda_concluida = await self.repository.atualizar_status_venda(
                id_venda=id_venda,
                novo_status=StatusVenda.CONCLUIDA,
                usuario_id=id_usuario
            )
            
            # Registrar auditoria
            await self.auditoria_service.registrar_acao(
                entidade="venda",
                acao="complete",
                id_registro=str(id_venda),
                dados_anteriores=venda.dict(),
                dados_novos=venda_concluida.dict(),
                id_usuario=id_usuario
            )
            
            return venda_concluida
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erro ao concluir venda: {str(e)}"
            ) 