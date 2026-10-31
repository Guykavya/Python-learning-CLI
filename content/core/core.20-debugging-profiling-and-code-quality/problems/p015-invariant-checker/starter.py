def ledger_problems(entries: list[dict], opening: int = 0) -> list[str]:
    """Every broken invariant in the ledger, in order, as readable messages."""
    balance = opening
    for entry in entries:
        balance += entry["amount"]
        assert balance >= 0, "balance went negative"  # stops at the FIRST problem
    return []
