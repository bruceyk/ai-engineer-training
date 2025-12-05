from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class StepTrace:
    round: int
    phase: str
    player_name: Optional[str]
    role: Optional[str]
    step_type: str
    thought: str
    action: str
    observation: str
    extra: Dict[str, Any]


class TraceCollector:
    def __init__(self) -> None:
        self._steps: List[StepTrace] = []

    def add_step(self, step: StepTrace) -> None:
        self._steps.append(step)

    def get_steps(self) -> List[StepTrace]:
        return list(self._steps)

    def get_steps_by_round(self, round_number: int) -> List[StepTrace]:
        return [s for s in self._steps if s.round == round_number]

    def get_steps_by_player(self, player_name: str) -> List[StepTrace]:
        return [s for s in self._steps if s.player_name == player_name]

    def to_timeline(self) -> Dict[int, Dict[str, List[StepTrace]]]:
        timeline: Dict[int, Dict[str, List[StepTrace]]] = {}
        for step in self._steps:
            round_bucket = timeline.setdefault(step.round, {})
            phase_bucket = round_bucket.setdefault(step.phase, [])
            phase_bucket.append(step)
        return timeline

    def get_key_decisions_for_winner(self, winner: Optional[str]) -> List[StepTrace]:
        if not winner:
            return []
        key_types = {"victim_vote", "vote"}
        return [
            s
            for s in self._steps
            if s.step_type in key_types
        ]
