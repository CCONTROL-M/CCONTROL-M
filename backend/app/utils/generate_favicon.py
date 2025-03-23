"""
Utilitário para gerar favicon para a documentação da API.
Este script cria um ícone simples com as iniciais "C-M" para o CCONTROL-M.
"""

import os
import sys
import logging
from pathlib import Path

# Configurar logger
logger = logging.getLogger(__name__)

# Verificar se PIL está disponível
PIL_AVAILABLE = False
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    logger.warning("Biblioteca PIL (Pillow) não encontrada. A geração de favicon será desativada.")

def generate_favicon():
    """Gera um favicon simples com as iniciais do projeto."""
    if not PIL_AVAILABLE:
        logger.warning("Não é possível gerar favicon: PIL (Pillow) não está instalado.")
        return False
        
    try:
        # Definir o caminho de saída do favicon
        current_dir = Path(__file__).parent
        static_dir = current_dir.parent / "static"
        os.makedirs(static_dir, exist_ok=True)
        favicon_path = static_dir / "favicon.png"
        
        # Verificar se o favicon já existe
        if os.path.exists(favicon_path):
            logger.info(f"Favicon já existe em: {favicon_path}")
            return True
        
        # Criar imagem de fundo
        img_size = (64, 64)
        background_color = (25, 118, 210)  # Azul
        text_color = (255, 255, 255)  # Branco
        
        # Criar a imagem e o objeto de desenho
        img = Image.new('RGB', img_size, background_color)
        draw = ImageDraw.Draw(img)
        
        try:
            # Tentar carregar uma fonte, ou usar o padrão
            font = ImageFont.truetype("arial.ttf", 24)
        except IOError:
            font = ImageFont.load_default()
        
        # Desenhar texto
        text = "C-M"
        text_width, text_height = draw.textsize(text, font=font) if hasattr(draw, 'textsize') else font.getsize(text)
        text_position = ((img_size[0] - text_width) // 2, (img_size[1] - text_height) // 2)
        draw.text(text_position, text, font=font, fill=text_color)
        
        # Salvar o favicon
        img.save(favicon_path)
        logger.info(f"Favicon gerado em: {favicon_path}")
        return True
    except Exception as e:
        logger.error(f"Erro ao gerar favicon: {str(e)}")
        return False

if __name__ == "__main__":
    generate_favicon() 