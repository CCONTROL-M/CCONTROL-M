"""
Configurações e utilitários para geração de PDFs usando wkhtmltopdf.
"""
import os
from typing import Dict, Optional
from app.core.config import settings
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

# Configurações padrão do wkhtmltopdf
DEFAULT_PDF_OPTIONS = {
    # Configurações gerais
    'quiet': True,  # Não exibir saída do wkhtmltopdf
    'print-media-type': True,  # Usar CSS de impressão
    'enable-local-file-access': True,  # Permitir acesso a arquivos locais
    
    # Configurações de página
    'page-size': 'A4',
    'margin-top': '20mm',
    'margin-right': '20mm',
    'margin-bottom': '20mm',
    'margin-left': '20mm',
    'orientation': 'Portrait',
    
    # Configurações de cabeçalho e rodapé
    'header-font-size': '9',
    'header-spacing': '5',
    'footer-font-size': '9',
    'footer-spacing': '5',
    
    # Configurações de codificação
    'encoding': 'UTF-8',
    
    # Configurações de qualidade
    'image-quality': 100,
    'image-dpi': 300,
}

def get_wkhtmltopdf_path() -> Optional[str]:
    """
    Retorna o caminho do executável wkhtmltopdf.
    
    Returns:
        Caminho do executável ou None se não encontrado
    """
    # Verificar configuração explícita
    if hasattr(settings, 'WKHTMLTOPDF_PATH') and settings.WKHTMLTOPDF_PATH:
        if os.path.exists(settings.WKHTMLTOPDF_PATH):
            return settings.WKHTMLTOPDF_PATH
        else:
            logger.warning(f"Caminho configurado para wkhtmltopdf não existe: {settings.WKHTMLTOPDF_PATH}")
    
    # Caminhos comuns em diferentes sistemas operacionais
    common_paths = [
        # Windows
        r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe',
        r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe',
        # Linux
        '/usr/local/bin/wkhtmltopdf',
        '/usr/bin/wkhtmltopdf',
        # macOS
        '/usr/local/share/wkhtmltopdf',
        '/usr/local/bin/wkhtmltopdf',
    ]
    
    # Verificar caminhos comuns
    for path in common_paths:
        if os.path.exists(path):
            return path
    
    logger.warning("wkhtmltopdf não encontrado nos caminhos padrão")
    return None

def get_pdf_options(
    orientation: str = 'portrait',
    page_size: str = 'A4',
    custom_options: Optional[Dict] = None
) -> Dict:
    """
    Retorna opções configuradas para geração de PDF.
    
    Args:
        orientation: Orientação da página ('portrait' ou 'landscape')
        page_size: Tamanho da página
        custom_options: Opções personalizadas para sobrescrever padrões
        
    Returns:
        Dicionário com opções para wkhtmltopdf
    """
    options = DEFAULT_PDF_OPTIONS.copy()
    
    # Atualizar orientação e tamanho
    options['orientation'] = orientation.capitalize()
    options['page-size'] = page_size.upper()
    
    # Adicionar opções personalizadas
    if custom_options:
        options.update(custom_options)
    
    # Configurar caminho do wkhtmltopdf
    wkhtmltopdf_path = get_wkhtmltopdf_path()
    if wkhtmltopdf_path:
        options['wkhtmltopdf'] = wkhtmltopdf_path
    
    return options

def configure_pdfkit():
    """
    Configura o pdfkit com as opções padrão.
    
    Returns:
        Configuração do pdfkit
    """
    import pdfkit
    
    # Obter caminho do wkhtmltopdf
    wkhtmltopdf_path = get_wkhtmltopdf_path()
    
    if wkhtmltopdf_path:
        config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
    else:
        config = None
        logger.warning("Usando configuração padrão do pdfkit (wkhtmltopdf deve estar no PATH)")
    
    return config 