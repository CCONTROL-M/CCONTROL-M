"""Configuração inicial para os testes."""
import logging
from logging.config import dictConfig

# Configurar logging para evitar erros durante os testes
logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
        }
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True
        }
    }
}

# Aplicar configuração de logging
dictConfig(logging_config) 