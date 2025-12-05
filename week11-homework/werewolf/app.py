import streamlit as st

from werewolf.agents import GameConfig
from werewolf.game_api import run_game_with_trace


def render_timeline(final_state: dict, trace_collector) -> None:
    timeline = trace_collector.to_timeline()
    rounds = sorted(timeline.keys())
    selected_round = st.selectbox("选择轮次", rounds) if rounds else None
    if selected_round is None:
        st.info("暂无数据")
        return

    st.subheader(f"第 {selected_round} 轮 时间轴")
    for phase in ["night", "announce", "discussion", "vote", "after_vote"]:
        steps = timeline.get(selected_round, {}).get(phase, [])
        if not steps:
            continue
        with st.expander(f"阶段: {phase}"):
            for step in steps:
                st.markdown(
                    f"**玩家**: {step.player_name or '系统'} | **角色**: {step.role or '-'} | **类型**: {step.step_type}"
                )
                st.markdown(f"- Thought: {step.thought}")
                st.markdown(f"- Action: {step.action}")
                st.markdown(f"- Observation: {step.observation}")
                st.markdown("---")


def render_decision_trace(final_state: dict, trace_collector) -> None:
    winner = final_state.get("winner")
    st.write(f"最终胜利阵营: {winner}")
    key_steps = trace_collector.get_key_decisions_for_winner(winner)
    if not key_steps:
        st.info("暂无关键决策记录")
        return
    for step in key_steps:
        st.markdown(
            f"**Round {step.round} | {step.phase} | {step.player_name or '系统'} ({step.role or '-'})**"
        )
        st.markdown(f"- Thought: {step.thought}")
        st.markdown(f"- Action: {step.action}")
        st.markdown(f"- Observation: {step.observation}")
        st.markdown("---")


def render_logs(final_state: dict) -> None:
    st.subheader("公共日志回放")
    for line in final_state.get("public_log", []):
        st.write(line)


def main() -> None:
    st.title("狼人杀多 Agent 系统可视化")

    max_rounds = st.slider("最大轮数", 1, 10, 5)
    num_werewolves = st.slider("狼人数量", 1, 4, 2)
    num_villagers = st.slider("村民数量", 1, 8, 3)

    if st.button("开始一局游戏"):
        config = GameConfig(
            max_rounds=max_rounds,
            num_werewolves=num_werewolves,
            num_villagers=num_villagers,
        )
        final_state, trace_collector = run_game_with_trace(config)

        st.success(f"游戏结束，胜利阵营: {final_state.get('winner')}")

        tab_timeline, tab_decision, tab_logs = st.tabs(
            ["时间轴", "关键决策溯源", "原始日志"]
        )

        with tab_timeline:
            render_timeline(final_state, trace_collector)

        with tab_decision:
            render_decision_trace(final_state, trace_collector)

        with tab_logs:
            render_logs(final_state)


if __name__ == "__main__":
    main()
