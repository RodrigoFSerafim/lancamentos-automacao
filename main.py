#!/usr/bin/env python3
"""CLI do Rastreador de Lançamentos (filmes, séries e jogos).

Exemplos:
    python main.py search "dune" --type movie
    python main.py add movie 693134
    python main.py list
    python main.py check --days 7
    python main.py upcoming --type game
"""

import argparse
import sys

from tracker import rawg, tmdb
from tracker.checker import check_watchlist, fetch_release
from tracker.config import ConfigError
from tracker.http import ApiError
from tracker.models import KIND_LABELS, KINDS, Release
from tracker.notifier import notify
from tracker.storage import Watchlist


def format_release(release: Release) -> str:
    """Linha legível com tipo, título, id e data."""
    when = (
        release.release_date.strftime("%d/%m/%Y")
        if release.release_date
        else "sem data"
    )
    note = f" ({release.note})" if release.note else ""
    return f"[{KIND_LABELS[release.kind]}] {release.title} | id {release.id} | {when}{note}"


def search_releases(kind: str, query: str):
    return rawg.search(query) if kind == "game" else tmdb.search(kind, query)


def upcoming_releases(kind: str, days: int):
    return rawg.upcoming(days) if kind == "game" else tmdb.upcoming(kind, days)


def run_for_kinds(kind_arg: str, action):
    """Executa `action(kind)` para um tipo ou para todos ('all').

    No modo 'all', um erro em uma API (ex.: chave ausente) vira só um aviso,
    para que as demais continuem funcionando.
    """
    kinds = KINDS if kind_arg == "all" else (kind_arg,)
    found = False
    for kind in kinds:
        try:
            results = action(kind)
        except (ConfigError, ApiError) as exc:
            if kind_arg != "all":
                raise
            print(f"Aviso ({KIND_LABELS[kind]}): {exc}")
            continue
        for release in results:
            print(format_release(release))
            found = True
    if not found:
        print("Nenhum resultado.")


# ---- comandos ---------------------------------------------------------------
def cmd_search(args):
    run_for_kinds(args.type, lambda kind: search_releases(kind, args.query))


def cmd_upcoming(args):
    run_for_kinds(args.type, lambda kind: upcoming_releases(kind, args.days))


def cmd_add(args):
    # Consulta a API antes de salvar: valida o id e obtém o título oficial.
    release = fetch_release(args.type, args.id)
    if Watchlist().add(release.kind, release.id, release.title):
        print(f"Adicionado: {format_release(release)}")
    else:
        print("Esse item já está na sua lista.")


def cmd_remove(args):
    if Watchlist().remove(args.type, args.id):
        print("Removido.")
    else:
        print("Esse item não está na sua lista.")


def cmd_list(_args):
    items = Watchlist().items
    if not items:
        print("Sua lista está vazia. Use 'search' e 'add' para começar.")
    for item in items:
        print(f"[{KIND_LABELS[item['kind']]}] {item['title']} | id {item['id']}")


def cmd_check(args):
    sent = check_watchlist(Watchlist(), args.days, notify)
    if not sent:
        print(f"Nenhuma estreia nova nos próximos {args.days} dia(s).")


# ---- parser -----------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Rastreador de lançamentos de filmes, séries e jogos."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("search", help="busca um título pelo nome")
    p.add_argument("query")
    p.add_argument("--type", choices=("all",) + KINDS, default="all")
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("upcoming", help="lista os próximos lançamentos")
    p.add_argument("--type", choices=("all",) + KINDS, default="all")
    p.add_argument("--days", type=int, default=90, help="janela em dias (padrão: 90)")
    p.set_defaults(func=cmd_upcoming)

    p = sub.add_parser("add", help="adiciona um título à sua lista")
    p.add_argument("type", choices=KINDS)
    p.add_argument("id", type=int)
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("remove", help="remove um título da sua lista")
    p.add_argument("type", choices=KINDS)
    p.add_argument("id", type=int)
    p.set_defaults(func=cmd_remove)

    p = sub.add_parser("list", help="mostra os títulos que você acompanha")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("check", help="verifica estreias próximas e notifica")
    p.add_argument("--days", type=int, default=7, help="avisar estreias em até N dias")
    p.set_defaults(func=cmd_check)

    return parser


def main() -> int:
    # Garante emojis/acentos corretos em consoles que não usam UTF-8 (ex.: Windows).
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    args = build_parser().parse_args()
    try:
        args.func(args)
    except (ConfigError, ApiError) as exc:
        print(f"Erro: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
