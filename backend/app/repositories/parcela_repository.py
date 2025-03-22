"""Repositório para operações com parcelas de lançamentos."""
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, select
from fastapi import HTTPException, status

from app.models.parcela import Parcela, ParcelaCompra, ParcelaVenda
from app.models.lancamento import Lancamento
from app.models.cliente import Cliente
from app.schemas.parcela import ParcelaCreate, ParcelaUpdate, StatusParcela
from app.repositories.base_repository import BaseRepository


class ParcelaRepository(BaseRepository[Parcela, ParcelaCreate, ParcelaUpdate]):
    """Repositório para operações com parcelas de lançamentos."""
    
    def __init__(self):
        """Inicializa o repositório com o modelo Parcela."""
        super().__init__(Parcela)
    
    def get(self, db: Session, id: UUID) -> Optional[Parcela]:
        """
        Obtém uma parcela pelo ID.
        
        Args:
            db: Sessão do banco de dados
            id: ID da parcela
            
        Returns:
            Parcela: Parcela encontrada ou None
        """
        return db.query(Parcela).filter(Parcela.id_parcela == id).first()
    
    def get_by_lancamento(
        self, 
        db: Session, 
        id_lancamento: UUID,
        status: Optional[str] = None
    ) -> List[Parcela]:
        """
        Obtém parcelas de um lançamento específico.
        
        Args:
            db: Sessão do banco de dados
            id_lancamento: ID do lançamento
            status: Filtro por status
            
        Returns:
            List[Parcela]: Lista de parcelas do lançamento
        """
        query = db.query(Parcela).filter(Parcela.id_lancamento == id_lancamento)
        
        if status:
            query = query.filter(Parcela.status == status)
            
        return query.order_by(Parcela.numero).all()
    
    def get_by_empresa(
        self, 
        db: Session, 
        id_empresa: UUID,
        status: Optional[str] = None
    ) -> List[Parcela]:
        """
        Obtém todas as parcelas de uma empresa.
        
        Args:
            db: Sessão do banco de dados
            id_empresa: ID da empresa
            status: Filtro por status
            
        Returns:
            List[Parcela]: Lista de parcelas da empresa
        """
        query = db.query(Parcela).join(Lancamento).filter(Lancamento.id_empresa == id_empresa)
        
        if status:
            query = query.filter(Parcela.status == status)
            
        return query.all()
    
    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        id_empresa: Optional[UUID] = None,
        id_lancamento: Optional[UUID] = None,
        id_cliente: Optional[UUID] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        status: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Parcela]:
        """
        Obtém múltiplas parcelas com paginação e filtragem opcional.
        
        Args:
            db: Sessão do banco de dados
            skip: Registros para pular
            limit: Limite de registros
            id_empresa: Filtrar por empresa específica
            id_lancamento: Filtrar por lançamento específico
            id_cliente: Filtrar por cliente específico
            data_inicio: Data inicial para filtro
            data_fim: Data final para filtro
            status: Filtrar por status
            filters: Filtros adicionais
            
        Returns:
            List[Parcela]: Lista de parcelas
        """
        query = db.query(Parcela)
        
        # Join com lançamento para filtros relacionados
        if id_empresa or id_cliente:
            query = query.join(Lancamento)
        
        # Aplicar filtros principais
        if id_empresa:
            query = query.filter(Lancamento.id_empresa == id_empresa)
        
        if id_lancamento:
            query = query.filter(Parcela.id_lancamento == id_lancamento)
            
        if id_cliente:
            query = query.filter(Lancamento.id_cliente == id_cliente)
            
        if status:
            query = query.filter(Parcela.status == status)
        
        # Filtro por período de datas
        if data_inicio and data_fim:
            query = query.filter(
                Parcela.data_vencimento.between(data_inicio, data_fim)
            )
        elif data_inicio:
            query = query.filter(Parcela.data_vencimento >= data_inicio)
        elif data_fim:
            query = query.filter(Parcela.data_vencimento <= data_fim)
        
        # Filtros adicionais
        if filters:
            # Tratamento especial para busca por descrição
            if "descricao" in filters and filters["descricao"]:
                termo_busca = f"%{filters['descricao']}%"
                query = query.join(Lancamento, isouter=True).filter(Lancamento.descricao.ilike(termo_busca))
                del filters["descricao"]  # Remove para não processar novamente
            
            # Processamento dos demais filtros
            for field, value in filters.items():
                if value is not None and hasattr(Parcela, field):
                    query = query.filter(getattr(Parcela, field) == value)
        
        # Ordenação padrão por data de vencimento
        query = query.order_by(Parcela.data_vencimento.asc())
        
        return query.offset(skip).limit(limit).all()
    
    def get_count(
        self, 
        db: Session, 
        id_empresa: Optional[UUID] = None,
        id_lancamento: Optional[UUID] = None,
        id_cliente: Optional[UUID] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        status: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Obtém a contagem total de parcelas com filtros opcionais.
        
        Args:
            db: Sessão do banco de dados
            id_empresa: Filtrar por empresa específica
            id_lancamento: Filtrar por lançamento específico
            id_cliente: Filtrar por cliente específico
            data_inicio: Data inicial para filtro
            data_fim: Data final para filtro
            status: Filtrar por status
            filters: Filtros adicionais
            
        Returns:
            int: Contagem de parcelas
        """
        query = db.query(Parcela)
        
        # Join com lançamento para filtros relacionados
        if id_empresa or id_cliente:
            query = query.join(Lancamento)
        
        # Aplicar filtros principais
        if id_empresa:
            query = query.filter(Lancamento.id_empresa == id_empresa)
        
        if id_lancamento:
            query = query.filter(Parcela.id_lancamento == id_lancamento)
            
        if id_cliente:
            query = query.filter(Lancamento.id_cliente == id_cliente)
            
        if status:
            query = query.filter(Parcela.status == status)
        
        # Filtro por período de datas
        if data_inicio and data_fim:
            query = query.filter(
                Parcela.data_vencimento.between(data_inicio, data_fim)
            )
        elif data_inicio:
            query = query.filter(Parcela.data_vencimento >= data_inicio)
        elif data_fim:
            query = query.filter(Parcela.data_vencimento <= data_fim)
        
        # Filtros adicionais
        if filters:
            # Tratamento especial para busca por descrição
            if "descricao" in filters and filters["descricao"]:
                termo_busca = f"%{filters['descricao']}%"
                query = query.join(Lancamento, isouter=True).filter(Lancamento.descricao.ilike(termo_busca))
                del filters["descricao"]  # Remove para não processar novamente
            
            # Processamento dos demais filtros
            for field, value in filters.items():
                if value is not None and hasattr(Parcela, field):
                    query = query.filter(getattr(Parcela, field) == value)
        
        return query.count()
    
    def get_totais(
        self, 
        db: Session, 
        id_empresa: UUID,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        id_cliente: Optional[UUID] = None
    ) -> Dict[str, float]:
        """
        Calcula os totais de parcelas para uma empresa.
        
        Args:
            db: Sessão do banco de dados
            id_empresa: ID da empresa
            data_inicio: Data inicial para filtro
            data_fim: Data final para filtro
            id_cliente: Filtrar por cliente específico
            
        Returns:
            Dict[str, float]: Dicionário com os totais calculados
        """
        # Filtros iniciais
        query = db.query(Parcela).join(Lancamento).filter(Lancamento.id_empresa == id_empresa)
        
        # Filtros adicionais
        if id_cliente:
            query = query.filter(Lancamento.id_cliente == id_cliente)
            
        # Filtro por período de datas
        if data_inicio and data_fim:
            query = query.filter(Parcela.data_vencimento.between(data_inicio, data_fim))
        elif data_inicio:
            query = query.filter(Parcela.data_vencimento >= data_inicio)
        elif data_fim:
            query = query.filter(Parcela.data_vencimento <= data_fim)
        
        # Totais por status
        total_pagas = db.query(func.sum(Parcela.valor)).filter(
            Parcela.id_parcela.in_(query.with_entities(Parcela.id_parcela)), 
            Parcela.status == "paga"
        ).scalar() or 0
        
        total_pendentes = db.query(func.sum(Parcela.valor)).filter(
            Parcela.id_parcela.in_(query.with_entities(Parcela.id_parcela)),
            Parcela.status == "pendente"
        ).scalar() or 0
        
        total_atrasadas = db.query(func.sum(Parcela.valor)).filter(
            Parcela.id_parcela.in_(query.with_entities(Parcela.id_parcela)),
            Parcela.status == "pendente",
            Parcela.data_vencimento < date.today()
        ).scalar() or 0
        
        total_canceladas = db.query(func.sum(Parcela.valor)).filter(
            Parcela.id_parcela.in_(query.with_entities(Parcela.id_parcela)),
            Parcela.status == "cancelada"
        ).scalar() or 0
        
        return {
            "total_pagas": float(total_pagas),
            "total_pendentes": float(total_pendentes),
            "total_atrasadas": float(total_atrasadas),
            "total_canceladas": float(total_canceladas),
            "total_geral": float(total_pagas + total_pendentes)
        }
    
    def create(
        self, 
        db: Session, 
        *, 
        obj_in: ParcelaCreate
    ) -> Parcela:
        """
        Cria uma nova parcela.
        
        Args:
            db: Sessão do banco de dados
            obj_in: Dados da parcela
            
        Returns:
            Parcela: Parcela criada
            
        Raises:
            HTTPException: Se o lançamento não existir
        """
        # Verificar se lançamento existe
        lancamento = db.query(Lancamento).filter(
            Lancamento.id_lancamento == obj_in.id_lancamento
        ).first()
        if not lancamento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lançamento não encontrado"
            )
        
        # Criar objeto parcela
        db_obj = Parcela(**obj_in.dict())
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj
    
    def update(
        self,
        db: Session,
        *,
        db_obj: Parcela,
        obj_in: ParcelaUpdate
    ) -> Parcela:
        """
        Atualiza uma parcela existente.
        
        Args:
            db: Sessão do banco de dados
            db_obj: Objeto parcela existente
            obj_in: Dados para atualizar
            
        Returns:
            Parcela: Parcela atualizada
        """
        # Guardar status anterior para verificar mudanças
        status_antigo = db_obj.status
        
        # Atualizar campos
        update_data = obj_in.dict(exclude_unset=True)
        
        # Verificar consistência entre status e data de pagamento
        if "status" in update_data and update_data["status"] == "paga" and not db_obj.data_pagamento:
            if "data_pagamento" not in update_data or not update_data["data_pagamento"]:
                update_data["data_pagamento"] = date.today()
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Atualizar status do lançamento se todas as parcelas tiverem o mesmo status
        lancamento = db.query(Lancamento).filter(
            Lancamento.id_lancamento == db_obj.id_lancamento
        ).first()
        
        if lancamento:
            self._verificar_status_lancamento(db, lancamento)
        
        return db_obj
    
    def pagar(
        self, 
        db: Session, 
        *, 
        parcela: Parcela, 
        data_pagamento: Optional[date] = None
    ) -> Parcela:
        """
        Marca uma parcela como paga.
        
        Args:
            db: Sessão do banco de dados
            parcela: Objeto da parcela
            data_pagamento: Data de pagamento (opcional, padrão=hoje)
            
        Returns:
            Parcela: Parcela paga
        """
        if parcela.status == "paga":
            return parcela
        
        if parcela.status == "cancelada":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível pagar uma parcela cancelada"
            )
        
        # Definir data de pagamento
        parcela.data_pagamento = data_pagamento or date.today()
        parcela.status = "paga"
        parcela.updated_at = datetime.now()
        
        db.add(parcela)
        db.commit()
        db.refresh(parcela)
        
        # Verificar se todas as parcelas estão pagas
        lancamento = db.query(Lancamento).filter(
            Lancamento.id_lancamento == parcela.id_lancamento
        ).first()
        
        if lancamento:
            self._verificar_status_lancamento(db, lancamento)
        
        return parcela
    
    def cancelar(
        self, 
        db: Session, 
        *, 
        parcela: Parcela
    ) -> Parcela:
        """
        Cancela uma parcela.
        
        Args:
            db: Sessão do banco de dados
            parcela: Objeto da parcela
            
        Returns:
            Parcela: Parcela cancelada
        """
        if parcela.status == "cancelada":
            return parcela
        
        # Alterar status para cancelada
        parcela.status = "cancelada"
        parcela.updated_at = datetime.now()
        
        db.add(parcela)
        db.commit()
        db.refresh(parcela)
        
        # Verificar se todas as parcelas estão canceladas
        lancamento = db.query(Lancamento).filter(
            Lancamento.id_lancamento == parcela.id_lancamento
        ).first()
        
        if lancamento:
            self._verificar_status_lancamento(db, lancamento)
        
        return parcela
    
    def create_parcelas_for_lancamento(
        self, 
        db: Session, 
        *, 
        lancamento: Lancamento, 
        total_parcelas: int
    ) -> List[Parcela]:
        """
        Cria múltiplas parcelas para um lançamento.
        
        Args:
            db: Sessão do banco de dados
            lancamento: Objeto do lançamento
            total_parcelas: Número total de parcelas
            
        Returns:
            List[Parcela]: Lista de parcelas criadas
            
        Raises:
            HTTPException: Se o total de parcelas for inválido
        """
        if total_parcelas <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O número de parcelas deve ser maior que zero"
            )
        
        valor_parcela = lancamento.valor / total_parcelas
        parcelas_criadas = []
        
        # Verificar se já existem parcelas
        parcelas_existentes = db.query(Parcela).filter(
            Parcela.id_lancamento == lancamento.id_lancamento
        ).count()
        
        if parcelas_existentes > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este lançamento já possui parcelas"
            )
        
        # Criar parcelas
        for i in range(1, total_parcelas + 1):
            # Calcular data de vencimento (mês a mês)
            dias_adicionais = (i - 1) * 30
            data_vencimento = lancamento.data_vencimento + datetime.timedelta(days=dias_adicionais)
            
            parcela_data = {
                "id_lancamento": lancamento.id_lancamento,
                "numero": i,
                "valor": round(valor_parcela, 2),  # Arredondar para 2 casas decimais
                "data_vencimento": data_vencimento,
                "status": lancamento.status if lancamento.status in ["pendente", "pago", "cancelado"] else "pendente",
                "data_pagamento": lancamento.data_pagamento if lancamento.status == "pago" else None
            }
            
            if i == total_parcelas:
                # Ajustar valor da última parcela para corrigir arredondamentos
                total_demais_parcelas = round(valor_parcela * (total_parcelas - 1), 2)
                parcela_data["valor"] = round(lancamento.valor - total_demais_parcelas, 2)
            
            # Criar objeto parcela
            parcela = Parcela(**parcela_data)
            db.add(parcela)
            parcelas_criadas.append(parcela)
        
        db.commit()
        
        # Atualizar o lançamento
        lancamento.parcelado = True
        lancamento.total_parcelas = total_parcelas
        db.add(lancamento)
        db.commit()
        
        # Atualizar as parcelas criadas com refresh
        for i, parcela in enumerate(parcelas_criadas):
            db.refresh(parcela)
        
        return parcelas_criadas
    
    def _verificar_status_lancamento(self, db: Session, lancamento: Lancamento) -> None:
        """
        Verifica e atualiza o status do lançamento com base no status das parcelas.
        
        Args:
            db: Sessão do banco de dados
            lancamento: Objeto do lançamento
        """
        # Buscar todas as parcelas do lançamento
        parcelas = db.query(Parcela).filter(
            Parcela.id_lancamento == lancamento.id_lancamento
        ).all()
        
        if not parcelas:
            return
        
        # Verificar status de todas as parcelas
        total_parcelas = len(parcelas)
        parcelas_pagas = sum(1 for p in parcelas if p.status == "paga")
        parcelas_canceladas = sum(1 for p in parcelas if p.status == "cancelada")
        
        # Atualizar status do lançamento
        if parcelas_canceladas == total_parcelas:
            lancamento.status = "cancelado"
        elif parcelas_pagas == total_parcelas:
            lancamento.status = "pago"
            if not lancamento.data_pagamento:
                # Usar a data de pagamento da última parcela paga
                ultima_paga = max((p for p in parcelas if p.status == "paga"), 
                                  key=lambda p: p.data_pagamento or date.min)
                lancamento.data_pagamento = ultima_paga.data_pagamento
        else:
            # Se houver pelo menos uma parcela paga, marcar como parcialmente pago
            if parcelas_pagas > 0:
                lancamento.status = "parcialmente_pago"
            else:
                lancamento.status = "pendente"
        
        lancamento.updated_at = datetime.now()
        db.add(lancamento)
        db.commit() 