"""Configurações do projeto."""
from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, PostgresDsn, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações do projeto."""
    PROJECT_NAME: str = "CCONTROL"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # JWT
    SECRET_KEY: str = "your-secret-key"  # Alterar em produção
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 dias
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Valida as origens CORS."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "ccontrol"
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    
    @model_validator(mode="before")
    def assemble_db_connection(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Monta a URL de conexão com o banco de dados."""
        if values.get("SQLALCHEMY_DATABASE_URI"):
            return values
        
        values["SQLALCHEMY_DATABASE_URI"] = PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}"
        )
        return values
    
    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    @field_validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        """Retorna o nome do projeto se o nome do remetente não for definido."""
        if not v:
            return values.data.get("PROJECT_NAME", "")
        return v
    
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEMPLATES_DIR: str = "app/email-templates"
    EMAILS_ENABLED: bool = False
    
    @model_validator(mode="before")
    def get_emails_enabled(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica se o envio de emails está habilitado."""
        values["EMAILS_ENABLED"] = bool(
            values.get("SMTP_HOST")
            and values.get("SMTP_PORT")
            and values.get("EMAILS_FROM_EMAIL")
        )
        return values
    
    # Backup
    BACKUP_DIR: str = "backups"
    BACKUP_RETENTION_DAYS: int = 7
    
    # Logs
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        extra="allow"
    )


settings = Settings() 