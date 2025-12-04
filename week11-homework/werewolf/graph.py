from typing import Any, Dict, List, Optional, TypedDict
from langgraph.graph import END, StateGraph
from . import logger
from .agents import (
    GameConfig,
    GameMemory,
    PlayerConfig,
    Role,
    create_llm,
    generate_player_speech,
    generate_player_vote,
    generate_victim_vote,
)

class GameState(TypedDict):
    round: int
    max_rounds: int
    phase: str
    alive_players: List[str]
    dead_players: List[str]
    roles: Dict[str, Role]
    public_log: List[str]
    last_night_killed: Optional[str]
    last_voted_out: Optional[str]
    winner: Optional[str]


def init_players_and_state(config: GameConfig):
    players: List[PlayerConfig] = []
    cnt = 1
    for i in range(config.num_werewolves):
        players.append(
            PlayerConfig(
                name=f"玩家{cnt}",
                role="werewolf",
                personality="狡猾而善于伪装",
            )
        )
        cnt += 1
    
    for i in range(config.num_villagers):
        players.append(
            PlayerConfig(
                name=f"玩家{cnt}",
                role="villager",
                personality="谨慎而爱思考",
            )
        )
        cnt += 1

    roles: Dict[str, Role] = {p.name: p.role for p in players}

    initial_state: GameState = {
        "round": 1,
        "max_rounds": config.max_rounds,
        "phase": "night",
        "alive_players": [p.name for p in players],
        "dead_players": [],
        "roles": roles,
        "public_log": [],
        "last_night_killed": None,
        "last_voted_out": None,
        "winner": None,
    }

    memory = GameMemory()

    return players, memory, initial_state


def night_phase(
    state: GameState,
    config: GameConfig,
    players: List[PlayerConfig],
    memory: GameMemory,
) -> GameState:
    llm = create_llm(config.model_name)

    werewolves = [
        p for p in players if p.role == "werewolf" and p.name in state["alive_players"]
    ]
    villagers = [
        p for p in players if p.role == "villager" and p.name in state["alive_players"]
    ]

    if not werewolves or not villagers:
        return state

    candidate_names = [v.name for v in villagers]
    vote_collection: List[Dict[str, Any]] = []
    private_log = state["public_log"].copy()
    for wolf in werewolves:
        vote = generate_victim_vote(
            llm=llm,
            player=wolf,
            candidate_names=candidate_names,
            state_round=state["round"],
            public_log=private_log[-1] if private_log else [],
            memory=memory,
        )
        logger.debug(str(vote))
        vote_collection.append({"name": wolf.name, "role": wolf.role, "vote": vote['name'], 'reason': vote['reason']})
        private_log.append(f"当前轮{state['round']}: " + " ".join([vote['role']+vote["name"] + " 击杀 " + vote['vote'] +', 原因是' + vote['reason'] for vote in vote_collection]))

    chosen = [vote["vote"] for vote in vote_collection]

    state["last_night_killed"] = chosen[-1]
    state["public_log"].append(f"第{state['round']}轮: 夜晚，狼人联合击杀了 {chosen[-1]}（对外暂不公布过程）。")
    memory.add_event(f"第{state['round']}轮夜晚：狼人讨论并击杀了 {chosen[-1]}。")
    logger.debug(str(state))
    return state


def announce_phase(state: GameState, memory: GameMemory) -> GameState:
    killed = state.get("last_night_killed")
    if killed and killed in state["alive_players"]:
        state["alive_players"].remove(killed)
        state["dead_players"].append(killed)
        announcement = f"第{state['round']}轮：天亮了，昨晚死亡的是：{killed}。"
    else:
        announcement = f"第{state['round']}轮：天亮了，昨晚无人死亡。"

    state["public_log"].append(announcement)
    memory.add_event(announcement)
    return state


def discussion_phase(
    state: GameState,
    config: GameConfig,
    players: List[PlayerConfig],
    memory: GameMemory,
) -> GameState:
    llm = create_llm(config.model_name)

    for player_name in list(state["alive_players"]):
        player = next(p for p in players if p.name == player_name)

        if player.role == "werewolf":
            candidates = [
                p.name
                for p in players
                if p.name in state["alive_players"]
                and p.name != player.name
                and p.role == "villager"
            ]
        else:
            candidates = [
                p.name
                for p in players
                if p.name in state["alive_players"] and p.name != player.name
            ]

        speech = generate_player_speech(
            llm=llm,
            player=player,
            candidates=candidates,
            state_round=state["round"],
            public_log=state["public_log"],
            memory=memory,
        )
        log_line = f"第{state['round']}轮：[发言][{player.name}] {speech}"
        logger.debug(log_line)
        state["public_log"].append(log_line)
        memory.add_event(log_line)
    logger.debug(str(state))
    return state


def vote_phase(
    state: GameState,
    config: GameConfig,
    players: List[PlayerConfig],
    memory: GameMemory,
) -> GameState:
    llm = create_llm(config.model_name)

    votes: Dict[str, int] = {name: 0 for name in state["alive_players"]}

    for voter_name in list(state["alive_players"]):
        voter = next(p for p in players if p.name == voter_name)
        if len(state["alive_players"]) <= 1:
            continue
        target = generate_player_vote(
            llm=llm,
            player=voter,
            state_round=state["round"],
            public_log=state["public_log"],
            memory=memory,
            alive_players=state["alive_players"],
        )
        if target in votes:
            votes[target] += 1
        vote_log = f"第{state['round']}轮：[投票]{voter.name} 投票给 {target}。"
        logger.debug(vote_log)
        state["public_log"].append(vote_log)
        memory.add_event(vote_log)

    if votes:
        sorted_votes = sorted(votes.items(), key=lambda kv: kv[1], reverse=True)
        top_name, top_count = sorted_votes[0]
        if top_count > 0:
            state["last_voted_out"] = top_name
            if top_name in state["alive_players"]:
                state["alive_players"].remove(top_name)
                state["dead_players"].append(top_name)
            result_log = f"第{state['round']}轮：白天投票结果：{top_name} 被处决。"
        else:
            state["last_voted_out"] = None
            result_log = "第{state['round']}轮：白天投票无有效结果。"
    else:
        state["last_voted_out"] = None
        result_log = "第{state['round']}轮：白天无人参与投票。"

    state["public_log"].append(result_log)
    memory.add_event(result_log)
    logger.debug(str(state))
    return state


def check_end_condition(state: GameState) -> GameState:
    roles = state["roles"]
    alive_wolves = [p for p in state["alive_players"] if roles[p] == "werewolf"]
    alive_villagers = [
        p for p in state["alive_players"] if roles[p] == "villager"
    ]

    if not alive_wolves and alive_villagers:
        state["winner"] = "villagers"
    elif len(alive_wolves) >= len(alive_villagers) and alive_wolves:
        state["winner"] = "werewolves"
    elif state["round"] >= state["max_rounds"]:
        if alive_wolves:
            state["winner"] = "werewolves"
        else:
            state["winner"] = "villagers"

    return state


def build_game_graph(
    config: GameConfig,
    players: List[PlayerConfig],
    memory: GameMemory,
) -> StateGraph:
    graph = StateGraph(GameState)

    graph.add_node("night", lambda s: night_phase(s, config, players, memory))
    graph.add_node("announce", lambda s: announce_phase(s, memory))
    graph.add_node("discussion", lambda s: discussion_phase(s, config, players, memory))
    graph.add_node("vote", lambda s: vote_phase(s, config, players, memory))

    def after_vote(state: GameState) -> GameState:
        state = check_end_condition(state)
        if not state.get("winner"):
            state["round"] = state["round"] + 1
            state["phase"] = "night"
        logger.debug("After_vote: " + str(state))
        return state

    graph.add_node("after_vote", after_vote)

    graph.set_entry_point("night")

    def night_router(state: GameState) -> str:
        if state.get("winner", False):
            return "end"
        return "announce"

    graph.add_conditional_edges(
        "night",
        night_router,
        {"announce": "announce", "end": END},
    )

    def announce_router(state: GameState) -> str:
        if state.get("winner"):
            return "end"
        return "discussion"

    graph.add_conditional_edges(
        "announce",
        announce_router,
        {"discussion": "discussion", "end": END},
    )

    def discussion_router(state: GameState) -> str:
        if state.get("winner"):
            return "end"
        return "vote"

    graph.add_conditional_edges(
        "discussion",
        discussion_router,
        {"vote": "vote", "end": END},
    )

    graph.add_conditional_edges(
        "vote",
        lambda s: "after_vote",
        {"after_vote": "after_vote"},
    )

    def after_vote_router(state: GameState) -> str:
        if state.get("winner"):
            return "end"
        return "night"

    graph.add_conditional_edges(
        "after_vote",
        after_vote_router,
        {"night": "night", "end": END},
    )

    return graph
