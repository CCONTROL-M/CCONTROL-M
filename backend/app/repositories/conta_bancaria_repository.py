"""Repositório para operações com contas bancárias."""
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import date, datetime
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.conta_bancaria import ContaBancaria
from app.models.lancamento import Lancamento
from app.schemas.conta_bancaria import ContaBancariaCreate, ContaBancariaUpdate, AtualizacaoSaldo
from app.repositories.base_repository import BaseRepository


class ContaBancariaRepository(BaseRepository[ContaBancaria, ContaBancariaCreate, ContaBancariaUpdate]):
    """Repositório para operações com contas bancárias."""
    
    def __init__(self, session: AsyncSession):
        """Inicializa o repositório com o modelo ContaBancaria."""
        self.session = session
        super().__init__(ContaBancaria)
    
    async def get_by_id(self, id_conta: UUID, id_empresa: UUID = None) -> Optional[ContaBancaria]:
        """
        Buscar conta bancária pelo ID e empresa.
        
        Args:
            id_conta: ID da conta bancária
            id_empresa: ID da empresa para validação (opcional)
            
        Returns:
            ContaBancaria se encontrada, None caso contrário
        """
        query = select(ContaBancaria).where(ContaBancaria.id_conta == id_conta)
        
        if id_empresa:
            query = query.where(ContaBancaria.id_empresa == id_empresa)
            
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_entity_id(self, id: UUID) -> Optional[ContaBancaria]:
        """
        Obtém uma conta bancária pelo ID.
        
        Args:
            id: ID da conta bancária
            
        Returns:
            ContaBancaria: Conta bancária encontrada ou None
        """
        query = select(ContaBancaria).where(ContaBancaria.id_conta == id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_nome(
        self, 
        nome: str,
        id_empresa: UUID
    ) -> Optional[ContaBancaria]:
        """
        Obtém uma conta bancária pelo nome.
        
        Args:
            nome: Nome da conta bancária
            id_empresa: ID da empresa
            
        Returns:
            ContaBancaria: Conta bancária encontrada ou None
        """
        query = select(ContaBancaria).where(
            ContaBancaria.nome == nome,
            ContaBancaria.id_empresa == id_empresa
        )
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_empresa(
        self, 
        id_empresa: UUID,
        ativa: Optional[bool] = None,
        mostrar_dashboard: Optional[bool] = None
    ) -> List[ContaBancaria]:
        """
        Obtém todas as contas bancárias de uma empresa.
        
        Args:
            id_empresa: ID da empresa
            ativa: Filtrar por status de ativação
            mostrar_dashboard: Filtrar por exibição no dashboard
            
        Returns:
            List[ContaBancaria]: Lista de contas bancárias da empresa
        """
        query = select(ContaBancaria).where(ContaBancaria.id_empresa == id_empresa)
        
        if ativa is not None:
            query = query.where(ContaBancaria.ativa == ativa)
            
        if mostrar_dashboard is not None:
            query = query.where(ContaBancaria.mostrar_dashboard == mostrar_dashboard)
        
        query = query.order_by(ContaBancaria.nome)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_saldo_total(self, id_empresa: UUID) -> float:
        """
        Calcula o saldo total de todas as contas bancárias ativas de uma empresa.
        
        Args:
            id_empresa: ID da empresa
            
        Returns:
            float: Saldo total das contas
        """
        query = select(func.sum(ContaBancaria.saldo_atual)).where(
            ContaBancaria.id_empresa == id_empresa,
            ContaBancaria.ativa == True
        )
        
        result = await self.session.execute(query)
        total = result.scalar_one() or 0
        
        return float(total)
    
    async def get_dashboard_contas(self, id_empresa: UUID) -> Dict[str, Any]:
        """
        Obtém dados para o dashboard de contas bancárias.
        
        Args:
            id_empresa: ID da empresa
            
        Returns:
            Dict[str, Any]: Dados do dashboard
        """
        # Obter contas para exibição no dashboard
        query = select(ContaBancaria).where(
            ContaBancaria.id_empresa == id_empresa,
            ContaBancaria.ativa == True,
            ContaBancaria.mostrar_dashboard == True
        ).order_by(ContaBancaria.nome)
        
        result = await self.session.execute(query)
        contas = list(result.scalars().all())
        
        # Calcular saldo total
        saldo_total = await self.get_saldo_total(id_empresa)
        
        # Calcular lançamentos pendentes para os próximos 30 dias
        hoje = date.today()
        data_limite = hoje.replace(day=hoje.day + 30)
        
        # Lançamentos pendentes de entrada
        entradas_query = select(func.sum(Lancamento.valor)).where(
            Lancamento.id_empresa == id_empresa,
            Lancamento.tipo == "entrada",
            Lancamento.status == "pendente",
            Lancamento.data_vencimento.between(hoje, data_limite)
        )
        
        result = await self.session.execute(entradas_query)
        entradas_pendentes = result.scalar_one() or 0
        
        # Lançamentos pendentes de saída
        saidas_query = select(func.sum(Lancamento.valor)).where(
            Lancamento.id_empresa == id_empresa,
            Lancamento.tipo == "saida",
            Lancamento.status == "pendente",
            Lancamento.data_vencimento.between(hoje, data_limite)
        )
        
        result = await self.session.execute(saidas_query)
        saidas_pendentes = result.scalar_one() or 0
        
        # Contas com maior saldo
        top_contas_query = select(ContaBancaria).where(
            ContaBancaria.id_empresa == id_empresa,
            ContaBancaria.ativa == True
        ).order_by(ContaBancaria.saldo_atual.desc()).limit(5)
        
        result = await self.session.execute(top_contas_query)
        contas_maior_saldo = list(result.scalars().all())
        
        return {
            "saldo_total": float(saldo_total),
            "entradas_pendentes_30dias": float(entradas_pendentes),
            "saidas_pendentes_30dias": float(saidas_pendentes),
            "saldo_projetado_30dias": float(saldo_total + entradas_pendentes - saidas_pendentes),
            "contas_dashboard": contas,
            "contas_maior_saldo": contas_maior_saldo
        }
    
    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        id_empresa: Optional[UUID] = None,
        ativa: Optional[bool] = None,
        mostrar_dashboard: Optional[bool] = None,
        tipo: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ContaBancaria]:
        """
        Obtém múltiplas contas bancárias com paginação e filtragem opcional.
        
        Args:
            skip: Registros para pular
            limit: Limite de registros
            id_empresa: Filtrar por empresa específica
            ativa: Filtrar por status de ativação
            mostrar_dashboard: Filtrar por exibição no dashboard
            tipo: Filtrar por tipo de conta
            filters: Filtros adicionais
            
        Returns:
            List[ContaBancaria]: Lista de contas bancárias
        """
        query = select(ContaBancaria)
        
        # Aplicar filtros principais
        if id_empresa:
            query = query.where(ContaBancaria.id_empresa == id_empresa)
            
        if ativa is not None:
            query = query.where(ContaBancaria.ativa == ativa)
            
        if mostrar_dashboard is not None:
            query = query.where(ContaBancaria.mostrar_dashboard == mostrar_dashboard)
            
        if tipo:
            query = query.where(ContaBancaria.tipo == tipo)
        
        # Filtros adicionais
        if filters:
            # Tratamento especial para busca por nome
            if "nome" in filters and filters["nome"]:
                termo_busca = f"%{filters['nome']}%"
                query = query.where(ContaBancaria.nome.ilike(termo_busca))
                
            # Tratamento para busca por banco
            if "banco" in filters and filters["banco"]:
                termo_busca = f"%{filters['banco']}%"
                query = query.where(ContaBancaria.banco.ilike(termo_busca))
            
            # Processamento dos demais filtros
            for field, value in filters.items():
                if value is not None and hasattr(ContaBancaria, field) and field not in ["nome", "banco"]:
                    query = query.where(getattr(ContaBancaria, field) == value)
        
        # Ordenação padrão por nome
        query = query.order_by(ContaBancaria.nome)
        
        # Aplicar paginação
        query = query.offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_count(
        self,
        id_empresa: Optional[UUID] = None,
        ativa: Optional[bool] = None,
        mostrar_dashboard: Optional[bool] = None,
        tipo: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Obtém a contagem total de contas bancárias com filtros opcionais.
        
        Args:
            id_empresa: Filtrar por empresa específica
            ativa: Filtrar por status de ativação
            mostrar_dashboard: Filtrar por exibição no dashboard
            tipo: Filtrar por tipo de conta
            filters: Filtros adicionais
            
        Returns:
            int: Contagem de contas bancárias
        """
        query = select(func.count()).select_from(ContaBancaria)
        
        # Aplicar filtros principais
        if id_empresa:
            query = query.where(ContaBancaria.id_empresa == id_empresa)
            
        if ativa is not None:
            query = query.where(ContaBancaria.ativa == ativa)
            
        if mostrar_dashboard is not None:
            query = query.where(ContaBancaria.mostrar_dashboard == mostrar_dashboard)
            
        if tipo:
            query = query.where(ContaBancaria.tipo == tipo)
        
        # Filtros adicionais
        if filters:
            # Tratamento especial para busca por nome
            if "nome" in filters and filters["nome"]:
                termo_busca = f"%{filters['nome']}%"
                query = query.where(ContaBancaria.nome.ilike(termo_busca))
                
            # Tratamento para busca por banco
            if "banco" in filters and filters["banco"]:
                termo_busca = f"%{filters['banco']}%"
                query = query.where(ContaBancaria.banco.ilike(termo_busca))
            
            # Processamento dos demais filtros
            for field, value in filters.items():
                if value is not None and hasattr(ContaBancaria, field) and field not in ["nome", "banco"]:
                    query = query.where(getattr(ContaBancaria, field) == value)
        
        result = await self.session.execute(query)
        return result.scalar_one() or 0
    
    async def create(self, data: Dict[str, Any]) -> ContaBancaria:
        """
        Cria uma nova conta bancária.
        
        Args:
            data: Dados da conta bancária
            
        Returns:
            ContaBancaria: Conta bancária criada
            
        Raises:
            HTTPException: Se já existir uma conta com o mesmo nome
        """
        try:
            # Verificar se já existe conta com o mesmo nome
            conta_existente = await self.get_by_nome(data["nome"], data["id_empresa"])
            if conta_existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Já existe uma conta bancária com este nome para esta empresa"
                )
            
            # Criar objeto conta bancária
            db_obj = ContaBancaria(**data)
            
            # Inicializar saldo atual com o saldo inicial
            db_obj.saldo_atual = db_obj.saldo_inicial
            
            self.session.add(db_obj)
            await self.session.commit()
            await self.session.refresh(db_obj)
            
            return db_obj
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao criar conta bancária: {str(e)}"
            )
    
    async def update(self, id_conta: UUID, data: Dict[str, Any], id_empresa: UUID) -> Optional[ContaBancaria]:
        """
        Atualiza uma conta bancária existente.
        
        Args:
            id_conta: ID da conta bancária
            data: Dados para atualização
            id_empresa: ID da empresa para validação
            
        Returns:
            ContaBancaria: Conta bancária atualizada ou None se não encontrada
            
        Raises:
            HTTPException: Se o novo nome já estiver em uso
        """
        try:
            # Primeiro verificar se a conta existe e pertence à empresa
            conta = await self.get_by_id(id_conta, id_empresa)
            if not conta:
                return None
            
            # Guardar valores antigos para verificar mudanças
            saldo_inicial_antigo = conta.saldo_inicial
            
            # Verificar se está alterando o nome e se o novo nome já existe
            data_copy = data.copy()
            
            if "nome" in data_copy and data_copy["nome"] != conta.nome:
                conta_existente = await self.get_by_nome(data_copy["nome"], id_empresa)
                if conta_existente and conta_existente.id_conta != id_conta:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Já existe uma conta bancária com este nome para esta empresa"
                    )
            
            # Se houver mudança no saldo inicial, ajustar o saldo atual
            if "saldo_inicial" in data_copy and data_copy["saldo_inicial"] != saldo_inicial_antigo:
                diferenca = data_copy["saldo_inicial"] - saldo_inicial_antigo
                conta.saldo_atual += diferenca
            
            # Atualizar campos
            for field, value in data_copy.items():
                if hasattr(conta, field):
                    setattr(conta, field, value)
            
            self.session.add(conta)
            await self.session.commit()
            await self.session.refresh(conta)
            
            return conta
        except HTTPException:
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao atualizar conta bancária: {str(e)}"
            )
    
    async def delete(self, id_conta: UUID, id_empresa: UUID) -> bool:
        """
        Remove uma conta bancária.
        
        Args:
            id_conta: ID da conta bancária
            id_empresa: ID da empresa para validação
            
        Returns:
            bool: True se removida com sucesso
            
        Raises:
            HTTPException: Se a conta não for encontrada ou tiver lançamentos associados
        """
        try:
            # Verificar se a conta existe e pertence à empresa
            query = select(ContaBancaria).where(
                ContaBancaria.id_conta == id_conta,
                ContaBancaria.id_empresa == id_empresa
            )
            
            result = await self.session.execute(query)
            conta = result.scalar_one_or_none()
            
            if not conta:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conta bancária não encontrada"
                )
            
            # Verificar se existem lançamentos utilizando esta conta
            query_lancamentos = select(func.count()).select_from(Lancamento).where(
                Lancamento.id_conta == id_conta
            )
            
            result = await self.session.execute(query_lancamentos)
            lancamentos = result.scalar_one() or 0
            
            if lancamentos > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Não é possível excluir esta conta pois ela está sendo utilizada em {lancamentos} lançamento(s)"
                )
            
            await self.session.delete(conta)
            await self.session.commit()
            
            return True
        except HTTPException:
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao excluir conta bancária: {str(e)}"
            )
    
    async def toggle_ativa(self, id_conta: UUID, id_empresa: UUID) -> ContaBancaria:
        """
        Alterna o status de ativação da conta bancária.
        
        Args:
            id_conta: ID da conta bancária
            id_empresa: ID da empresa para validação
            
        Returns:
            ContaBancaria: Conta bancária atualizada
            
        Raises:
            HTTPException: Se a conta bancária não for encontrada
        """
        try:
            # Verificar se a conta existe e pertence à empresa
            query = select(ContaBancaria).where(
                ContaBancaria.id_conta == id_conta,
                ContaBancaria.id_empresa == id_empresa
            )
            
            result = await self.session.execute(query)
            conta = result.scalar_one_or_none()
            
            if not conta:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conta bancária não encontrada"
                )
            
            conta.ativa = not conta.ativa
            
            self.session.add(conta)
            await self.session.commit()
            await self.session.refresh(conta)
            
            return conta
        except HTTPException:
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao alternar status da conta bancária: {str(e)}"
            )
    
    async def toggle_dashboard(self, id_conta: UUID, id_empresa: UUID) -> ContaBancaria:
        """
        Alterna a exibição da conta no dashboard.
        
        Args:
            id_conta: ID da conta bancária
            id_empresa: ID da empresa para validação
            
        Returns:
            ContaBancaria: Conta bancária atualizada
            
        Raises:
            HTTPException: Se a conta bancária não for encontrada
        """
        try:
            # Verificar se a conta existe e pertence à empresa
            query = select(ContaBancaria).where(
                ContaBancaria.id_conta == id_conta,
                ContaBancaria.id_empresa == id_empresa
            )
            
            result = await self.session.execute(query)
            conta = result.scalar_one_or_none()
            
            if not conta:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conta bancária não encontrada"
                )
            
            conta.mostrar_dashboard = not conta.mostrar_dashboard
            
            self.session.add(conta)
            await self.session.commit()
            await self.session.refresh(conta)
            
            return conta
        except HTTPException:
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao alternar exibição no dashboard: {str(e)}"
            )
    
    async def atualizar_saldo(
        self, 
        id_conta: UUID, 
        operacao: AtualizacaoSaldo,
        id_empresa: UUID
    ) -> ContaBancaria:
        """
        Atualiza o saldo de uma conta bancária.
        
        Args:
            id_conta: ID da conta bancária
            operacao: Operação de atualização do saldo
            id_empresa: ID da empresa para validação
            
        Returns:
            ContaBancaria: Conta bancária atualizada
            
        Raises:
            HTTPException: Se a conta bancária não for encontrada
        """
        try:
            # Verificar se a conta existe e pertence à empresa
            query = select(ContaBancaria).where(
                ContaBancaria.id_conta == id_conta,
                ContaBancaria.id_empresa == id_empresa
            )
            
            result = await self.session.execute(query)
            conta = result.scalar_one_or_none()
            
            if not conta:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conta bancária não encontrada"
                )
            
            # Aplicar operação
            if operacao.tipo_operacao == "credito":
                conta.saldo_atual += operacao.valor
            elif operacao.tipo_operacao == "debito":
                if conta.saldo_atual < operacao.valor:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Saldo insuficiente para realizar esta operação"
                    )
                conta.saldo_atual -= operacao.valor
            elif operacao.tipo_operacao == "ajuste":
                conta.saldo_atual = operacao.valor
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Tipo de operação inválido. Use 'credito', 'debito' ou 'ajuste'."
                )
            
            conta.updated_at = datetime.now()
            
            self.session.add(conta)
            await self.session.commit()
            await self.session.refresh(conta)
            
            return conta
        except HTTPException:
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao atualizar saldo: {str(e)}"
            ) 