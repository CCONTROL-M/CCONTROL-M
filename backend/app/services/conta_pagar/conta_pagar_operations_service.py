"""Serviço para operações especializadas de contas a pagar."""
from uuid import UUID
from typing import Dict, Any, List, Optional, Tuple
from datetime import date, datetime, timedelta
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.repositories.conta_pagar_repository import ContaPagarRepository
from app.schemas.conta_pagar import ContaPagarCreate, ContaPagarUpdate, ContaPagar
from app.services.auditoria_service import AuditoriaService
from app.services.conta_pagar.conta_pagar_service import ContaPagarService


class ContaPagarOperationsService:
    """
    Serviço para operações especializadas de contas a pagar.
    
    Este serviço implementa operações complexas relacionadas a contas a pagar,
    como parcelamento, duplicação, e outras operações específicas.
    """
    
    def __init__(
        self, 
        session: AsyncSession = Depends(get_async_session),
        conta_pagar_service: ContaPagarService = Depends(),
        auditoria_service: AuditoriaService = Depends()
    ):
        """Inicializar serviço com dependências necessárias."""
        self.repository = ContaPagarRepository(session)
        self.conta_pagar_service = conta_pagar_service
        self.auditoria_service = auditoria_service
        
    async def criar_parcelas(
        self,
        conta_base: ContaPagarCreate,
        numero_parcelas: int,
        intervalo_dias: int,
        usuario_id: UUID,
        empresa_id: UUID
    ) -> List[ContaPagar]:
        """
        Cria múltiplas parcelas de contas a pagar a partir de uma conta base.
        
        Parameters:
            conta_base: Dados base da conta a pagar
            numero_parcelas: Número de parcelas a criar
            intervalo_dias: Intervalo em dias entre as parcelas
            usuario_id: ID do usuário que está criando as parcelas
            empresa_id: ID da empresa
            
        Returns:
            Lista de contas a pagar criadas como parcelas
        """
        if numero_parcelas <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O número de parcelas deve ser maior que zero"
            )
            
        if intervalo_dias <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O intervalo entre parcelas deve ser maior que zero"
            )
            
        # Verificar empresa
        if conta_base.id_empresa != empresa_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A conta deve pertencer à mesma empresa do usuário"
            )
            
        # Calcular valor das parcelas
        valor_total = float(conta_base.valor)
        valor_parcela = round(valor_total / numero_parcelas, 2)
        
        # Ajustar última parcela para compensar arredondamentos
        ultima_parcela = valor_total - (valor_parcela * (numero_parcelas - 1))
        
        parcelas_criadas = []
        
        # Criar parcelas
        for i in range(numero_parcelas):
            parcela = ContaPagarCreate(
                **dict(conta_base)
            )
            
            # Ajustar descrição
            parcela.descricao = f"{conta_base.descricao} - Parcela {i+1}/{numero_parcelas}"
            
            # Ajustar valor
            if i == numero_parcelas - 1:
                parcela.valor = ultima_parcela
            else:
                parcela.valor = valor_parcela
                
            # Ajustar vencimento
            parcela.data_vencimento = conta_base.data_vencimento + timedelta(days=i * intervalo_dias)
            
            # Criar parcela
            parcela_criada = await self.conta_pagar_service.create(
                parcela, usuario_id, empresa_id
            )
            parcelas_criadas.append(parcela_criada)
            
        # Registrar ação de auditoria
        await self.auditoria_service.registrar_acao(
            usuario_id=usuario_id,
            empresa_id=empresa_id,
            acao="PARCELAR",
            entidade="ContaPagar",
            entidade_id=",".join([str(p.id) for p in parcelas_criadas]),
            descricao=f"Criação de {numero_parcelas} parcelas para {conta_base.descricao}"
        )
        
        return parcelas_criadas
        
    async def duplicar_conta(
        self,
        id_conta: UUID,
        novo_vencimento: date,
        usuario_id: UUID,
        empresa_id: UUID,
        manter_valor: bool = True,
        novo_valor: Optional[float] = None,
        nova_descricao: Optional[str] = None
    ) -> ContaPagar:
        """
        Duplica uma conta a pagar existente com novas informações.
        
        Parameters:
            id_conta: ID da conta a ser duplicada
            novo_vencimento: Nova data de vencimento
            usuario_id: ID do usuário realizando a operação
            empresa_id: ID da empresa
            manter_valor: Se deve manter o valor original
            novo_valor: Novo valor (se manter_valor for False)
            nova_descricao: Nova descrição (opcional)
            
        Returns:
            Nova conta a pagar criada
        """
        # Buscar conta original
        conta_original = await self.conta_pagar_service.get_by_id(id_conta, empresa_id)
        
        # Criar nova conta baseada na original
        nova_conta = ContaPagarCreate(
            descricao=nova_descricao or f"{conta_original.descricao} (Duplicada)",
            valor=novo_valor if not manter_valor and novo_valor else float(conta_original.valor),
            data_vencimento=novo_vencimento,
            fornecedor_id=conta_original.fornecedor_id,
            categoria_id=conta_original.categoria_id,
            id_empresa=empresa_id,
            observacoes=f"Duplicada da conta {id_conta} em {datetime.now().strftime('%d/%m/%Y')}"
        )
        
        # Criar a nova conta
        nova_conta_criada = await self.conta_pagar_service.create(
            nova_conta, usuario_id, empresa_id
        )
        
        # Registrar ação de auditoria
        await self.auditoria_service.registrar_acao(
            usuario_id=usuario_id,
            empresa_id=empresa_id,
            acao="DUPLICAR",
            entidade="ContaPagar",
            entidade_id=str(nova_conta_criada.id),
            descricao=f"Conta duplicada a partir de {id_conta}"
        )
        
        return nova_conta_criada
        
    async def reagendar_vencimentos(
        self,
        empresa_id: UUID,
        ids_contas: List[UUID],
        nova_data: date,
        usuario_id: UUID
    ) -> List[ContaPagar]:
        """
        Reagenda a data de vencimento de múltiplas contas.
        
        Parameters:
            empresa_id: ID da empresa
            ids_contas: Lista de IDs das contas a reagendar
            nova_data: Nova data de vencimento
            usuario_id: ID do usuário realizando a operação
            
        Returns:
            Lista de contas atualizadas
        """
        contas_atualizadas = []
        
        for id_conta in ids_contas:
            try:
                # Verificar se a conta existe e pertence à empresa
                conta = await self.conta_pagar_service.get_by_id(id_conta, empresa_id)
                
                # Verificar se a conta pode ser reagendada
                if conta.status not in ["pendente", "atrasado"]:
                    continue
                    
                # Atualizar data de vencimento
                conta_update = ContaPagarUpdate(
                    data_vencimento=nova_data,
                    observacoes=f"{conta.observacoes or ''}\nVencimento reagendado de {conta.data_vencimento} para {nova_data}"
                )
                
                # Atualizar a conta
                conta_atualizada = await self.conta_pagar_service.update(
                    id_conta, conta_update, usuario_id, empresa_id
                )
                
                contas_atualizadas.append(conta_atualizada)
                
            except HTTPException:
                # Ignorar contas que não existem ou não pertencem à empresa
                continue
                
        # Registrar ação de auditoria
        if contas_atualizadas:
            await self.auditoria_service.registrar_acao(
                usuario_id=usuario_id,
                empresa_id=empresa_id,
                acao="REAGENDAR",
                entidade="ContaPagar",
                entidade_id=",".join([str(c.id) for c in contas_atualizadas]),
                descricao=f"Reagendamento de {len(contas_atualizadas)} contas para {nova_data}"
            )
            
        return contas_atualizadas
