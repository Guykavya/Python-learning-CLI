def can_attend_all(meetings):
    """True if no two (start, end) meetings overlap; touching is fine."""
    ordered = sorted(meetings)
    for i in range(len(ordered) - 1):
        if ordered[i][1] > ordered[i + 1][0]:     # ends after the next one starts
            return False
    return True
