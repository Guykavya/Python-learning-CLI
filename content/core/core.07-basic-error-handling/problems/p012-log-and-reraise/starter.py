def load_score(scores, name, log):
    """Return scores[name]. On KeyError, log 'missing score: <name>' and re-raise."""
    try:
        return scores[name]
    except KeyError:
        log.append("missing score: " + name)
        return None
