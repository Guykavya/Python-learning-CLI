## Hint 1

Two separate questions. First: is there enough fuel in total? Compare `sum(gas)` with `sum(cost)`. Second, if there is: where to start? Write the **net gain** `gas[i] - cost[i]` for each station and look at where the running total goes negative.

## Hint 2

Drive from `start = 0` and keep a tank. If after station `i` the tank is negative, every start from `start` to `i` fails: each of them would arrive at `i` with no more fuel than you had (you reached them with a tank `>= 0`). So restart at `i + 1` with an empty tank. Because the total is not negative, the last restart point is the answer.

## Hint 3

```
if sum(gas) < sum(cost): return -1
tank = 0; start = 0
for i in range(n):
    tank += gas[i] - cost[i]
    if tank < 0:
        start = i + 1
        tank = 0
return start
```
