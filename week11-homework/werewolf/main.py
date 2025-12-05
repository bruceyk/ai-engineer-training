from pathlib import Path

from .agents import GameConfig
from .game_api import run_game

def main():
    # 可以根据需要修改最大轮数
    final_state = run_game(GameConfig(max_rounds=5))
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
