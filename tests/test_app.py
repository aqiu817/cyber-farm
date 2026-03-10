import json
import uuid
import unittest
from pathlib import Path

from app import GameState, SessionStore


class GameStateTests(unittest.TestCase):
    def test_legacy_plot_fields_are_normalized(self) -> None:
        legacy_payload = {
            "state": {
                "day": 3,
                "tickInDay": 0,
                "selectedPlot": 0,
                "inventory": {"turnip": 1, "tomato": 1, "melon": 1, "corn": 1},
            },
            "plots": [
                {"seed": "turnip", "moisture": 55, "growth": 2},
            ],
        }
        game = GameState.from_dict(legacy_payload)

        self.assertEqual(len(game.plots), 16)
        self.assertEqual(game.plots[0]["soilLevel"], 1)
        self.assertFalse(game.plots[0]["fertilized"])

    def test_fertilize_bonus_is_consumed_on_water(self) -> None:
        game = GameState()
        game.select(4)
        game.fertilize_selected()
        game.plant("turnip")

        before = game.plots[4]["growth"]
        game.water_selected()

        self.assertEqual(game.plots[4]["growth"], before + 2)
        self.assertFalse(game.plots[4]["fertilized"])


class SessionStoreTests(unittest.TestCase):
    def test_store_persists_state_and_accepts_debounce_config(self) -> None:
        test_dir = Path("data")
        test_dir.mkdir(parents=True, exist_ok=True)
        session_file = test_dir / f"test-session-{uuid.uuid4().hex}.json"
        try:
            store = SessionStore(session_file, save_debounce_ms=0)
            session_id, _, _ = store.ensure_session(None)
            store.mutate(session_id, lambda game: game.select(1))

            self.assertTrue(session_file.exists())
            payload = json.loads(session_file.read_text(encoding="utf-8"))
            self.assertIn("sessions", payload)
            self.assertIn(session_id, payload["sessions"])

            store.set_save_debounce_ms(250)
            self.assertAlmostEqual(store.save_debounce_seconds, 0.25)
        finally:
            if session_file.exists():
                session_file.unlink()


if __name__ == "__main__":
    unittest.main()
