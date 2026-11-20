def reconstruct_queue(people):
    order = sorted(((h, k) for h, k in people), key=lambda p: (-p[0], p[1]))
    queue = []
    for h, k in order:
        queue.insert(k, (h, k))
    return queue
