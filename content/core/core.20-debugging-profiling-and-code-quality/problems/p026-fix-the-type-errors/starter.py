def parse_scores(lines: list[str]) -> dict[str, int]:
    """'name: score' lines -> {name: score}. Lines without a ':' are skipped."""
    scores = {}
    for line in lines:
        if ":" not in line:
            continue
        name, raw = line.split(":", 1)
        scores[name.strip()] = raw.strip()
    return scores


def best(scores: dict[str, int]) -> str:
    """Name with the highest score, or None when there are no scores."""
    if not scores:
        return None
    return max(scores, key=lambda name: scores[name])


def average(scores: dict[str, int]) -> float:
    """Mean score; 0.0 when there are no scores."""
    if not scores:
        return 0.0
    return sum(scores.values()) / len(scores)


def report(lines: list[str]) -> str:
    scores = parse_scores(lines)
    top = best(scores)
    return f"best: {top.upper()}, average: {average(scores):.1f}"
