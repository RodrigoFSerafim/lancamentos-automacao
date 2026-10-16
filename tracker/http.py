"""Cliente HTTP mínimo usado pelos módulos de API."""

from typing import Any, Dict

import requests

TIMEOUT = 10  # segundos


class ApiError(Exception):
    """Falha ao consultar uma API externa."""


def get_json(url: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Faz um GET e devolve o JSON.

    As mensagens de erro NÃO incluem a URL completa, porque ela carrega a
    chave de API na query string e acabaria vazando no terminal/logs.
    """
    try:
        response = requests.get(url, params=params, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "?"
        raise ApiError(f"A API respondeu com HTTP {status}.") from None
    except requests.RequestException as exc:
        raise ApiError(f"Falha de rede ({type(exc).__name__}).") from None
    except ValueError:
        raise ApiError("A API devolveu uma resposta que não é JSON válido.") from None
