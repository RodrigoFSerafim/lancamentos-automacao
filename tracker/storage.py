"""Persistência da watchlist em um arquivo JSON local."""

import json
from pathlib import Path
from typing import Dict, List

# data/watchlist.json na raiz do projeto, independente de onde o script roda.
DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "watchlist.json"


class Watchlist:
    """Lista de títulos acompanhados + registro do que já foi notificado."""

    def __init__(self, path: Path = DEFAULT_PATH):
        self.path = Path(path)
        self._data: Dict[str, list] = {"items": [], "notified": []}
        if self.path.exists():
            self._data = json.loads(self.path.read_text(encoding="utf-8"))

    # ---- itens acompanhados -------------------------------------------------
    @property
    def items(self) -> List[dict]:
        return list(self._data["items"])

    def add(self, kind: str, item_id: int, title: str) -> bool:
        """Adiciona um item. Retorna False se já estava na lista."""
        if self._find(kind, item_id) is not None:
            return False
        self._data["items"].append({"kind": kind, "id": item_id, "title": title})
        self._save()
        return True

    def remove(self, kind: str, item_id: int) -> bool:
        """Remove um item. Retorna False se não estava na lista."""
        found = self._find(kind, item_id)
        if found is None:
            return False
        self._data["items"].remove(found)
        self._save()
        return True

    # ---- controle de notificações ------------------------------------------
    def was_notified(self, key: str) -> bool:
        return key in self._data["notified"]

    def mark_notified(self, key: str) -> None:
        if key not in self._data["notified"]:
            self._data["notified"].append(key)
            self._save()

    # ---- internos -----------------------------------------------------------
    def _find(self, kind: str, item_id: int):
        for item in self._data["items"]:
            if item["kind"] == kind and item["id"] == item_id:
                return item
        return None

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self._data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
