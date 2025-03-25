"""
Servidor de teste simplificado para o CCONTROL-M.
Implementa rotas básicas para teste sem dependências externas.
"""

from fastapi import FastAPI, Query, HTTPException
from uuid import UUID, uuid4
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uvicorn
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

# Criar aplicação FastAPI
app = FastAPI(
    title="CCONTROL-M Teste",
    description="Servidor de teste para rotas básicas",
    version="1.0.0"
)

# Adicionar middleware CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos simplificados
class Lancamento(BaseModel):
    id: UUID
    descricao: str
    valor: float
    data_lancamento: str
    data_pagamento: Optional[str] = None
    tipo: str  # "RECEITA" ou "DESPESA"
    status: str  # "PENDENTE", "PAGO" ou "CANCELADO"
    id_categoria: UUID
    id_empresa: UUID

class LancamentoWithDetalhes(Lancamento):
    categoria_nome: Optional[str] = None
    conta_nome: Optional[str] = None
    centro_custo_nome: Optional[str] = None
    criado_por: Optional[str] = None
    criado_em: Optional[str] = None
    atualizado_em: Optional[str] = None

class LancamentoCreate(BaseModel):
    descricao: str
    valor: float
    data_lancamento: str
    data_pagamento: Optional[str] = None
    tipo: str  # "RECEITA" ou "DESPESA"
    id_categoria: UUID
    id_empresa: UUID
    id_conta: Optional[UUID] = None
    id_centro_custo: Optional[UUID] = None

class LancamentoUpdate(BaseModel):
    descricao: Optional[str] = None
    valor: Optional[float] = None
    data_lancamento: Optional[str] = None
    data_pagamento: Optional[str] = None
    tipo: Optional[str] = None  # "RECEITA" ou "DESPESA"
    status: Optional[str] = None  # "PENDENTE", "PAGO" ou "CANCELADO"
    id_categoria: Optional[UUID] = None

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    pages: int

# Funções utilitárias
def paginate(items: List[Any], total: int, page: int, page_size: int) -> Dict[str, Any]:
    """
    Cria uma resposta paginada a partir de uma lista de itens.
    
    Args:
        items: Lista de itens para paginar
        total: Total de itens (sem paginação)
        page: Página atual (começando de 1)
        page_size: Tamanho da página
    
    Returns:
        Dicionário com os itens paginados e metadados
    """
    # Cálculo do total de páginas
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    
    # Ajuste da página atual se estiver fora dos limites
    page = max(1, min(page, pages))
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages
    }

# Rotas
@app.get("/health")
async def health_check():
    """Verificação de saúde da API."""
    return {"status": "ok", "version": "1.0.0-test"}

@app.get("/api/v1/dashboard/resumo")
async def dashboard_resumo():
    """Dados resumidos para o dashboard financeiro."""
    # Dados mockados para o dashboard
    hoje = datetime.now().strftime("%Y-%m-%d")
    
    # Gerar dados de fluxo dos últimos 10 dias
    fluxo_diario = []
    for i in range(10, 0, -1):
        data_anterior = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        # Valores variados - positivos e negativos
        valor = float(f"{((-1) ** i) * (500 + i * 120) + (i * 50):.2f}")
        fluxo_diario.append({"data": data_anterior, "valor": valor})
    
    # Adicionar dados para o dia atual
    fluxo_diario.append({"data": hoje, "valor": 1250.00 - 750.35})
    
    return {
        "caixaAtual": 23574.89,
        "aReceber": 15680.23,
        "aPagar": 5240.78,
        "recebimentosHoje": 1250.00,
        "pagamentosHoje": 750.35,
        "saldoLiquido": 18334.11,
        "fluxoDiario": fluxo_diario
    }

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
    """Listar lançamentos financeiros com filtros e paginação."""
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

@app.put("/api/v1/lancamentos/{id_lancamento}", response_model=LancamentoWithDetalhes)
async def atualizar_lancamento(
    id_lancamento: UUID,
    lancamento_update: LancamentoUpdate,
    id_empresa: UUID = Query(..., description="ID da empresa"),
):
    """Atualizar um lançamento existente."""
    return LancamentoWithDetalhes(
        id=id_lancamento,
        descricao=lancamento_update.descricao or "Lançamento atualizado",
        valor=lancamento_update.valor or 200.0,
        data_lancamento=lancamento_update.data_lancamento or "2023-01-01",
        data_pagamento=lancamento_update.data_pagamento,
        tipo=lancamento_update.tipo or "DESPESA",
        status=lancamento_update.status or "PENDENTE",
        id_categoria=lancamento_update.id_categoria or UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6"),
        id_empresa=id_empresa,
        categoria_nome="Categoria Atualizada",
        conta_nome="Conta Atualizada",
        centro_custo_nome="Centro de Custo Atualizado",
        criado_por="Usuário Teste",
        criado_em="2023-01-01T10:00:00",
        atualizado_em=datetime.now().isoformat()
    )

@app.delete("/api/v1/lancamentos/{id_lancamento}")
async def excluir_lancamento(
    id_lancamento: UUID,
    id_empresa: UUID = Query(..., description="ID da empresa"),
):
    """Excluir um lançamento existente."""
    # Numa API real, aqui seria feita a busca e exclusão no banco
    # Nesse caso, apenas simulamos a exclusão retornando uma resposta de sucesso
    return {"message": "Lançamento excluído com sucesso", "id": str(id_lancamento)}

if __name__ == "__main__":
    print("Iniciando servidor de teste...")
    print("Acesse: http://localhost:8002/docs para ver a documentação")
    uvicorn.run(app, host="0.0.0.0", port=8002) 