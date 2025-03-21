"""Repositório para operações com lançamentos financeiros."""
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, select
from fastapi import HTTPException, status

from app.models.lancamento import Lancamento
from app.models.cliente import Cliente
from app.models.conta_bancaria import ContaBancaria
from app.models.forma_pagamento import FormaPagamento
from app.models.parcela import Parcela
from app.schemas.lancamento import LancamentoCreate, LancamentoUpdate, StatusLancamento, TipoLancamento
from app.repositories.base_repository import BaseRepository


class LancamentoRepository(BaseRepository[Lancamento, LancamentoCreate, LancamentoUpdate]):
    """Repositório para operações com lançamentos financeiros."""
    
    def __init__(self):
        """Inicializa o repositório com o modelo Lancamento."""
        super().__init__(Lancamento)
    
    def get(self, db: Session, id: UUID) -> Optional[Lancamento]:
        """
        Obtém um lançamento pelo ID.
        
        Args:
            db: Sessão do banco de dados
            id: ID do lançamento
            
        Returns:
            Lancamento: Lançamento encontrado ou None
        """
        return db.query(Lancamento).filter(Lancamento.id_lancamento == id).first()
    
    def get_with_cliente_form_conta(
        self, 
        db: Session, 
        id: UUID
    ) -> Optional[Lancamento]:
        """
        Obtém um lançamento pelo ID com informações relacionadas de cliente, forma de pagamento e conta.
        
        Args:
            db: Sessão do banco de dados
            id: ID do lançamento
            
        Returns:
            Lancamento: Lançamento encontrado ou None
        """
        return db.query(Lancamento).filter(
            Lancamento.id_lancamento == id
        ).first()
    
    def get_by_empresa(
        self, 
        db: Session, 
        id_empresa: UUID,
        tipo: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Lancamento]:
        """
        Obtém todos os lançamentos de uma empresa.
        
        Args:
            db: Sessão do banco de dados
            id_empresa: ID da empresa
            tipo: Filtro por tipo (entrada/saída)
            status: Filtro por status
            
        Returns:
            List[Lancamento]: Lista de lançamentos da empresa
        """
        query = db.query(Lancamento).filter(Lancamento.id_empresa == id_empresa)
        
        if tipo:
            query = query.filter(Lancamento.tipo == tipo)
            
        if status:
            query = query.filter(Lancamento.status == status)
            
        return query.all()
    
    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        id_empresa: Optional[UUID] = None,
        id_cliente: Optional[UUID] = None,
        id_conta: Optional[UUID] = None,
        id_forma_pagamento: Optional[UUID] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        tipo: Optional[str] = None,
        status: Optional[str] = None,
        conciliado: Optional[bool] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Lancamento]:
        """
        Obtém múltiplos lançamentos com paginação e filtragem opcional.
        
        Args:
            db: Sessão do banco de dados
            skip: Registros para pular
            limit: Limite de registros
            id_empresa: Filtrar por empresa específica
            id_cliente: Filtrar por cliente específico
            id_conta: Filtrar por conta bancária específica
            id_forma_pagamento: Filtrar por forma de pagamento específica
            data_inicio: Data inicial para filtro
            data_fim: Data final para filtro
            tipo: Filtrar por tipo (entrada/saída)
            status: Filtrar por status
            conciliado: Filtrar por status de conciliação
            filters: Filtros adicionais
            
        Returns:
            List[Lancamento]: Lista de lançamentos
        """
        query = db.query(Lancamento)
        
        # Aplicar filtros principais
        if id_empresa:
            query = query.filter(Lancamento.id_empresa == id_empresa)
        
        if id_cliente:
            query = query.filter(Lancamento.id_cliente == id_cliente)
            
        if id_conta:
            query = query.filter(Lancamento.id_conta == id_conta)
            
        if id_forma_pagamento:
            query = query.filter(Lancamento.id_forma_pagamento == id_forma_pagamento)
        
        if tipo:
            query = query.filter(Lancamento.tipo == tipo)
            
        if status:
            query = query.filter(Lancamento.status == status)
            
        if conciliado is not None:
            query = query.filter(Lancamento.conciliado == conciliado)
        
        # Filtro por período de datas
        if data_inicio and data_fim:
            query = query.filter(
                Lancamento.data_vencimento.between(data_inicio, data_fim)
            )
        elif data_inicio:
            query = query.filter(Lancamento.data_vencimento >= data_inicio)
        elif data_fim:
            query = query.filter(Lancamento.data_vencimento <= data_fim)
        
        # Filtros adicionais
        if filters:
            # Tratamento especial para busca por descrição
            if "descricao" in filters and filters["descricao"]:
                termo_busca = f"%{filters['descricao']}%"
                query = query.filter(Lancamento.descricao.ilike(termo_busca))
                del filters["descricao"]  # Remove para não processar novamente
            
            # Processamento dos demais filtros
            for field, value in filters.items():
                if value is not None and hasattr(Lancamento, field):
                    query = query.filter(getattr(Lancamento, field) == value)
        
        # Ordenação padrão por data
        query = query.order_by(Lancamento.data_vencimento.desc())
        
        return query.offset(skip).limit(limit).all()
    
    def get_count(
        self, 
        db: Session, 
        id_empresa: Optional[UUID] = None,
        id_cliente: Optional[UUID] = None,
        id_conta: Optional[UUID] = None,
        id_forma_pagamento: Optional[UUID] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        tipo: Optional[str] = None,
        status: Optional[str] = None,
        conciliado: Optional[bool] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Obtém a contagem total de lançamentos com filtros opcionais.
        
        Args:
            db: Sessão do banco de dados
            id_empresa: Filtrar por empresa específica
            id_cliente: Filtrar por cliente específico
            id_conta: Filtrar por conta bancária específica
            id_forma_pagamento: Filtrar por forma de pagamento específica
            data_inicio: Data inicial para filtro
            data_fim: Data final para filtro
            tipo: Filtrar por tipo (entrada/saída)
            status: Filtrar por status
            conciliado: Filtrar por status de conciliação
            filters: Filtros adicionais
            
        Returns:
            int: Contagem de lançamentos
        """
        query = db.query(Lancamento)
        
        # Aplicar filtros principais
        if id_empresa:
            query = query.filter(Lancamento.id_empresa == id_empresa)
        
        if id_cliente:
            query = query.filter(Lancamento.id_cliente == id_cliente)
            
        if id_conta:
            query = query.filter(Lancamento.id_conta == id_conta)
            
        if id_forma_pagamento:
            query = query.filter(Lancamento.id_forma_pagamento == id_forma_pagamento)
        
        if tipo:
            query = query.filter(Lancamento.tipo == tipo)
            
        if status:
            query = query.filter(Lancamento.status == status)
            
        if conciliado is not None:
            query = query.filter(Lancamento.conciliado == conciliado)
        
        # Filtro por período de datas
        if data_inicio and data_fim:
            query = query.filter(
                Lancamento.data_vencimento.between(data_inicio, data_fim)
            )
        elif data_inicio:
            query = query.filter(Lancamento.data_vencimento >= data_inicio)
        elif data_fim:
            query = query.filter(Lancamento.data_vencimento <= data_fim)
        
        # Filtros adicionais
        if filters:
            # Tratamento especial para busca por descrição
            if "descricao" in filters and filters["descricao"]:
                termo_busca = f"%{filters['descricao']}%"
                query = query.filter(Lancamento.descricao.ilike(termo_busca))
                del filters["descricao"]  # Remove para não processar novamente
            
            # Processamento dos demais filtros
            for field, value in filters.items():
                if value is not None and hasattr(Lancamento, field):
                    query = query.filter(getattr(Lancamento, field) == value)
        
        return query.count()
    
    def get_totais(
        self, 
        db: Session, 
        id_empresa: UUID,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        id_cliente: Optional[UUID] = None,
        id_conta: Optional[UUID] = None
    ) -> Dict[str, float]:
        """
        Calcula os totais de lançamentos para uma empresa.
        
        Args:
            db: Sessão do banco de dados
            id_empresa: ID da empresa
            data_inicio: Data inicial para filtro
            data_fim: Data final para filtro
            id_cliente: Filtrar por cliente específico
            id_conta: Filtrar por conta bancária específica
            
        Returns:
            Dict[str, float]: Dicionário com os totais calculados
        """
        # Filtros base
        filtros = [Lancamento.id_empresa == id_empresa]
        
        # Adicionar filtros opcionais
        if id_cliente:
            filtros.append(Lancamento.id_cliente == id_cliente)
            
        if id_conta:
            filtros.append(Lancamento.id_conta == id_conta)
        
        # Filtro por período de datas
        if data_inicio and data_fim:
            filtros.append(Lancamento.data_vencimento.between(data_inicio, data_fim))
        elif data_inicio:
            filtros.append(Lancamento.data_vencimento >= data_inicio)
        elif data_fim:
            filtros.append(Lancamento.data_vencimento <= data_fim)
        
        # Filtros para diferentes status e tipos
        total_entradas = db.query(func.sum(Lancamento.valor)).filter(
            *filtros, 
            Lancamento.tipo == "entrada",
            Lancamento.status != "cancelado"
        ).scalar() or 0
        
        total_saidas = db.query(func.sum(Lancamento.valor)).filter(
            *filtros, 
            Lancamento.tipo == "saida",
            Lancamento.status != "cancelado"
        ).scalar() or 0
        
        total_pendentes = db.query(func.sum(Lancamento.valor)).filter(
            *filtros, 
            Lancamento.status == "pendente"
        ).scalar() or 0
        
        total_pagos = db.query(func.sum(Lancamento.valor)).filter(
            *filtros, 
            Lancamento.status == "pago"
        ).scalar() or 0
        
        total_cancelados = db.query(func.sum(Lancamento.valor)).filter(
            *filtros, 
            Lancamento.status == "cancelado"
        ).scalar() or 0
        
        return {
            "total_entradas": float(total_entradas),
            "total_saidas": float(total_saidas),
            "saldo": float(total_entradas - total_saidas),
            "total_pendentes": float(total_pendentes),
            "total_pagos": float(total_pagos),
            "total_cancelados": float(total_cancelados)
        }
    
    def create(
        self, 
        db: Session, 
        *, 
        obj_in: LancamentoCreate
    ) -> Lancamento:
        """
        Cria um novo lançamento.
        
        Args:
            db: Sessão do banco de dados
            obj_in: Dados do lançamento
            
        Returns:
            Lancamento: Lançamento criado
            
        Raises:
            HTTPException: Se cliente, conta ou forma de pagamento não existirem
        """
        # Verificar se cliente existe, se fornecido
        if obj_in.id_cliente:
            cliente = db.query(Cliente).filter(
                Cliente.id_cliente == obj_in.id_cliente,
                Cliente.id_empresa == obj_in.id_empresa
            ).first()
            if not cliente:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente não encontrado ou não pertence a esta empresa"
                )
        
        # Verificar se conta bancária existe e pertence à empresa
        conta = db.query(ContaBancaria).filter(
            ContaBancaria.id_conta == obj_in.id_conta,
            ContaBancaria.id_empresa == obj_in.id_empresa
        ).first()
        if not conta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conta bancária não encontrada ou não pertence a esta empresa"
            )
        
        # Verificar se forma de pagamento existe e pertence à empresa
        forma = db.query(FormaPagamento).filter(
            FormaPagamento.id_forma == obj_in.id_forma_pagamento,
            FormaPagamento.id_empresa == obj_in.id_empresa
        ).first()
        if not forma:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Forma de pagamento não encontrada ou não pertence a esta empresa"
            )
        
        # Criar objeto de lançamento
        lancamento_data = obj_in.dict(exclude={"parcelas"} if hasattr(obj_in, "parcelas") else {})
        db_obj = Lancamento(**lancamento_data)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Atualizar saldo da conta se o lançamento estiver pago
        if db_obj.status == "pago":
            self._atualizar_saldo_conta(db, db_obj)
        
        return db_obj
    
    def update(
        self,
        db: Session,
        *,
        db_obj: Lancamento,
        obj_in: LancamentoUpdate
    ) -> Lancamento:
        """
        Atualiza um lançamento existente.
        
        Args:
            db: Sessão do banco de dados
            db_obj: Objeto lançamento existente
            obj_in: Dados para atualizar
            
        Returns:
            Lancamento: Lançamento atualizado
            
        Raises:
            HTTPException: Se cliente, conta ou forma de pagamento não existirem
        """
        # Guardar status e valor antigos para verificar mudanças
        status_antigo = db_obj.status
        conta_antiga_id = db_obj.id_conta
        
        # Verificar se cliente existe, se estiver sendo alterado
        if obj_in.id_cliente is not None and obj_in.id_cliente != db_obj.id_cliente:
            cliente = db.query(Cliente).filter(
                Cliente.id_cliente == obj_in.id_cliente,
                Cliente.id_empresa == db_obj.id_empresa
            ).first()
            if not cliente:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente não encontrado ou não pertence a esta empresa"
                )
        
        # Verificar se conta bancária existe, se estiver sendo alterada
        if obj_in.id_conta is not None and obj_in.id_conta != db_obj.id_conta:
            conta = db.query(ContaBancaria).filter(
                ContaBancaria.id_conta == obj_in.id_conta,
                ContaBancaria.id_empresa == db_obj.id_empresa
            ).first()
            if not conta:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conta bancária não encontrada ou não pertence a esta empresa"
                )
        
        # Verificar se forma de pagamento existe, se estiver sendo alterada
        if obj_in.id_forma_pagamento is not None and obj_in.id_forma_pagamento != db_obj.id_forma_pagamento:
            forma = db.query(FormaPagamento).filter(
                FormaPagamento.id_forma == obj_in.id_forma_pagamento,
                FormaPagamento.id_empresa == db_obj.id_empresa
            ).first()
            if not forma:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Forma de pagamento não encontrada ou não pertence a esta empresa"
                )
        
        # Atualizar os campos
        update_data = obj_in.dict(exclude_unset=True)
        
        # Verificar consistência entre status e data de pagamento
        if "status" in update_data and update_data["status"] == "pago" and not db_obj.data_pagamento:
            if "data_pagamento" not in update_data or not update_data["data_pagamento"]:
                update_data["data_pagamento"] = date.today()
        
        # Para cada campo no dicionário de atualização, definir no objeto do banco
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Atualizar saldo da conta se o status mudou para/de pago ou se a conta mudou
        if (status_antigo != db_obj.status and (status_antigo == "pago" or db_obj.status == "pago")) or \
           (db_obj.status == "pago" and conta_antiga_id != db_obj.id_conta):
            self._atualizar_saldo_conta(db, db_obj, conta_antiga_id if conta_antiga_id != db_obj.id_conta else None)
        
        return db_obj
    
    def remove(self, db: Session, *, id: UUID) -> Lancamento:
        """
        Remove um lançamento.
        
        Args:
            db: Sessão do banco de dados
            id: ID do lançamento
            
        Returns:
            Lancamento: Lançamento removido
            
        Raises:
            HTTPException: Se o lançamento não for encontrado
        """
        lancamento = db.query(Lancamento).filter(Lancamento.id_lancamento == id).first()
        if not lancamento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lançamento não encontrado"
            )
        
        # Se o lançamento estiver pago, estornar o saldo da conta
        if lancamento.status == "pago":
            self._estornar_saldo_conta(db, lancamento)
        
        # Remover parcelas associadas
        db.query(Parcela).filter(Parcela.id_lancamento == id).delete()
        
        db.delete(lancamento)
        db.commit()
        
        return lancamento
    
    def cancelar(self, db: Session, *, lancamento: Lancamento) -> Lancamento:
        """
        Cancela um lançamento.
        
        Args:
            db: Sessão do banco de dados
            lancamento: Objeto do lançamento
            
        Returns:
            Lancamento: Lançamento cancelado
        """
        # Se o lançamento estiver pago, estornar o saldo da conta
        if lancamento.status == "pago":
            self._estornar_saldo_conta(db, lancamento)
        
        # Alterar status para cancelado
        lancamento.status = "cancelado"
        lancamento.updated_at = datetime.now()
        
        # Cancelar parcelas associadas
        parcelas = db.query(Parcela).filter(Parcela.id_lancamento == lancamento.id_lancamento).all()
        for parcela in parcelas:
            parcela.status = "cancelado"
            parcela.updated_at = datetime.now()
            db.add(parcela)
        
        db.add(lancamento)
        db.commit()
        db.refresh(lancamento)
        
        return lancamento
    
    def pagar(
        self, 
        db: Session, 
        *, 
        lancamento: Lancamento, 
        data_pagamento: Optional[date] = None
    ) -> Lancamento:
        """
        Marca um lançamento como pago.
        
        Args:
            db: Sessão do banco de dados
            lancamento: Objeto do lançamento
            data_pagamento: Data de pagamento (opcional, padrão=hoje)
            
        Returns:
            Lancamento: Lançamento pago
        """
        if lancamento.status == "pago":
            return lancamento
        
        if lancamento.status == "cancelado":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível pagar um lançamento cancelado"
            )
        
        # Definir data de pagamento
        lancamento.data_pagamento = data_pagamento or date.today()
        lancamento.status = "pago"
        lancamento.updated_at = datetime.now()
        
        db.add(lancamento)
        db.commit()
        db.refresh(lancamento)
        
        # Atualizar saldo da conta
        self._atualizar_saldo_conta(db, lancamento)
        
        return lancamento
    
    def _atualizar_saldo_conta(
        self, 
        db: Session, 
        lancamento: Lancamento, 
        id_conta_antiga: Optional[UUID] = None
    ) -> None:
        """
        Atualiza o saldo da conta bancária com base no lançamento.
        
        Args:
            db: Sessão do banco de dados
            lancamento: Objeto do lançamento
            id_conta_antiga: ID da conta anterior, se houve mudança de conta
        """
        # Se estava pago e houve mudança de conta, estornar da conta antiga
        if id_conta_antiga:
            conta_antiga = db.query(ContaBancaria).filter(ContaBancaria.id_conta == id_conta_antiga).first()
            if conta_antiga:
                if lancamento.tipo == "entrada":
                    conta_antiga.saldo_atual -= lancamento.valor
                else:
                    conta_antiga.saldo_atual += lancamento.valor
                db.add(conta_antiga)
        
        # Atualizar saldo da conta atual
        conta = db.query(ContaBancaria).filter(ContaBancaria.id_conta == lancamento.id_conta).first()
        if not conta:
            return
        
        # Se foi cancelado, não alterar o saldo
        if lancamento.status == "cancelado":
            return
        
        # Se for pago e entrada, aumentar o saldo
        if lancamento.status == "pago" and lancamento.tipo == "entrada":
            conta.saldo_atual += lancamento.valor
        
        # Se for pago e saída, diminuir o saldo
        if lancamento.status == "pago" and lancamento.tipo == "saida":
            conta.saldo_atual -= lancamento.valor
        
        db.add(conta)
        db.commit()
    
    def _estornar_saldo_conta(self, db: Session, lancamento: Lancamento) -> None:
        """
        Estorna o valor do lançamento do saldo da conta.
        
        Args:
            db: Sessão do banco de dados
            lancamento: Objeto do lançamento
        """
        conta = db.query(ContaBancaria).filter(ContaBancaria.id_conta == lancamento.id_conta).first()
        if not conta:
            return
        
        # Estornar conforme o tipo
        if lancamento.tipo == "entrada":
            conta.saldo_atual -= lancamento.valor
        else:
            conta.saldo_atual += lancamento.valor
        
        db.add(conta)
        db.commit() 