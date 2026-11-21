def worth_it(minutes_per_run, runs_per_year, minutes_to_build, minutes_to_maintain_per_year, years=3):
    """Return (worth, minutes_saved) using the payoff formula of chapter 1.1."""
    if min(minutes_per_run, runs_per_year, minutes_to_build, minutes_to_maintain_per_year) < 0 or years < 1:
        raise ValueError("times and counts must not be negative, and years must be at least 1")
    saved = minutes_per_run * runs_per_year * years
    cost = minutes_to_build + minutes_to_maintain_per_year * years
    return saved > 2 * cost, saved
