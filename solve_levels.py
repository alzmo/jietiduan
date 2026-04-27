from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from solver import solve_level

MAX_SOLUTIONS = 10
MAX_NODES = 10000
LEVELS_DIR = Path("levels")
OUTPUT_DIR = Path("output")
OUTPUT_FILE = OUTPUT_DIR / "solve_results.json"


def _format_summary(result: Dict[str, Any]) -> str:
    keys = [
        "id",
        "status",
        "solvable",
        "solutionCount",
        "solutionCountCapped",
        "expandedNodes",
        "solution",
    ]
    return "\n".join(f"  {key}: {result.get(key)}" for key in keys)


def main() -> int:
    if not LEVELS_DIR.exists() or not LEVELS_DIR.is_dir():
        print(f"未找到关卡目录: {LEVELS_DIR.resolve()}")
        print("请先在项目根目录创建 levels/ 并放入关卡 JSON 文件。")

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        payload = {
            "maxSolutions": MAX_SOLUTIONS,
            "maxNodes": MAX_NODES,
            "levelsDir": str(LEVELS_DIR),
            "results": [],
            "error": f"levels directory not found: {LEVELS_DIR}",
        }
        with OUTPUT_FILE.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        print(f"已写入空结果文件: {OUTPUT_FILE.resolve()}")
        return 0

    level_files = sorted(LEVELS_DIR.glob("*.json"), key=lambda path: path.name)
    if not level_files:
        print(f"levels/ 下没有找到 .json 文件: {LEVELS_DIR.resolve()}")

    all_results: List[Dict[str, Any]] = []

    for level_file in level_files:
        file_result: Dict[str, Any] = {"file": level_file.name}

        try:
            with level_file.open("r", encoding="utf-8") as f:
                level_data = json.load(f)
            if not isinstance(level_data, dict):
                raise ValueError("关卡 JSON 顶层必须是对象(dict)。")

            solve_result = solve_level(
                level_data,
                max_solutions=MAX_SOLUTIONS,
                max_nodes=MAX_NODES,
            )
            file_result.update({"ok": True, "result": solve_result})

            print(f"[{level_file.name}] 解题摘要:")
            print(_format_summary(solve_result))

        except (OSError, json.JSONDecodeError, ValueError, TypeError) as exc:
            error_message = f"{type(exc).__name__}: {exc}"
            file_result.update({"ok": False, "error": error_message})
            print(f"[{level_file.name}] 处理失败: {error_message}")

        all_results.append(file_result)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "maxSolutions": MAX_SOLUTIONS,
        "maxNodes": MAX_NODES,
        "levelsDir": str(LEVELS_DIR),
        "results": all_results,
    }
    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"\n已写入结果文件: {OUTPUT_FILE.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
