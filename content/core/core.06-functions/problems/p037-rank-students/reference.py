def rank_students(records, *, top=None):
    """Return names ordered by marks (high first), ties by name ignoring case; only `top` if given."""
    ranked = sorted(records, key=lambda r: (-r[1], r[0].lower()))
    names = [name for name, marks in ranked]
    if top is None:
        return names
    return names[:top]
