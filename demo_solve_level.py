import json

from solver import solve_level


def main() -> None:
    level = {
        "id": "LEVEL_DEMO_0001",
        "size": 8,
        "blocks": [
            {"code": "1.1.COLOR_1", "cellId": 1, "layer": 1, "color": "COLOR_1"},
            {"code": "2.1.COLOR_1", "cellId": 2, "layer": 1, "color": "COLOR_1"},
            {"code": "3.1.COLOR_1", "cellId": 3, "layer": 1, "color": "COLOR_1"},
        ],
        "basketSequence": ["COLOR_1", "COLOR_2", "COLOR_3"],
    }

    result = solve_level(level)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
