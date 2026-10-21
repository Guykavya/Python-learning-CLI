def clean_scores(tokens):
    """Return (scores, rejected): valid 0-100 ints, and the tokens that were not."""
    scores = []
    rejected = []
    for token in tokens:
        if token.isdigit():
            scores.append(int(token))
        else:
            rejected.append(token)
    return scores, rejected
