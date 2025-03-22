"""Módulo com classes base para modelos do sistema."""
from datetime import datetime
from typing import Optional
from sqlalchemy import func
from sqlalchemy.orm import mapped_column, Mapped, declared_attr


class TimestampedModel:
    """
    Classe base para adicionar colunas de timestamp a modelos.
    
    Utilizada como mixin para adicionar campos created_at e updated_at automaticamente
    mantidos pelo SQLAlchemy.
    """
    
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        onupdate=func.now(),
        nullable=True
    ) 