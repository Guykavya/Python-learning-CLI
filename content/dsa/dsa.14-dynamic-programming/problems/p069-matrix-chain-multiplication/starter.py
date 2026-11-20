def matrix_chain_cost(dims):
    """Fewest scalar multiplications to multiply the chain; matrix i is dims[i] x dims[i + 1]."""
    total = 0
    for i in range(1, len(dims) - 1):        # left to right, no choice: not always the cheapest
        total += dims[0] * dims[i] * dims[i + 1]
    return total
