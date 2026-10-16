"""Lógica principal: consulta as APIs e decide o que notificar."""

from datetime import date
from typing import Callable, List, Optional

from . import rawg, tmdb
from .http import ApiError
from .models import Release
from .storage import Watchlist

EMOJI = {"movie": "🎬", "tv": "📺", "game": "🎮"}


def fetch_release(kind: str, item_id: int) -> Release:
    """Consulta a API correta (TMDB ou RAWG) conforme o tipo do item."""
    if kind == "game":
        return rawg.get_release(item_id)
    return tmdb.get_release(kind, item_id)


def build_message(release: Release, days_left: int) -> str:
    """Monta o texto da notificação."""
    if days_left == 0:
        when = "estreia HOJE"
    elif days_left == 1:
        when = "estreia amanhã"
    else:
        when = f"estreia em {days_left} dias"
    note = f" - {release.note}" if release.note else ""
    return (
        f"{EMOJI.get(release.kind, '')} {release.title}{note} {when} "
        f"({release.release_date.strftime('%d/%m/%Y')})"
    )


def check_watchlist(
    watchlist: Watchlist,
    days: int,
    send: Callable[[str], None],
    today: Optional[date] = None,
) -> List[str]:
    """Verifica cada item da watchlist e notifica estreias nos próximos `days` dias.

    Cada (item + data) só é notificado uma vez; se a data mudar, notifica de novo.
    Retorna a lista de mensagens enviadas.
    """
    today = today or date.today()
    sent: List[str] = []

    for item in watchlist.items:
        try:
            release = fetch_release(item["kind"], item["id"])
        except ApiError as exc:
            # Uma falha em um título não pode derrubar a verificação dos demais.
            print(f"Aviso: não foi possível consultar '{item['title']}': {exc}")
            continue

        if release.release_date is None:
            continue

        days_left = (release.release_date - today).days
        if not 0 <= days_left <= days:
            continue

        key = f"{release.kind}:{release.id}:{release.release_date.isoformat()}"
        if watchlist.was_notified(key):
            continue

        message = build_message(release, days_left)
        send(message)
        watchlist.mark_notified(key)
        sent.append(message)

    return sent
