from typing import Tuple

from .agents import GameConfig
from .graph import build_game_moderator, init_players_and_state
from .tracking import TraceCollector


def run_game(config: GameConfig) -> dict:
    players, memory, initial_state = init_players_and_state(config)
    app = build_game_moderator(config, players, memory)
    final_state = app.invoke(initial_state)
    return final_state


def run_game_with_trace(config: GameConfig) -> Tuple[dict, TraceCollector]:
    players, memory, initial_state = init_players_and_state(config)
    trace_collector = TraceCollector()
    app = build_game_moderator(config, players, memory, trace_collector)
    final_state = app.invoke(initial_state)
    return final_state, trace_collector
