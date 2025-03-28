from typing import List, Optional, Set, Union
from pydantic import field_validator, AnyHttpUrl, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from dotenv import load_dotenv


# Carregar variáveis de ambiente do arquivo .env
load_dotenv(".env")

# Carregar variáveis de ambiente do arquivo .env.prod em produção
if os.getenv("APP_ENV") == "production":
    load_dotenv(".env.prod", override=True)


class Settings(BaseSettings):
    # Configurações da aplicação
    APP_NAME: str = "CCONTROL-M"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = os.getenv("APP_ENV", "development")
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    PROJECT_NAME: str = "CCONTROL-M"
    ALLOWED_HOSTS: List[str] = ["*"]
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR: str = os.getenv("LOG_DIR", "logs")

    # Banco de dados
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+asyncpg://postgres:postgres@localhost/ccontrolm"
    )
    DATABASE_URL_TEST: str = os.getenv(
        "DATABASE_URL_TEST",
        "postgresql+asyncpg://postgres:postgres@localhost/ccontrolm_test"
    )

    # Segurança (JWT)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-for-development-only")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 horas
    SECURE_COOKIES: bool = False
    
    # OAuth e Swagger UI
    CLIENT_ID: str = os.getenv("CLIENT_ID", "ccontrolm-webapp")
    CLIENT_SECRET: str = os.getenv("CLIENT_SECRET", "ccontrolm-secret")
    SWAGGER_UI_OAUTH2_REDIRECT_URL: str = "/api/v1/oauth2-redirect"
    SWAGGER_UI_CLIENT_ID: str = CLIENT_ID
    SWAGGER_UI_CLIENT_SECRET: str = CLIENT_SECRET

    # Monitoramento
    ENABLE_MONITORING: bool = os.getenv("ENABLE_MONITORING", "true").lower() == "true"
    SLOW_QUERY_THRESHOLD: float = float(os.getenv("SLOW_QUERY_THRESHOLD", "1.0"))  # segundos
    SLOW_REQUEST_THRESHOLD: float = float(os.getenv("SLOW_REQUEST_THRESHOLD", "1.0"))  # segundos
    COLLECT_METRICS_INTERVAL: int = int(os.getenv("COLLECT_METRICS_INTERVAL", "60"))  # segundos
    METRICS_RETENTION_DAYS: int = int(os.getenv("METRICS_RETENTION_DAYS", "7"))
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    METRICS_BASIC_AUTH: bool = os.getenv("METRICS_BASIC_AUTH", "true").lower() == "true"
    METRICS_USERNAME: str = os.getenv("METRICS_USERNAME", "prometheus")
    METRICS_PASSWORD: str = os.getenv("METRICS_PASSWORD", "ccontrolm")
    ENABLE_DB_METRICS: bool = os.getenv("ENABLE_DB_METRICS", "false").lower() == "true"
    PROMETHEUS_NAMESPACE: str = os.getenv("PROMETHEUS_NAMESPACE", "ccontrolm")

    # Cache
    CACHE_EXPIRY: int = int(os.getenv("CACHE_EXPIRATION", "300"))  # 5 minutos

    # Paginação
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100

    # Uploads
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS: List[str] = ["png", "jpg", "jpeg", "pdf", "xlsx", "xls", "csv", "txt"]

    # E-mail (valores padrão para desenvolvimento)
    MAIL_USERNAME: Optional[str] = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD: Optional[str] = os.getenv("MAIL_PASSWORD")
    MAIL_FROM: Optional[str] = os.getenv("MAIL_FROM")
    MAIL_PORT: Optional[int] = int(os.getenv("MAIL_PORT", "587"))
    MAIL_SERVER: Optional[str] = os.getenv("MAIL_SERVER")
    MAIL_FROM_NAME: Optional[str] = os.getenv("MAIL_FROM_NAME", APP_NAME)
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False

    # Supabase
    SUPABASE_URL: str = "https://seu-projeto.supabase.co"
    SUPABASE_ANON_KEY: str = "sua-chave-anon-aqui"
    SUPABASE_DB_HOST: str = "db.seu-projeto.supabase.co"
    SUPABASE_DB_PORT: int = 5432
    SUPABASE_DB_NAME: str = "postgres"
    SUPABASE_DB_USER: str = "postgres"
    SUPABASE_DB_PASSWORD: str = "sua-senha-db-supabase"
    
    # Configurações adicionais
    PORT: int = 8000
    WORKERS: int = 4
    ENABLE_HEALTH_CHECK: bool = True
    CORS_ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3003", "http://127.0.0.1:3003", "http://localhost:8000", "http://localhost"]
    CORS_ALLOWED_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    CORS_ALLOWED_HEADERS: List[str] = ["Content-Type", "Authorization", "X-Requested-With", "X-Request-ID"]
    CORS_ALLOW_CREDENTIALS: bool = True
    SENTRY_DSN: str = ""
    ENABLE_HTTPS_REDIRECT: bool = False
    
    # Parâmetros de segurança HTTP
    SECURITY_HEADERS: bool = True  # Se os cabeçalhos de segurança devem ser adicionados
    HSTS_ENABLED: bool = False  # HTTP Strict Transport Security
    HSTS_MAX_AGE: int = 31536000  # 1 ano em segundos
    
    # Parâmetros de rate limiting (limitação de taxa)
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # segundos
    RATE_LIMIT_BY_IP: bool = True
    RATE_LIMIT_BY_USER: bool = True
    RATE_LIMIT_USER_MULTIPLIER: float = 2.0  # Usuários autenticados têm o dobro do limite
    RATE_LIMIT_ADMIN_EXEMPT: bool = True  # Administradores estão isentos
    RATE_LIMIT_EXEMPT_PATHS: List[str] = [
        "/health", 
        "/api/v1/docs", 
        "/api/v1/openapi.json",
        "/api/v1/auth/token",
        "/api/metrics"
    ]

    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD", None)

    # Auditoria
    ENABLE_AUDIT_LOG: bool = True
    SENSITIVE_FIELDS: List[str] = [
        "password", "senha", "token", "secret", 
        "credit_card", "cartao_credito", "cpf", "cnpj",
        "api_key", "authorization", "auth", "key"
    ]
    AUDIT_IGNORE_PATHS: List[str] = [
        "/health", 
        "/api/v1/docs", 
        "/api/v1/openapi.json",
        "/api/metrics"
    ]
    
    # Logging
    REQUEST_LOGGING: bool = True
    MASK_SENSITIVE_DATA: bool = True
    REQUEST_ID_HEADER: str = "X-Request-ID"

    @field_validator("SECRET_KEY")
    def validate_secret_key(cls, v: str) -> str:
        if not v or len(v) < 32:
            raise ValueError("A chave secreta deve ter pelo menos 32 caracteres")
        return v
    
    @field_validator("CORS_ALLOWED_ORIGINS")
    def validate_cors_origins(cls, v: List[str]) -> List[str]:
        if not v:
            return []
        
        # Remover espaços em branco de cada origem
        return [origin.strip() for origin in v if origin.strip()]

    @property
    def is_development(self) -> bool:
        return self.APP_ENV.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        return self.APP_ENV.lower() == "production"
    
    @property
    def is_testing(self) -> bool:
        return self.APP_ENV.lower() == "testing"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Ignorar variáveis de ambiente extras
    )


settings = Settings()

# Configurações específicas para ambiente de produção
if settings.APP_ENV == "production":
    settings.DEBUG = False
    settings.SECURE_COOKIES = True
    settings.ALLOWED_HOSTS = [host for host in settings.ALLOWED_HOSTS if host != "*"]
    settings.CORS_ALLOWED_ORIGINS = [origin for origin in settings.CORS_ALLOWED_ORIGINS if origin != "*"]
    settings.ENABLE_MONITORING = True
    settings.ENABLE_AUDIT_LOG = True
    settings.ENABLE_METRICS = True
    settings.METRICS_BASIC_AUTH = True 