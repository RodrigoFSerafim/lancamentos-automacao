"""Integração com a API do TMDB (filmes e séries).

Documentação: https://developer.themoviedb.org/reference/intro/getting-started
"""

from datetime import date, timedelta
from typing import List

from .config import require_key
from .http import get_json
from .models import Release, parse_date

BASE_URL = "https://api.themoviedb.org/3"


def _get(path: str, **params):
    """GET autenticado na API v3 (chave via query string)."""
    params["api_key"] = require_key("TMDB_API_KEY")
    params.setdefault("language", "pt-BR")
    return get_json(f"{BASE_URL}{path}", params)


def _to_release(kind: str, item: dict) -> Release:
    """Converte um item de busca/descoberta do TMDB em Release."""
    # Filmes usam "title"/"release_date"; séries usam "name"/"first_air_date".
    title = item.get("title") or item.get("name") or "(sem título)"
    day = parse_date(item.get("release_date") or item.get("first_air_date"))
    return Release(kind=kind, id=item["id"], title=title, release_date=day)


def search(kind: str, query: str, limit: int = 10) -> List[Release]:
    """Busca filmes (kind='movie') ou séries (kind='tv') pelo nome."""
    data = _get(f"/search/{kind}", query=query)
    return [_to_release(kind, item) for item in data.get("results", [])[:limit]]


def get_release(kind: str, item_id: int) -> Release:
    """Consulta a data de estreia atual de um filme ou série."""
    data = _get(f"/{kind}/{item_id}")

    if kind == "movie":
        return Release(
            kind=kind,
            id=item_id,
            title=data.get("title", "(sem título)"),
            release_date=parse_date(data.get("release_date")),
        )

    # Séries: o que interessa é o PRÓXIMO episódio; se não houver, a estreia.
    next_ep = data.get("next_episode_to_air")
    if next_ep:
        note = f"S{next_ep.get('season_number', 0):02d}E{next_ep.get('episode_number', 0):02d}"
        return Release(
            kind=kind,
            id=item_id,
            title=data.get("name", "(sem título)"),
            release_date=parse_date(next_ep.get("air_date")),
            note=note,
        )
    return Release(
        kind=kind,
        id=item_id,
        title=data.get("name", "(sem título)"),
        release_date=parse_date(data.get("first_air_date")),
    )


def upcoming(kind: str, days: int = 90, limit: int = 10) -> List[Release]:
    """Lista os próximos lançamentos (mais populares primeiro) na janela de dias."""
    start = date.today()
    end = start + timedelta(days=days)
    field = "primary_release_date" if kind == "movie" else "first_air_date"
    data = _get(
        f"/discover/{kind}",
        sort_by="popularity.desc",
        **{f"{field}.gte": start.isoformat(), f"{field}.lte": end.isoformat()},
    )
    return [_to_release(kind, item) for item in data.get("results", [])[:limit]]
