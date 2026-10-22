def parse_line(line: str) -> tuple[str, int] | None:
    parts = line.split(",")
    if len(parts) != 2:
        return None
    name = parts[0].strip()
    try:
        score = int(parts[1])
    except ValueError:
        return None
    if name == "" or score < 0 or score > 100:
        return None
    return name, score


def load(lines: list[str]) -> dict[str, list[int]]:
    book: dict[str, list[int]] = {}
    for line in lines:
        parsed = parse_line(line)
        if parsed is None:
            continue
        name, score = parsed
        book.setdefault(name, []).append(score)
    return book


def average(scores: list[int]) -> float:
    if not scores:
        return 0.0
    return sum(scores) / len(scores)


def ranking(book: dict[str, list[int]]) -> list[tuple[str, float]]:
    pairs = [(name, average(scores)) for name, scores in book.items()]
    return sorted(pairs, key=lambda pair: (-pair[1], pair[0]))


def best_student(book: dict[str, list[int]]) -> str | None:
    ranked = ranking(book)
    if not ranked:
        return None
    return ranked[0][0]


def report(book: dict[str, list[int]]) -> list[str]:
    return [f"{name}: {avg:.1f}" for name, avg in ranking(book)]
