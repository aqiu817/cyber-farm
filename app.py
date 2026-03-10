#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import threading
import uuid
from copy import deepcopy
from dataclasses import dataclass, field
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
SITE_DIR = ROOT / "skills" / "cyber-farm" / "assets" / "site"
DATA_DIR = ROOT / "data"
SESSION_FILE = DATA_DIR / "farm_sessions.json"
SESSION_HEADER = "X-Farm-Session"
SESSION_COOKIE = "cyber_farm_session"
TICKS_PER_DAY = 4
DAYS_PER_SEASON = 4
DEFAULT_AUTO_TICK_SECONDS = 20
DEFAULT_SAVE_DEBOUNCE_MS = 600
WEATHER_ORDER = ["sunny", "breezy", "cloudy", "rainy"]
WEATHER_LABELS = {
    "sunny": "晴朗",
    "breezy": "微风",
    "cloudy": "多云",
    "rainy": "降雨",
}
SEASONS = ["spring", "summer", "autumn", "winter"]
SEASON_LABELS = {
    "spring": "春季",
    "summer": "夏季",
    "autumn": "秋季",
    "winter": "冬季",
}
MARKET_RATES = [0.9, 1.0, 1.1, 1.25]
RUNTIME_CONFIG = {"autoTickSeconds": DEFAULT_AUTO_TICK_SECONDS}
MISSION_TYPES = {
    "plant": {"label": "播种", "reward_coins": 18, "reward_energy": 6},
    "water": {"label": "浇水", "reward_coins": 16, "reward_energy": 4},
    "harvest": {"label": "收获", "reward_coins": 22, "reward_energy": 5},
    "sell": {"label": "卖货", "reward_coins": 20, "reward_energy": 4},
}

SEEDS: dict[str, dict[str, Any]] = {
    "turnip": {
        "label": "萝卜",
        "cost": 8,
        "growTime": 4,
        "bagKey": "turnip",
        "yield": 2,
        "sellPrice": 12,
        "preferredSeason": "spring",
        "sprite": {"row": 0, "group": 0},
    },
    "tomato": {
        "label": "番茄",
        "cost": 10,
        "growTime": 4,
        "bagKey": "tomato",
        "yield": 2,
        "sellPrice": 14,
        "preferredSeason": "summer",
        "sprite": {"row": 2, "group": 0},
    },
    "melon": {
        "label": "甜瓜",
        "cost": 14,
        "growTime": 4,
        "bagKey": "melon",
        "yield": 3,
        "sellPrice": 18,
        "preferredSeason": "summer",
        "sprite": {"row": 2, "group": 1},
    },
    "corn": {
        "label": "玉米",
        "cost": 12,
        "growTime": 4,
        "bagKey": "corn",
        "yield": 2,
        "sellPrice": 16,
        "preferredSeason": "autumn",
        "sprite": {"row": 9, "group": 0},
    },
}

INITIAL_PLOTS: list[dict[str, Any]] = [
    {"seed": "melon", "moisture": 88, "growth": 4},
    {"seed": "turnip", "moisture": 70, "growth": 2},
    {"seed": "corn", "moisture": 66, "growth": 3},
    {"seed": "tomato", "moisture": 84, "growth": 4},
    {"seed": None, "moisture": 0, "growth": 0},
    {"seed": "melon", "moisture": 76, "growth": 2},
    {"seed": "turnip", "moisture": 83, "growth": 4},
    {"seed": "corn", "moisture": 22, "growth": 2},
    {"seed": "tomato", "moisture": 63, "growth": 3},
    {"seed": "melon", "moisture": 91, "growth": 4},
    {"seed": "turnip", "moisture": 61, "growth": 2},
    {"seed": None, "moisture": 0, "growth": 0},
    {"seed": "corn", "moisture": 86, "growth": 4},
    {"seed": "tomato", "moisture": 68, "growth": 2},
    {"seed": "melon", "moisture": 28, "growth": 1},
    {"seed": "turnip", "moisture": 72, "growth": 2},
]


def mission_for_day(day: int) -> dict[str, Any]:
    cycle = ["plant", "water", "harvest", "sell"]
    mission_type = cycle[(day - 1) % len(cycle)]
    target = 1 if mission_type == "plant" else 2 + ((day - 1) % 2)
    info = MISSION_TYPES[mission_type]
    return {
        "type": mission_type,
        "label": info["label"],
        "target": target,
        "progress": 0,
        "claimed": False,
        "reward": {"coins": info["reward_coins"], "energy": info["reward_energy"]},
    }


def market_rate_for_day(day: int) -> float:
    return MARKET_RATES[(day - 1) % len(MARKET_RATES)]


def season_for_day(day: int) -> str:
    return SEASONS[((day - 1) // DAYS_PER_SEASON) % len(SEASONS)]


INITIAL_STATE: dict[str, Any] = {
    "energy": 72,
    "crops": 9,
    "water": 68,
    "coins": 248,
    "warehouse": 9,
    "selectedPlot": 0,
    "day": 9,
    "tickInDay": 0,
    "weather": "sunny",
    "season": season_for_day(9),
    "marketRate": market_rate_for_day(9),
    "inventory": {
        "turnip": 8,
        "tomato": 6,
        "melon": 5,
        "corn": 6,
    },
    "mission": mission_for_day(9),
}


@dataclass
class GameState:
    seeds: dict[str, dict[str, Any]] = field(default_factory=lambda: deepcopy(SEEDS))
    state: dict[str, Any] = field(default_factory=lambda: deepcopy(INITIAL_STATE))
    plots: list[dict[str, Any]] = field(default_factory=lambda: deepcopy(INITIAL_PLOTS))

    def __post_init__(self) -> None:
        self._normalize()

    @staticmethod
    def _as_int(value: Any, fallback: int) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return fallback

    @classmethod
    def _normalize_plot(cls, raw_plot: dict[str, Any]) -> dict[str, Any]:
        soil_level = cls._as_int(raw_plot.get("soilLevel", 1), 1)
        return {
            "seed": raw_plot.get("seed"),
            "moisture": max(0, min(100, cls._as_int(raw_plot.get("moisture", 0), 0))),
            "growth": max(0, cls._as_int(raw_plot.get("growth", 0), 0)),
            "soilLevel": max(1, min(3, soil_level)),
            "fertilized": bool(raw_plot.get("fertilized", False)),
        }

    def _normalize(self) -> None:
        for key in ("energy", "crops", "water", "coins", "warehouse", "selectedPlot", "day", "tickInDay"):
            self.state.setdefault(key, INITIAL_STATE[key])
        self.state["water"] = max(0, min(100, self._as_int(self.state.get("water"), INITIAL_STATE["water"])))
        self.state["day"] = max(1, self._as_int(self.state.get("day"), INITIAL_STATE["day"]))
        self.state["tickInDay"] = max(0, self._as_int(self.state.get("tickInDay"), 0))
        self.state["selectedPlot"] = max(0, self._as_int(self.state.get("selectedPlot"), 0))
        self.state.setdefault("inventory", {})
        inventory = self.state["inventory"]
        if not isinstance(inventory, dict):
            inventory = {}
            self.state["inventory"] = inventory
        for seed in self.seeds.values():
            bag_key = seed["bagKey"]
            inventory[bag_key] = max(0, self._as_int(inventory.get(bag_key, 0), 0))
        self.state.setdefault("weather", WEATHER_ORDER[(self.state["day"] - 1) % len(WEATHER_ORDER)])
        self.state.setdefault("season", season_for_day(self.state["day"]))
        self.state.setdefault("marketRate", market_rate_for_day(self.state["day"]))
        self.state.setdefault("mission", mission_for_day(self.state["day"]))

        raw_plots = self.plots if isinstance(self.plots, list) else []
        normalized = [self._normalize_plot(plot) for plot in raw_plots if isinstance(plot, dict)]
        if not normalized:
            normalized = [self._normalize_plot(plot) for plot in INITIAL_PLOTS]
        self.plots = normalized[: len(INITIAL_PLOTS)]
        while len(self.plots) < len(INITIAL_PLOTS):
            self.plots.append(self._normalize_plot(INITIAL_PLOTS[len(self.plots)]))
        self.state["selectedPlot"] = min(self.state["selectedPlot"], len(self.plots) - 1)

    def reset(self) -> str:
        self.state = deepcopy(INITIAL_STATE)
        self.plots = deepcopy(INITIAL_PLOTS)
        self._normalize()
        return "Farm has been reset to initial state."

    def selected_plot(self) -> dict[str, Any]:
        return self.plots[self.state["selectedPlot"]]

    def plot_status(self, plot: dict[str, Any]) -> str:
        if not plot["seed"]:
            return "empty"
        if plot["moisture"] < 30:
            return "dry"
        if plot["growth"] >= self.seeds[plot["seed"]]["growTime"]:
            return "ripe"
        return "grow"

    def _inc_mission(self, mission_type: str, amount: int = 1) -> None:
        mission = self.state["mission"]
        if mission["type"] != mission_type or mission["claimed"]:
            return
        mission["progress"] = min(mission["target"], mission["progress"] + amount)

    def _start_new_day(self) -> None:
        self.state["day"] += 1
        self.state["tickInDay"] = 0
        self.state["weather"] = WEATHER_ORDER[(self.state["day"] - 1) % len(WEATHER_ORDER)]
        self.state["season"] = season_for_day(self.state["day"])
        self.state["marketRate"] = market_rate_for_day(self.state["day"])
        self.state["mission"] = mission_for_day(self.state["day"])
        self.state["energy"] = min(100, self.state["energy"] + 8)
        self.state["water"] = min(100, self.state["water"] + 10)

    def serialize(self) -> dict[str, Any]:
        return {
            "state": deepcopy(self.state),
            "plots": deepcopy(self.plots),
            "seeds": deepcopy(self.seeds),
            "meta": {
                "weatherLabel": WEATHER_LABELS[self.state["weather"]],
                "seasonLabel": SEASON_LABELS[self.state["season"]],
                "ticksPerDay": TICKS_PER_DAY,
                "sellPriceEach": round(12 * self.state["marketRate"]),
            },
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "GameState":
        instance = cls()
        instance.seeds = deepcopy(payload.get("seeds", SEEDS))
        instance.state = deepcopy(payload.get("state", INITIAL_STATE))
        instance.plots = deepcopy(payload.get("plots", INITIAL_PLOTS))
        instance._normalize()
        return instance

    def select(self, plot_index: int) -> str:
        if plot_index < 0 or plot_index >= len(self.plots):
            raise ValueError("plot index out of range")
        self.state["selectedPlot"] = plot_index
        return f"已选中 {plot_index + 1} 号地。"

    def plant(self, seed_key: str) -> str:
        if seed_key not in self.seeds:
            raise ValueError("unknown seed")
        plot = self.selected_plot()
        seed = self.seeds[seed_key]
        if plot["seed"]:
            raise ValueError("selected plot already has a crop")
        if self.state["inventory"][seed["bagKey"]] <= 0:
            raise ValueError("seed inventory is empty")
        plot["seed"] = seed_key
        plot["moisture"] = 72
        plot["growth"] = 1
        self.state["inventory"][seed["bagKey"]] -= 1
        self.state["coins"] = max(0, self.state["coins"] - seed["cost"])
        self.state["energy"] = max(12, self.state["energy"] - 5)
        self._inc_mission("plant", 1)
        return f"{self.state['selectedPlot'] + 1} 号地已播下 {seed['label']}。"

    def water_selected(self) -> str:
        plot = self.selected_plot()
        if not plot["seed"]:
            raise ValueError("cannot water an empty plot")
        plot["moisture"] = min(100, plot["moisture"] + 22)
        growth_gain = 1
        if plot["fertilized"]:
            growth_gain += 1
            plot["fertilized"] = False
        plot["growth"] = min(self.seeds[plot["seed"]]["growTime"], plot["growth"] + growth_gain)
        self.state["water"] = max(8, self.state["water"] - 6)
        self.state["energy"] = max(8, self.state["energy"] - 3)
        self._inc_mission("water", 1)
        return f"{self.state['selectedPlot'] + 1} 号地已浇水。"

    def harvest_selected(self) -> str:
        plot = self.selected_plot()
        if not plot["seed"]:
            raise ValueError("selected plot is empty")
        if self.plot_status(plot) != "ripe":
            raise ValueError("crop is not ripe yet")
        seed = self.seeds[plot["seed"]]
        bonus = 1 if seed["preferredSeason"] == self.state["season"] else 0
        total_yield = seed["yield"] + bonus + max(0, plot["soilLevel"] - 1)
        self.state["warehouse"] += total_yield
        self.state["crops"] += total_yield
        self.state["energy"] = max(8, self.state["energy"] - 4)
        plot["seed"] = None
        plot["moisture"] = 0
        plot["growth"] = 0
        self._inc_mission("harvest", 1)
        return f"收获完成，仓库新增 {total_yield} 箱{seed['label']}。"

    def clear_selected(self) -> str:
        plot = self.selected_plot()
        if not plot["seed"]:
            raise ValueError("plot is already empty")
        plot["seed"] = None
        plot["moisture"] = 0
        plot["growth"] = 0
        self.state["energy"] = max(8, self.state["energy"] - 2)
        return f"{self.state['selectedPlot'] + 1} 号地已清理。"

    def fertilize_selected(self) -> str:
        plot = self.selected_plot()
        if self.state["coins"] < 10:
            raise ValueError("not enough coins to fertilize")
        if plot["fertilized"]:
            raise ValueError("plot is already fertilized")
        plot["fertilized"] = True
        self.state["coins"] -= 10
        return f"{self.state['selectedPlot'] + 1} 号地已施肥。"

    def upgrade_selected(self) -> str:
        plot = self.selected_plot()
        current_level = plot["soilLevel"]
        if current_level >= 3:
            raise ValueError("plot is already at max level")
        cost = current_level * 20
        if self.state["coins"] < cost:
            raise ValueError("not enough coins to upgrade plot")
        plot["soilLevel"] = current_level + 1
        self.state["coins"] -= cost
        return f"Plot {self.state['selectedPlot'] + 1} upgraded to Lv.{plot['soilLevel']}."

    def buy_seed(self, seed_key: str) -> str:
        if seed_key not in self.seeds:
            raise ValueError("unknown seed")
        seed = self.seeds[seed_key]
        if self.state["coins"] < seed["cost"]:
            raise ValueError("not enough coins")
        self.state["coins"] -= seed["cost"]
        self.state["inventory"][seed["bagKey"]] += 1
        return f"已购入 1 份{seed['label']}种子。"

    def sell(self, amount: int) -> str:
        if amount <= 0:
            raise ValueError("amount must be positive")
        if self.state["warehouse"] < amount:
            raise ValueError("not enough warehouse inventory")
        each_price = round(12 * self.state["marketRate"])
        self.state["warehouse"] -= amount
        self.state["crops"] = max(0, self.state["crops"] - amount)
        self.state["coins"] += amount * each_price
        self._inc_mission("sell", amount)
        return f"已卖出 {amount} 箱作物，单价 {each_price} 金币。"

    def claim_reward(self) -> str:
        mission = self.state["mission"]
        if mission["claimed"]:
            raise ValueError("mission reward already claimed")
        if mission["progress"] < mission["target"]:
            raise ValueError("mission is not complete yet")
        mission["claimed"] = True
        self.state["coins"] += mission["reward"]["coins"]
        self.state["energy"] = min(100, self.state["energy"] + mission["reward"]["energy"])
        return f"已领取每日任务奖励：{mission['reward']['coins']} 金币。"

    def tick(self) -> str:
        weather = self.state["weather"]
        season = self.state["season"]
        moisture_delta = {"sunny": -6, "breezy": -4, "cloudy": -2, "rainy": 6}[weather]
        for plot in self.plots:
            if not plot["seed"]:
                continue
            soil_level = plot["soilLevel"]
            adjusted_delta = moisture_delta + max(0, soil_level - 1)
            plot["moisture"] = max(0, min(100, plot["moisture"] + adjusted_delta))
            seed = self.seeds[plot["seed"]]
            if plot["moisture"] > 44 and plot["growth"] < seed["growTime"]:
                growth_gain = 1 + max(0, plot["soilLevel"] - 1)
                if plot["fertilized"]:
                    growth_gain += 1
                    plot["fertilized"] = False
                if weather == "rainy":
                    growth_gain += 1
                if seed["preferredSeason"] == season:
                    growth_gain += 1
                elif season == "winter":
                    growth_gain = max(1, growth_gain - 1)
                plot["growth"] = min(seed["growTime"], plot["growth"] + growth_gain)
        self.state["water"] = max(10, min(100, self.state["water"] + (3 if weather == "rainy" else -1)))
        self.state["tickInDay"] += 1
        message = f"时间向前推进了一轮，当前天气为{WEATHER_LABELS[weather]}。"
        if self.state["tickInDay"] >= TICKS_PER_DAY:
            self._start_new_day()
            message = f"新的一天开始了：Day {self.state['day']}，{SEASON_LABELS[self.state['season']]} / {WEATHER_LABELS[self.state['weather']]}。"
        return message


class SessionStore:
    def __init__(self, session_file: Path, save_debounce_ms: int = DEFAULT_SAVE_DEBOUNCE_MS) -> None:
        self.session_file = session_file
        self.lock = threading.RLock()
        self.sessions: dict[str, GameState] = {}
        self._save_timer: threading.Timer | None = None
        self.save_debounce_seconds = max(0.0, save_debounce_ms / 1000.0)
        self._load()

    def _load(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not self.session_file.exists():
            return
        try:
            payload = json.loads(self.session_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return
        raw_sessions = payload.get("sessions", {})
        if not isinstance(raw_sessions, dict):
            return
        for session_id, state_payload in raw_sessions.items():
            if isinstance(session_id, str) and isinstance(state_payload, dict):
                self.sessions[session_id] = GameState.from_dict(state_payload)

    def set_save_debounce_ms(self, debounce_ms: int) -> None:
        with self.lock:
            self.save_debounce_seconds = max(0.0, debounce_ms / 1000.0)
            if self.save_debounce_seconds <= 0 and self._save_timer:
                self._save_timer.cancel()
                self._save_timer = None

    def _save_now_locked(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        payload = {"sessions": {sid: game.serialize() for sid, game in self.sessions.items()}}
        tmp = self.session_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.session_file)

    def _flush_timer(self) -> None:
        with self.lock:
            self._save_timer = None
            self._save_now_locked()

    def _save_debounced_locked(self) -> None:
        if self.save_debounce_seconds <= 0:
            self._save_now_locked()
            return
        if self._save_timer:
            self._save_timer.cancel()
        self._save_timer = threading.Timer(self.save_debounce_seconds, self._flush_timer)
        self._save_timer.daemon = True
        self._save_timer.start()

    def flush(self) -> None:
        with self.lock:
            if self._save_timer:
                self._save_timer.cancel()
                self._save_timer = None
            self._save_now_locked()

    def ensure_session(self, session_id: str | None) -> tuple[str, GameState, bool]:
        with self.lock:
            if session_id and session_id in self.sessions:
                return session_id, self.sessions[session_id], False
            new_session_id = uuid.uuid4().hex
            game_state = GameState()
            self.sessions[new_session_id] = game_state
            self._save_debounced_locked()
            return new_session_id, game_state, True

    def snapshot(self, session_id: str) -> dict[str, Any]:
        with self.lock:
            return self.sessions[session_id].serialize()

    def mutate(self, session_id: str, operation: Any) -> tuple[str, dict[str, Any]]:
        with self.lock:
            message = operation(self.sessions[session_id])
            self._save_debounced_locked()
            return message, self.sessions[session_id].serialize()


store = SessionStore(SESSION_FILE)


class CyberFarmHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.session_id: str | None = None
        super().__init__(*args, directory=str(SITE_DIR), **kwargs)

    def do_GET(self) -> None:
        if self.path == "/api/health":
            self._resolve_session()
            self._send_json(HTTPStatus.OK, {"ok": True, "status": "healthy", "session": self.session_id})
            return
        if self.path == "/api/config":
            self._send_json(HTTPStatus.OK, {"ok": True, "config": RUNTIME_CONFIG})
            return
        if self.path == "/api/state":
            self._resolve_session()
            self._send_json(HTTPStatus.OK, {"ok": True, "session": self.session_id, "state": store.snapshot(self.session_id)})
            return
        super().do_GET()

    def do_POST(self) -> None:
        if not self.path.startswith("/api/"):
            self.send_error(HTTPStatus.NOT_FOUND, "Unknown API endpoint")
            return

        self._resolve_session()
        payload = self._read_json_body()
        try:
            if self.path == "/api/select":
                message, state = store.mutate(self.session_id, lambda game: game.select(int(payload.get("plot", -1))))
            elif self.path == "/api/action":
                message, state = store.mutate(self.session_id, lambda game: self._handle_action(game, payload))
            elif self.path == "/api/reset":
                message, state = store.mutate(self.session_id, lambda game: game.reset())
            elif self.path == "/api/tick":
                message, state = store.mutate(self.session_id, lambda game: game.tick())
            else:
                self.send_error(HTTPStatus.NOT_FOUND, "Unknown API endpoint")
                return
        except ValueError as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "session": self.session_id, "error": str(exc), "state": store.snapshot(self.session_id)})
            return

        self._send_json(HTTPStatus.OK, {"ok": True, "session": self.session_id, "message": message, "state": state})

    def _resolve_session(self) -> None:
        if self.session_id:
            return
        incoming = self.headers.get(SESSION_HEADER) or self._cookie_session()
        self.session_id, _, _ = store.ensure_session(incoming)

    def _cookie_session(self) -> str | None:
        raw_cookie = self.headers.get("Cookie")
        if not raw_cookie:
            return None
        cookie = SimpleCookie()
        cookie.load(raw_cookie)
        morsel = cookie.get(SESSION_COOKIE)
        return morsel.value if morsel else None

    def _handle_action(self, game: GameState, payload: dict[str, Any]) -> str:
        action = payload.get("type")
        if action == "plant":
            return game.plant(str(payload.get("seed", "")))
        if action == "water":
            return game.water_selected()
        if action == "harvest":
            return game.harvest_selected()
        if action == "clear":
            return game.clear_selected()
        if action == "buy":
            return game.buy_seed(str(payload.get("seed", "")))
        if action == "sell":
            return game.sell(int(payload.get("amount", 0)))
        if action == "fertilize":
            return game.fertilize_selected()
        if action == "upgrade_plot":
            return game.upgrade_selected()
        if action == "claim_reward":
            return game.claim_reward()
        raise ValueError("unknown action")

    def _read_json_body(self) -> dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(content_length) if content_length else b"{}"
        if not raw:
            return {}
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid json body: {exc.msg}") from exc

    def _send_json(self, status: HTTPStatus, data: dict[str, Any]) -> None:
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        if self.session_id:
            self.send_header(SESSION_HEADER, self.session_id)
            self.send_header("Set-Cookie", f"{SESSION_COOKIE}={self.session_id}; Path=/; SameSite=Lax")
        self.end_headers()
        self.wfile.write(payload)


class ReusableHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve the Cyber Farm site and JSON API.")
    parser.add_argument("--host", default="0.0.0.0", help="Host interface to bind to.")
    parser.add_argument("--port", type=int, default=4173, help="Port to listen on.")
    parser.add_argument(
        "--auto-tick-seconds",
        type=int,
        default=DEFAULT_AUTO_TICK_SECONDS,
        help="Automatic frontend tick interval in seconds (0 to disable).",
    )
    parser.add_argument(
        "--save-debounce-ms",
        type=int,
        default=DEFAULT_SAVE_DEBOUNCE_MS,
        help="Debounce window for session persistence writes in milliseconds.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not SITE_DIR.exists():
        raise SystemExit(f"Site directory not found: {SITE_DIR}")

    RUNTIME_CONFIG["autoTickSeconds"] = max(0, args.auto_tick_seconds)
    store.set_save_debounce_ms(max(0, args.save_debounce_ms))

    with ReusableHTTPServer((args.host, args.port), CyberFarmHandler) as httpd:
        print(f"Cyber Farm available at http://{args.host}:{args.port}")
        print(f"Agent API available at http://{args.host}:{args.port}/api/state")
        print(f"Runtime config endpoint: http://{args.host}:{args.port}/api/config")
        print(f"Frontend auto tick: {RUNTIME_CONFIG['autoTickSeconds']}s")
        print(f"Session save debounce: {max(0, args.save_debounce_ms)}ms")
        print(f"Persistent session store: {SESSION_FILE}")
        try:
            httpd.serve_forever()
        finally:
            store.flush()


if __name__ == "__main__":
    main()

