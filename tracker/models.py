"""Modelos de dados compartilhados entre os módulos."""

from dataclasses import dataclass
from datetime import date
from typing import Optional

# Tipos de mídia aceitos. "movie" e "tv" vêm do TMDB; "game" vem do RAWG.
KINDS = ("movie", "tv", "game")
KIND_LABELS = {"movie": "Filme", "tv": "Série", "game": "Jogo"}


@dataclass
class Release:
    """Um lançamento (filme, série ou jogo) com a sua data de estreia."""

    kind: str
    id: int
    title: str
    release_date: Optional[date] = None
    note: str = ""  # ex.: "S02E05" para séries ou "data a confirmar" para jogos


def parse_date(value: Optional[str]) -> Optional[date]:
    """Converte 'AAAA-MM-DD' em date. Retorna None se vazio ou inválido."""
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None
