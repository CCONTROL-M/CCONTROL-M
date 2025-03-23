"""
Validações extras centralizadas para o sistema CCONTROL-M.

Este módulo centraliza validações comuns utilizadas em diferentes partes do sistema,
evitando duplicação de código e mantendo consistência nas validações.
"""
from typing import List, Optional, Dict, Any
import re
from datetime import datetime
from decimal import Decimal
from validate_docbr import CPF, CNPJ

# Instâncias dos validadores
_cpf = CPF()
_cnpj = CNPJ()

# Expressões regulares para validação
REGEX_PATTERNS = {
    "cep": re.compile(r"^\d{5}-?\d{3}$"),
    "telefone": re.compile(r"^\(?(?:[14689][1-9]|2[12478]|3[1234578]|5[1345]|7[134579])\)? ?(?:[2-8]|9[1-9])[0-9]{3}(?:-| )?[0-9]{4}$"),
    "data": re.compile(r"^(?:19|20)\d\d[- /.](?:0[1-9]|1[012])[- /.](?:0[1-9]|[12][0-9]|3[01])$"),
    "decimal": re.compile(r"^-?\d*[.,]?\d+$"),
    "email": re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._%+-]*@[a-zA-Z0-9][a-zA-Z0-9.-]*\.[a-zA-Z]{2,}$")
}

# Lista de UFs válidas
UFS_VALIDAS = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", 
    "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", 
    "SP", "SE", "TO"
]

def validar_cep(cep: Optional[str]) -> str:
    """
    Valida e formata um CEP.
    
    Args:
        cep: String contendo o CEP a ser validado
        
    Returns:
        String do CEP formatado (00000-000)
        
    Raises:
        ValueError: Se o CEP for inválido
    """
    if not cep or not isinstance(cep, str):
        raise ValueError("CEP não pode ser vazio")
        
    # Remover caracteres não numéricos
    cep_limpo = re.sub(r'[^\d]', '', cep)
    
    # Verificar se tem 8 dígitos
    if len(cep_limpo) != 8:
        raise ValueError("CEP deve conter 8 dígitos")
        
    # Formatar como padrão: 00000-000
    return f"{cep_limpo[:5]}-{cep_limpo[5:]}"

def validar_uf(uf: Optional[str]) -> str:
    """
    Valida uma UF.
    
    Args:
        uf: String contendo a UF a ser validada
        
    Returns:
        String da UF em maiúsculas
        
    Raises:
        ValueError: Se a UF for inválida
    """
    if not uf or not isinstance(uf, str):
        raise ValueError("UF não pode ser vazia")
        
    uf = uf.upper()
    if uf not in UFS_VALIDAS:
        raise ValueError("UF inválida")
    return uf

def validar_telefone(telefone: Optional[str]) -> str:
    """
    Valida e formata um número de telefone.
    
    Args:
        telefone: String contendo o telefone a ser validado
        
    Returns:
        String do telefone formatado ((00) 00000-0000)
        
    Raises:
        ValueError: Se o telefone for inválido
    """
    if not telefone or not isinstance(telefone, str):
        raise ValueError("Telefone não pode ser vazio")
        
    # Remover caracteres não numéricos
    tel_limpo = re.sub(r'[^\d]', '', telefone)
    
    # Verificar comprimento
    if len(tel_limpo) < 10 or len(tel_limpo) > 11:
        raise ValueError("Telefone deve ter 10 ou 11 dígitos")
    
    # Verificar DDD
    ddd = tel_limpo[:2]
    if not REGEX_PATTERNS["telefone"].match(tel_limpo):
        raise ValueError("Telefone inválido")
    
    # Formatar
    if len(tel_limpo) == 11:
        return f"({ddd}) {tel_limpo[2:7]}-{tel_limpo[7:]}"
    return f"({ddd}) {tel_limpo[2:6]}-{tel_limpo[6:]}"

def validar_data(data: Optional[str], formatos: Optional[List[str]] = None) -> str:
    """
    Valida uma data em diferentes formatos.
    
    Args:
        data: String contendo a data a ser validada
        formatos: Lista de formatos aceitos (padrão: ['%Y-%m-%d', '%d/%m/%Y'])
        
    Returns:
        String da data no formato original se válida
        
    Raises:
        ValueError: Se a data for inválida
    """
    if not data or not isinstance(data, str):
        raise ValueError("Data não pode ser vazia")
        
    if not formatos:
        formatos = ['%Y-%m-%d', '%d/%m/%Y']
        
    for fmt in formatos:
        try:
            datetime.strptime(data, fmt)
            return data
        except ValueError:
            continue
            
    raise ValueError(f"Data inválida. Formatos aceitos: {', '.join(formatos)}")

def validar_decimal(valor: Any) -> Decimal:
    """
    Valida e converte um valor para Decimal.
    
    Args:
        valor: Valor a ser validado e convertido
        
    Returns:
        Decimal do valor convertido
        
    Raises:
        ValueError: Se o valor não puder ser convertido para Decimal
    """
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        raise ValueError("Valor decimal não pode ser vazio")
        
    try:
        if isinstance(valor, str):
            valor = valor.replace(',', '.')
        return Decimal(str(valor))
    except:
        raise ValueError("Valor decimal inválido")

def validar_email(email: Optional[str]) -> str:
    """
    Valida um endereço de e-mail.
    
    Args:
        email: String contendo o e-mail a ser validado
        
    Returns:
        String do e-mail se válido
        
    Raises:
        ValueError: Se o e-mail for inválido
    """
    if not email or not isinstance(email, str):
        raise ValueError("E-mail não pode ser vazio")
        
    # Remover espaços em branco
    email = email.strip()
    
    # Verificar se tem caracteres especiais não permitidos
    if re.search(r'[^\x00-\x7F]', email):
        raise ValueError("E-mail não pode conter caracteres especiais")
        
    # Verificar se tem dois pontos consecutivos
    if '..' in email:
        raise ValueError("E-mail não pode conter dois pontos consecutivos")
        
    # Verificar se tem espaços
    if ' ' in email:
        raise ValueError("E-mail não pode conter espaços")
        
    # Verificar formato geral
    if not REGEX_PATTERNS["email"].match(email):
        raise ValueError("E-mail inválido")
        
    return email

def validar_tipo_contato(tipo: Optional[str]) -> str:
    """
    Valida o tipo de contato.
    
    Args:
        tipo: String contendo o tipo de contato
        
    Returns:
        String do tipo de contato em minúsculas
        
    Raises:
        ValueError: Se o tipo de contato for inválido
    """
    if not tipo or not isinstance(tipo, str):
        raise ValueError("Tipo de contato não pode ser vazio")
        
    tipos_validos = ["celular", "telefone", "email", "whatsapp", "instagram", "facebook", "outro"]
    tipo = tipo.lower()
    if tipo not in tipos_validos:
        raise ValueError(f"Tipo de contato inválido. Tipos válidos: {', '.join(tipos_validos)}")
    return tipo

def validar_valor_contato(tipo: Optional[str], valor: Optional[str]) -> str:
    """
    Valida o valor do contato com base no tipo.
    
    Args:
        tipo: String contendo o tipo de contato
        valor: String contendo o valor do contato
        
    Returns:
        String do valor validado e formatado
        
    Raises:
        ValueError: Se o valor for inválido para o tipo
    """
    if not tipo or not isinstance(tipo, str):
        raise ValueError("Tipo de contato não pode ser vazio")
        
    if not valor or not isinstance(valor, str):
        raise ValueError("Valor do contato não pode ser vazio")
        
    tipo = tipo.lower()
    
    if tipo in ["celular", "telefone", "whatsapp"]:
        return validar_telefone(valor)
    elif tipo == "email":
        return validar_email(valor)
    
    return valor  # Para outros tipos, retorna o valor original 