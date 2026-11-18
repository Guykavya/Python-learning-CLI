def reconstruct_queue(people):
    """people: (h, k) pairs. Return the original queue, front first, as a list of (h, k) tuples."""
    return sorted((h, k) for h, k in people)
