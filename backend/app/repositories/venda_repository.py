"""Repositório para operações com vendas."""
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, select
from fastapi import HTTPException, status

from app.models.venda import Venda
from app.models.cliente import Cliente
from app.models.produto import Produto
from app.models.lancamento import Lancamento
from app.models.conta_bancaria import ContaBancaria
from app.models.forma_pagamento import FormaPagamento
from app.schemas.venda import VendaCreate, VendaUpdate, StatusVenda, ItemVenda
from app.repositories.base_repository import BaseRepository
from app.repositories.lancamento_repository import LancamentoRepository


class VendaRepository(BaseRepository[Venda, VendaCreate, VendaUpdate]):
    """Repositório para operações com vendas."""
    
    def __init__(self):
        """Inicializa o repositório com o modelo Venda."""
        super().__init__(Venda)
    
    def get(self, db: Session, id: UUID) -> Optional[Venda]:
        """
        Obtém uma venda pelo ID.
        
        Args:
            db: Sessão do banco de dados
            id: ID da venda
            
        Returns:
            Venda: Venda encontrada ou None
        """
        return db.query(Venda).filter(Venda.id_venda == id).first()
    
    def get_with_relacionamentos(
        self, 
        db: Session, 
        id: UUID
    ) -> Optional[Venda]:
        """
        Obtém uma venda pelo ID com informações relacionadas de cliente e lançamentos.
        
        Args:
            db: Sessão do banco de dados
            id: ID da venda
            
        Returns:
            Venda: Venda encontrada ou None
        """
        return db.query(Venda).filter(
            Venda.id_venda == id
        ).first()
    
    def get_by_empresa(
        self, 
        db: Session, 
        id_empresa: UUID,
        status: Optional[str] = None
    ) -> List[Venda]:
        """
        Obtém todas as vendas de uma empresa.
        
        Args:
            db: Sessão do banco de dados
            id_empresa: ID da empresa
            status: Filtro por status
            
        Returns:
            List[Venda]: Lista de vendas da empresa
        """
        query = db.query(Venda).filter(Venda.id_empresa == id_empresa)
            
        if status:
            query = query.filter(Venda.status == status)
            
        return query.all()
    
    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        id_empresa: Optional[UUID] = None,
        id_cliente: Optional[UUID] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        status: Optional[str] = None,
        parcelado: Optional[bool] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Venda]:
        """
        Obtém múltiplas vendas com paginação e filtragem opcional.
        
        Args:
            db: Sessão do banco de dados
            skip: Registros para pular
            limit: Limite de registros
            id_empresa: Filtrar por empresa específica
            id_cliente: Filtrar por cliente específico
            data_inicio: Data inicial para filtro
            data_fim: Data final para filtro
            status: Filtrar por status
            parcelado: Filtrar por vendas parceladas/não-parceladas
            filters: Filtros adicionais
            
        Returns:
            List[Venda]: Lista de vendas
        """
        query = db.query(Venda)
        
        # Aplicar filtros principais
        if id_empresa:
            query = query.filter(Venda.id_empresa == id_empresa)
        
        if id_cliente:
            query = query.filter(Venda.id_cliente == id_cliente)
            
        if status:
            query = query.filter(Venda.status == status)
            
        if parcelado is not None:
            query = query.filter(Venda.parcelado == parcelado)
        
        # Filtro por período de datas
        if data_inicio and data_fim:
            query = query.filter(
                Venda.data_venda.between(data_inicio, data_fim)
            )
        elif data_inicio:
            query = query.filter(Venda.data_venda >= data_inicio)
        elif data_fim:
            query = query.filter(Venda.data_venda <= data_fim)
        
        # Filtros adicionais
        if filters:
            # Tratamento especial para busca por descrição
            if "descricao" in filters and filters["descricao"]:
                termo_busca = f"%{filters['descricao']}%"
                query = query.filter(Venda.descricao.ilike(termo_busca))
                del filters["descricao"]  # Remove para não processar novamente
            
            # Tratamento para busca por número da venda
            if "numero_venda" in filters and filters["numero_venda"]:
                termo_busca = f"%{filters['numero_venda']}%"
                query = query.filter(Venda.numero_venda.ilike(termo_busca))
                del filters["numero_venda"]  # Remove para não processar novamente
            
            # Processamento dos demais filtros
            for field, value in filters.items():
                if value is not None and hasattr(Venda, field):
                    query = query.filter(getattr(Venda, field) == value)
        
        # Ordenação padrão por data
        query = query.order_by(Venda.data_venda.desc())
        
        return query.offset(skip).limit(limit).all()
    
    def get_count(
        self, 
        db: Session, 
        id_empresa: Optional[UUID] = None,
        id_cliente: Optional[UUID] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        status: Optional[str] = None,
        parcelado: Optional[bool] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Obtém a contagem total de vendas com filtros opcionais.
        
        Args:
            db: Sessão do banco de dados
            id_empresa: Filtrar por empresa específica
            id_cliente: Filtrar por cliente específico
            data_inicio: Data inicial para filtro
            data_fim: Data final para filtro
            status: Filtrar por status
            parcelado: Filtrar por vendas parceladas/não-parceladas
            filters: Filtros adicionais
            
        Returns:
            int: Contagem de vendas
        """
        query = db.query(Venda)
        
        # Aplicar filtros principais
        if id_empresa:
            query = query.filter(Venda.id_empresa == id_empresa)
        
        if id_cliente:
            query = query.filter(Venda.id_cliente == id_cliente)
            
        if status:
            query = query.filter(Venda.status == status)
            
        if parcelado is not None:
            query = query.filter(Venda.parcelado == parcelado)
        
        # Filtro por período de datas
        if data_inicio and data_fim:
            query = query.filter(
                Venda.data_venda.between(data_inicio, data_fim)
            )
        elif data_inicio:
            query = query.filter(Venda.data_venda >= data_inicio)
        elif data_fim:
            query = query.filter(Venda.data_venda <= data_fim)
        
        # Filtros adicionais
        if filters:
            # Tratamento especial para busca por descrição
            if "descricao" in filters and filters["descricao"]:
                termo_busca = f"%{filters['descricao']}%"
                query = query.filter(Venda.descricao.ilike(termo_busca))
                del filters["descricao"]  # Remove para não processar novamente
            
            # Tratamento para busca por número da venda
            if "numero_venda" in filters and filters["numero_venda"]:
                termo_busca = f"%{filters['numero_venda']}%"
                query = query.filter(Venda.numero_venda.ilike(termo_busca))
                del filters["numero_venda"]  # Remove para não processar novamente
            
            # Processamento dos demais filtros
            for field, value in filters.items():
                if value is not None and hasattr(Venda, field):
                    query = query.filter(getattr(Venda, field) == value)
        
        return query.count()
    
    def get_totais(
        self, 
        db: Session, 
        id_empresa: UUID,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        id_cliente: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Calcula os totais de vendas para uma empresa.
        
        Args:
            db: Sessão do banco de dados
            id_empresa: ID da empresa
            data_inicio: Data inicial para filtro
            data_fim: Data final para filtro
            id_cliente: Filtrar por cliente específico
            
        Returns:
            Dict[str, Any]: Dicionário com os totais calculados
        """
        # Filtros base
        filtros = [Venda.id_empresa == id_empresa]
        
        # Adicionar filtros opcionais
        if id_cliente:
            filtros.append(Venda.id_cliente == id_cliente)
        
        # Filtro por período de datas
        if data_inicio and data_fim:
            filtros.append(Venda.data_venda.between(data_inicio, data_fim))
        elif data_inicio:
            filtros.append(Venda.data_venda >= data_inicio)
        elif data_fim:
            filtros.append(Venda.data_venda <= data_fim)
        
        # Total de vendas por status
        total_pendentes = db.query(func.sum(Venda.valor_liquido)).filter(
            *filtros, 
            Venda.status == "pendente"
        ).scalar() or 0
        
        total_concluidas = db.query(func.sum(Venda.valor_liquido)).filter(
            *filtros, 
            Venda.status == "concluida"
        ).scalar() or 0
        
        total_canceladas = db.query(func.sum(Venda.valor_liquido)).filter(
            *filtros, 
            Venda.status == "cancelada"
        ).scalar() or 0
        
        # Total geral
        total_geral = float(total_pendentes) + float(total_concluidas)
        
        # Total de itens vendidos
        total_itens = 0
        vendas = db.query(Venda).filter(*filtros, Venda.status != "cancelada").all()
        for venda in vendas:
            itens = venda.itens_venda
            if isinstance(itens, dict) and "itens" in itens:
                total_itens += len(itens["itens"])
        
        return {
            "total_pendentes": float(total_pendentes),
            "total_concluidas": float(total_concluidas),
            "total_canceladas": float(total_canceladas),
            "total_geral": total_geral,
            "total_itens_vendidos": total_itens,
            "periodo_inicio": data_inicio,
            "periodo_fim": data_fim
        }
    
    def create(
        self, 
        db: Session, 
        *, 
        obj_in: VendaCreate,
        criar_lancamento: bool = True,
        id_conta: Optional[UUID] = None,
        id_forma_pagamento: Optional[UUID] = None
    ) -> Venda:
        """
        Cria uma nova venda.
        
        Args:
            db: Sessão do banco de dados
            obj_in: Dados da venda
            criar_lancamento: Se deve criar lançamento(s) financeiro(s) associado(s)
            id_conta: ID da conta bancária para o lançamento (obrigatório se criar_lancamento=True)
            id_forma_pagamento: ID da forma de pagamento (obrigatório se criar_lancamento=True)
            
        Returns:
            Venda: Venda criada
            
        Raises:
            HTTPException: Se cliente não existir ou se parâmetros de lançamento estiverem inválidos
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
        
        # Verificar produtos existentes
        for item in obj_in.itens_venda:
            produto = db.query(Produto).filter(
                Produto.id_produto == item.id_produto,
                Produto.id_empresa == obj_in.id_empresa
            ).first()
            if not produto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Produto com ID {item.id_produto} não encontrado ou não pertence a esta empresa"
                )
        
        # Validar informações para criação de lançamento
        if criar_lancamento:
            if not id_conta:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="ID da conta bancária é necessário para criar lançamento"
                )
            
            if not id_forma_pagamento:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="ID da forma de pagamento é necessário para criar lançamento"
                )
            
            # Verificar se conta e forma de pagamento existem
            conta = db.query(ContaBancaria).filter(
                ContaBancaria.id_conta == id_conta,
                ContaBancaria.id_empresa == obj_in.id_empresa
            ).first()
            if not conta:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conta bancária não encontrada ou não pertence a esta empresa"
                )
            
            forma = db.query(FormaPagamento).filter(
                FormaPagamento.id_forma == id_forma_pagamento,
                FormaPagamento.id_empresa == obj_in.id_empresa
            ).first()
            if not forma:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Forma de pagamento não encontrada ou não pertence a esta empresa"
                )
            
        # Preparar dados da venda
        itens_json = {
            "itens": [item.dict() for item in obj_in.itens_venda]
        }
        
        venda_data = obj_in.dict(exclude={"itens_venda"})
        venda_data["itens_venda"] = itens_json
        
        db_obj = Venda(**venda_data)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Criar lançamento(s) financeiros se solicitado
        if criar_lancamento:
            self._criar_lancamentos_venda(
                db=db, 
                venda=db_obj, 
                id_conta=id_conta, 
                id_forma_pagamento=id_forma_pagamento
            )
        
        return db_obj
    
    def update(
        self,
        db: Session,
        *,
        db_obj: Venda,
        obj_in: VendaUpdate
    ) -> Venda:
        """
        Atualiza uma venda existente.
        
        Args:
            db: Sessão do banco de dados
            db_obj: Objeto venda existente
            obj_in: Dados para atualizar
            
        Returns:
            Venda: Venda atualizada
            
        Raises:
            HTTPException: Se cliente não existir ou se a venda já tiver lançamentos
        """
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
        
        # Verificar se existem lançamentos associados
        tem_lancamentos = db.query(Lancamento).filter(
            Lancamento.id_venda == db_obj.id_venda
        ).count() > 0
        
        # Se houver lançamentos, restringir os campos que podem ser alterados
        if tem_lancamentos:
            campos_permitidos = {"status", "observacao", "nota_fiscal"}
            update_data = {}
            
            # Filtrar apenas os campos permitidos
            data_dict = obj_in.dict(exclude_unset=True)
            for field in campos_permitidos:
                if field in data_dict:
                    update_data[field] = data_dict[field]
                    
            # Se não houver campos válidos para atualizar, retornar erro
            if not update_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Não é possível alterar os dados principais de uma venda com lançamentos. Apenas status, observação e nota fiscal podem ser alterados."
                )
        else:
            # Se não houver lançamentos, permitir alteração completa
            update_data = obj_in.dict(exclude_unset=True)
        
        # Atualizar campos
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj
    
    def cancelar(
        self, 
        db: Session, 
        *, 
        venda: Venda, 
        cancelar_lancamentos: bool = True
    ) -> Venda:
        """
        Cancela uma venda e opcionalmente seus lançamentos.
        
        Args:
            db: Sessão do banco de dados
            venda: Objeto da venda
            cancelar_lancamentos: Se deve cancelar os lançamentos associados
            
        Returns:
            Venda: Venda cancelada
            
        Raises:
            HTTPException: Se a venda já estiver cancelada
        """
        if venda.status == "cancelada":
            return venda
        
        # Alterar status para cancelada
        venda.status = "cancelada"
        venda.updated_at = datetime.now()
        
        db.add(venda)
        db.commit()
        db.refresh(venda)
        
        # Cancelar lançamentos associados se solicitado
        if cancelar_lancamentos:
            lancamentos = db.query(Lancamento).filter(
                Lancamento.id_venda == venda.id_venda
            ).all()
            
            lancamento_repo = LancamentoRepository()
            for lancamento in lancamentos:
                lancamento_repo.cancelar(db=db, lancamento=lancamento)
        
        return venda
    
    def concluir(
        self, 
        db: Session, 
        *, 
        venda: Venda
    ) -> Venda:
        """
        Marca uma venda como concluída.
        
        Args:
            db: Sessão do banco de dados
            venda: Objeto da venda
            
        Returns:
            Venda: Venda concluída
            
        Raises:
            HTTPException: Se a venda já estiver cancelada
        """
        if venda.status == "concluida":
            return venda
        
        if venda.status == "cancelada":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível concluir uma venda cancelada"
            )
        
        # Alterar status para concluída
        venda.status = "concluida"
        venda.updated_at = datetime.now()
        
        db.add(venda)
        db.commit()
        db.refresh(venda)
        
        return venda
    
    def remove(self, db: Session, *, id: UUID) -> Venda:
        """
        Remove uma venda.
        
        Args:
            db: Sessão do banco de dados
            id: ID da venda
            
        Returns:
            Venda: Venda removida
            
        Raises:
            HTTPException: Se a venda não for encontrada ou tiver lançamentos associados
        """
        venda = db.query(Venda).filter(Venda.id_venda == id).first()
        if not venda:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Venda não encontrada"
            )
        
        # Verificar se existem lançamentos associados
        tem_lancamentos = db.query(Lancamento).filter(
            Lancamento.id_venda == id
        ).count() > 0
        
        if tem_lancamentos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível excluir uma venda com lançamentos associados. Cancele a venda em vez de excluí-la."
            )
        
        db.delete(venda)
        db.commit()
        
        return venda
    
    def _criar_lancamentos_venda(
        self, 
        db: Session, 
        venda: Venda, 
        id_conta: UUID, 
        id_forma_pagamento: UUID
    ) -> List[Lancamento]:
        """
        Cria lançamentos financeiros para uma venda.
        
        Args:
            db: Sessão do banco de dados
            venda: Objeto da venda
            id_conta: ID da conta bancária
            id_forma_pagamento: ID da forma de pagamento
            
        Returns:
            List[Lancamento]: Lista de lançamentos criados
        """
        from app.schemas.lancamento import LancamentoCreate
        
        lancamento_repo = LancamentoRepository()
        lancamentos_criados = []
        
        # Verificar se a venda é parcelada
        if venda.parcelado and venda.total_parcelas and venda.total_parcelas > 1:
            # Calcular valor de cada parcela
            valor_parcela = venda.valor_liquido / venda.total_parcelas
            
            # Criar um lançamento para cada parcela
            for i in range(1, venda.total_parcelas + 1):
                # Calcular data de vencimento (30 dias entre parcelas)
                dias_adicionais = (i - 1) * 30
                data_vencimento = venda.data_venda + timedelta(days=dias_adicionais)
                
                # Criar lançamento
                lancamento_data = {
                    "id_empresa": venda.id_empresa,
                    "id_cliente": venda.id_cliente,
                    "id_conta": id_conta,
                    "id_forma_pagamento": id_forma_pagamento,
                    "id_venda": venda.id_venda,
                    "descricao": f"{venda.descricao} - Parcela {i}/{venda.total_parcelas}",
                    "tipo": "entrada",
                    "valor": round(valor_parcela, 2),  # Arredondar para 2 casas decimais
                    "data_lancamento": venda.data_venda,
                    "data_vencimento": data_vencimento,
                    "status": "pendente",
                    "numero_parcela": i,
                    "total_parcelas": venda.total_parcelas
                }
                
                lancamento = lancamento_repo.create(
                    db=db, 
                    obj_in=LancamentoCreate(**lancamento_data)
                )
                lancamentos_criados.append(lancamento)
                
        else:
            # Criar um único lançamento
            lancamento_data = {
                "id_empresa": venda.id_empresa,
                "id_cliente": venda.id_cliente,
                "id_conta": id_conta,
                "id_forma_pagamento": id_forma_pagamento,
                "id_venda": venda.id_venda,
                "descricao": venda.descricao,
                "tipo": "entrada",
                "valor": venda.valor_liquido,
                "data_lancamento": venda.data_venda,
                "data_vencimento": venda.data_venda,
                "status": "pendente"
            }
            
            lancamento = lancamento_repo.create(
                db=db, 
                obj_in=LancamentoCreate(**lancamento_data)
            )
            lancamentos_criados.append(lancamento)
            
        return lancamentos_criados 