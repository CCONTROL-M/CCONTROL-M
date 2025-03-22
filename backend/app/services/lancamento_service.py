"""Serviço para gerenciamento de lançamentos financeiros no sistema CCONTROL-M."""
from uuid import UUID
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
import logging

from app.schemas.lancamento import LancamentoCreate, LancamentoUpdate, Lancamento, TipoLancamento, StatusLancamento
from app.repositories.lancamento_repository import LancamentoRepository
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.centro_custo_repository import CentroCustoRepository
from app.repositories.cliente_repository import ClienteRepository
from app.repositories.fornecedor_repository import FornecedorRepository
from app.repositories.conta_bancaria_repository import ContaBancariaRepository
from app.repositories.parcela_repository import ParcelaRepository
from app.services.log_sistema_service import LogSistemaService
from app.schemas.log_sistema import LogSistemaCreate
from app.database import get_async_session


class LancamentoService:
    """Serviço para gerenciamento de lançamentos financeiros."""
    
    def __init__(self, 
                 session: AsyncSession = Depends(get_async_session),
                 log_service: LogSistemaService = Depends()):
        """Inicializar serviço com repositórios."""
        self.repository = LancamentoRepository(session)
        self.categoria_repository = CategoriaRepository(session)
        self.centro_custo_repository = CentroCustoRepository(session)
        self.cliente_repository = ClienteRepository(session)
        self.fornecedor_repository = FornecedorRepository(session)
        self.conta_bancaria_repository = ContaBancariaRepository(session)
        self.parcela_repository = ParcelaRepository(session)
        self.log_service = log_service
        self.logger = logging.getLogger(__name__)
        
    async def get_lancamento(self, id_lancamento: UUID, id_empresa: UUID) -> Lancamento:
        """
        Obter lançamento pelo ID.
        
        Args:
            id_lancamento: ID do lançamento
            id_empresa: ID da empresa para validação de acesso
            
        Returns:
            Lançamento encontrado
            
        Raises:
            HTTPException: Se o lançamento não for encontrado
        """
        self.logger.info(f"Buscando lançamento ID: {id_lancamento}")
        
        lancamento = await self.repository.get_by_id(id_lancamento, id_empresa)
        if not lancamento:
            self.logger.warning(f"Lançamento não encontrado: {id_lancamento}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lançamento não encontrado"
            )
        return lancamento
        
    async def listar_lancamentos(
        self,
        id_empresa: UUID,
        skip: int = 0,
        limit: int = 100,
        tipo: Optional[TipoLancamento] = None,
        status: Optional[StatusLancamento] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        id_categoria: Optional[UUID] = None,
        id_centro_custo: Optional[UUID] = None,
        id_cliente: Optional[UUID] = None,
        id_fornecedor: Optional[UUID] = None,
        id_conta_bancaria: Optional[UUID] = None,
        id_parcela: Optional[UUID] = None,
        descricao: Optional[str] = None,
        valor_min: Optional[float] = None,
        valor_max: Optional[float] = None
    ) -> Tuple[List[Lancamento], int]:
        """
        Listar lançamentos com paginação e filtros.
        
        Args:
            id_empresa: ID da empresa
            skip: Número de registros a pular
            limit: Número máximo de registros a retornar
            tipo: Filtrar por tipo de lançamento
            status: Filtrar por status do lançamento
            data_inicio: Filtrar por data inicial
            data_fim: Filtrar por data final
            id_categoria: Filtrar por categoria
            id_centro_custo: Filtrar por centro de custo
            id_cliente: Filtrar por cliente
            id_fornecedor: Filtrar por fornecedor
            id_conta_bancaria: Filtrar por conta bancária
            id_parcela: Filtrar por parcela
            descricao: Filtrar por descrição
            valor_min: Filtrar por valor mínimo
            valor_max: Filtrar por valor máximo
            
        Returns:
            Lista de lançamentos e contagem total
        """
        self.logger.info(f"Buscando lançamentos com filtros: empresa={id_empresa}, tipo={tipo}, status={status}")
        
        filters = [{"id_empresa": id_empresa}]
        
        if tipo:
            filters.append({"tipo": tipo})
            
        if status:
            filters.append({"status": status})
            
        if data_inicio:
            filters.append({"data_lancamento__gte": data_inicio})
            
        if data_fim:
            filters.append({"data_lancamento__lte": data_fim})
            
        if id_categoria:
            filters.append({"id_categoria": id_categoria})
            
        if id_centro_custo:
            filters.append({"id_centro_custo": id_centro_custo})
            
        if id_cliente:
            filters.append({"id_cliente": id_cliente})
            
        if id_fornecedor:
            filters.append({"id_fornecedor": id_fornecedor})
            
        if id_conta_bancaria:
            filters.append({"id_conta_bancaria": id_conta_bancaria})
            
        if id_parcela:
            filters.append({"id_parcela": id_parcela})
            
        if descricao:
            filters.append({"descricao__ilike": f"%{descricao}%"})
            
        if valor_min is not None:
            filters.append({"valor__gte": valor_min})
            
        if valor_max is not None:
            filters.append({"valor__lte": valor_max})
            
        return await self.repository.list_with_filters(
            skip=skip,
            limit=limit,
            filters=filters
        )
        
    async def criar_lancamento(self, lancamento: LancamentoCreate, id_usuario: UUID) -> Lancamento:
        """
        Criar novo lançamento.
        
        Args:
            lancamento: Dados do lançamento a ser criado
            id_usuario: ID do usuário que está criando o lançamento
            
        Returns:
            Lançamento criado
            
        Raises:
            HTTPException: Se ocorrer um erro na validação
        """
        self.logger.info(f"Criando novo lançamento para empresa: {lancamento.id_empresa}")
        
        # Validar valor
        if lancamento.valor <= 0:
            self.logger.warning(f"Valor inválido: {lancamento.valor}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valor deve ser maior que zero"
            )
            
        # Validar categoria
        if lancamento.id_categoria:
            categoria = await self.categoria_repository.get_by_id(lancamento.id_categoria, lancamento.id_empresa)
            if not categoria:
                self.logger.warning(f"Categoria não encontrada: {lancamento.id_categoria}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Categoria não encontrada"
                )
                
            # Validar tipo de categoria conforme o tipo de lançamento
            if lancamento.tipo == TipoLancamento.RECEITA and categoria.tipo != "RECEITA":
                self.logger.warning(f"Categoria incompatível com o tipo do lançamento: {categoria.tipo}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Para lançamentos do tipo RECEITA, a categoria também deve ser do tipo RECEITA"
                )
                
            if lancamento.tipo == TipoLancamento.DESPESA and categoria.tipo != "DESPESA":
                self.logger.warning(f"Categoria incompatível com o tipo do lançamento: {categoria.tipo}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Para lançamentos do tipo DESPESA, a categoria também deve ser do tipo DESPESA"
                )
                
        # Validar centro de custo
        if lancamento.id_centro_custo:
            centro_custo = await self.centro_custo_repository.get_by_id(lancamento.id_centro_custo, lancamento.id_empresa)
            if not centro_custo:
                self.logger.warning(f"Centro de custo não encontrado: {lancamento.id_centro_custo}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Centro de custo não encontrado"
                )
                
        # Validar cliente
        if lancamento.id_cliente:
            cliente = await self.cliente_repository.get_by_id(lancamento.id_cliente, lancamento.id_empresa)
            if not cliente:
                self.logger.warning(f"Cliente não encontrado: {lancamento.id_cliente}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cliente não encontrado"
                )
                
        # Validar fornecedor
        if lancamento.id_fornecedor:
            fornecedor = await self.fornecedor_repository.get_by_id(lancamento.id_fornecedor, lancamento.id_empresa)
            if not fornecedor:
                self.logger.warning(f"Fornecedor não encontrado: {lancamento.id_fornecedor}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Fornecedor não encontrado"
                )
                
        # Validar conta bancária
        if lancamento.id_conta_bancaria:
            conta = await self.conta_bancaria_repository.get_by_id(lancamento.id_conta_bancaria, lancamento.id_empresa)
            if not conta:
                self.logger.warning(f"Conta bancária não encontrada: {lancamento.id_conta_bancaria}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Conta bancária não encontrada"
                )
                
        # Validar parcela
        if lancamento.id_parcela:
            parcela = await self.parcela_repository.get_by_id(lancamento.id_parcela, lancamento.id_empresa)
            if not parcela:
                self.logger.warning(f"Parcela não encontrada: {lancamento.id_parcela}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parcela não encontrada"
                )
                
        # Criar lançamento
        try:
            lancamento_data = lancamento.model_dump()
            
            # Adicionar data atual se não fornecida
            if "data_lancamento" not in lancamento_data or lancamento_data["data_lancamento"] is None:
                lancamento_data["data_lancamento"] = datetime.now().date()
                
            # Definir status padrão se não fornecido
            if "status" not in lancamento_data or lancamento_data["status"] is None:
                lancamento_data["status"] = StatusLancamento.PENDENTE
                
            novo_lancamento = await self.repository.create(lancamento_data)
            
            # Registrar log
            await self.log_service.registrar_log(
                LogSistemaCreate(
                    id_empresa=lancamento.id_empresa,
                    id_usuario=id_usuario,
                    acao="criar_lancamento",
                    descricao=f"Lançamento criado com ID {novo_lancamento.id_lancamento}",
                    dados={
                        "id_lancamento": str(novo_lancamento.id_lancamento), 
                        "tipo": novo_lancamento.tipo.value,
                        "valor": float(novo_lancamento.valor)
                    }
                )
            )
            
            return novo_lancamento
        except Exception as e:
            self.logger.error(f"Erro ao criar lançamento: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao criar lançamento"
            )
        
    async def atualizar_lancamento(self, id_lancamento: UUID, lancamento: LancamentoUpdate, id_empresa: UUID, id_usuario: UUID) -> Lancamento:
        """
        Atualizar lançamento existente.
        
        Args:
            id_lancamento: ID do lançamento a ser atualizado
            lancamento: Dados para atualização
            id_empresa: ID da empresa para validação de acesso
            id_usuario: ID do usuário que está atualizando o lançamento
            
        Returns:
            Lançamento atualizado
            
        Raises:
            HTTPException: Se o lançamento não for encontrado ou ocorrer erro na validação
        """
        self.logger.info(f"Atualizando lançamento: {id_lancamento}")
        
        # Verificar se o lançamento existe
        lancamento_atual = await self.get_lancamento(id_lancamento, id_empresa)
        
        # Validações de atualização
        
        # Não permitir alterar tipo de lançamento já efetivado
        if lancamento.tipo and lancamento.tipo != lancamento_atual.tipo and lancamento_atual.status == StatusLancamento.EFETIVADO:
            self.logger.warning(f"Não é possível alterar o tipo de um lançamento efetivado: {id_lancamento}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível alterar o tipo de um lançamento efetivado"
            )
            
        # Validar valor se estiver sendo atualizado
        if lancamento.valor is not None and lancamento.valor <= 0:
            self.logger.warning(f"Valor inválido: {lancamento.valor}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valor deve ser maior que zero"
            )
            
        # Validar categoria se estiver sendo atualizada
        if lancamento.id_categoria:
            categoria = await self.categoria_repository.get_by_id(lancamento.id_categoria, id_empresa)
            if not categoria:
                self.logger.warning(f"Categoria não encontrada: {lancamento.id_categoria}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Categoria não encontrada"
                )
                
            # Definir o tipo de lançamento para validar com a categoria
            tipo_lancamento = lancamento.tipo if lancamento.tipo else lancamento_atual.tipo
                
            # Validar tipo de categoria conforme o tipo de lançamento
            if tipo_lancamento == TipoLancamento.RECEITA and categoria.tipo != "RECEITA":
                self.logger.warning(f"Categoria incompatível com o tipo do lançamento: {categoria.tipo}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Para lançamentos do tipo RECEITA, a categoria também deve ser do tipo RECEITA"
                )
                
            if tipo_lancamento == TipoLancamento.DESPESA and categoria.tipo != "DESPESA":
                self.logger.warning(f"Categoria incompatível com o tipo do lançamento: {categoria.tipo}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Para lançamentos do tipo DESPESA, a categoria também deve ser do tipo DESPESA"
                )
                
        # Demais validações seguem o mesmo padrão do método criar_lancamento
        
        # Validar centro de custo
        if lancamento.id_centro_custo:
            centro_custo = await self.centro_custo_repository.get_by_id(lancamento.id_centro_custo, id_empresa)
            if not centro_custo:
                self.logger.warning(f"Centro de custo não encontrado: {lancamento.id_centro_custo}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Centro de custo não encontrado"
                )
                
        # Validar cliente
        if lancamento.id_cliente:
            cliente = await self.cliente_repository.get_by_id(lancamento.id_cliente, id_empresa)
            if not cliente:
                self.logger.warning(f"Cliente não encontrado: {lancamento.id_cliente}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cliente não encontrado"
                )
                
        # Validar fornecedor
        if lancamento.id_fornecedor:
            fornecedor = await self.fornecedor_repository.get_by_id(lancamento.id_fornecedor, id_empresa)
            if not fornecedor:
                self.logger.warning(f"Fornecedor não encontrado: {lancamento.id_fornecedor}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Fornecedor não encontrado"
                )
                
        # Validar conta bancária
        if lancamento.id_conta_bancaria:
            conta = await self.conta_bancaria_repository.get_by_id(lancamento.id_conta_bancaria, id_empresa)
            if not conta:
                self.logger.warning(f"Conta bancária não encontrada: {lancamento.id_conta_bancaria}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Conta bancária não encontrada"
                )
                
        # Validar parcela
        if lancamento.id_parcela:
            parcela = await self.parcela_repository.get_by_id(lancamento.id_parcela, id_empresa)
            if not parcela:
                self.logger.warning(f"Parcela não encontrada: {lancamento.id_parcela}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parcela não encontrada"
                )
                
        # Atualizar lançamento
        try:
            # Remover campos None do modelo de atualização
            update_data = {k: v for k, v in lancamento.model_dump().items() if v is not None}
            
            lancamento_atualizado = await self.repository.update(id_lancamento, update_data, id_empresa)
            
            if not lancamento_atualizado:
                self.logger.warning(f"Lançamento não encontrado após tentativa de atualização: {id_lancamento}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Lançamento não encontrado"
                )
                
            # Registrar log
            await self.log_service.registrar_log(
                LogSistemaCreate(
                    id_empresa=id_empresa,
                    id_usuario=id_usuario,
                    acao="atualizar_lancamento",
                    descricao=f"Lançamento atualizado com ID {id_lancamento}",
                    dados={"id_lancamento": str(id_lancamento), "atualizacoes": update_data}
                )
            )
            
            return lancamento_atualizado
        except Exception as e:
            self.logger.error(f"Erro ao atualizar lançamento: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao atualizar lançamento"
            )
            
    async def efetivar_lancamento(self, id_lancamento: UUID, id_empresa: UUID, id_usuario: UUID, data_efetivacao: Optional[date] = None) -> Lancamento:
        """
        Efetivar um lançamento.
        
        Args:
            id_lancamento: ID do lançamento a ser efetivado
            id_empresa: ID da empresa para validação de acesso
            id_usuario: ID do usuário que está efetivando o lançamento
            data_efetivacao: Data da efetivação (padrão: data atual)
            
        Returns:
            Lançamento efetivado
            
        Raises:
            HTTPException: Se o lançamento não for encontrado ou já estiver efetivado
        """
        self.logger.info(f"Efetivando lançamento: {id_lancamento}")
        
        # Verificar se o lançamento existe
        lancamento = await self.get_lancamento(id_lancamento, id_empresa)
        
        # Verificar se já está efetivado
        if lancamento.status == StatusLancamento.EFETIVADO:
            self.logger.warning(f"Lançamento já está efetivado: {id_lancamento}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Lançamento já está efetivado"
            )
            
        # Verificar se está cancelado
        if lancamento.status == StatusLancamento.CANCELADO:
            self.logger.warning(f"Não é possível efetivar um lançamento cancelado: {id_lancamento}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível efetivar um lançamento cancelado"
            )
            
        # Verificar se tem conta bancária associada
        if not lancamento.id_conta_bancaria:
            self.logger.warning(f"Lançamento sem conta bancária associada: {id_lancamento}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="É necessário associar uma conta bancária para efetivar o lançamento"
            )
            
        # Atualizar lançamento como efetivado
        update_data = {
            "status": StatusLancamento.EFETIVADO,
            "data_efetivacao": data_efetivacao or datetime.now().date()
        }
        
        lancamento_efetivado = await self.repository.update(id_lancamento, update_data, id_empresa)
        
        # Atualizar saldo da conta bancária
        # Nota: Em um sistema real, isso provavelmente seria feito em uma transação
        # para garantir a consistência dos dados
        # Aqui estamos apenas simulando
        
        # Registrar log
        await self.log_service.registrar_log(
            LogSistemaCreate(
                id_empresa=id_empresa,
                id_usuario=id_usuario,
                acao="efetivar_lancamento",
                descricao=f"Lançamento efetivado com ID {id_lancamento}",
                dados={
                    "id_lancamento": str(id_lancamento),
                    "data_efetivacao": str(update_data["data_efetivacao"]),
                    "valor": float(lancamento.valor),
                    "tipo": lancamento.tipo.value
                }
            )
        )
        
        return lancamento_efetivado
        
    async def cancelar_lancamento(self, id_lancamento: UUID, id_empresa: UUID, id_usuario: UUID, motivo: str) -> Lancamento:
        """
        Cancelar um lançamento.
        
        Args:
            id_lancamento: ID do lançamento a ser cancelado
            id_empresa: ID da empresa para validação de acesso
            id_usuario: ID do usuário que está cancelando o lançamento
            motivo: Motivo do cancelamento
            
        Returns:
            Lançamento cancelado
            
        Raises:
            HTTPException: Se o lançamento não for encontrado ou já estiver cancelado
        """
        self.logger.info(f"Cancelando lançamento: {id_lancamento}")
        
        # Verificar se o lançamento existe
        lancamento = await self.get_lancamento(id_lancamento, id_empresa)
        
        # Verificar se já está cancelado
        if lancamento.status == StatusLancamento.CANCELADO:
            self.logger.warning(f"Lançamento já está cancelado: {id_lancamento}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Lançamento já está cancelado"
            )
            
        # Se já foi efetivado, será necessário reverter o saldo da conta
        if lancamento.status == StatusLancamento.EFETIVADO:
            self.logger.warning(f"Cancelando lançamento já efetivado: {id_lancamento}")
            # Nota: Em um sistema real, isso provavelmente seria feito em uma transação
            # para garantir a consistência dos dados
            # Aqui estamos apenas simulando
            
        # Cancelar lançamento
        update_data = {
            "status": StatusLancamento.CANCELADO,
            "observacoes": f"CANCELADO: {motivo}" if not lancamento.observacoes else f"{lancamento.observacoes}\nCANCELADO: {motivo}"
        }
        
        lancamento_cancelado = await self.repository.update(id_lancamento, update_data, id_empresa)
        
        # Registrar log
        await self.log_service.registrar_log(
            LogSistemaCreate(
                id_empresa=id_empresa,
                id_usuario=id_usuario,
                acao="cancelar_lancamento",
                descricao=f"Lançamento cancelado com ID {id_lancamento}",
                dados={
                    "id_lancamento": str(id_lancamento),
                    "motivo": motivo,
                    "valor": float(lancamento.valor),
                    "tipo": lancamento.tipo.value
                }
            )
        )
        
        return lancamento_cancelado
        
    async def remover_lancamento(self, id_lancamento: UUID, id_empresa: UUID, id_usuario: UUID) -> Dict[str, Any]:
        """
        Remover lançamento pelo ID.
        
        Args:
            id_lancamento: ID do lançamento a ser removido
            id_empresa: ID da empresa para validação de acesso
            id_usuario: ID do usuário que está removendo o lançamento
            
        Returns:
            Mensagem de confirmação
            
        Raises:
            HTTPException: Se o lançamento não for encontrado ou não puder ser removido
        """
        self.logger.info(f"Removendo lançamento: {id_lancamento}")
        
        # Verificar se o lançamento existe
        lancamento = await self.get_lancamento(id_lancamento, id_empresa)
        
        # Verificar status
        if lancamento.status == StatusLancamento.EFETIVADO:
            self.logger.warning(f"Não é possível remover um lançamento efetivado: {id_lancamento}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível remover um lançamento efetivado. Cancele-o primeiro."
            )
            
        # Remover lançamento
        await self.repository.delete(id_lancamento, id_empresa)
        
        # Registrar log
        await self.log_service.registrar_log(
            LogSistemaCreate(
                id_empresa=id_empresa,
                id_usuario=id_usuario,
                acao="remover_lancamento",
                descricao=f"Lançamento removido com ID {id_lancamento}",
                dados={"id_lancamento": str(id_lancamento)}
            )
        )
        
        return {"detail": "Lançamento removido com sucesso"} 