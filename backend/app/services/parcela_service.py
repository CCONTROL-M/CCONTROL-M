"""Serviço para gerenciamento de parcelas no sistema CCONTROL-M."""
from uuid import UUID
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
import logging

from app.schemas.parcela import ParcelaCreate, ParcelaUpdate, Parcela, StatusParcela
from app.repositories.parcela_repository import ParcelaRepository
from app.repositories.venda_repository import VendaRepository
from app.repositories.lancamento_repository import LancamentoRepository
from app.services.log_sistema_service import LogSistemaService
from app.schemas.log_sistema import LogSistemaCreate
from app.database import get_async_session


class ParcelaService:
    """Serviço para gerenciamento de parcelas."""
    
    def __init__(self, 
                 session: AsyncSession = Depends(get_async_session),
                 log_service: LogSistemaService = Depends()):
        """Inicializar serviço com repositórios."""
        self.repository = ParcelaRepository(session)
        self.venda_repository = VendaRepository(session)
        self.lancamento_repository = LancamentoRepository(session)
        self.log_service = log_service
        self.logger = logging.getLogger(__name__)
        
    async def get_parcela(self, id_parcela: UUID, id_empresa: UUID) -> Parcela:
        """
        Obter parcela pelo ID.
        
        Args:
            id_parcela: ID da parcela
            id_empresa: ID da empresa para validação de acesso
            
        Returns:
            Parcela encontrada
            
        Raises:
            HTTPException: Se a parcela não for encontrada
        """
        self.logger.info(f"Buscando parcela ID: {id_parcela}")
        
        parcela = await self.repository.get_by_id(id_parcela, id_empresa)
        if not parcela:
            self.logger.warning(f"Parcela não encontrada: {id_parcela}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parcela não encontrada"
            )
        return parcela
        
    async def listar_parcelas(
        self,
        id_empresa: UUID,
        skip: int = 0,
        limit: int = 100,
        id_venda: Optional[UUID] = None,
        vencimento_inicial: Optional[date] = None,
        vencimento_final: Optional[date] = None,
        status: Optional[StatusParcela] = None,
        valor_min: Optional[float] = None,
        valor_max: Optional[float] = None
    ) -> Tuple[List[Parcela], int]:
        """
        Listar parcelas com paginação e filtros.
        
        Args:
            id_empresa: ID da empresa
            skip: Número de registros a pular
            limit: Número máximo de registros a retornar
            id_venda: Filtrar por ID da venda
            vencimento_inicial: Filtrar por data de vencimento inicial
            vencimento_final: Filtrar por data de vencimento final
            status: Filtrar por status da parcela
            valor_min: Filtrar por valor mínimo
            valor_max: Filtrar por valor máximo
            
        Returns:
            Lista de parcelas e contagem total
        """
        self.logger.info(f"Buscando parcelas com filtros: empresa={id_empresa}, venda={id_venda}, status={status}")
        
        filters = [{"id_empresa": id_empresa}]
        
        if id_venda:
            filters.append({"id_venda": id_venda})
            
        if vencimento_inicial:
            filters.append({"data_vencimento__gte": vencimento_inicial})
            
        if vencimento_final:
            filters.append({"data_vencimento__lte": vencimento_final})
            
        if status:
            filters.append({"status": status})
            
        if valor_min is not None:
            filters.append({"valor__gte": valor_min})
            
        if valor_max is not None:
            filters.append({"valor__lte": valor_max})
            
        return await self.repository.list_with_filters(
            skip=skip,
            limit=limit,
            filters=filters
        )
        
    async def criar_parcela(self, parcela: ParcelaCreate, id_usuario: UUID) -> Parcela:
        """
        Criar nova parcela.
        
        Args:
            parcela: Dados da parcela a ser criada
            id_usuario: ID do usuário que está criando a parcela
            
        Returns:
            Parcela criada
            
        Raises:
            HTTPException: Se ocorrer um erro na validação
        """
        self.logger.info(f"Criando nova parcela para empresa: {parcela.id_empresa}")
        
        # Validar venda
        if parcela.id_venda:
            venda = await self.venda_repository.get_by_id(parcela.id_venda, parcela.id_empresa)
            if not venda:
                self.logger.warning(f"Venda não encontrada: {parcela.id_venda}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Venda não encontrada"
                )
                
        # Validar valor
        if parcela.valor <= 0:
            self.logger.warning(f"Valor inválido: {parcela.valor}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valor deve ser maior que zero"
            )
            
        # Validar data de vencimento
        if parcela.data_vencimento < date.today():
            self.logger.warning(f"Data de vencimento no passado: {parcela.data_vencimento}")
            # Apenas avisar, não impedir (pode ser um lançamento retroativo)
            self.logger.warning("Criando parcela com data de vencimento no passado")
            
        # Criar parcela
        try:
            parcela_data = parcela.model_dump()
            
            # Definir status padrão se não fornecido
            if "status" not in parcela_data or parcela_data["status"] is None:
                parcela_data["status"] = StatusParcela.PENDENTE
                
            nova_parcela = await self.repository.create(parcela_data)
            
            # Registrar log
            await self.log_service.registrar_log(
                LogSistemaCreate(
                    id_empresa=parcela.id_empresa,
                    id_usuario=id_usuario,
                    acao="criar_parcela",
                    descricao=f"Parcela criada com ID {nova_parcela.id_parcela}",
                    dados={
                        "id_parcela": str(nova_parcela.id_parcela), 
                        "valor": float(nova_parcela.valor),
                        "id_venda": str(parcela.id_venda) if parcela.id_venda else None
                    }
                )
            )
            
            return nova_parcela
        except Exception as e:
            self.logger.error(f"Erro ao criar parcela: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao criar parcela"
            )
        
    async def atualizar_parcela(self, id_parcela: UUID, parcela: ParcelaUpdate, id_empresa: UUID, id_usuario: UUID) -> Parcela:
        """
        Atualizar parcela existente.
        
        Args:
            id_parcela: ID da parcela a ser atualizada
            parcela: Dados para atualização
            id_empresa: ID da empresa para validação de acesso
            id_usuario: ID do usuário que está atualizando a parcela
            
        Returns:
            Parcela atualizada
            
        Raises:
            HTTPException: Se a parcela não for encontrada ou ocorrer erro na validação
        """
        self.logger.info(f"Atualizando parcela: {id_parcela}")
        
        # Verificar se a parcela existe
        parcela_atual = await self.get_parcela(id_parcela, id_empresa)
        
        # Validar venda se estiver sendo atualizada
        if parcela.id_venda:
            venda = await self.venda_repository.get_by_id(parcela.id_venda, id_empresa)
            if not venda:
                self.logger.warning(f"Venda não encontrada: {parcela.id_venda}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Venda não encontrada"
                )
                
        # Validar valor se estiver sendo atualizado
        if parcela.valor is not None and parcela.valor <= 0:
            self.logger.warning(f"Valor inválido: {parcela.valor}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valor deve ser maior que zero"
            )
            
        # Validar transição de status
        if parcela.status and parcela.status != parcela_atual.status:
            # Regras específicas para transição de status
            # Ex: PENDENTE -> PAGO, PENDENTE -> ATRASADO, etc.
            # Aqui podemos adicionar regras conforme necessidade do negócio
            pass
            
        # Atualizar parcela
        try:
            # Remover campos None do modelo de atualização
            update_data = {k: v for k, v in parcela.model_dump().items() if v is not None}
            
            # Se estiver atualizando para PAGO, registre a data de pagamento
            if parcela.status == StatusParcela.PAGO and "data_pagamento" not in update_data:
                update_data["data_pagamento"] = datetime.now().date()
                
            parcela_atualizada = await self.repository.update(id_parcela, update_data, id_empresa)
            
            if not parcela_atualizada:
                self.logger.warning(f"Parcela não encontrada após tentativa de atualização: {id_parcela}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parcela não encontrada"
                )
                
            # Registrar log
            await self.log_service.registrar_log(
                LogSistemaCreate(
                    id_empresa=id_empresa,
                    id_usuario=id_usuario,
                    acao="atualizar_parcela",
                    descricao=f"Parcela atualizada com ID {id_parcela}",
                    dados={"id_parcela": str(id_parcela), "atualizacoes": update_data}
                )
            )
            
            return parcela_atualizada
        except Exception as e:
            self.logger.error(f"Erro ao atualizar parcela: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao atualizar parcela"
            )
            
    async def registrar_pagamento(self, id_parcela: UUID, id_empresa: UUID, id_usuario: UUID, data_pagamento: Optional[date] = None) -> Parcela:
        """
        Registrar pagamento de uma parcela.
        
        Args:
            id_parcela: ID da parcela a ser paga
            id_empresa: ID da empresa para validação de acesso
            id_usuario: ID do usuário que está registrando o pagamento
            data_pagamento: Data do pagamento (padrão: data atual)
            
        Returns:
            Parcela atualizada
            
        Raises:
            HTTPException: Se a parcela não for encontrada ou já estiver paga
        """
        self.logger.info(f"Registrando pagamento da parcela: {id_parcela}")
        
        # Verificar se a parcela existe
        parcela = await self.get_parcela(id_parcela, id_empresa)
        
        # Verificar se já está paga
        if parcela.status == StatusParcela.PAGO:
            self.logger.warning(f"Parcela já está paga: {id_parcela}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parcela já está paga"
            )
            
        # Registrar pagamento
        update_data = {
            "status": StatusParcela.PAGO,
            "data_pagamento": data_pagamento or datetime.now().date()
        }
        
        parcela_paga = await self.repository.update(id_parcela, update_data, id_empresa)
        
        # Registrar log
        await self.log_service.registrar_log(
            LogSistemaCreate(
                id_empresa=id_empresa,
                id_usuario=id_usuario,
                acao="registrar_pagamento",
                descricao=f"Pagamento registrado para parcela ID {id_parcela}",
                dados={
                    "id_parcela": str(id_parcela),
                    "data_pagamento": str(update_data["data_pagamento"]),
                    "valor": float(parcela.valor)
                }
            )
        )
        
        return parcela_paga
        
    async def cancelar_parcela(self, id_parcela: UUID, id_empresa: UUID, id_usuario: UUID, motivo: str) -> Parcela:
        """
        Cancelar uma parcela.
        
        Args:
            id_parcela: ID da parcela a ser cancelada
            id_empresa: ID da empresa para validação de acesso
            id_usuario: ID do usuário que está cancelando a parcela
            motivo: Motivo do cancelamento
            
        Returns:
            Parcela cancelada
            
        Raises:
            HTTPException: Se a parcela não for encontrada ou já estiver cancelada/paga
        """
        self.logger.info(f"Cancelando parcela: {id_parcela}")
        
        # Verificar se a parcela existe
        parcela = await self.get_parcela(id_parcela, id_empresa)
        
        # Verificar status atual
        if parcela.status == StatusParcela.CANCELADO:
            self.logger.warning(f"Parcela já está cancelada: {id_parcela}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parcela já está cancelada"
            )
            
        if parcela.status == StatusParcela.PAGO:
            self.logger.warning(f"Não é possível cancelar uma parcela já paga: {id_parcela}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível cancelar uma parcela já paga"
            )
            
        # Verificar se tem lançamentos associados
        lancamentos = await self.lancamento_repository.get_by_parcela(id_parcela, id_empresa)
        if lancamentos and len(lancamentos) > 0:
            self.logger.warning(f"Parcela possui lançamentos associados: {id_parcela}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível cancelar uma parcela com lançamentos associados"
            )
            
        # Cancelar parcela
        update_data = {
            "status": StatusParcela.CANCELADO,
            "observacoes": f"CANCELADA: {motivo}" if not parcela.observacoes else f"{parcela.observacoes}\nCANCELADA: {motivo}"
        }
        
        parcela_cancelada = await self.repository.update(id_parcela, update_data, id_empresa)
        
        # Registrar log
        await self.log_service.registrar_log(
            LogSistemaCreate(
                id_empresa=id_empresa,
                id_usuario=id_usuario,
                acao="cancelar_parcela",
                descricao=f"Parcela cancelada com ID {id_parcela}",
                dados={"id_parcela": str(id_parcela), "motivo": motivo}
            )
        )
        
        return parcela_cancelada
        
    async def remover_parcela(self, id_parcela: UUID, id_empresa: UUID, id_usuario: UUID) -> Dict[str, Any]:
        """
        Remover parcela pelo ID.
        
        Args:
            id_parcela: ID da parcela a ser removida
            id_empresa: ID da empresa para validação de acesso
            id_usuario: ID do usuário que está removendo a parcela
            
        Returns:
            Mensagem de confirmação
            
        Raises:
            HTTPException: Se a parcela não for encontrada ou não puder ser removida
        """
        self.logger.info(f"Removendo parcela: {id_parcela}")
        
        # Verificar se a parcela existe
        parcela = await self.get_parcela(id_parcela, id_empresa)
        
        # Verificar se já tem lançamentos associados
        lancamentos = await self.lancamento_repository.get_by_parcela(id_parcela, id_empresa)
        if lancamentos and len(lancamentos) > 0:
            self.logger.warning(f"Parcela possui lançamentos associados: {id_parcela}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível remover uma parcela com lançamentos associados"
            )
            
        # Verificar status
        if parcela.status == StatusParcela.PAGO:
            self.logger.warning(f"Não é possível remover uma parcela já paga: {id_parcela}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível remover uma parcela já paga"
            )
            
        # Remover parcela
        await self.repository.delete(id_parcela, id_empresa)
        
        # Registrar log
        await self.log_service.registrar_log(
            LogSistemaCreate(
                id_empresa=id_empresa,
                id_usuario=id_usuario,
                acao="remover_parcela",
                descricao=f"Parcela removida com ID {id_parcela}",
                dados={"id_parcela": str(id_parcela)}
            )
        )
        
        return {"detail": "Parcela removida com sucesso"}

    async def get_dashboard_parcelas(
        self,
        id_empresa: UUID,
        dias_vencidas: int = 30,
        dias_proximas: int = 15
    ) -> Any:
        """
        Obter dados de parcelas para o dashboard.
        
        Args:
            id_empresa: ID da empresa
            dias_vencidas: Quantidade de dias para considerar parcelas vencidas
            dias_proximas: Quantidade de dias para considerar próximas de vencer
            
        Returns:
            Dados das parcelas para o dashboard
        """
        self.logger.info(f"Obtendo parcelas para dashboard: empresa={id_empresa}")
        
        try:
            dados_dashboard = await self.repository.get_dashboard_data(
                id_empresa=id_empresa,
                dias_vencidas=dias_vencidas,
                dias_proximas=dias_proximas
            )
            return dados_dashboard
        except Exception as e:
            self.logger.error(f"Erro ao obter dados para dashboard: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao obter dados para dashboard"
            )
            
    async def get_recebimentos_dia(
        self,
        id_empresa: UUID,
        data: date
    ) -> float:
        """
        Calcular total de recebimentos em um dia específico.
        
        Args:
            id_empresa: ID da empresa
            data: Data para calcular os recebimentos
            
        Returns:
            Total de recebimentos no dia
        """
        self.logger.info(f"Calculando recebimentos do dia {data}: empresa={id_empresa}")
        
        try:
            # Buscar parcelas pagas na data especificada
            filters = [
                {"id_empresa": id_empresa},
                {"status": StatusParcela.PAGO},
                {"data_pagamento": data}
            ]
            
            parcelas_pagas, _ = await self.repository.list_with_filters(
                skip=0,
                limit=1000,  # Valor alto para trazer todas
                filters=filters
            )
            
            # Calcular total recebido
            total_recebido = sum(float(parcela.valor) for parcela in parcelas_pagas)
            
            return total_recebido
        except Exception as e:
            self.logger.error(f"Erro ao calcular recebimentos do dia: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao calcular recebimentos do dia"
            ) 