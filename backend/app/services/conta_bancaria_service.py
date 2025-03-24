"""Serviço para gerenciamento de contas bancárias no sistema CCONTROL-M."""
from uuid import UUID
from typing import Dict, Any, List, Optional, Tuple
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
import logging
from datetime import datetime

from app.schemas.conta_bancaria import ContaBancariaCreate, ContaBancariaUpdate, ContaBancaria
from app.repositories.conta_bancaria_repository import ContaBancariaRepository
from app.repositories.lancamento_repository import LancamentoRepository
from app.services.log_sistema_service import LogSistemaService
from app.schemas.log_sistema import LogSistemaCreate
from app.database import get_async_session
from app.schemas.pagination import PaginatedResponse
from app.services.auditoria_service import AuditoriaService


# Configurar logger
logger = logging.getLogger(__name__)


class ContaBancariaService:
    """Serviço para gerenciamento de contas bancárias."""
    
    def __init__(self, 
                 session: AsyncSession = Depends(get_async_session),
                 log_service: LogSistemaService = Depends(),
                 auditoria_service: AuditoriaService = Depends()):
        """Inicializar serviço com repositórios."""
        self.repository = ContaBancariaRepository(session)
        self.lancamento_repository = LancamentoRepository(session)
        self.log_service = log_service
        self.auditoria_service = auditoria_service
        self.logger = logger
        
    async def get_conta_bancaria(self, id_conta: UUID, id_empresa: UUID) -> ContaBancaria:
        """
        Obter conta bancária pelo ID.
        
        Args:
            id_conta: ID da conta bancária
            id_empresa: ID da empresa para validação de acesso
            
        Returns:
            Conta bancária encontrada
            
        Raises:
            HTTPException: Se a conta bancária não for encontrada
        """
        self.logger.info(f"Buscando conta bancária ID: {id_conta}")
        
        conta_bancaria = await self.repository.get_by_id(id_conta, id_empresa)
        if not conta_bancaria:
            self.logger.warning(f"Conta bancária não encontrada: {id_conta}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conta bancária não encontrada"
            )
        return conta_bancaria
        
    async def listar_contas_bancarias(
        self,
        id_empresa: UUID,
        skip: int = 0,
        limit: int = 100,
        filtros: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[ContaBancaria], int]:
        """
        Listar contas bancárias com paginação e filtros.
        
        Args:
            id_empresa: ID da empresa
            skip: Número de registros a pular
            limit: Número máximo de registros a retornar
            filtros: Dicionário de filtros (nome, banco, tipo, ativo)
            
        Returns:
            Lista de contas bancárias e contagem total
        """
        self.logger.info(f"Buscando contas bancárias com filtros: empresa={id_empresa}, filtros={filtros}")
        
        # Garantir que filtros seja um dicionário
        if not filtros:
            filtros = {}
            
        # Adicionar id_empresa aos filtros
        filtros_lista = [{"id_empresa": id_empresa}]
        
        # Adicionar demais filtros
        for campo, valor in filtros.items():
            if valor is not None:
                if campo in ["nome", "banco"]:
                    filtros_lista.append({f"{campo}__ilike": f"%{valor}%"})
                else:
                    filtros_lista.append({campo: valor})
            
        return await self.repository.list_with_filters(
            skip=skip,
            limit=limit,
            filters=filtros_lista
        )
        
    async def criar_conta_bancaria(self, conta_bancaria: ContaBancariaCreate, id_usuario: UUID) -> ContaBancaria:
        """
        Criar nova conta bancária.
        
        Args:
            conta_bancaria: Dados da conta bancária a ser criada
            id_usuario: ID do usuário que está criando a conta bancária
            
        Returns:
            Conta bancária criada
            
        Raises:
            HTTPException: Se ocorrer um erro na validação
        """
        self.logger.info(f"Criando nova conta bancária: {conta_bancaria.nome}")
        
        # Verificar se já existe conta com mesmo nome na empresa
        conta_existente = await self.repository.get_by_nome(conta_bancaria.nome, conta_bancaria.id_empresa)
        if conta_existente:
            self.logger.warning(f"Já existe uma conta bancária com o nome '{conta_bancaria.nome}' na empresa")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Já existe uma conta bancária com o nome '{conta_bancaria.nome}'"
            )
            
        # Criar conta bancária
        try:
            conta_bancaria_data = conta_bancaria.model_dump()
            
            # Definir como ativo por padrão se não especificado
            if "ativa" not in conta_bancaria_data or conta_bancaria_data["ativa"] is None:
                conta_bancaria_data["ativa"] = True
                
            # Definir saldo inicial como 0 se não especificado
            if "saldo_inicial" not in conta_bancaria_data or conta_bancaria_data["saldo_inicial"] is None:
                conta_bancaria_data["saldo_inicial"] = Decimal("0.0")
                
            # Definir saldo atual igual ao inicial
            conta_bancaria_data["saldo_atual"] = conta_bancaria_data["saldo_inicial"]
                
            nova_conta = await self.repository.create(conta_bancaria_data)
            
            # Registrar auditoria
            await self.auditoria_service.registrar_acao(
                usuario_id=id_usuario,
                acao="CRIAR_CONTA_BANCARIA",
                detalhes={
                    "id_conta": str(nova_conta.id_conta),
                    "nome": nova_conta.nome,
                    "banco": nova_conta.banco,
                    "saldo_inicial": float(nova_conta.saldo_inicial)
                },
                empresa_id=conta_bancaria.id_empresa
            )
            
            return nova_conta
        except Exception as e:
            self.logger.error(f"Erro ao criar conta bancária: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao criar conta bancária"
            )
        
    async def atualizar_conta_bancaria(
        self, 
        id_conta: UUID, 
        conta_bancaria: ContaBancariaUpdate, 
        id_empresa: UUID, 
        id_usuario: UUID
    ) -> ContaBancaria:
        """
        Atualizar conta bancária existente.
        
        Args:
            id_conta: ID da conta bancária a ser atualizada
            conta_bancaria: Dados para atualização
            id_empresa: ID da empresa para validação de acesso
            id_usuario: ID do usuário que está atualizando a conta bancária
            
        Returns:
            Conta bancária atualizada
            
        Raises:
            HTTPException: Se a conta bancária não for encontrada ou ocorrer erro na validação
        """
        self.logger.info(f"Atualizando conta bancária: {id_conta}")
        
        # Verificar se a conta bancária existe
        conta_atual = await self.get_conta_bancaria(id_conta, id_empresa)
        
        # Verificar unicidade do nome se estiver sendo atualizado
        if conta_bancaria.nome:
            conta_existente = await self.repository.get_by_nome(conta_bancaria.nome, id_empresa)
            if conta_existente and conta_existente.id_conta != id_conta:
                self.logger.warning(f"Já existe uma conta bancária com o nome '{conta_bancaria.nome}' na empresa")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Já existe uma conta bancária com o nome '{conta_bancaria.nome}'"
                )
                
        # Não permitir alterar saldo_inicial se já existirem lançamentos
        if conta_bancaria.saldo_inicial is not None and conta_bancaria.saldo_inicial != conta_atual.saldo_inicial:
            tem_lancamentos = await self.lancamento_repository.has_by_conta_bancaria(id_conta, id_empresa)
            if tem_lancamentos:
                self.logger.warning(f"Não é possível alterar o saldo inicial de uma conta com lançamentos: {id_conta}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Não é possível alterar o saldo inicial de uma conta que já possui lançamentos"
                )
                
        # Atualizar conta bancária
        try:
            # Remover campos None do modelo de atualização
            update_data = {k: v for k, v in conta_bancaria.model_dump().items() if v is not None}
            
            # Se estiver atualizando o saldo inicial, atualizar o saldo atual também
            if "saldo_inicial" in update_data:
                # Calcular diferença para atualizar o saldo atual proporcionalmente
                diferenca = update_data["saldo_inicial"] - conta_atual.saldo_inicial
                update_data["saldo_atual"] = conta_atual.saldo_atual + diferenca
                
            conta_atualizada = await self.repository.update(id_conta, update_data, id_empresa)
            
            if not conta_atualizada:
                self.logger.warning(f"Conta bancária não encontrada após tentativa de atualização: {id_conta}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conta bancária não encontrada"
                )
            
            # Registrar auditoria
            await self.auditoria_service.registrar_acao(
                usuario_id=id_usuario,
                acao="ATUALIZAR_CONTA_BANCARIA",
                detalhes={
                    "id_conta": str(id_conta),
                    "campos_alterados": list(update_data.keys())
                },
                empresa_id=id_empresa
            )
                
            return conta_atualizada
        except Exception as e:
            self.logger.error(f"Erro ao atualizar conta bancária: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao atualizar conta bancária"
            )
            
    async def ativar_conta_bancaria(self, id_conta_bancaria: UUID, id_empresa: UUID, id_usuario: UUID) -> ContaBancaria:
        """
        Ativar uma conta bancária.
        
        Args:
            id_conta_bancaria: ID da conta bancária a ser ativada
            id_empresa: ID da empresa para validação de acesso
            id_usuario: ID do usuário que está ativando a conta bancária
            
        Returns:
            Conta bancária ativada
            
        Raises:
            HTTPException: Se a conta bancária não for encontrada
        """
        self.logger.info(f"Ativando conta bancária: {id_conta_bancaria}")
        
        # Verificar se a conta bancária existe
        conta_bancaria = await self.get_conta_bancaria(id_conta_bancaria, id_empresa)
        
        # Verificar se já está ativa
        if conta_bancaria.ativa:
            self.logger.warning(f"Conta bancária já está ativa: {id_conta_bancaria}")
            return conta_bancaria
            
        # Ativar conta bancária
        update_data = {"ativa": True}
        
        conta_atualizada = await self.repository.update(id_conta_bancaria, update_data, id_empresa)
        
        # Registrar log
        await self.log_service.registrar_log(
            LogSistemaCreate(
                id_empresa=id_empresa,
                id_usuario=id_usuario,
                acao="ativar_conta_bancaria",
                descricao=f"Conta bancária ativada: {conta_bancaria.nome}",
                dados={"id_conta_bancaria": str(id_conta_bancaria)}
            )
        )
        
        # Registrar ação
        await self.auditoria_service.registrar_acao(
            usuario_id=id_usuario,
            acao="ATIVAR_CONTA_BANCARIA",
            detalhes={"id_conta": str(id_conta_bancaria)},
            empresa_id=id_empresa
        )
        
        return conta_atualizada
        
    async def desativar_conta_bancaria(self, id_conta_bancaria: UUID, id_empresa: UUID, id_usuario: UUID) -> ContaBancaria:
        """
        Desativar uma conta bancária.
        
        Args:
            id_conta_bancaria: ID da conta bancária a ser desativada
            id_empresa: ID da empresa para validação de acesso
            id_usuario: ID do usuário que está desativando a conta bancária
            
        Returns:
            Conta bancária desativada
            
        Raises:
            HTTPException: Se a conta bancária não for encontrada
        """
        self.logger.info(f"Desativando conta bancária: {id_conta_bancaria}")
        
        # Verificar se a conta bancária existe
        conta_bancaria = await self.get_conta_bancaria(id_conta_bancaria, id_empresa)
        
        # Verificar se já está inativa
        if not conta_bancaria.ativa:
            self.logger.warning(f"Conta bancária já está inativa: {id_conta_bancaria}")
            return conta_bancaria
            
        # Desativar conta bancária
        update_data = {"ativa": False}
        
        conta_atualizada = await self.repository.update(id_conta_bancaria, update_data, id_empresa)
        
        # Registrar log
        await self.log_service.registrar_log(
            LogSistemaCreate(
                id_empresa=id_empresa,
                id_usuario=id_usuario,
                acao="desativar_conta_bancaria",
                descricao=f"Conta bancária desativada: {conta_bancaria.nome}",
                dados={"id_conta_bancaria": str(id_conta_bancaria)}
            )
        )
        
        # Registrar ação
        await self.auditoria_service.registrar_acao(
            usuario_id=id_usuario,
            acao="DESATIVAR_CONTA_BANCARIA",
            detalhes={"id_conta": str(id_conta_bancaria)},
            empresa_id=id_empresa
        )
        
        return conta_atualizada
        
    async def ajustar_saldo(self, id_conta_bancaria: UUID, id_empresa: UUID, id_usuario: UUID, novo_saldo: Decimal, motivo: str) -> ContaBancaria:
        """
        Ajustar o saldo de uma conta bancária.
        
        Args:
            id_conta_bancaria: ID da conta bancária
            id_empresa: ID da empresa para validação de acesso
            id_usuario: ID do usuário que está ajustando o saldo
            novo_saldo: Novo valor do saldo
            motivo: Motivo do ajuste
            
        Returns:
            Conta bancária com saldo ajustado
            
        Raises:
            HTTPException: Se a conta bancária não for encontrada
        """
        self.logger.info(f"Ajustando saldo da conta bancária: {id_conta_bancaria}")
        
        # Verificar se a conta bancária existe
        conta_bancaria = await self.get_conta_bancaria(id_conta_bancaria, id_empresa)
        
        # Verificar se a conta está ativa
        if not conta_bancaria.ativa:
            self.logger.warning(f"Não é possível ajustar o saldo de uma conta inativa: {id_conta_bancaria}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível ajustar o saldo de uma conta inativa"
            )
            
        # Verificar se o novo saldo é diferente do atual
        if novo_saldo == conta_bancaria.saldo_atual:
            self.logger.warning(f"O novo saldo é igual ao saldo atual: {novo_saldo}")
            return conta_bancaria
            
        # Ajustar saldo
        update_data = {"saldo_atual": novo_saldo}
        
        conta_atualizada = await self.repository.update(id_conta_bancaria, update_data, id_empresa)
        
        # Registrar log
        await self.log_service.registrar_log(
            LogSistemaCreate(
                id_empresa=id_empresa,
                id_usuario=id_usuario,
                acao="ajustar_saldo_conta",
                descricao=f"Saldo ajustado na conta {conta_bancaria.nome}",
                dados={
                    "id_conta_bancaria": str(id_conta_bancaria),
                    "saldo_anterior": float(conta_bancaria.saldo_atual),
                    "novo_saldo": float(novo_saldo),
                    "diferenca": float(novo_saldo - conta_bancaria.saldo_atual),
                    "motivo": motivo
                }
            )
        )
        
        # Registrar ação
        await self.auditoria_service.registrar_acao(
            usuario_id=id_usuario,
            acao="AJUSTAR_SALDO_CONTA",
            detalhes={
                "id_conta": str(id_conta_bancaria),
                "saldo_anterior": float(conta_bancaria.saldo_atual),
                "novo_saldo": float(novo_saldo),
                "diferenca": float(novo_saldo - conta_bancaria.saldo_atual),
                "motivo": motivo
            },
            empresa_id=id_empresa
        )
        
        return conta_atualizada
        
    async def remover_conta_bancaria(self, id_conta: UUID, id_empresa: UUID) -> Dict[str, Any]:
        """
        Remover conta bancária.
        
        Args:
            id_conta: ID da conta bancária a ser removida
            id_empresa: ID da empresa para validação de acesso
            
        Returns:
            Mensagem de confirmação
            
        Raises:
            HTTPException: Se a conta bancária não for encontrada ou não puder ser removida
        """
        self.logger.info(f"Removendo conta bancária: {id_conta}")
        
        # Verificar se a conta bancária existe
        conta = await self.get_conta_bancaria(id_conta, id_empresa)
        
        # Verificar se há lançamentos vinculados
        tem_lancamentos = await self.lancamento_repository.has_by_conta_bancaria(id_conta, id_empresa)
        if tem_lancamentos:
            self.logger.warning(f"Não é possível remover conta bancária com lançamentos: {id_conta}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível remover conta bancária que possui lançamentos vinculados"
            )
            
        # Remover conta bancária
        try:
            resultado = await self.repository.delete(id_conta, id_empresa)
            if not resultado:
                self.logger.warning(f"Conta bancária não encontrada ou já removida: {id_conta}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conta bancária não encontrada"
                )
                
            return {"message": "Conta bancária removida com sucesso", "id": str(id_conta)}
        except Exception as e:
            self.logger.error(f"Erro ao remover conta bancária: {str(e)}")
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao remover conta bancária"
            ) 