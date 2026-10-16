"""Integração com a API do RAWG (jogos).

Documentação: https://api.rawg.io/docs/
"""

from datetime import date, timedelta
from typing import List

from .config import require_key
from .http import get_json
from .models import Release, parse_date

BASE_URL = "https://api.rawg.io/api"


def _get(path: str, **params):
    """GET autenticado (chave via query string)."""
    params["key"] = require_key("RAWG_API_KEY")
    return get_json(f"{BASE_URL}{path}", params)


def _to_release(game: dict) -> Release:
    note = "data a confirmar" if game.get("tba") else ""
    return Release(
        kind="game",
        id=game["id"],
        title=game.get("name", "(sem título)"),
        release_date=parse_date(game.get("released")),
        note=note,
    )


def search(query: str, limit: int = 10) -> List[Release]:
    """Busca jogos pelo nome."""
    data = _get("/games", search=query, page_size=limit)
    return [_to_release(game) for game in data.get("results", [])]


def get_release(game_id: int) -> Release:
    """Consulta a data de lançamento atual de um jogo."""
    return _to_release(_get(f"/games/{game_id}"))


def upcoming(days: int = 90, limit: int = 10) -> List[Release]:
    """Lista os jogos que serão lançados nos próximos `days` dias."""
    start = date.today()
    end = start + timedelta(days=days)
    data = _get(
        "/games",
        dates=f"{start.isoformat()},{end.isoformat()}",
        ordering="released",
        page_size=limit,
    )
    return [_to_release(game) for game in data.get("results", [])]
