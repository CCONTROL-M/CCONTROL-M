"""Serviço de consultas especializadas para contas a pagar."""
from uuid import UUID
from typing import Dict, Any, List, Optional
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status

from app.database import get_async_session
from app.repositories.conta_pagar_repository import ContaPagarRepository
from app.schemas.pagination import PaginatedResponse
from app.schemas.conta_pagar import ContaPagar
from app.schemas.relatorio import RelatorioContasPagar, ResumoPagamentos


class ContaPagarQueryService:
    """
    Serviço especializado em consultas e relatórios de contas a pagar.
    
    Este serviço implementa consultas analíticas e relatórios avançados sobre
    contas a pagar, separado do serviço principal para manter a clareza
    e a separação de responsabilidades.
    """
    
    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        """Inicializar serviço com dependências necessárias."""
        self.repository = ContaPagarRepository(session)
        
    async def gerar_relatorio_contas(
        self,
        empresa_id: UUID,
        data_inicial: Optional[date] = None,
        data_final: Optional[date] = None,
        status: Optional[str] = None,
        fornecedor_id: Optional[UUID] = None,
        categoria_id: Optional[UUID] = None
    ) -> RelatorioContasPagar:
        """
        Gera um relatório analítico de contas a pagar com filtros especificados.
        
        Parameters:
            empresa_id: ID da empresa
            data_inicial: Data inicial para filtro
            data_final: Data final para filtro
            status: Status das contas a filtrar
            fornecedor_id: ID do fornecedor para filtro
            categoria_id: ID da categoria para filtro
            
        Returns:
            Relatório analítico de contas a pagar
        """
        # Obter dados para o relatório
        contas = await self.repository.get_contas_para_relatorio(
            empresa_id=empresa_id,
            data_inicial=data_inicial,
            data_final=data_final,
            status=status,
            fornecedor_id=fornecedor_id,
            categoria_id=categoria_id
        )
        
        # Calcular totais
        total_geral = sum(float(conta.valor) for conta in contas)
        total_pago = sum(
            float(conta.valor_pago or 0) 
            for conta in contas 
            if conta.status in ["pago", "parcial"]
        )
        total_pendente = sum(
            float(conta.valor) - float(conta.valor_pago or 0)
            for conta in contas
            if conta.status in ["pendente", "parcial"]
        )
        
        # Agrupar por vencimento
        vencidas = []
        a_vencer = []
        hoje = datetime.now().date()
        
        for conta in contas:
            if conta.status in ["pendente", "parcial"]:
                if conta.data_vencimento < hoje:
                    vencidas.append(conta)
                else:
                    a_vencer.append(conta)
        
        # Resumo por status
        por_status = {
            "pendente": sum(float(conta.valor) for conta in contas if conta.status == "pendente"),
            "parcial": sum(float(conta.valor) for conta in contas if conta.status == "parcial"),
            "pago": sum(float(conta.valor) for conta in contas if conta.status == "pago"),
            "cancelado": sum(float(conta.valor) for conta in contas if conta.status == "cancelado"),
            "atrasado": sum(float(conta.valor) for conta in contas if conta.status == "atrasado")
        }
        
        # Resumo por categorias
        categorias = {}
        for conta in contas:
            if conta.categoria_id and conta.categoria:
                categoria_nome = conta.categoria.nome
                if categoria_nome not in categorias:
                    categorias[categoria_nome] = 0
                categorias[categoria_nome] += float(conta.valor)
        
        # Criar relatório
        return RelatorioContasPagar(
            total_geral=total_geral,
            total_pago=total_pago,
            total_pendente=total_pendente,
            total_contas=len(contas),
            contas_vencidas=len(vencidas),
            contas_a_vencer=len(a_vencer),
            valor_vencido=sum(float(conta.valor) - float(conta.valor_pago or 0) for conta in vencidas),
            valor_a_vencer=sum(float(conta.valor) - float(conta.valor_pago or 0) for conta in a_vencer),
            por_status=por_status,
            por_categoria=categorias,
            data_geracao=datetime.now(),
            periodo_inicial=data_inicial,
            periodo_final=data_final
        )
        
    async def obter_resumo_pagamentos(
        self,
        empresa_id: UUID,
        periodo: str = "mensal",
        ano: Optional[int] = None,
        mes: Optional[int] = None
    ) -> ResumoPagamentos:
        """
        Obtém um resumo de pagamentos por período.
        
        Parameters:
            empresa_id: ID da empresa
            periodo: Tipo de agrupamento ("diario", "mensal", "anual")
            ano: Ano para filtro
            mes: Mês para filtro
            
        Returns:
            Resumo de pagamentos no período
        """
        # Definir ano e mês padrão se não especificados
        if not ano:
            ano = datetime.now().year
        if not mes and periodo == "mensal":
            mes = datetime.now().month
            
        # Obter dados de pagamentos no período
        pagamentos = await self.repository.get_pagamentos_por_periodo(
            empresa_id=empresa_id,
            periodo=periodo,
            ano=ano,
            mes=mes
        )
        
        # Transformar em estrutura de resumo
        resumo = ResumoPagamentos(
            periodo=periodo,
            ano=ano,
            mes=mes,
            total_valor=sum(pagamento["valor"] for pagamento in pagamentos),
            quantidade=len(pagamentos),
            dados=pagamentos
        )
        
        return resumo
        
    async def buscar_contas_por_fornecedor(
        self,
        empresa_id: UUID,
        fornecedor_id: UUID,
        incluir_pagas: bool = False
    ) -> PaginatedResponse[ContaPagar]:
        """
        Busca todas as contas de um fornecedor específico.
        
        Parameters:
            empresa_id: ID da empresa
            fornecedor_id: ID do fornecedor
            incluir_pagas: Se deve incluir contas já pagas
            
        Returns:
            Lista paginada de contas do fornecedor
        """
        return await self.repository.get_contas_por_fornecedor(
            empresa_id=empresa_id,
            fornecedor_id=fornecedor_id,
            incluir_pagas=incluir_pagas
        )
        
    async def buscar_contas_vencidas(
        self,
        empresa_id: UUID,
        dias_atraso: Optional[int] = None
    ) -> List[ContaPagar]:
        """
        Busca contas vencidas, opcionalmente com filtro de dias de atraso.
        
        Parameters:
            empresa_id: ID da empresa
            dias_atraso: Filtro de número mínimo de dias de atraso
            
        Returns:
            Lista de contas vencidas
        """
        hoje = datetime.now().date()
        data_limite = None
        
        if dias_atraso:
            # Calcular data limite baseada nos dias de atraso
            from datetime import timedelta
            data_limite = hoje - timedelta(days=dias_atraso)
        
        return await self.repository.get_contas_vencidas(
            empresa_id=empresa_id,
            data_limite=data_limite
        )
