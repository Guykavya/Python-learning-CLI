from datetime import datetime


def dedupe_latest(records: list[dict]) -> list[dict]:
    """One record per id: the latest updated_at; ties keep the last seen; first-seen id order."""
    best: dict[int, tuple[datetime, dict]] = {}
    for record in records:
        when = datetime.fromisoformat(record["updated_at"])
        current = best.get(record["id"])
        if current is None or when >= current[0]:   # >= : a tie lets the later record win
            best[record["id"]] = (when, record)       # replacing a key keeps its first position
    return [record for _, record in best.values()]
