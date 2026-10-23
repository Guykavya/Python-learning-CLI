def group_scores(pairs: list[tuple[str, int]]) -> dict[str, list[int]]:
    groups: dict[str, list[int]] = {}
    for name, score in pairs:
        groups.setdefault(name, []).append(score)
    return groups


def best_per_student(groups: dict[str, list[int]]) -> dict[str, int]:
    return {name: max(scores) for name, scores in groups.items()}


def students_above(groups: dict[str, list[int]], limit: float) -> list[str]:
    return sorted(name for name, scores in groups.items() if sum(scores) / len(scores) > limit)
