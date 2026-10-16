"""Leitura das chaves de API a partir de variáveis de ambiente / arquivo .env."""

import os

from dotenv import load_dotenv

# Carrega o arquivo .env (se existir) para os.environ.
load_dotenv()


class ConfigError(Exception):
    """Configuração obrigatória ausente (ex.: chave de API)."""


def require_key(name: str) -> str:
    """Retorna o valor da variável de ambiente ou levanta ConfigError."""
    value = os.getenv(name, "").strip()
    if not value:
        raise ConfigError(
            f"Variável {name} não configurada. Copie .env.example para .env e preencha."
        )
    return value
