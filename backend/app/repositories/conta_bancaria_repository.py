"""Repositório para operações com contas bancárias."""
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from fastapi import HTTPException, status

from app.models.conta_bancaria import ContaBancaria
from app.models.lancamento import Lancamento
from app.schemas.conta_bancaria import ContaBancariaCreate, ContaBancariaUpdate, AtualizacaoSaldo
from app.repositories.base_repository import BaseRepository


class ContaBancariaRepository(BaseRepository[ContaBancaria, ContaBancariaCreate, ContaBancariaUpdate]):
    """Repositório para operações com contas bancárias."""
    
    def __init__(self):
        """Inicializa o repositório com o modelo ContaBancaria."""
        super().__init__(ContaBancaria)
    
    def get(self, db: Session, id: UUID) -> Optional[ContaBancaria]:
        """
        Obtém uma conta bancária pelo ID.
        
        Args:
            db: Sessão do banco de dados
            id: ID da conta bancária
            
        Returns:
            ContaBancaria: Conta bancária encontrada ou None
        """
        return db.query(ContaBancaria).filter(ContaBancaria.id_conta == id).first()
    
    def get_by_nome(
        self, 
        db: Session, 
        nome: str,
        id_empresa: UUID
    ) -> Optional[ContaBancaria]:
        """
        Obtém uma conta bancária pelo nome.
        
        Args:
            db: Sessão do banco de dados
            nome: Nome da conta bancária
            id_empresa: ID da empresa
            
        Returns:
            ContaBancaria: Conta bancária encontrada ou None
        """
        return db.query(ContaBancaria).filter(
            ContaBancaria.nome == nome,
            ContaBancaria.id_empresa == id_empresa
        ).first()
    
    def get_by_empresa(
        self, 
        db: Session, 
        id_empresa: UUID,
        ativa: Optional[bool] = None,
        mostrar_dashboard: Optional[bool] = None
    ) -> List[ContaBancaria]:
        """
        Obtém todas as contas bancárias de uma empresa.
        
        Args:
            db: Sessão do banco de dados
            id_empresa: ID da empresa
            ativa: Filtrar por status de ativação
            mostrar_dashboard: Filtrar por exibição no dashboard
            
        Returns:
            List[ContaBancaria]: Lista de contas bancárias da empresa
        """
        query = db.query(ContaBancaria).filter(ContaBancaria.id_empresa == id_empresa)
        
        if ativa is not None:
            query = query.filter(ContaBancaria.ativa == ativa)
            
        if mostrar_dashboard is not None:
            query = query.filter(ContaBancaria.mostrar_dashboard == mostrar_dashboard)
            
        return query.order_by(ContaBancaria.nome).all()
    
    def get_saldo_total(self, db: Session, id_empresa: UUID) -> float:
        """
        Calcula o saldo total de todas as contas bancárias ativas de uma empresa.
        
        Args:
            db: Sessão do banco de dados
            id_empresa: ID da empresa
            
        Returns:
            float: Saldo total das contas
        """
        total = db.query(func.sum(ContaBancaria.saldo_atual)).filter(
            ContaBancaria.id_empresa == id_empresa,
            ContaBancaria.ativa == True
        ).scalar() or 0
        
        return float(total)
    
    def get_dashboard_contas(self, db: Session, id_empresa: UUID) -> Dict[str, Any]:
        """
        Obtém dados para o dashboard de contas bancárias.
        
        Args:
            db: Sessão do banco de dados
            id_empresa: ID da empresa
            
        Returns:
            Dict[str, Any]: Dados do dashboard
        """
        # Obter contas para exibição no dashboard
        contas = db.query(ContaBancaria).filter(
            ContaBancaria.id_empresa == id_empresa,
            ContaBancaria.ativa == True,
            ContaBancaria.mostrar_dashboard == True
        ).order_by(ContaBancaria.nome).all()
        
        # Calcular saldo total
        saldo_total = self.get_saldo_total(db, id_empresa)
        
        # Calcular lançamentos pendentes para os próximos 30 dias
        hoje = date.today()
        data_limite = hoje.replace(day=hoje.day + 30)
        
        # Lançamentos pendentes de entrada
        entradas_pendentes = db.query(func.sum(Lancamento.valor)).filter(
            Lancamento.id_empresa == id_empresa,
            Lancamento.tipo == "entrada",
            Lancamento.status == "pendente",
            Lancamento.data_vencimento.between(hoje, data_limite)
        ).scalar() or 0
        
        # Lançamentos pendentes de saída
        saidas_pendentes = db.query(func.sum(Lancamento.valor)).filter(
            Lancamento.id_empresa == id_empresa,
            Lancamento.tipo == "saida",
            Lancamento.status == "pendente",
            Lancamento.data_vencimento.between(hoje, data_limite)
        ).scalar() or 0
        
        # Contas com maior saldo
        contas_maior_saldo = db.query(ContaBancaria).filter(
            ContaBancaria.id_empresa == id_empresa,
            ContaBancaria.ativa == True
        ).order_by(ContaBancaria.saldo_atual.desc()).limit(5).all()
        
        return {
            "saldo_total": float(saldo_total),
            "entradas_pendentes_30dias": float(entradas_pendentes),
            "saidas_pendentes_30dias": float(saidas_pendentes),
            "saldo_projetado_30dias": float(saldo_total + entradas_pendentes - saidas_pendentes),
            "contas_dashboard": contas,
            "contas_maior_saldo": contas_maior_saldo
        }
    
    def get_multi(
        self,
        db: Session,
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
            db: Sessão do banco de dados
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
        query = db.query(ContaBancaria)
        
        # Aplicar filtros principais
        if id_empresa:
            query = query.filter(ContaBancaria.id_empresa == id_empresa)
            
        if ativa is not None:
            query = query.filter(ContaBancaria.ativa == ativa)
            
        if mostrar_dashboard is not None:
            query = query.filter(ContaBancaria.mostrar_dashboard == mostrar_dashboard)
            
        if tipo:
            query = query.filter(ContaBancaria.tipo == tipo)
        
        # Filtros adicionais
        if filters:
            # Tratamento especial para busca por nome
            if "nome" in filters and filters["nome"]:
                termo_busca = f"%{filters['nome']}%"
                query = query.filter(ContaBancaria.nome.ilike(termo_busca))
                del filters["nome"]  # Remove para não processar novamente
                
            # Tratamento para busca por banco
            if "banco" in filters and filters["banco"]:
                termo_busca = f"%{filters['banco']}%"
                query = query.filter(ContaBancaria.banco.ilike(termo_busca))
                del filters["banco"]  # Remove para não processar novamente
            
            # Processamento dos demais filtros
            for field, value in filters.items():
                if value is not None and hasattr(ContaBancaria, field):
                    query = query.filter(getattr(ContaBancaria, field) == value)
        
        # Ordenação padrão por nome
        query = query.order_by(ContaBancaria.nome)
        
        return query.offset(skip).limit(limit).all()
    
    def get_count(
        self, 
        db: Session, 
        id_empresa: Optional[UUID] = None,
        ativa: Optional[bool] = None,
        mostrar_dashboard: Optional[bool] = None,
        tipo: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Obtém a contagem total de contas bancárias com filtros opcionais.
        
        Args:
            db: Sessão do banco de dados
            id_empresa: Filtrar por empresa específica
            ativa: Filtrar por status de ativação
            mostrar_dashboard: Filtrar por exibição no dashboard
            tipo: Filtrar por tipo de conta
            filters: Filtros adicionais
            
        Returns:
            int: Contagem de contas bancárias
        """
        query = db.query(ContaBancaria)
        
        # Aplicar filtros principais
        if id_empresa:
            query = query.filter(ContaBancaria.id_empresa == id_empresa)
            
        if ativa is not None:
            query = query.filter(ContaBancaria.ativa == ativa)
            
        if mostrar_dashboard is not None:
            query = query.filter(ContaBancaria.mostrar_dashboard == mostrar_dashboard)
            
        if tipo:
            query = query.filter(ContaBancaria.tipo == tipo)
        
        # Filtros adicionais
        if filters:
            # Tratamento especial para busca por nome
            if "nome" in filters and filters["nome"]:
                termo_busca = f"%{filters['nome']}%"
                query = query.filter(ContaBancaria.nome.ilike(termo_busca))
                del filters["nome"]  # Remove para não processar novamente
                
            # Tratamento para busca por banco
            if "banco" in filters and filters["banco"]:
                termo_busca = f"%{filters['banco']}%"
                query = query.filter(ContaBancaria.banco.ilike(termo_busca))
                del filters["banco"]  # Remove para não processar novamente
            
            # Processamento dos demais filtros
            for field, value in filters.items():
                if value is not None and hasattr(ContaBancaria, field):
                    query = query.filter(getattr(ContaBancaria, field) == value)
        
        return query.count()
    
    def create(
        self, 
        db: Session, 
        *, 
        obj_in: ContaBancariaCreate
    ) -> ContaBancaria:
        """
        Cria uma nova conta bancária.
        
        Args:
            db: Sessão do banco de dados
            obj_in: Dados da conta bancária
            
        Returns:
            ContaBancaria: Conta bancária criada
            
        Raises:
            HTTPException: Se já existir uma conta com o mesmo nome
        """
        # Verificar se já existe conta com o mesmo nome
        conta_existente = self.get_by_nome(db, obj_in.nome, obj_in.id_empresa)
        if conta_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe uma conta bancária com este nome para esta empresa"
            )
        
        # Criar objeto conta bancária
        db_obj = ContaBancaria(**obj_in.dict())
        
        # Inicializar saldo atual com o saldo inicial
        db_obj.saldo_atual = db_obj.saldo_inicial
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj
    
    def update(
        self,
        db: Session,
        *,
        db_obj: ContaBancaria,
        obj_in: ContaBancariaUpdate
    ) -> ContaBancaria:
        """
        Atualiza uma conta bancária existente.
        
        Args:
            db: Sessão do banco de dados
            db_obj: Objeto conta bancária existente
            obj_in: Dados para atualizar
            
        Returns:
            ContaBancaria: Conta bancária atualizada
            
        Raises:
            HTTPException: Se o novo nome já estiver em uso
        """
        # Guardar valores antigos para verificar mudanças
        saldo_inicial_antigo = db_obj.saldo_inicial
        
        # Verificar se está alterando o nome e se o novo nome já existe
        update_data = obj_in.dict(exclude_unset=True)
        
        if "nome" in update_data and update_data["nome"] != db_obj.nome:
            conta_existente = self.get_by_nome(db, update_data["nome"], db_obj.id_empresa)
            if conta_existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Já existe uma conta bancária com este nome para esta empresa"
                )
        
        # Se houver mudança no saldo inicial, ajustar o saldo atual
        if "saldo_inicial" in update_data and update_data["saldo_inicial"] != saldo_inicial_antigo:
            diferenca = update_data["saldo_inicial"] - saldo_inicial_antigo
            db_obj.saldo_atual += diferenca
        
        # Atualizar campos
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj
    
    def remove(self, db: Session, *, id: UUID) -> ContaBancaria:
        """
        Remove uma conta bancária.
        
        Args:
            db: Sessão do banco de dados
            id: ID da conta bancária
            
        Returns:
            ContaBancaria: Conta bancária removida
            
        Raises:
            HTTPException: Se a conta não for encontrada ou tiver lançamentos associados
        """
        conta = db.query(ContaBancaria).filter(ContaBancaria.id_conta == id).first()
        if not conta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conta bancária não encontrada"
            )
        
        # Verificar se existem lançamentos utilizando esta conta
        lancamentos = db.query(Lancamento).filter(
            Lancamento.id_conta == id
        ).count()
        
        if lancamentos > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Não é possível excluir esta conta pois ela está sendo utilizada em {lancamentos} lançamento(s)"
            )
        
        db.delete(conta)
        db.commit()
        
        return conta
    
    def toggle_ativa(self, db: Session, *, id: UUID) -> ContaBancaria:
        """
        Alterna o status de ativação da conta bancária.
        
        Args:
            db: Sessão do banco de dados
            id: ID da conta bancária
            
        Returns:
            ContaBancaria: Conta bancária atualizada
            
        Raises:
            HTTPException: Se a conta bancária não for encontrada
        """
        conta = db.query(ContaBancaria).filter(ContaBancaria.id_conta == id).first()
        if not conta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conta bancária não encontrada"
            )
        
        conta.ativa = not conta.ativa
        
        db.add(conta)
        db.commit()
        db.refresh(conta)
        
        return conta
    
    def toggle_dashboard(self, db: Session, *, id: UUID) -> ContaBancaria:
        """
        Alterna a exibição da conta no dashboard.
        
        Args:
            db: Sessão do banco de dados
            id: ID da conta bancária
            
        Returns:
            ContaBancaria: Conta bancária atualizada
            
        Raises:
            HTTPException: Se a conta bancária não for encontrada
        """
        conta = db.query(ContaBancaria).filter(ContaBancaria.id_conta == id).first()
        if not conta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conta bancária não encontrada"
            )
        
        conta.mostrar_dashboard = not conta.mostrar_dashboard
        
        db.add(conta)
        db.commit()
        db.refresh(conta)
        
        return conta
    
    def atualizar_saldo(
        self, 
        db: Session, 
        *, 
        id: UUID, 
        operacao: AtualizacaoSaldo
    ) -> ContaBancaria:
        """
        Atualiza o saldo de uma conta bancária.
        
        Args:
            db: Sessão do banco de dados
            id: ID da conta bancária
            operacao: Operação de atualização do saldo
            
        Returns:
            ContaBancaria: Conta bancária atualizada
            
        Raises:
            HTTPException: Se a conta bancária não for encontrada
        """
        conta = db.query(ContaBancaria).filter(ContaBancaria.id_conta == id).first()
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
        
        db.add(conta)
        db.commit()
        db.refresh(conta)
        
        return conta 