from pathlib import Path

from .agents import GameConfig
from .graph import build_game_graph, init_players_and_state


def main():
    # 可以根据需要修改最大轮数
    config = GameConfig(max_rounds=5)

    players, memory, initial_state = init_players_and_state(config)
    graph = build_game_graph(config, players, memory)
    app = graph.compile()

    from IPython.display import Image, display
    # 尝试将图导出为图片（需要安装 graphviz）
    try:
        graph_filename = "workflow_graph.png"
        with open(graph_filename, 'wb') as f:
            f.write(app.get_graph().draw_mermaid_png())
    except:
        print("无法生成Mermaid图，请安装graphviz")

    final_state = app.invoke(initial_state)

    log_lines = final_state["public_log"]

    # 控制台打印
    print("\n=== 游戏结束 ===")
    print(f"胜利阵营: {final_state.get('winner')}")
    print("\n=== 游戏日志回放 ===")
    for line in log_lines:
        print(line)

    # 保存到文件，便于作业提交
    logs_dir = Path(__file__).resolve().parent / "game_log"
    logs_dir.mkdir(exist_ok=True)
    log_file = logs_dir / "game_log.txt"
    log_file.write_text("\n".join(log_lines), encoding="utf-8")
    print(f"\n游戏日志已保存到: {log_file}")


if __name__ == "__main__":
    main()
