def counterexample():
    """Return (amount, machine, better) for coins 1, 3, 4, with amount != 6."""
    # 10: the machine pays 4 + 4 + 1 + 1 (four coins), but 4 + 3 + 3 is three coins.
    return (10, [4, 4, 1, 1], [4, 3, 3])
