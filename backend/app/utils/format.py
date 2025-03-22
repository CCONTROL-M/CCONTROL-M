"""Utilitários de formatação para o sistema CCONTROL-M."""
from datetime import datetime, date, time, timedelta
from typing import Optional, Union, Dict, Any
import re


def parse_date(date_str: Optional[str], end_of_day: bool = False) -> Optional[datetime]:
    """
    Converte uma string de data no formato YYYY-MM-DD para objeto datetime.
    
    Args:
        date_str: String de data no formato YYYY-MM-DD
        end_of_day: Se True, retorna a data com hora 23:59:59, caso contrário 00:00:00
        
    Returns:
        Objeto datetime ou None se a string for inválida
    """
    if not date_str:
        return None
        
    try:
        # Tenta converter diretamente se for uma data ISO
        if "T" in date_str:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            
        # Padrão YYYY-MM-DD
        pattern = r"^(\d{4})-(\d{1,2})-(\d{1,2})$"
        match = re.match(pattern, date_str)
        
        if match:
            year, month, day = map(int, match.groups())
            base_date = date(year, month, day)
            
            if end_of_day:
                return datetime.combine(base_date, time(23, 59, 59))
            else:
                return datetime.combine(base_date, time.min)
                
        return None
    except (ValueError, TypeError):
        return None


def format_decimal(value: Union[float, int], decimal_places: int = 2) -> str:
    """
    Formata um valor decimal com número específico de casas decimais.
    
    Args:
        value: Valor para formatar
        decimal_places: Número de casas decimais
        
    Returns:
        String formatada com o valor
    """
    if value is None:
        return "0,00"
        
    format_string = f"{{:.{decimal_places}f}}"
    formatted = format_string.format(value).replace(".", ",")
    
    return formatted


def format_currency(value: Union[float, int], symbol: str = "R$") -> str:
    """
    Formata um valor como moeda brasileira.
    
    Args:
        value: Valor para formatar
        symbol: Símbolo da moeda
        
    Returns:
        String formatada como moeda
    """
    if value is None:
        return f"{symbol} 0,00"
        
    # Formatar com duas casas decimais
    formatted = format_decimal(value, 2)
    
    # Adicionar separador de milhar
    parts = formatted.split(",")
    integer_part = parts[0]
    decimal_part = parts[1] if len(parts) > 1 else "00"
    
    # Adicionar separador de milhar para valores maiores
    if len(integer_part) > 3:
        groups = []
        while integer_part:
            groups.insert(0, integer_part[-3:])
            integer_part = integer_part[:-3]
        integer_part = ".".join(groups)
    
    return f"{symbol} {integer_part},{decimal_part}"


def format_percentage(value: Union[float, int], decimal_places: int = 2) -> str:
    """
    Formata um valor como porcentagem.
    
    Args:
        value: Valor para formatar (0.1 = 10%)
        decimal_places: Número de casas decimais
        
    Returns:
        String formatada como porcentagem
    """
    if value is None:
        return "0%"
        
    # Multiplicar por 100 para converter para porcentagem
    value_percent = value * 100
    
    # Formatar com casas decimais especificadas
    formatted = format_decimal(value_percent, decimal_places)
    
    return f"{formatted}%" 