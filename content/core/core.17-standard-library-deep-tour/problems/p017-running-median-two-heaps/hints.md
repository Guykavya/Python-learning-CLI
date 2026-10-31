## Hint 1

Where should a new number go? Compare it with the top of `low` (that is `-low[0]`): if `low` is empty or the number is `<=` that top, it belongs to the small half; otherwise to the big half. After that, one heap may be too big. Which way do you move one item to fix rule 2?

## Hint 2

Rebalance after each insert:
- if `len(low) > len(high) + 1`: pop the top of `low` and push it into `high`;
- if `len(high) > len(low)`: pop the top of `high` and push it into `low`.

Moving the **top** keeps rule 1 true. Remember the sign flip every time you touch `low`: push `-x`, read `-low[0]`.

## Hint 3

```
add(x):
    if not low or x <= -low[0]: heappush(low, -x)
    else:                       heappush(high, x)
    if len(low) > len(high) + 1: heappush(high, -heappop(low))
    elif len(high) > len(low):   heappush(low, -heappop(high))

median():
    if not low: raise ValueError
    if len(low) > len(high): return -low[0]
    return (-low[0] + high[0]) / 2
```
