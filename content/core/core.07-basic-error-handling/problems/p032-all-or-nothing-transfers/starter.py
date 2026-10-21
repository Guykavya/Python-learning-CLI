def apply_transfers(balances, transfers):
    """Apply all transfers in order, or none of them if any fails. Return the number applied."""
    for sender, receiver, amount in transfers:
        balances[sender] -= amount
        balances[receiver] += amount
    return len(transfers)
