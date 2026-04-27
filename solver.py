from __future__ import annotations

from copy import deepcopy
from collections import Counter
from typing import Dict, List, Optional, Tuple


def solve_level(level: dict, max_solutions: int = 10, max_nodes: int = 10000) -> dict:
    """Solve one level with DFS and return minimal solver result."""

    level_id = level.get("id", "")
    basket_sequence: List[str] = list(level.get("basketSequence", []))
    blocks: List[dict] = list(level.get("blocks", []))

    if len(basket_sequence) < 2:
        return {
            "id": level_id,
            "solvable": False,
            "solution": [],
            "solutionCount": 0,
            "solutionCountCapped": False,
            "expandedNodes": 0,
            "status": "unsolvable",
        }

    remaining_blocks = _build_stacks(blocks)
    active_baskets = [
        {"color": basket_sequence[0], "count": 0},
        {"color": basket_sequence[1], "count": 0},
    ]

    first_solution: List[int] = []
    solution_count = 0
    expanded_nodes = 0
    node_limit_hit = False
    failed_states = set()

    def dfs(
        remaining: Dict[int, List[str]],
        baskets: List[dict],
        temp_storage: List[str],
        basket_index: int,
        path: List[int],
    ) -> None:
        nonlocal first_solution, solution_count, expanded_nodes, node_limit_hit

        if solution_count >= max_solutions:
            return
        if expanded_nodes >= max_nodes:
            node_limit_hit = True
            return

        expanded_nodes += 1

        if _all_cleared(remaining):
            solution_count += 1
            if not first_solution:
                first_solution = path[:]
            return

        state_key = _build_state_key(remaining, baskets, temp_storage, basket_index)
        if state_key in failed_states:
            return

        clickable_cells = _prioritize_clickable_cells(remaining, baskets, temp_storage)
        if not clickable_cells:
            failed_states.add(state_key)
            return

        solution_count_before = solution_count
        for cell_id in clickable_cells:
            if solution_count >= max_solutions:
                return
            if expanded_nodes >= max_nodes:
                node_limit_hit = True
                return

            next_remaining = deepcopy(remaining)
            next_baskets = deepcopy(baskets)
            next_temp = temp_storage[:]
            next_path = path + [cell_id]

            color = next_remaining[cell_id].pop()
            if not next_remaining[cell_id]:
                del next_remaining[cell_id]

            matched = False
            for basket in next_baskets:
                if basket["color"] == color:
                    basket["count"] += 1
                    matched = True
                    break

            if not matched:
                next_temp.append(color)
                if len(next_temp) > 5:
                    continue

            resolved = _resolve_baskets(next_baskets, next_temp, basket_sequence, basket_index)
            if resolved is None:
                continue

            resolved_baskets, resolved_temp, resolved_index = resolved
            if len(resolved_temp) > 5:
                continue

            dfs(next_remaining, resolved_baskets, resolved_temp, resolved_index, next_path)

        if (
            solution_count == solution_count_before
            and not node_limit_hit
            and solution_count < max_solutions
        ):
            failed_states.add(state_key)

    dfs(remaining_blocks, active_baskets, [], 2, [])

    if solution_count > 0:
        return {
            "id": level_id,
            "solvable": True,
            "solution": first_solution,
            "solutionCount": solution_count,
            "solutionCountCapped": solution_count >= max_solutions,
            "expandedNodes": expanded_nodes,
            "status": "solvable",
        }

    status = "unknown" if node_limit_hit else "unsolvable"
    return {
        "id": level_id,
        "solvable": False,
        "solution": [],
        "solutionCount": 0,
        "solutionCountCapped": False,
        "expandedNodes": expanded_nodes,
        "status": status,
    }


def _build_stacks(blocks: List[dict]) -> Dict[int, List[str]]:
    by_cell: Dict[int, List[Tuple[int, str]]] = {}
    for block in blocks:
        cell_id = int(block["cellId"])
        layer = int(block["layer"])
        color = str(block["color"])
        by_cell.setdefault(cell_id, []).append((layer, color))

    result: Dict[int, List[str]] = {}
    for cell_id, entries in by_cell.items():
        entries.sort(key=lambda item: item[0])
        result[cell_id] = [color for _, color in entries]
    return result


def _build_state_key(
    remaining: Dict[int, List[str]],
    baskets: List[dict],
    temp_storage: List[str],
    basket_index: int,
) -> Tuple[Tuple[Tuple[int, Tuple[str, ...]], ...], Tuple[Tuple[str, int], ...], Tuple[Tuple[str, int], ...], int]:
    remaining_key = tuple(
        (cell_id, tuple(stack)) for cell_id, stack in sorted(remaining.items(), key=lambda item: item[0])
    )
    baskets_key = tuple((str(basket["color"]), int(basket["count"])) for basket in baskets)
    temp_counter = Counter(temp_storage)
    temp_key = tuple(sorted(temp_counter.items(), key=lambda item: item[0]))
    return remaining_key, baskets_key, temp_key, basket_index


def _prioritize_clickable_cells(
    remaining: Dict[int, List[str]],
    baskets: List[dict],
    temp_storage: List[str],
) -> List[int]:
    basket_counts = {basket["color"]: int(basket["count"]) for basket in baskets}
    temp_colors = set(temp_storage)

    def sort_key(cell_id: int) -> Tuple[int, int, int, int, int]:
        color = remaining[cell_id][-1]
        in_basket = color in basket_counts
        distance_to_full = 3
        if in_basket:
            after_count = basket_counts[color] + 1
            distance_to_full = max(0, 3 - after_count)

        has_temp_match = color in temp_colors
        introduces_new_temp_color = 0 if (in_basket or has_temp_match) else 1

        return (
            0 if in_basket else 1,
            distance_to_full,
            0 if has_temp_match else 1,
            introduces_new_temp_color,
            cell_id,
        )

    clickable_cells = [cell_id for cell_id, stack in remaining.items() if stack]
    clickable_cells.sort(key=sort_key)
    return clickable_cells


def _all_cleared(remaining: Dict[int, List[str]]) -> bool:
    return not remaining


def _resolve_baskets(
    baskets: List[dict],
    temp_storage: List[str],
    basket_sequence: List[str],
    basket_index: int,
) -> Optional[Tuple[List[dict], List[str], int]]:
    while True:
        cleared_any = False

        for idx, basket in enumerate(baskets):
            if basket["count"] < 3:
                continue

            cleared_any = True
            if basket_index >= len(basket_sequence):
                return None

            new_color = basket_sequence[basket_index]
            basket_index += 1
            baskets[idx] = {"color": new_color, "count": 0}

            while True:
                try:
                    temp_idx = temp_storage.index(new_color)
                except ValueError:
                    break

                temp_storage.pop(temp_idx)
                baskets[idx]["count"] += 1
                if baskets[idx]["count"] >= 3:
                    break

        if not cleared_any:
            break

    return baskets, temp_storage, basket_index
