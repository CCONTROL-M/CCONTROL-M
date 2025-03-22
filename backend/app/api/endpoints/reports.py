"""
Endpoints para geração e exportação de relatórios.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.empresa import Empresa
from app.models.produto import Produto
from app.models.centro_custo import CentroCusto
from app.models.categoria import Categoria
from app.schemas.reports import ReportType, ReportFormat, ReportFilter
from app.utils.export import create_report_exporter
from app.utils.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/export/{report_type}")
async def export_report(
    report_type: ReportType,
    format: ReportFormat = ReportFormat.PDF,
    filters: Optional[ReportFilter] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_active_user),
) -> str:
    """
    Exporta relatório no formato especificado.
    
    Args:
        report_type: Tipo do relatório
        format: Formato de exportação (PDF ou Excel)
        filters: Filtros a serem aplicados
        db: Sessão do banco de dados
        current_user: Usuário atual
        
    Returns:
        Caminho do arquivo gerado
    """
    try:
        # Criar exportador de relatórios
        exporter = create_report_exporter()
        
        # Preparar dados do relatório
        data = await _get_report_data(report_type, filters, db, current_user)
        
        # Definir nome do arquivo
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{report_type.value}_{timestamp}"
        
        if format == ReportFormat.PDF:
            output_file = f"{filename}.pdf"
            return await exporter.export_to_pdf(
                data=data,
                template_name="base_report.html",
                output_filename=output_file,
                title=_get_report_title(report_type),
                subtitle=_get_report_subtitle(report_type, filters),
                filters=filters.dict() if filters else None
            )
        else:  # Excel
            output_file = f"{filename}.xlsx"
            return await exporter.export_to_excel(
                data=data,
                output_filename=output_file,
                sheet_name=_get_report_title(report_type),
                title=_get_report_title(report_type),
                subtitle=_get_report_subtitle(report_type, filters),
                filters=filters.dict() if filters else None
            )
    
    except Exception as e:
        logger.error(f"Erro ao exportar relatório: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar relatório: {str(e)}"
        )

async def _get_report_data(
    report_type: ReportType,
    filters: Optional[ReportFilter],
    db: Session,
    current_user: User
) -> List[dict]:
    """
    Obtém dados para o relatório especificado.
    
    Args:
        report_type: Tipo do relatório
        filters: Filtros a serem aplicados
        db: Sessão do banco de dados
        current_user: Usuário atual
        
    Returns:
        Lista de dicionários com dados do relatório
    """
    # Aplicar filtro de empresa do usuário
    empresa_id = current_user.empresa_id
    
    if report_type == ReportType.PRODUTOS:
        # Relatório de produtos
        query = db.query(Produto).filter(Produto.empresa_id == empresa_id)
        
        if filters:
            if filters.categoria_id:
                query = query.filter(Produto.categoria_id == filters.categoria_id)
            if filters.search:
                query = query.filter(Produto.nome.ilike(f"%{filters.search}%"))
        
        produtos = query.all()
        return [
            {
                "Código": p.codigo,
                "Nome": p.nome,
                "Categoria": p.categoria.nome if p.categoria else "Sem categoria",
                "Preço": f"R$ {p.preco:.2f}",
                "Estoque": p.estoque,
                "Última Atualização": p.updated_at.strftime("%d/%m/%Y %H:%M")
            }
            for p in produtos
        ]
    
    elif report_type == ReportType.CENTROS_CUSTO:
        # Relatório de centros de custo
        query = db.query(CentroCusto).filter(CentroCusto.empresa_id == empresa_id)
        
        if filters and filters.search:
            query = query.filter(CentroCusto.nome.ilike(f"%{filters.search}%"))
        
        centros = query.all()
        return [
            {
                "Código": c.codigo,
                "Nome": c.nome,
                "Descrição": c.descricao or "",
                "Status": "Ativo" if c.ativo else "Inativo",
                "Criado em": c.created_at.strftime("%d/%m/%Y")
            }
            for c in centros
        ]
    
    elif report_type == ReportType.CATEGORIAS:
        # Relatório de categorias
        query = db.query(Categoria).filter(Categoria.empresa_id == empresa_id)
        
        if filters and filters.search:
            query = query.filter(Categoria.nome.ilike(f"%{filters.search}%"))
        
        categorias = query.all()
        return [
            {
                "Código": c.codigo,
                "Nome": c.nome,
                "Descrição": c.descricao or "",
                "Produtos": len(c.produtos),
                "Criado em": c.created_at.strftime("%d/%m/%Y")
            }
            for c in categorias
        ]
    
    else:
        raise ValueError(f"Tipo de relatório não suportado: {report_type}")

def _get_report_title(report_type: ReportType) -> str:
    """Retorna o título do relatório."""
    titles = {
        ReportType.PRODUTOS: "Relatório de Produtos",
        ReportType.CENTROS_CUSTO: "Relatório de Centros de Custo",
        ReportType.CATEGORIAS: "Relatório de Categorias"
    }
    return titles.get(report_type, "Relatório")

def _get_report_subtitle(
    report_type: ReportType,
    filters: Optional[ReportFilter]
) -> str:
    """Retorna o subtítulo do relatório com base nos filtros."""
    if not filters:
        return None
    
    subtitles = []
    
    if filters.search:
        subtitles.append(f"Pesquisa: {filters.search}")
    
    if filters.categoria_id and report_type == ReportType.PRODUTOS:
        subtitles.append(f"Categoria: {filters.categoria_id}")
    
    if filters.data_inicio and filters.data_fim:
        periodo = f"Período: {filters.data_inicio.strftime('%d/%m/%Y')} a {filters.data_fim.strftime('%d/%m/%Y')}"
        subtitles.append(periodo)
    
    return " | ".join(subtitles) if subtitles else None 