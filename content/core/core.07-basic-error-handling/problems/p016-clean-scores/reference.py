def clean_scores(tokens):
    """Return (scores, rejected): valid 0-100 ints, and the tokens that were not."""
    scores = []
    rejected = []
    for token in tokens:
        try:
            value = int(token)
        except ValueError:
            rejected.append(token)
            continue
        if 0 <= value <= 100:
            scores.append(value)
        else:
            rejected.append(token)
    return scores, rejected
