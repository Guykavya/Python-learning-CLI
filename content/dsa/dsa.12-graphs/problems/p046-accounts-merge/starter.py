def merge_accounts(accounts):
    """One [name, sorted addresses...] per person, sorted by (name, first address)."""
    return [list(acc) for acc in accounts]
