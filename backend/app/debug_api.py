"""
API de depuração para testes de rotas e endpoints do CCONTROL-M.

Este módulo oferece uma versão simplificada da API para testes rápidos
sem dependências de banco de dados ou autenticação.
"""

from fastapi import FastAPI, HTTPException, Query
from uuid import UUID, uuid4
from typing import Optional, List, Dict, Any
from datetime import datetime
import uvicorn

# Importar esquemas simplificados
from app.schemas.lancamento_simples import (
    Lancamento,
    LancamentoCreate,
    LancamentoUpdate,
    LancamentoWithDetalhes,
    PaginatedResponse,
    RelatorioFinanceiro
)

# Utilidades
from app.utils.pagination import paginate

# Criar aplicação FastAPI
app = FastAPI(
    title="CCONTROL-M Teste",
    description="Servidor de teste para rotas de lançamentos",
    version="1.0.0"
)

# Rota de saúde para teste de conexão
@app.get("/health")
async def health():
    """Teste de conexão da API de teste."""
    return {"status": "ok", "version": "debug"}


# Rota de teste para lançamentos
@app.get("/api/v1/lancamentos", response_model=PaginatedResponse)
async def listar_lancamentos(
    id_empresa: UUID = Query(..., description="ID da empresa"),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo (RECEITA, DESPESA)"),
    id_categoria: Optional[UUID] = Query(None, description="Filtrar por categoria"),
    id_centro_custo: Optional[UUID] = Query(None, description="Filtrar por centro de custo"),
    id_conta: Optional[UUID] = Query(None, description="Filtrar por conta bancária"),
    status: Optional[str] = Query(None, description="Filtrar por status (PENDENTE, PAGO, CANCELADO)"),
    data_inicio: Optional[str] = Query(None, description="Data inicial (formato YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data final (formato YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Página atual"),
    page_size: int = Query(10, ge=1, le=100, description="Itens por página"),
):
    """Rota de teste para listar lançamentos financeiros."""
    # Gerar dados de exemplo
    lancamentos = [
        Lancamento(
            id=uuid4(),
            descricao=f"Lançamento de teste {i}",
            valor=100.0 * i,
            data_lancamento=f"2023-{i:02d}-01",
            data_pagamento=f"2023-{i:02d}-10" if i % 3 != 0 else None,
            tipo="RECEITA" if i % 2 == 0 else "DESPESA",
            status="PENDENTE" if i % 3 == 0 else ("PAGO" if i % 3 == 1 else "CANCELADO"),
            id_categoria=UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6"),
            id_empresa=id_empresa
        )
        for i in range(1, 21)  # Gerar 20 itens para mostrar paginação
    ]
    
    # Filtrar resultados conforme parâmetros
    if tipo:
        lancamentos = [l for l in lancamentos if l.tipo == tipo]
    
    if status:
        lancamentos = [l for l in lancamentos if l.status == status]
    
    if id_categoria:
        lancamentos = [l for l in lancamentos if l.id_categoria == id_categoria]
    
    if data_inicio:
        lancamentos = [l for l in lancamentos if l.data_lancamento >= data_inicio]
    
    if data_fim:
        lancamentos = [l for l in lancamentos if l.data_lancamento <= data_fim]
    
    # Calcular total após filtros
    total = len(lancamentos)
    
    # Aplicar paginação
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, total)
    page_items = lancamentos[start_idx:end_idx]
    
    # Usar a função paginate para padronizar a resposta
    return paginate(page_items, total, page, page_size)


@app.get("/api/v1/lancamentos/{id_lancamento}", response_model=LancamentoWithDetalhes)
async def obter_lancamento(
    id_lancamento: UUID,
    id_empresa: UUID = Query(..., description="ID da empresa"),
):
    """Obter detalhes de um lançamento específico."""
    
    return LancamentoWithDetalhes(
        id=id_lancamento,
        descricao=f"Lançamento detalhado #{id_lancamento}",
        valor=150.0,
        data_lancamento="2023-01-15",
        data_pagamento="2023-01-20",
        tipo="DESPESA",
        status="PAGO",
        id_categoria=UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6"),
        id_empresa=id_empresa,
        categoria_nome="Despesas Gerais",
        conta_nome="Conta Principal",
        centro_custo_nome="Administrativo",
        criado_por="Usuário Teste",
        criado_em="2023-01-15T10:00:00",
        atualizado_em="2023-01-20T14:30:00"
    )


@app.post("/api/v1/lancamentos", response_model=LancamentoWithDetalhes)
async def criar_lancamento(
    lancamento: LancamentoCreate,
):
    """Criar um novo lançamento."""
    id_lancamento = uuid4()
    
    return LancamentoWithDetalhes(
        id=id_lancamento,
        descricao=lancamento.descricao,
        valor=lancamento.valor,
        data_lancamento=lancamento.data_lancamento,
        data_pagamento=lancamento.data_pagamento,
        tipo=lancamento.tipo,
        status="PENDENTE",
        id_categoria=lancamento.id_categoria,
        id_empresa=lancamento.id_empresa,
        categoria_nome="Categoria Teste",
        conta_nome="Conta Teste" if lancamento.id_conta else None,
        centro_custo_nome="Centro de Custo Teste" if lancamento.id_centro_custo else None,
        criado_por="Usuário Teste",
        criado_em=datetime.now().isoformat(),
        atualizado_em=datetime.now().isoformat()
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001) 