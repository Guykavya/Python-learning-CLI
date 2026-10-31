def ledger_problems(entries: list[dict], opening: int = 0) -> list[str]:
    """Every broken invariant in the ledger, in order, as readable messages."""
    problems = []
    seen_ids = set()
    previous_date = None
    balance = opening
    for i, entry in enumerate(entries):
        entry_id, date, amount = entry["id"], entry["date"], entry["amount"]
        if entry_id in seen_ids:
            problems.append(f"entry {i}: duplicate id {entry_id!r}")
        seen_ids.add(entry_id)
        if previous_date is not None and date < previous_date:
            problems.append(f"entry {i}: date {date} is before {previous_date}")
        previous_date = date
        balance += amount
        if balance < 0:
            problems.append(f"entry {i}: balance {balance} is negative")
    return problems
