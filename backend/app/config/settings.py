from typing import List
from pydantic import field_validator, AnyHttpUrl, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Configurações da aplicação
    APP_NAME: str = "CCONTROL-M"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Banco de dados
    DATABASE_URL: PostgresDsn = "postgresql://postgres:postgres@localhost:5432/ccontrolm"

    # Segurança (JWT)
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # Monitoramento
    ENABLE_MONITORING: bool = True
    SLOW_QUERY_THRESHOLD: float = 1.0
    COLLECT_METRICS_INTERVAL: int = 60

    # Cache
    CACHE_EXPIRATION: int = 900  # 15 minutos

    # Paginação
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Uploads
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5 MB
    ALLOWED_EXTENSIONS: List[str] = ["png", "jpg", "jpeg", "pdf", "xlsx", "xls", "csv", "txt"]

    # E-mail
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False

    @field_validator("SECRET_KEY")
    def validate_secret_key(cls, v: str) -> str:
        if not v or len(v) < 32:
            raise ValueError("A chave secreta deve ter pelo menos 32 caracteres")
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings() 