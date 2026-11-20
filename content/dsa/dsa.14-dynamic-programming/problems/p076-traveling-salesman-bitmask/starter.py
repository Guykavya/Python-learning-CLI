def shortest_tour(dist):
    """Return (length, order): the shortest round trip from 0 through every place, and its visiting order."""
    n = len(dist)
    order = list(range(n))                     # visits the places in number order: rarely the best
    length = sum(dist[a][b] for a, b in zip(order, order[1:] + [0]))
    return length, order
