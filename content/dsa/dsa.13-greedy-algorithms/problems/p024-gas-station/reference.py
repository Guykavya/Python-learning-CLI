def can_complete_circuit(gas, cost):
    if sum(gas) < sum(cost):
        return -1
    tank = 0
    start = 0
    for i in range(len(gas)):
        tank += gas[i] - cost[i]
        if tank < 0:              # cannot get past station i from `start`
            start = i + 1         # so no station up to i works
            tank = 0
    return start
