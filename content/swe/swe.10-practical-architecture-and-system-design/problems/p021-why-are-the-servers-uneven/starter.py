def simulate(policy, durations, servers):
    # TODO: one request per time unit; FIFO per server; round_robin and least_connections
    return {"requests": [0] * servers, "busy": [0] * servers, "max_wait": 0}
