"""Módulo com classes base para modelos do sistema."""
from datetime import datetime
from typing import Optional
from sqlalchemy import func
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.ext.declarative import declared_attr


class TimestampedModel:
    """
    Mixin para adicionar campos de timestamp (created_at e updated_at) aos modelos.
    
    Esta classe deve ser herdada por todos os modelos que precisam desses campos.
    """
    
    @declared_attr
    def created_at(cls) -> Mapped[Optional[datetime]]:
        """Data e hora de criação do registro."""
        return mapped_column(default=func.now(), nullable=True)
    
    @declared_attr
    def updated_at(cls) -> Mapped[Optional[datetime]]:
        """Data e hora da última atualização do registro."""
        return mapped_column(default=func.now(), onupdate=func.now(), nullable=True) 