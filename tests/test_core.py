"""Testes offline: nenhuma chamada real às APIs é feita."""

import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from tracker import tmdb
from tracker.checker import check_watchlist
from tracker.models import Release, parse_date
from tracker.storage import Watchlist

TODAY = date(2026, 10, 16)


class ParseDateTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(parse_date("2026-10-16"), TODAY)

    def test_empty_or_invalid(self):
        self.assertIsNone(parse_date(""))
        self.assertIsNone(parse_date(None))
        self.assertIsNone(parse_date("16/10/2026"))


class WatchlistTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "watchlist.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_add_and_remove(self):
        wl = Watchlist(self.path)
        self.assertTrue(wl.add("movie", 1, "Filme X"))
        self.assertFalse(wl.add("movie", 1, "Filme X"))  # duplicado
        self.assertTrue(wl.remove("movie", 1))
        self.assertFalse(wl.remove("movie", 1))

    def test_persists_to_disk(self):
        Watchlist(self.path).add("game", 7, "Jogo Y")
        self.assertEqual(Watchlist(self.path).items[0]["title"], "Jogo Y")


class CheckWatchlistTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.wl = Watchlist(Path(self.tmp.name) / "watchlist.json")
        self.wl.add("movie", 1, "Filme X")
        self.sent = []

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, release_date):
        release = Release("movie", 1, "Filme X", release_date)
        with patch("tracker.checker.fetch_release", return_value=release):
            return check_watchlist(self.wl, 7, self.sent.append, today=TODAY)

    def test_notifies_release_within_window(self):
        self._run(date(2026, 10, 20))
        self.assertEqual(len(self.sent), 1)
        self.assertIn("estreia em 4 dias", self.sent[0])

    def test_notifies_only_once(self):
        self._run(date(2026, 10, 20))
        self._run(date(2026, 10, 20))
        self.assertEqual(len(self.sent), 1)

    def test_renotifies_if_date_changes(self):
        self._run(date(2026, 10, 20))
        self._run(date(2026, 10, 22))
        self.assertEqual(len(self.sent), 2)

    def test_ignores_far_past_and_undated(self):
        self._run(date(2026, 12, 1))  # longe demais
        self._run(date(2026, 10, 1))  # já passou
        self._run(None)  # sem data
        self.assertEqual(self.sent, [])


class TmdbTests(unittest.TestCase):
    @patch("tracker.tmdb.require_key", return_value="fake-key")
    @patch("tracker.tmdb.get_json")
    def test_tv_uses_next_episode(self, mock_get, _key):
        mock_get.return_value = {
            "name": "Série Z",
            "first_air_date": "2020-01-01",
            "next_episode_to_air": {
                "air_date": "2026-10-18",
                "season_number": 2,
                "episode_number": 5,
            },
        }
        release = tmdb.get_release("tv", 99)
        self.assertEqual(release.release_date, date(2026, 10, 18))
        self.assertEqual(release.note, "S02E05")


if __name__ == "__main__":
    unittest.main()
